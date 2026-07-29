# Quick Start Guide

Get your Idea-to-POC bot running in 5 minutes!

## Prerequisites

- Python 3.8+
- Discord account
- GitHub account
- AWS account with Bedrock access

## Step-by-Step Setup

### 1. Install Dependencies

```bash
cd idea-to-poc
pip3 install -r requirements.txt
```

### 2. Set Up Discord Bot

1. Go to https://discord.com/developers/applications
2. Click "New Application" and give it a name (e.g., "Idea-to-POC Bot")
3. Go to "Bot" section → Click "Add Bot"
4. **Copy the bot token** (you'll need this for `.env`)
5. Enable these Privileged Gateway Intents:
   - Message Content Intent ✓
6. Go to "OAuth2" → "URL Generator"
7. Select scopes:
   - `bot` ✓
   - `applications.commands` ✓
8. Select bot permissions:
   - Send Messages ✓
   - Send Messages in Threads ✓
   - Create Public Threads ✓
   - Read Messages/View Channels ✓
   - Read Message History ✓
   - Add Reactions ✓
   - Manage Messages ✓ (for pinning status)
9. **Copy the generated URL** and open it in browser to invite bot to your server
10. Select your server and authorize

### 3. Get Discord Channel ID

1. In Discord, go to User Settings → Advanced → Enable "Developer Mode"
2. Right-click the channel where you want the bot to work
3. Click "Copy ID" - this is your `DISCORD_CHANNEL_ID`

### 4. Set Up AWS Bedrock Access

1. **Enable Bedrock Model Access**:
   - Go to AWS Console → Bedrock → Model access (in us-east-1 region)
   - Click "Manage model access" or "Enable specific models"
   - Find "Claude Haiku 4.5" and enable it
   - Wait for status to show "Access granted" (usually instant)

2. **Create IAM User with Bedrock Access**:
   - Go to AWS Console → IAM → Users
   - Click "Create user"
   - Give it a name (e.g., "bedrock-bot-user")
   - Click "Next"
   - Select "Attach policies directly"
   - Search for and select `AmazonBedrockFullAccess`
   - Click "Next" → "Create user"

3. **Create Access Keys**:
   - Click on your newly created user
   - Go to "Security credentials" tab
   - Scroll to "Access keys" → Click "Create access key"
   - Select "Application running outside AWS"
   - Click "Next" → "Create access key"
   - **Copy both the Access Key ID and Secret Access Key** (you can't see the secret again!)

### 5. Get GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a note (e.g., "Idea-to-POC Bot")
4. Select scopes:
   - `repo` (Full control of private repositories) ✓
5. Click "Generate token" at bottom
6. **Copy the token immediately** (you can't see it again!)

### 6. Create Your `.env` File

```bash
cp .env.example .env
```

Edit `.env` with your values:

```
DISCORD_BOT_TOKEN=your_bot_token_from_step_2
DISCORD_CHANNEL_ID=your_channel_id_from_step_3
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key_from_step_4
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_from_step_4
GITHUB_TOKEN=your_github_token_from_step_5
GITHUB_USERNAME=your_github_username
```

### 7. Run the Bot

```bash
python bot.py
```

You should see:
```
<BotName>#1234 has connected to Discord!
Monitoring channel ID: 123456789...
```

### 8. Test It Out!

1. Go to your designated Discord channel
2. Type `!template` to see the idea submission template
3. Post an idea (try the example from the template!)
4. Watch the bot create a thread and start asking questions
5. Answer the questions in the thread
6. Review the generated specs
7. React with ✅ to build the POC
8. Get your GitHub repo!

## Troubleshooting

### Bot doesn't respond to messages
- Check that Message Content Intent is enabled in Discord Developer Portal
- Verify the bot has permissions to read/send messages in the channel
- Make sure `DISCORD_CHANNEL_ID` matches the channel you're posting in

### Bot can't create threads
- Ensure bot has "Create Public Threads" permission
- Check that the channel allows threads

### Bot can't pin status message
- Grant "Manage Messages" permission to the bot

### GitHub repo creation fails
- Verify your GitHub token has `repo` scope
- Check that `GITHUB_USERNAME` is correct
- Make sure you haven't hit GitHub's rate limit

### AWS Bedrock / Claude errors
- Verify your AWS credentials are correct
- Check that you enabled model access for Claude Haiku 4.5 in Bedrock console
- Make sure you're using us-east-1 region (or update `AWS_REGION` in `.env`)
- Verify IAM user has `AmazonBedrockFullAccess` permission
- Check AWS CloudWatch logs for detailed error messages

## Next Steps

- Customize the clarifying questions by editing `bot.py`
- Adjust the spec generation prompts for your specific needs
- Add more commands for your workflow
- Deploy to a server so it runs 24/7 (not just on your laptop)

## Support

Issues? Check the main README.md or create an issue on GitHub.
