# Idea to POC Bot

Discord bot that helps you go from idea to POC collaboratively.

## Setup

1. Install dependencies:
```bash
pip3 install -r requirements.txt
```

2. Create a `.env` file with:
```
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_CHANNEL_ID=your_channel_id
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_github_username
```

3. Run the bot:
```bash
python bot.py
```

## Getting tokens

### Discord Bot Token
1. Go to https://discord.com/developers/applications
2. Create New Application
3. Go to Bot → Add Bot
4. Copy the token
5. Go to OAuth2 → URL Generator
6. Select scopes: `bot`, permissions: `Send Messages`, `Read Messages`, `Add Reactions`, `Use Slash Commands`
7. Use generated URL to invite bot to your server

### Discord Channel ID
1. Enable Developer Mode in Discord (Settings → Advanced → Developer Mode)
2. Right-click the channel → Copy ID

### AWS Credentials (for Bedrock)
1. Go to AWS Console → IAM → Users
2. Create a new user or select existing user
3. Add permissions: `AmazonBedrockFullAccess`
4. Create access key (Access Keys tab → Create access key)
5. Copy the Access Key ID and Secret Access Key
6. **Important**: Ensure Claude Haiku 4.5 model access is enabled in AWS Bedrock console (us-east-1 region)
   - Go to AWS Bedrock Console → Model access
   - Request access to "Claude Haiku 4.5" if not already enabled

### GitHub Token
1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: `repo` (full control)

## Usage

### Getting Started

1. **Check bot status**: The bot maintains a pinned status message showing current state
2. **Get the template**: Type `!template` to see the idea submission template
3. **Submit an idea**: Post your idea (optionally using the template for better results)

### Workflow

1. Post an idea in the designated Discord channel
2. Bot creates a thread and asks clarifying questions - respond in the thread
3. Bot generates product + technical specs
4. Review and give feedback by replying in thread (or react with ✅ to approve)
5. React with ✅ to start building the POC
6. Bot creates a GitHub repo and posts deployment instructions
7. Status message updates automatically throughout the process

### Commands

- `!template` - Display the idea submission template
- `!status` - Check current bot status

### Status Display

The bot maintains a pinned status message that shows:
- Current state (Ready / Clarifying / Reviewing specs / Building / Complete)
- Current idea being worked on
- Link to active thread
- Progress indicators (questions asked, etc.)

### Idea Template

For best results, use the structured template when submitting ideas. It helps provide:
- Clear problem statement
- Target user definition
- Specific POC features
- Success criteria
- Tech preferences

Type `!template` in Discord or see `idea_template.md` for details.
