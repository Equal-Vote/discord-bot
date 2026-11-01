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
import threading
import time
import crontab
import datetime

import sqlite3

from STARCustomLibs import BVWebInteract as BVI, PunkinLogging, rateLimitCheck
from Views import PollViews

   

#TODO implement error handling
#TODO deintegrate DiscordBotAssist
if __name__ == "__main__":
    logger = PunkinLogging.logWrapper()
    logger.log("Deploying Bot. Beginning startup")
    #create bot 
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
    initBallotViews = PollViews.InitBallotTracker()

    #Object that tracks rate limiting
    rateLimits = rateLimitCheck.rateCheck()

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

        index = await pollLink(interaction, electionid)
        await rateLimits.wait()
        msg = await interaction.response.send_message(embeds = initBallotViews.initBallots[index].titleTXT, view=initBallotViews.initBallots[index])
        initBallotViews.initBallots[index].saveToSQL(msg.message_id, interaction.channel_id)

    async def pollLink(interaction: discord.Interaction, electionid: str) -> str:
        Translator: BVI.BVWebTranslator = BVI.BVWebTranslator()
        Translator.createToken("DisBot")
        try:
            Translator.assignElection(electionid)
            Translator.cookieLead = "vd-"
        except:
            await rateLimits.wait()
            interaction.response.send_message("Oops! That is not a valid election ID")
        elections[electionid] = Translator
        
        #With election object created, create view and send message for ballot casting. Then save the data to the database to be pulled after redeploy
        view = PollViews.InitBallot(bot, elections[electionid].electJSON, Translator, rateLimits, interaction)
        index = initBallotViews.addInitBallot(view)
        return str(index)

    @bot.event
    async def on_message(message: discord.Message):
        #Is message from self or is the message not a poll? If so ignore it
        #Bot never does the standard check if the message is from itself as it should not send discord native polls
        if message.poll == None:
            return
        
        #If the message is a poll respond with the turnToBV view which alows the user to turn it into a STAR poll
        view = PollViews.turnToBV(bot, message, initBallotViews, rateLimits)
        await rateLimits.wait()
        sentMessage : discord.Message = await message.reply(view=view)
        #this function is necessary so the message can delete itself after 5 minutes
        view.ownData(sentMessage.channel.id, sentMessage.id)
        
    

    @bot.event
    async def on_ready():
        #Immediate API request for logging in
        await rateLimits.wait()
        #start doing loops to check for rate limiting
        bot.loop.create_task(rateLimitLoop())
        bot.loop.create_task(databaseFailsafeLoop())
        bot.loop.create_task(checkInitBallots())
        await rateLimits.wait()
        await bot.change_presence(status= discord.Status.invisible)
        #exists as a workaround since git doesnt take empty dirs
        if not os.path.exists("graphTemp"):
            os.makedirs("graphTemp")
        logger.log("Logged into discord. Appearing offline until ready.")
        logger.log("Syncing persistent views. InitBallot views from before this deployment will be unusable until this is done")
        #TODO safeguard against rate limiting
        #Make previous InitBallot views functional
        if os.path.exists(os.getenv("BOT_DATABASE_PATH")):
            database = sqlite3.connect(os.getenv("BOT_DATABASE_PATH"))
            db = database.cursor()
            db.execute("SELECT * FROM InitBallots")
            rows = db.fetchall()

            msg: discord.Message = None
            Translator: BVI.BVWebTranslator = None
            

            #Replace InitBallot Views in batches of 40 to avoid rate limiting and overloading hardware
            async def replaceInitBallot(column1, column2, column3):
                try:
                    await rateLimits.wait()
                    msg = await bot.get_channel(column2).fetch_message(column1)
                    index = await pollLink(None, column3)
                    await rateLimits.wait()
                    await msg.edit(view=initBallotViews.initBallots[index])
                    initBallotViews.initBallots[index].messageID = column1
                    initBallotViews.initBallots[index].channelID = column2
                except Exception as e:
                    logger.log(log="message not found, likely deleted by users", type="debug", lead = column3)

            tasks = []
            for i in range(len(rows)):
                try:
                    logger.log(log = f"{rows[i][2]}\n\n{rows[i][1]}", type="debug", lead = rows[i][3])
                    tasks.append(asyncio.create_task(replaceInitBallot(rows[i][1], rows[i][2], rows[i][3])))
                    #Complete tasks in batches of 40
                    if len(tasks) >= 40:
                        await asyncio.gather(*tasks, return_exceptions=True)
                        tasks = []
                except:
                    logger.log(log="message not found, likely deleted by users", type = "debug", lead = rows[i][3])
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.log("Persistent views synced. Prior InitBallots are usable")   
        else:
            logger.log(log="No database found. If this is the first deployment, this is normal. If not, please check your environment variable BOT_DATABASE_PATH", type="warning")
        
        #set up slash commands
        logger.log("Syncing slash commands")
        try:
            #await rateLimits.wait()
            await bot.tree.sync()
            logger.log("Slash commands synced")
        except Exception as e:
            logger.log(f"Error syncing slash commands: {e}", type = "error")
            exit(1)
        
        await rateLimits.wait()
        await bot.change_presence(status=discord.Status.online)
        logger.log("Bot is fully ready. Appearing online")
    
    
  
    #run bot and database failsafe
    def databaseFailsafe():
        #TODO This throws an error. It cannot find the file. May be a directory issue
        subprocess.run(["./databaseFailsafe"])
    async def databaseFailsafeLoop():
        while True:
            databaseFailsafe()
            await asyncio.sleep(43200)
    #run scheduled tasks
    async def rateLimitLoop():
        logger.log("Rate Limit Loop Started", type="debug")
        while True:
            try:
                #schedule.run_pending()
                rateLimits.tickDown()
                await asyncio.sleep(rateLimits.decrementAmount)
            except Exception as e:
                logger.log(log = e, type = "error")
        raise Exception
    #Run a loop to check initBallots for completion
    async def checkInitBallots():
        logger.log("Check InitBallots Loop Started", "debug")
        #If the loop takes longer than this allocated log it, as we should investigate what is taking so long
        maxAllocatedTime = datetime.timedelta(seconds=5)
        while True:
            try:
                timeBefore = datetime.datetime.now()
                await initBallotViews.checkFinish()
                timeAfter = datetime.datetime.now()
                diff = timeAfter - timeBefore
                if diff > maxAllocatedTime:
                    logger.log(f"InitBallotTracker took exceedingly long to clear completed ballots. Took ({diff}) to complete. This could be a discord bot or a bettervoting.com issue", "error")
                await asyncio.sleep(1)
            except Exception as e:
                logger.log(str(e), "error")
            

    #run bot
    bot.run(TOKEN)
    logger.log("THIS MEANS THAT bot.run() REACHED ITS END. A CRITICAL ERROR HAS OCCURED AND MEANS THE BOT IS OFFLINE", "error")
    raise Exception