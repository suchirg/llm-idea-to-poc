import discord
from discord.ext import commands
import boto3
import json
import os
from pathlib import Path
from github import Github
from dotenv import load_dotenv

load_dotenv()

# Configuration
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')

# Initialize clients
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix='!', intents=intents)
bedrock_client = boto3.client(
    service_name='bedrock-runtime',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
github_client = Github(GITHUB_TOKEN)

# State management
STATE_FILE = 'state.json'

# Claude model configuration
CLAUDE_MODEL_ID = "us.anthropic.claude-3-5-haiku-20241022-v1:0"

def call_claude(messages, max_tokens=2000):
    """Call Claude via AWS Bedrock"""
    # Convert messages to Bedrock format
    bedrock_messages = []
    for msg in messages:
        bedrock_messages.append({
            "role": msg["role"],
            "content": [{"text": msg["content"]}]
        })

    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": bedrock_messages
    }

    response = bedrock_client.invoke_model(
        modelId=CLAUDE_MODEL_ID,
        body=json.dumps(request_body)
    )

    response_body = json.loads(response['body'].read())
    return response_body['content'][0]['text']

def load_state():
    if Path(STATE_FILE).exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

async def create_status_message(channel):
    """Create a new status message and pin it"""
    msg = await channel.send(embed=get_status_embed())
    await msg.pin()
    current_idea['status_message_id'] = str(msg.id)
    save_state(current_idea)
    return msg

async def update_status_message():
    """Update the existing status message"""
    global status_message
    if status_message:
        await status_message.edit(embed=get_status_embed())

def get_status_embed():
    """Generate status embed based on current state"""
    embed = discord.Embed(title="🚀 Idea-to-POC Bot Status", color=0x00ff00)

    if not current_idea or not current_idea.get('thread_id'):
        embed.description = "**Status:** 🟢 Ready for new ideas!\n\nPost an idea below to get started."
        embed.color = 0x00ff00
    else:
        stage = current_idea.get('stage', 'unknown')
        stage_display = {
            'clarification': '💬 Asking clarifying questions',
            'spec_review': '📝 Reviewing specs',
            'building': '🔨 Building POC',
            'complete': '✅ Complete'
        }.get(stage, stage)

        embed.description = f"**Status:** {stage_display}"
        embed.color = 0xffaa00

        if current_idea.get('original_message'):
            idea_preview = current_idea['original_message'][:100]
            if len(current_idea['original_message']) > 100:
                idea_preview += "..."
            embed.add_field(name="Current Idea", value=idea_preview, inline=False)

        if current_idea.get('thread_id'):
            embed.add_field(name="Thread", value=f"<#{current_idea['thread_id']}>", inline=True)

        if current_idea.get('question_count'):
            embed.add_field(name="Questions Asked", value=str(current_idea['question_count']), inline=True)

    embed.set_footer(text="Use the template below to submit ideas with context")
    return embed

# Global state
current_idea = load_state()
status_message = None  # Will hold the pinned status message

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Monitoring channel ID: {DISCORD_CHANNEL_ID}')

    # Create or update status message
    global status_message
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if channel:
        # Check if we have a saved status message ID
        if current_idea.get('status_message_id'):
            try:
                status_message = await channel.fetch_message(int(current_idea['status_message_id']))
                await update_status_message()
            except discord.NotFound:
                status_message = await create_status_message(channel)
        else:
            status_message = await create_status_message(channel)

@bot.event
async def on_message(message):
    # Ignore bot messages
    if message.author == bot.user:
        return

    # Process commands first
    await bot.process_commands(message)

    # Only respond in the designated channel
    if message.channel.id != DISCORD_CHANNEL_ID:
        return

    # Don't process idea messages if it's a command
    if message.content.startswith('!'):
        return

    global current_idea

    # If this is a new idea (not in a thread or no current idea)
    if not isinstance(message.channel, discord.Thread) and not current_idea.get('thread_id'):
        await handle_new_idea(message)
    # If this is a response in the active thread
    elif isinstance(message.channel, discord.Thread) and str(message.channel.id) == current_idea.get('thread_id'):
        await handle_thread_response(message)

@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return

    global current_idea

    # Check if this is the ✅ reaction on the spec message
    if (str(reaction.emoji) == '✅' and
        current_idea.get('stage') == 'spec_review' and
        str(reaction.message.id) == current_idea.get('spec_message_id')):
        await build_poc(reaction.message)

async def handle_new_idea(message):
    global current_idea

    # Create a thread for this idea
    thread = await message.create_thread(name=f"Idea: {message.content[:50]}...")

    # Initialize state
    current_idea = {
        'thread_id': str(thread.id),
        'original_message': message.content,
        'stage': 'clarification',
        'conversation_history': [],
        'question_count': 0
    }
    save_state(current_idea)
    await update_status_message()

    # Ask first clarifying question
    await ask_clarifying_question(thread)

async def ask_clarifying_question(thread):
    global current_idea

    # Build conversation history for Claude
    messages = [
        {
            "role": "user",
            "content": f"I have a business idea: {current_idea['original_message']}\n\nI need you to ask me clarifying questions to understand this idea better. Ask ONE question at a time. Focus on understanding: the target users, the core problem being solved, key features needed for a POC, and technical requirements."
        }
    ]

    # Add conversation history
    for entry in current_idea['conversation_history']:
        messages.append({"role": "assistant", "content": entry['question']})
        messages.append({"role": "user", "content": entry['answer']})

    # Add prompt for next question or to generate specs
    if current_idea['question_count'] < 5:
        messages.append({
            "role": "user",
            "content": "Ask me the next most important clarifying question. Just ask the question, nothing else."
        })
    else:
        # Move to spec generation
        await generate_specs(thread)
        return

    question = call_claude(messages, max_tokens=500)
    current_idea['current_question'] = question
    save_state(current_idea)

    await thread.send(question)

async def handle_thread_response(message):
    global current_idea

    if current_idea['stage'] == 'clarification':
        # Store the answer
        current_idea['conversation_history'].append({
            'question': current_idea['current_question'],
            'answer': message.content
        })
        current_idea['question_count'] += 1
        save_state(current_idea)

        # Ask next question or generate specs
        await ask_clarifying_question(message.channel)

    elif current_idea['stage'] == 'spec_review':
        # Handle feedback on specs
        await handle_spec_feedback(message)

async def generate_specs(thread):
    global current_idea

    await thread.send("Got it! Let me generate the product and technical specs for this POC...")

    # Build context from conversation
    context = f"Original idea: {current_idea['original_message']}\n\n"
    context += "Clarifications:\n"
    for entry in current_idea['conversation_history']:
        context += f"Q: {entry['question']}\nA: {entry['answer']}\n\n"

    # Generate product spec
    product_spec = call_claude([{
        "role": "user",
        "content": f"{context}\n\nGenerate a brief product spec for this POC. Include: target users, core problem, key features (max 3-5 for POC), success criteria. Keep it under 300 words."
    }], max_tokens=2000)

    # Generate technical spec
    tech_spec = call_claude([{
        "role": "user",
        "content": f"{context}\n\nProduct Spec:\n{product_spec}\n\nGenerate a brief technical spec for this POC. Include: tech stack recommendation, architecture overview, key components, deployment approach. Keep it under 300 words."
    }], max_tokens=2000)

    # Post specs
    spec_message = await thread.send(
        f"## Product Spec\n\n{product_spec}\n\n## Technical Spec\n\n{tech_spec}\n\n"
        f"---\n\n✅ React with checkmark to build this POC, or reply with feedback to iterate on the specs."
    )

    await spec_message.add_reaction('✅')

    current_idea['stage'] = 'spec_review'
    current_idea['product_spec'] = product_spec
    current_idea['tech_spec'] = tech_spec
    current_idea['spec_message_id'] = str(spec_message.id)
    save_state(current_idea)
    await update_status_message()

async def handle_spec_feedback(message):
    global current_idea

    await message.channel.send("Got your feedback! Let me update the specs...")

    # Use Claude to iterate on specs based on feedback
    updated_specs = call_claude([{
        "role": "user",
        "content": f"Product Spec:\n{current_idea['product_spec']}\n\nTechnical Spec:\n{current_idea['tech_spec']}\n\nFeedback: {message.content}\n\nUpdate the specs based on this feedback. Return both updated specs in the same format."
    }], max_tokens=2000)

    # Parse and update specs (simple parsing, assumes Claude returns both)
    if "Product Spec" in updated_specs and "Technical Spec" in updated_specs:
        parts = updated_specs.split("Technical Spec")
        product_spec = parts[0].replace("Product Spec", "").strip()
        tech_spec = parts[1].strip()

        current_idea['product_spec'] = product_spec
        current_idea['tech_spec'] = tech_spec
        save_state(current_idea)

        spec_message = await message.channel.send(
            f"## Product Spec (Updated)\n\n{product_spec}\n\n## Technical Spec (Updated)\n\n{tech_spec}\n\n"
            f"---\n\n✅ React with checkmark to build this POC, or reply with more feedback."
        )

        await spec_message.add_reaction('✅')
        current_idea['spec_message_id'] = str(spec_message.id)
        save_state(current_idea)

async def build_poc(message):
    global current_idea

    thread = message.channel
    await thread.send("Building your POC... This may take a few minutes.")

    current_idea['stage'] = 'building'
    save_state(current_idea)
    await update_status_message()

    # Generate code using Claude
    code_response = call_claude([{
        "role": "user",
        "content": f"""Product Spec:
{current_idea['product_spec']}

Technical Spec:
{current_idea['tech_spec']}

Generate a complete, working POC codebase. Include:
1. All necessary source files with full implementation
2. Package/dependency configuration files
3. README with setup and deployment instructions
4. Any configuration files needed

Format your response as a JSON object with this structure:
{{
  "repo_name": "suggested-repo-name",
  "description": "brief repo description",
  "files": [
    {{"path": "file/path.ext", "content": "file content"}},
    ...
  ]
}}

Make this a real, deployable POC - not pseudocode or placeholders."""
    }], max_tokens=4000)

    try:
        # Parse the response
        code_json = json.loads(code_response)

        # Create GitHub repo
        user = github_client.get_user()
        repo = user.create_repo(
            name=code_json['repo_name'],
            description=code_json['description'],
            private=False,
            auto_init=True
        )

        # Add files to repo
        for file_info in code_json['files']:
            repo.create_file(
                path=file_info['path'],
                message=f"Add {file_info['path']}",
                content=file_info['content']
            )

        current_idea['stage'] = 'complete'
        current_idea['repo_url'] = repo.html_url
        save_state(current_idea)

        await thread.send(
            f"✅ POC built successfully!\n\n"
            f"**GitHub Repository:** {repo.html_url}\n\n"
            f"**Next Steps:**\n"
            f"1. Clone the repo: `git clone {repo.clone_url}`\n"
            f"2. Check the README for setup and deployment instructions\n"
            f"3. Deploy and share with users!\n\n"
            f"Ready for the next idea!"
        )

        # Reset state for next idea
        current_idea = {}
        save_state(current_idea)
        await update_status_message()

    except json.JSONDecodeError:
        await thread.send("❌ Failed to parse generated code. Let me try again...")
        await build_poc(message)
    except Exception as e:
        await thread.send(f"❌ Error creating repository: {str(e)}")
        current_idea['stage'] = 'spec_review'
        save_state(current_idea)

@bot.command(name='template')
async def post_template(ctx):
    """Post the idea submission template"""
    if ctx.channel.id != DISCORD_CHANNEL_ID:
        return

    template = """**Idea Submission Template** - Copy and fill this out for better results!

```
**Idea:** [One sentence description]

**Problem:** [What problem does this solve? Who has this problem?]

**Target Users:** [Who is this for? Be specific]

**Core Features (POC):**
- [Feature 1]
- [Feature 2]
- [Feature 3]

**Success Criteria:** [How will you validate this POC?]

**Tech Preferences (optional):** [Any specific tech requirements?]

**Reference Examples (optional):** [Similar products or inspiration]
```

**Example:**
```
**Idea:** SMS-based waitlist for small restaurants

**Problem:** Small restaurants lose customers during wait times because people leave. Existing solutions are too complex/expensive.

**Target Users:** Independent restaurant/cafe owners (1-2 locations)

**Core Features (POC):**
- Customers text to join waitlist
- Owner dashboard to see queue
- SMS notification when table ready
- Basic queue management

**Success Criteria:** 2-3 local cafes test it for a week

**Tech Preferences:** Simple deployment, cheap SMS (Twilio)

**Reference Examples:** Yelp Waitlist (simpler), Waitwhile (cheaper)
```

See `idea_template.md` for more details!"""

    await ctx.send(template)

@bot.command(name='status')
async def check_status(ctx):
    """Check current bot status"""
    if ctx.channel.id != DISCORD_CHANNEL_ID:
        return

    await ctx.send(embed=get_status_embed())

bot.run(DISCORD_BOT_TOKEN)
