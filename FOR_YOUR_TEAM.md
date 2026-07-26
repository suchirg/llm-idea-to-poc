# For Your Team: Using the Idea-to-POC Bot

Hey team! Here's how to use our new bot to turn ideas into POCs.

## What This Bot Does

Posts an idea → Bot asks questions → Reviews specs with you → Generates working code → Creates GitHub repo

No more spending hours scaffolding projects or debating tech stacks. The bot handles it.

## How to Use It

### 1. Check If Bot Is Ready

Look for the pinned status message at the top of the channel. If it says "Ready for new ideas", you're good to go.

**One idea at a time** - if someone else is working through an idea, wait for it to complete.

### 2. Get the Template (Optional but Recommended)

Type: `!template`

The bot will post a template. Using it gives better results because you provide more context upfront.

### 3. Post Your Idea

Either:
- **Quick version**: Just describe your idea naturally
- **Better version**: Use the template (copy, fill out, post)

**Example without template:**
```
I want to build a tool where users can vote on feature requests for products
```

**Example with template:**
```
**Idea:** Public feature voting board for SaaS products

**Problem:** Companies don't know which features users actually want. Users feel unheard.

**Target Users:** SaaS companies with 10-1000 customers

**Core Features (POC):**
- Public board where anyone can submit feature requests
- Upvoting on requests
- Admin dashboard to see top requests
- Email notifications when status changes

**Success Criteria:** We use it ourselves for a week and find it useful

**Tech Preferences:** Fast to deploy, works on mobile

**Reference Examples:** Canny, ProductBoard (but way simpler)
```

### 4. Answer Questions in the Thread

The bot will:
1. Create a thread for your idea
2. Ask ~5 clarifying questions
3. Answer them in the thread (not the main channel)

Be specific in your answers. The better your answers, the better the POC.

### 5. Review the Specs

After questions, the bot generates:
- **Product Spec** - what the POC does, who it's for, key features
- **Technical Spec** - tech stack, architecture, how to deploy

**Now you have 2 options:**

**Option A - Good to go:** React with ✅ to the spec message

**Option B - Need changes:** Reply in the thread with feedback like:
- "Make it work offline"
- "Use Python instead of Node"
- "Add authentication"
- "Remove the analytics feature"

The bot will update the specs. Keep iterating until you're happy, then react with ✅.

### 6. Get Your POC

The bot will:
1. Generate complete, working code
2. Create a GitHub repo under the configured account
3. Post the repo link and deployment instructions

Then you can:
- Clone it: `git clone <repo-url>`
- Follow the README to deploy
- Share it with users to test the idea

### 7. Start the Next Idea

Once a POC is complete, the bot resets and the status message shows "Ready for new ideas". Next person can go!

## Tips for Success

### Write Better Ideas
- **Be specific about the problem**: "Restaurants lose customers during waits" > "Restaurants have problems"
- **Define your users narrowly**: "Freelance designers" > "Creative professionals"
- **Limit POC features**: Pick 3-5 core features max. You're validating an idea, not building a product.
- **Include success criteria**: How will you know if this idea is worth pursuing?

### During Clarification
- Answer questions concretely: "Yes, real-time updates are critical" > "Yeah, real-time would be nice"
- Reference existing products as examples: "Like Typeform but for..."
- Mention technical constraints: "Needs to work on mobile", "Must be free to host"

### When Reviewing Specs
- Check that the POC is actually buildable in a reasonable time
- Make sure it tests your core hypothesis
- Don't scope creep - save nice-to-haves for later

### After Getting Your Repo
- Actually deploy and test it (don't just clone and forget)
- Get it in front of real users quickly
- Report back to the team whether it validated or invalidated the idea

## Commands

- `!template` - Show the idea submission template
- `!status` - Check current bot status (though the pinned message shows this too)

## Troubleshooting

**"I posted an idea but the bot didn't respond"**
- Is another idea already in progress? Check the status message.
- Did you post in the right channel?
- Is the bot online? (You'll see it as "online" in the member list)

**"The bot is stuck/not responding in the thread"**
- Tag someone who can restart it
- Check if there was an error message

**"I want to change my idea after starting"**
- Just give feedback on the specs when they're posted
- You can iterate as many times as needed before building

**"The generated code doesn't work"**
- The bot generates real code, but it's a POC - some assembly required
- Check the README in the generated repo
- If something is fundamentally broken, start a new idea with more specific tech requirements

## Remember

The goal is **speed** and **validation**, not perfection. 

- POCs should take hours to deploy, not days
- Test with real users as soon as possible  
- Kill bad ideas quickly and move to the next one
- Use what you learn to refine your next idea

Good luck! 🚀
