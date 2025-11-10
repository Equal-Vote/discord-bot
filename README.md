# discord-bot
Discord Bot for running star elections


## Adding bot to a server

1. Enable Developer Mode for your User: User Gear -> App Settings -> Advanced -> Developer Mode
1. [Add bot to server where you have admin access](https://discord.com/oauth2/authorize?client_id=1019135068805005333&permissions=534723950656&scope=bot%20applications.commands)
1. Reference [bettervoting.py](https://github.com/Equal-Vote/discord-bot/blob/main/bettervoting.py) for commands (example: ``.list_star_candidates "Yoda" "Han Solo"``)


## Running Personal Instance

1. **Clone the repository**:
   ```bash
   git clone git@github.com:Equal-Vote/discord-bot.git
   cd discord-bot
   ```
2. **Install Dependencies**:
   Ensure you have Python 3.10+ and pip installed.  Then run:
   ```bash
   pip install -r requirements.txt
   ```
3. **Create a Discord Application and Bot User**:
   * Go to the Discord Developer Portal.
   * Create a new application and add a Bot user.
   * Copy the Bot Token from the Developer Portal.
4. **Enable Priviledged Intents**
   * Under your appication -> Bot -> Priviledged Gateway intents, enable all 3 intents
5. **Set environment variables**:
   Create a `.env` file in the project directory, and:
   ```env
   DISCORD_TOKEN=your-token-here
   ```
   Of course, use the token you copied in the previous step in place of `your-token-here`.
6. **Run the bot**:
   ```bash
   python bettervoting.py
   ```
   If successful, you should see
   ```
   YourBotName#XXXX has connected to Discord!
   ```
7. **Invite the bot to your server**:
   * In the Discord Developer Portal's OAuth2 tab, select the `bot` and `applications.commands` scopes.
   * Copy the generated invite link and open it in a browser.
   * Authorize the bot to join your server.



