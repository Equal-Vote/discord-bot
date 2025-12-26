import discord
from discord.ext import commands
from discord import app_commands

import jwt
import asyncio
import os
import schedule
from dotenv import load_dotenv

from STARCustomLibs import BVWebInteract as BVI, PunkinLogging
from Views import PollViews

   

#TODO implement error handling
#TODO deintegrate DiscordBotAssist
if __name__ == "__main__":
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
        Translator: BVI.BVWebTranslator = BVI.BVWebTranslator()
        Translator.createToken("DisBot")
        try:
            Translator.assignElection(electionid, Translator.token)
        except:
            interaction.response.send_message("Oops! That is not a valid election ID")
        elections[electionid] = Translator
        
        #With election object created, create view and send message for ballot casting
        view = PollViews.InitBallot(bot, elections[electionid].electJSON, Translator)
        views[electionid] = view
        await interaction.response.send_message(embed = view.titleTXT, view=view)


    @bot.event
    async def on_ready():
        print("Syncing slash commands")
        try:
            await bot.tree.sync()
            print("Slash commands synced")
        except Exception as e:
            print(f"Error syncing slash commands: {e}")
            exit(1)

    bot.run(TOKEN)
    


