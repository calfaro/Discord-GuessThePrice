# Discord - GuessThePrice Bot
A simple betting/prediction bot that allows members to submit predictions on NFT auctions - A winner is the member with the closest prediction without going over the final price.

### Heroku hosting ready


### Discord Bot Token and Server Invitation

1. Login to Discord web - https://discord.com
2. Navigate to Discord Developer Portal - https://discord.com/developers/applications
3. Click *New Application*
4. Give the Appplication a name and *Create*
5. Add image for Discord icon
6. Go to Bot tab and click *Add Bot*
7. Enable **SERVER MEMBERS INTENT**
8. Add a bot image
9. Copy the token - you'll need this for step 4 in the Heroku instructions.
10. Navigate to OAuth2 Tab > URL Generator
11. Check **BOT** and **applications.commands** under the SCOPES section (note slash commands may take up to 1 hour to register with Discord)
12. In the BOT PERMISSIONS section, check the following:
    - Read Messages/View Channels
    - Send Messages
    - Attach Files
    - Embed Links

13. Copy the GENERATED URL link and paste it into your browser or in a discord message. Click the link to invite the bot


### Getting Started
**Github**
1. Login to github
2. Fork this repo - make it private


**Heroku**
1. Login to Heroku - https://id.heroku.com/login
2. Create a new app - give it a name
3. Settings > Config vars - Reveal Config Vars
4. Replace KEY with TOKEN and VALUE with your bot token from above (step 9)
5. Add and head back to Deploy
6. Deployment Method - Connnect with Github
7. Add the forked repo to your Heroku account
8. Select the branch to deploy
9. Deploy the branch
10. Navigate to Resources tab - Dynos
11. Click Edit icon - enable the worker
12. Save
13. Top right corner - More - View Logs
14. Should see the bot load and print the message line that the bot is online and ready.

