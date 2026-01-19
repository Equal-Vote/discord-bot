import discord
from discord.ext import commands
from discord import app_commands

import jwt
import asyncio
import os
import schedule
from dotenv import load_dotenv
import multiprocessing
import subprocess
import time

import sqlite3

from STARCustomLibs import BVWebInteract as BVI, PunkinLogging
from Views import PollViews

   

#TODO implement error handling
#TODO deintegrate DiscordBotAssist
if __name__ == "__main__":
    print("Preparing Bot")
    #create bot and assign it to DiscordBotAssist, as well as toggle the TOKEN.
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    bot = commands.Bot(intents=intents, command_prefix="debug")
    #tree = app_commands.CommandTree(bot)

    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    #jwt_secret_key = os.getenv('JWT_SECRET_KEY')
    #jwt_token = os.getenv('JWT_TOKEN')

    #dictionary containing BVI Translator objects. There is one per election
    elections: BVI.BVWebTranslator = {}
    views = {}

    #Command to get an election from better voting and begin voting in discord
    #command syntax is /linkpoll [electionID]
    @bot.tree.command(
        name="link_poll",
        description="Link a poll from bettervoting.com using the electionID"
    )
    @app_commands.describe(
        electionid="The ID of the poll to link"
    )
    async def link_poll(interaction: discord.Interaction, electionid: str):
        #With election object created, create view and send message for ballot casting. Then save the data to the database to be pulled after redeploy
        view = await pollLink(interaction, electionid)
        msg = await interaction.response.send_message(embed = view.titleTXT, view=view)
        view.saveToSQL(msg.message_id, interaction.channel_id)

    async def pollLink(interaction: discord.Interaction, electionid: str) -> discord.ui.View:
        Translator: BVI.BVWebTranslator = BVI.BVWebTranslator()
        Translator.createToken("DisBot")
        try:
            Translator.assignElection(electionid)
            Translator.cookieLead = "vd-"
        except:
            interaction.response.send_message("Oops! That is not a valid election ID")
        elections[electionid] = Translator
        
        #With election object created, create view and send message for ballot casting. Then save the data to the database to be pulled after redeploy
        view = PollViews.InitBallot(bot, elections[electionid].electJSON, Translator)
        views[electionid] = view
        return view

    @bot.event
    async def on_message(message: discord.Message):
        #this functionality isnt ready yet
        return
        #Is message from self or is the message not a poll? If so ignore it
        #Bot never does the standard check if the message is from itself as it should not send discord native polls
        if message.poll == None:
            return
        
        #If the message is a poll respond with the turnToBV view which alows the user to turn it into a STAR poll
        view = PollViews.turnToBV(bot, message)
        await message.reply(view=view)
    

    @bot.event
    async def on_ready():
        await bot.change_presence(status= discord.Status.invisible)
        print("Logged into discord. Appearing offline until ready.")
        print("Syncing persistent views. InitBallot views from before this deployment will be unusable until this is done")
        #TODO safeguard against rate limiting
        #Make previous InitBallot views functional
        if os.path.exists(os.getenv("BOT_DATABASE_PATH")):
            database = sqlite3.connect(os.getenv("BOT_DATABASE_PATH"))
            db = database.cursor()
            db.execute("SELECT * FROM InitBallots")
            rows = db.fetchall()

            msg: discord.Message = None
            Translator: BVI.BVWebTranslator = None
            for i in range(len(rows)):
                msg = await bot.get_channel(rows[i][2]).fetch_message(rows[i][1])
                view = await pollLink(None, rows[i][3])
                await msg.edit(view=view)
            print("Persistent views synced. Prior InitBallots are usable")   
        else:
            print("No database found. If this is the first deployment, this is normal. If not, please check your environment variable BOT_DATABASE_PATH")
        
        #set up slash commands
        print("Syncing slash commands")
        try:
            await bot.tree.sync()
            print("Slash commands synced")
        except Exception as e:
            print(f"Error syncing slash commands: {e}")
            exit(1)
        
        await bot.change_presence(status=discord.Status.online)
        print("Bot is fully ready. Appearing online")
    
    def databaseFailsafe():
        #run databaseFailsafe twice a day
        while True:
            subprocess.run(["./databaseFailsafe"])
            time.sleep(43200)
    #run bot and database failsafe
    #botRun = multiprocessing.Process(runBot)
    failsafe = multiprocessing.Process(target=databaseFailsafe)
    failsafe.start()

    bot.run(TOKEN)

    
        
    


