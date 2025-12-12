import discord
from discord.ext import commands

import jwt
import asyncio

from STARCustomLibs import BVWebInteract as BVI, DiscordBotAssist as DBA
from Views import PollViews
   

#TODO implement error handling
#TODO deintegrate DBA
if __name__ == "__main__":
     #create bot and assign it to DiscordBotAssist, as well as toggle the TOKEN.

    #ALWAYS DELETE TOKENS BEFORE PUSHING TO REPO!!! NO TOKEN SHOULD EVER BE PUBLIC INCLUDING ALPHA ONES!!!
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    bot = commands.Bot(intents=intents, command_prefix="?")
    client = DBA.DisBotAssist(bot)
    #ALWAYS DELETE TOKENS BEFORE PUSHING TO REPO!!! NO TOKEN SHOULD EVER BE PUBLIC INCLUDING ALPHA ONES!!!
    TOKEN = DBA.toggleToken("", "null", "null", False)

    load_dotenv()
    discord_token = os.getenv('DISCORD_TOKEN')
    jwt_secret_key = os.getenv('JWT_SECRET_KEY')
    jwt_token = os.getenv('JWT_TOKEN')

    #Create BetterVoting Web Translator Object to interact with website
    elections: BVI.BVWebTranslator = {}

    #Command to get an election from better voting and begin voting in discord
    #command syntax is ?createPoll [electionID]
    @bot.command()
    async def createPoll(ctx):
        #get election ID from command, setup BVWebTranslator Object, add it to elections dict with electionID as key
        electionID: str = client.getCommArg(str(ctx.message.content))
        Translator: BVI.BVWebTranslator = BVI.BVWebTranslator()
        Translator.createToken("DisBot")
        Translator.assignElection(electionID, Translator.token)
        elections[electionID] = Translator
        
        #With election object created, create view and send message for ballot casting
        view = PollViews.InitBallot(bot, elections[electionID].electJSON, Translator)
        await ctx.send(embed = view.titleTXT, view=view)
        


    bot.run(TOKEN)
    


