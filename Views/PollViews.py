#This file contains views relating to polls. Views are objects in the discord API that house buttons and other advanced graphics
import json
import os
from dotenv import load_dotenv
import datetime
import time
import schedule
import asyncio
import traceback

import discord
from discord import File
from discord.ui import Button, View
from discord.ext import commands

import sqlite3

from STARCustomLibs import PunkinLogging, BVWebInteract as BVI

import sys; sys.stdout = sys.stderr

#TODO have these each created once when a new election is made, not every time a ballot is made

load_dotenv()
logger = PunkinLogging.logWrapper()
database = sqlite3.connect(os.getenv('BOT_DATABASE_PATH'))
cursor = database.cursor()
#Time is never null, even when election expires, as a failsafe
cursor.execute("CREATE TABLE IF NOT EXISTS InitBallots (id INTEGER PRIMARY KEY, messageID INTEGER NOT NULL, channelID INTEGER NOT NULL, electionID TEXT NOT NULL, time INTEGER NOT NULL)")
database.commit()

#get data set up in a dictionary to prep for pollViews
#takes a BVWebTranslator object and returns the relevant data from its JSON
def prepView(BVIObject) -> dict:
    data = BVIObject.electJSON
    retData = {}
    retData["title"] = data['election']['title']
    retData["description"] = data['election']['description']

    #get just candidate names
    candidates = []
    for i in range(len(data['election']['races'][0]['candidates'])):
        candidates.append(data['election']['races'][0]['candidates'][i]['candidate_name'])

    retData["candidates"] = candidates

    return retData

#Class to keep track of ballot views. There should only be one object of this class
#TODO automatically cull old IBs
class InitBallotTracker():
    def __init__(self):
        self.initBallots = {}
        self.counter = 1
        #Are we currently checking for finished polls?
        self.inCycle = False

    def addInitBallot(self, view):
        self.counter += 1
        num = self.counter
        self.initBallots[str(num)] = view
        return num
    
    async def checkFinish(self):
        async def finishElection(key):
            try:
                if self.initBallots[key].channelId:
                    await self.initBallots[key].completeElection()
                    del self.initBallots[key]
            except Exception as e:
                logger.log(f"Attempted to complete an InitBallot but got this error: {e}", "error", lead=f"election ID: {self.initBallots[key].BVIObject.electionID}")
                traceback.print_exc()
        
        #If it is currently scanning, wait for it to finish
        if self.inCycle:
            return
        tasks = []
        for key, value in self.initBallots.items():
            if self.initBallots[key].BVIObject.checkForCompletion():
                logger.log(f"Positioning election for completion in discord", type="debug", lead=f"{self.initBallots[key].BVIObject.electionID}")
                tasks.append(asyncio.create_task(finishElection(key)))
        logger.log(f"Completing positioned elections", type="debug")
        asyncio.gather(*tasks, return_exceptions=True)
        logger.log(f"Positioned elections completed in discord, if any, any errors printed above", type="debug")
        

        

        

#defer an interaction
async def deferInt(interaction: discord.Interaction, rateLimits):
    logger.log(log=f"Responding to interaction that expires at {interaction.expires_at} initiated by user {interaction.user}", type="debug", lead=interaction)
    try:
        await rateLimits.wait()
        await interaction.response.defer(ephemeral=True)
    except Exception as e:
        logger.log(log=e, type="error", lead=interaction)
    logger.log(log=f"Responded to interaction, it is now {datetime.datetime.now()}", type="debug", lead=interaction)


#View for message that will initiate ballot casting. This shows title, desc, options, and the cast vote button. This is not the ballot itself
class InitBallot(discord.ui.View):
    def __init__(self, bot: commands.bot, data: dict, BVIObject: BVI.BVWebTranslator, rateLimits, originalInteraction: discord.Interaction):
        try:
            logger.log(log="Creating InitBallot", type="debug", lead=BVIObject.electionID)   
            super().__init__(timeout=None)

            #These will be set later by the saveToSQL
            self.messageId: str = ""
            self.channelId: str = ""

            self.bot = bot
            self.BVIObject = BVIObject
            self.rateLimits = rateLimits

            #sort relevant dict entries into easy to access variables
            self.title = data['election']['title']
            self.description = data['election']["description"]
            self.candidates = data['election']['races'][0]['candidates']
            self.titleTXT = [discord.Embed(title=self.title, description= self.description)]

            #Determine whether to use buttons or bullet points. Usually use buttons, unless a candidater is longer than 15 char or theres more than 20 cands
            buttons: bool = True
            if len(self.candidates) > 20:
                buttons = False

            if buttons:
                #set up candidates as items in the UI
                self.candItems = []
                for i in range(len(self.candidates)):
                    if len(self.candidates[i]['candidate_name']) > 30:
                        buttons = False
                        break
                    self.candItems.append(Button(label=self.candidates[i]['candidate_name']))
                    self.candItems[i].callback = self.button_callback
                if buttons:
                    for i in self.candItems:
                        self.add_item(i)
            if not buttons:
                text = ""
                for cand in self.candidates:
                    text = f"{text}\n● {cand['candidate_name']}"
                embed = discord.Embed(description=text)
                self.titleTXT.append(embed)
                

            #set up cast vote button
            self.btn: discord.ui.button = (Button(label="Click Here to Cast Vote", style=discord.ButtonStyle.primary, custom_id="InitButton", row=2))
            self.btn.callback= self.button_callback
            self.add_item(self.btn)
            self.results: discord.ui.button = Button(label="Click Here to See Current Leader", style=discord.ButtonStyle.primary, row=2)
            self.results.callback = self.seeCurrentResults
            self.add_item(self.results)

            #Ballots will be added to this list to avoid the "one user votes at a time" glitch.
            #This class will check every 20 minutes for ballots that are either complete or timed out and clear them from memory
            #TODO adjust this to use a dictionary
            self.ballotViews: Ballot = []
            def cleanBallotViews():
                endCriteria = range(len(self.ballotViews))
                for ballot in endCriteria:
                    if self.ballotViews[ballot].complete:
                        del self.ballotViews[ballot]
                        ballot -= 1
                        endCriteria -= 1
            schedule.every(20).minutes.do(cleanBallotViews)
        except Exception as e:
            logger.log(log=e, type="error", lead=BVIObject.electionID)
        
        


    #function to send Ballot. Technically all buttons can begin a ballot to avoid frusturations with users who dont understand STAR voting
    async def button_callback(self, interaction:discord.Interaction):
        try:
            #respond immeditately, interactions fail if not responded to in 3 seconds
            await deferInt(interaction, self.rateLimits)
            alrVot = self.BVIObject.alreadyVoted(interaction.user.id)
            if alrVot:
                await self.rateLimits.wait()
                await interaction.followup.send("You have already voted in this election", ephemeral=True)
            elif not alrVot:
                view = Ballot(self.bot, self.title, self.candidates, self.BVIObject, self.rateLimits)
                self.ballotViews.append(view)
                await self.rateLimits.wait()
                msgID = await interaction.followup.send(view.description, view= self.ballotViews[-1], ephemeral=True)
                self.ballotViews[-1].msgID = msgID.id
            else:
                await self.rateLimits.wait()
                await interaction.followup.send("There was a server error. Please try again later.", ephemeral=True)
        except Exception as e:
            logger.log(log=f"Error creating Ballot\n\nf{e}", type="error", lead=self.BVIObject.electionID)
    
    #Send ephemeral message with current leader
    async def seeCurrentResults(self, interaction:discord.Interaction):
        try:
            await deferInt(interaction, self.rateLimits)
            '''try:
                imgID = self.BVIObject.createBar()
            except Exception as e:
                #secondLogger.log(f"This was a false ballot by {interaction.user}", True, False)
                #secondLogger.log(e, True, False)
                #secondLogger.log(self.BVIObject.resultsJSON, True, False)
            score = f"graphTemp/2{imgID}.png"
            runoff = f"graphTemp/1{imgID}.png"
            files = [File(score, filename="score.png"), File(runoff, filename="runoff.png")]'''
            self.BVIObject.updateResults()
            text = f"# {self.title}\n## The current leader is {self.BVIObject.winner} and there are {self.BVIObject.numVotes} votes so far.\n\nSee https://bettervoting.com/{self.BVIObject.electionID}/results for more details"
            submitView = Submission(self.bot, text, self.BVIObject, None, self.rateLimits)
            await self.rateLimits.wait()
            msg = await interaction.followup.send(content=text, view=submitView, ephemeral=True)
            submitView.msgID = msg.id
        except Exception as e:
            logger.log(log=f"Error showing current results: {e}", type="error", lead=self.BVIObject.electionID)
            traceback.print_exc()
    
    #Election closed 
    #Replace own view with the current leader view, with some small alterations
    #Send message with same view
    async def completeElection(self):
        try:
            await self.rateLimits.wait()
            msg: discord.Message = await self.bot.get_channel(self.channelId).fetch_message(self.messageId)
            graphText = self.BVIObject.createASCIIBar()
            msgContent = f"# The poll {self.title} is complete\n## The winner was {self.BVIObject.winner} and there were {self.BVIObject.numVotes} votes.\n\nSee https://bettervoting.com/{self.BVIObject.electionID}/results for more details\n\n```{graphText}```"
            endEmbed = discord.Embed()
            await self.rateLimits.wait()
            await msg.edit(content=msgContent, view=None, embeds=[])
            await self.rateLimits.wait()
            await msg.channel.send(msgContent)
            cursor.execute(f"DELETE FROM InitBallots WHERE messageID = {int(self.messageId)} AND channelID = {int(self.channelId)}")
            database.commit()
        except Exception as e:
            traceback.print_exc()

    #Save data to database
    def saveToSQL(self, messageId: str, channelId: str) -> None:
        try:
            self.messageId = messageId
            self.channelId = channelId
            cursor.execute("INSERT INTO InitBallots (messageID, channelID, electionID, time) VALUES (?, ?, ?, ?)", (int(messageId), int(channelId), self.BVIObject.electionID, int(time.time())))
            database.commit()
            logger.log(log="Committed to database", type="debug", lead=self.BVIObject.electionID)
        except Exception as e:
            logger.log(log=f"Error submitting to database\n\n{e}", type="error", lead=self.BVIObject.electionID)



#translate emojis to integer scores
def translateEmoji(emoji: str) -> int:
    if emoji == "❌":
        return 0
    else:
        return len(emoji)


#ballot view, sent when user interacts with InitBallot. Users vote is submitted when submit is pressed
#A paginated menu. Works by deleting and replacing UI contents to give the illusion of swiping left and right
class Ballot(discord.ui.View):

    #class for dropdown menus
    class rankMenu(discord.ui.Select):
        def __init__(self, candidate: int, candName: str, save, rateLimits):
            #integer that refers to the candidate. (if a candidate is the 4th object in the candidate list, the 4th object in the dropdown list will refer to it)
            self.candNum = candidate
            #candidate name
            self.candName = candName
            self.save = save
            self.rateLimits = rateLimits

            #has this dropdown been used before?
            self.used = False
            
            options = []
            rankLabels = ["❌", "⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]
            #concats candidate name and rank labels for select menu options
            for i in range(len(rankLabels)):
                text = (f"{candName}: {rankLabels[i]}")
                options.append(discord.SelectOption(label=text, value=rankLabels[i]))

            super().__init__(placeholder=self.candName, min_values=0, max_values=1, options=options)

        #called when option is selected
        async def callback(self, interaction: discord.Interaction):
            #this line seems to do nothing, but discord doesnt consider the interaction responded without it
            await deferInt(interaction, self.rateLimits)
            #this dropdown has been used
            self.used = True
            #save score
            self.save.scores[self.candNum] = self.values[0]
        #keeps option selects persistent in when navigating pages, otherwise it always goes back to X.
        def refreshDefault(self):
            #this if statement ensures it just stays blank if it has not been interacted with yet
            if self.used:
                for i in self.options:
                    i.default = i.value == self.save.scores[self.candNum]

    #class for one page in the menu
    class subView(discord.ui.View):
        def __init__(self, dropdowns: list):
            super().__init__()
            self.dropdowns: list = dropdowns
            for i in self.dropdowns:
                self.add_item(i)
    
    #class to store choices until votes are submitted
    class saveData():
        def __init__(self, length: int):
            self.scores = []
            for i in range(length):
                self.scores.append("❌")



    #init for Ballot
    def __init__(self, bot:commands.bot, title:str, candidates:dict, BVIObject, rateLimits, description:str = "Not scoring is the same as scoring 0. Feel free to skip candidates you don't know and to score multiple candidates the same", timeout: float = 300.0):
        super().__init__(timeout=900)
        self.bot = bot
        self.BVIObject = BVIObject
        self.rateLimits = rateLimits
        self.title = title
        self.candidates = candidates
        self.description = description
        #This variable is set to True when the ballot is either submitted or times out so the InitBallot can clear it from memory
        self.complete = False
        #this views message ID. Will be assigned by initBallot
        self.msgID = None

        self.introText: str = self.description

        #save votes here so they are persistent when swiping left/right. This will also be used to send the vote
        self.save = self.saveData(len(candidates))

        #nav and submit buttons
        self.navButtons: list = [
        Button(label = "◀️", style=discord.ButtonStyle.primary, row=4),
        Button(label="Submit Ballot", style= discord.ButtonStyle.primary, row=4),
        Button(label="▶️", style= discord.ButtonStyle.primary, row=4),
        Button(label="", row=4)]

        self.navButtons[0].callback = self.prevCallback
        self.navButtons[2].callback = self.nextCallback
        self.navButtons[1].callback = self.submitCallback
        self.navButtons[3].callback = self.pageCounterCallback

        #A 2D array that will contain the content of each page
        self.pages: View = []
        self.currentPage:int = 0

        #create pages of 4 dropdowns per page
        temp: int = 0
        tempPage: list = []
        tempView = ""
        for i in range(len(self.candidates)):
            tempPage.append(self.rankMenu(i, self.candidates[i]['candidate_name'], self.save, self.rateLimits))
            temp += 1
            if temp == 4 or i == (len(self.candidates) - 1):
                temp = 0
                self.pages.append(self.subView(tempPage))
                tempPage = []
        #add nav buttons to pages
        for i in range(len(self.pages)):
            for j in self.navButtons:
                self.pages[i].add_item(j)
        
        #used by navButtons
        self.lastPage = len(self.pages) - 1

        #Has the last page ever been hit
        self.allSeen = False
        #set correct labels for nav buttons
        #this is called here since the current and last page variables are needed
        self.setNavs()
        self.refreshDropdowns()

        #start view
        for i in self.pages[0].children:
            self.add_item(i)
                

        
    #The below are functions relating to changing pages

    #Change pages
    #set nav buttons based on what page we are on
    #TODO disable and enable left and right buttons as well
    def setNavs(self):
        #disable submit button until last page has been viewed
        if self.currentPage == self.lastPage:
            self.allSeen = True

        if self.allSeen:
            self.navButtons[1].label = "Click Here to Submit Ballot"
            self.navButtons[1].disabled = False
            self.navButtons[1].style = discord.ButtonStyle.primary
            self.allSeen = True
        else:
            self.navButtons[1].label = "View All Pages Before Submitting"
            self.navButtons[1].disabled = True
            self.navButtons[1].style = discord.ButtonStyle.secondary

        #Page counter update
        self.navButtons[3].label = f"Page {str(self.currentPage + 1)}/{str(self.lastPage + 1)}"
    #refresh dropdown menus
    def refreshDropdowns(self):
        for child in self.pages[self.currentPage].children:
            if isinstance(child, discord.ui.Select):
                child.refreshDefault()
        self.setNavs()

        

    #callbacks for buttons
    #TODO there is likely a slightly more efficient way to do this
    async def prevCallback(self, interaction:discord.Interaction):
        #respond immeditately, interactions fail if not responded to in 3 seconds
        await deferInt(interaction, self.rateLimits)
        if not self.currentPage == 0:
            self.currentPage -= 1
            self.refreshDropdowns()
            await self.rateLimits.wait()
            await interaction.edit_original_response(view=self.pages[self.currentPage])
    async def nextCallback(self, interaction:discord.Interaction):
        #respond immeditately, interactions fail if not responded to in 3 seconds
        await deferInt(interaction, self.rateLimits)
        if not self.currentPage == self.lastPage:
            self.currentPage += 1
            self.refreshDropdowns()
            await self.rateLimits.wait()
            await interaction.edit_original_response(view=self.pages[self.currentPage])
    async def submitCallback(self, interaction:discord.Interaction):
        #respond immeditately, interactions fail if not responded to in 3 seconds
        await deferInt(interaction, self.rateLimits)
        #prepare scores
        scores = []
        for i in self.save.scores:
            scores.append(translateEmoji(i))

        #TODO implement responses for user already voted and failed to send vote
        #Submit ballot, or handle errors
        switch = self.BVIObject.submitBallot(interaction.user.id, scores)
        if switch:
            #Show current leader, a ballot copy, and link to better voting for more
            text = "You voted: \n"
            for i in range(len(self.candidates)):
                text = text + (f"•{self.candidates[i]['candidate_name']}: {self.save.scores[i]} \n")
            self.BVIObject.updateResults()
            URL = f"https://bettervoting.com/{self.BVIObject.electionID}/results"
            text = f"# {self.title}\n## The current leader is {self.BVIObject.winner} and there are {self.BVIObject.numVotes} votes so far.\n\nSee https://bettervoting.com/{self.BVIObject.electionID}/results for more details"
        elif not switch:
            text = "You have already voted in this election"
        else:
            text = "There was a server error. Please try again later."
        text = f"{text}\n\n"
        
        '''#prepare graphs
        try:
            imgID = self.BVIObject.createBar()
        except Exception as e:
            secondLogger.log(f"This was a false ballot by {interaction.user}", True, False)
            secondLogger.log(e, True, True)
            secondLogger.log(self.BVIObject.resultsJSON, True, False)
        score = f"graphTemp/2{imgID}.png"
        score = f"graphTemp/2{imgID}.png"
        runoff = f"graphTemp/1{imgID}.png"
        files = [File(score, filename="score.png"), File(runoff, filename="runoff.png")]'''
        
        submitView = Submission(self.bot, text, self.BVIObject, self.msgID, self.rateLimits)
        #Send confirmation
        await self.rateLimits.wait()
        await interaction.followup.edit_message(message_id=self.msgID, content=f"{text}", view=submitView)
    async def pageCounterCallback(self, interaction: discord.Interaction):
        await deferInt(interaction, self.rateLimits)
    #ballot is void after 900 seconds
    #TODO add a feature that resets the timer after any activity
    async def on_timeout(self):
        self.complete = True


    #used for debugging
    def debugPages(self):
        print("page debug")
        print(self.currentPage)
        print(self.lastPage)
        print(len(self.pages))

#Sends the main response text as well as a button that will generate graphs
class Submission(discord.ui.View):
    def __init__(self, bot:commands.bot, text, BVIObject, msgID, rateLimits):
        super().__init__(timeout=300)
        self.bot = bot
        self.text = text
        self.BVIObject = BVIObject
        self.msgID = msgID
        self.rateLimits = rateLimits

        self.btn: discord.ui.Button = (discord.ui.Button(label="Click here to learn more", style=discord.ButtonStyle.primary))
        self.btn.callback= self.button_callback
        self.add_item(self.btn)
    
    async def button_callback(self, interaction):
        await deferInt(interaction, self.rateLimits)
        #back ticks cause discord to post as a code snippet, which avoids formatting errors
        graphText = f"```{self.BVIObject.createASCIIBar()}```"
        text = f"{self.text}{graphText}"
        await self.rateLimits.wait()
        await interaction.followup.edit_message(message_id=self.msgID, content=text, view=None)





#Sent after discord native poll is sent. Clicking the button deletes the poll and makes a STAR poll with that data
class turnToBV(discord.ui.View):
    def __init__(self, bot: commands.bot, message: discord.Message, initBallotTrackerObj : InitBallotTracker, rateLimits):
        super().__init__(timeout=300)
        self.bot = bot
        self.rateLimits = rateLimits
        self.message:discord.Message = message
        self.initBallotTrackerObj = initBallotTrackerObj
        self.btn = Button(label="Click Here to Turn Into a STAR Poll", style=discord.ButtonStyle.primary)
        self.btn.callback = self.callback
        self.add_item(self.btn)


    #when button is pressed stop timeout, get poll data,  and turn into a star poll
    async def callback(self, interaction: discord.Interaction):
        await deferInt(interaction, self.rateLimits)

        #if button user isnt the user who made the poll, refuse to make it
        if not interaction.user.id == self.message.author.id:
            await self.rateLimits.wait()
            interaction.followup.send("Only the creator of this poll can turn it into a STAR poll", ephemeral=True)
            return

        #stops this message from timing out, otherwise the InitBallot view will also timeout
        self.timeout = None
        poll = self.message.poll

        question: str = poll.question
        duration = poll.expires_at

        answers = poll.answers

        for i in range(len(answers)):
            answers[i] = getattr(answers[i].media, "text", None)

        logger.log(log=f"Turning poll into STAR poll{question}\n{answers}\n{duration}", type="debug", lead=question)

        Translator = BVI.BVWebTranslator()
        Translator.createElection(question, duration, self.message.author.id, answers)

        #make Init ballot, save it to database, and delete the change to STAR button
        view=InitBallot(self.bot, Translator.electJSON, Translator, self.rateLimits, interaction)
        index = str(self.initBallotTrackerObj.addInitBallot(view))
        await self.rateLimits.wait()
        msg: discord.Message = await interaction.followup.send(embeds=self.initBallotTrackerObj.initBallots[index].titleTXT, view=self.initBallotTrackerObj.initBallots[index])
        self.initBallotTrackerObj.initBallots[index].saveToSQL(msg.id, msg.channel.id)
        await self.rateLimits.wait()
        await self.message.delete()
        await self.rateLimits.wait()
        await self.on_timeout()

    #delete self after 5 minutes of non use
    async def on_timeout(self):
        await self.rateLimits.wait()
        msg : discord.Message = await self.bot.get_channel(self.channelID).fetch_message(self.messageID)
        await self.rateLimits.wait()
        await msg.delete()
    #get own message data for deletion purposes
    def ownData(self, channelID, messageID):
        self.messageID = messageID
        self.channelID = channelID    