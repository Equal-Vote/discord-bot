#This file contains views relating to polls. Views are objects in the discord API that house buttons and other advanced graphics
import json
import os
from dotenv import load_dotenv
import datetime
import time


import discord
from discord.ui import Button, View
from discord.ext import commands

import sqlite3

from STARCustomLibs import PunkinLogging, BVWebInteract as BVI

import sys; sys.stdout = sys.stderr

#TODO have these each created once when a new election is made, not every time a ballot is made

load_dotenv()
logger = PunkinLogging.errorLogger(f"{os.getenv('PUNKIN_PATH')}/{datetime.datetime.now()}.txt")
database = sqlite3.connect(os.getenv('BOT_DATABASE_PATH'))
database = database.cursor()
#Time is never null, even when election expires, as a failsafe
database.execute("CREATE TABLE IF NOT EXISTS InitBallots (id INTEGER PRIMARY KEY, messageID INTEGER NOT NULL, channelID INTEGER NOT NULL, electionID TEXT NOT NULL, time INTEGER NOT NULL)")

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
#defer an interaction
async def deferInt(interaction: discord.Interaction):
    logger.log(f"Responding to interaction that expires at {interaction.expires_at} initiated by user {interaction.user}", False, False)
    await interaction.response.defer(ephemeral=True)
    logger.log(f"Responded to interaction, it is now {datetime.datetime.now()}", False, False)


#View for message that will initiate ballot casting. This shows title, desc, options, and the cast vote button. This is not the ballot itself
class InitBallot(discord.ui.View):
    def __init__(self, bot: commands.bot, data: dict, BVIObject: BVI.BVWebTranslator):
        super().__init__(timeout=None)
        self.bot = bot
        self.BVIObject = BVIObject

        #sort relevant dict entries into easy to access variables
        self.title = data['election']['title']
        self.description = data['election']["description"]
        self.candidates = data['election']['races'][0]['candidates']

        self.titleTXT = discord.Embed(title=self.title, description= self.description)

        #set up candidates as items in the UI
        self.candItems = []
        for i in range(len(self.candidates)):
            self.candItems.append(Button(label=self.candidates[i]['candidate_name']))
            self.candItems[i].callback = self.button_callback
            self.add_item(self.candItems[i])

        #set up cast vote button
        self.btn: discord.ui.button = (Button(label="Click Here to Cast Vote", style=discord.ButtonStyle.primary, custom_id="InitButton", row=2))
        self.btn.callback= self.button_callback
        self.add_item(self.btn)
        self.results: discord.ui.button = Button(label="Click Here to See Current Leader", style=discord.ButtonStyle.primary, row=2)
        self.results.callback = self.seeCurrentResults
        self.add_item(self.results)

        

    #function to send Ballot. Technically all buttons can begin a ballot to avoid frusturations with users who dont understand STAR voting
    async def button_callback(self, interaction:discord.Interaction):
        #respond immeditately, interactions fail if not responded to in 3 seconds
        await deferInt(interaction)
        if self.BVIObject.alreadyVoted(interaction.user.id):
            await interaction.followup.send("You have already voted in this election", ephemeral=True)
        else:
            view = Ballot(self.bot, self.title, self.candidates, self.BVIObject)
            await interaction.followup.send(view.description, view= view, ephemeral=True)
    
    #Send ephemeral message with current leader
    async def seeCurrentResults(self, interaction:discord.Interaction):
        await deferInt(interaction)
        self.BVIObject.updateResults()
        await interaction.followup.send(f"The current leader is {self.BVIObject.winner}\nSee https://bettervoting.com/{self.BVIObject.electionID}/results for more details", ephemeral=True)

    #Save data to database
    def saveToSQL(self, messageId: str, channelId: str) -> None:
        database.execute("INSERT INTO InitBallots (messageID, channelID, electionID, time) VALUES (?, ?, ?, ?)", (int(messageId), int(channelId), self.BVIObject.electionID, int(time.time())))
        database.connection.commit()
        print("Committed to database")



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
        def __init__(self, candidate: int, candName: str, save):
            #integer that refers to the candidate. (if a candidate is the 4th object in the candidate list, the 4th object in the dropdown list will refer to it)
            self.candNum = candidate
            #candidate name
            self.candName = candName
            self.save = save

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
            await deferInt(interaction)
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
    def __init__(self, bot:commands.bot, title:str, candidates:dict, BVIObject, description:str = "Not scoring is the same as scoring 0. Feel free to skip candidates you don't know and to score multiple candidates the same", timeout: float = 300.0):
        super().__init__(timeout=900)
        self.bot = bot
        self.BVIObject = BVIObject
        self.title = title
        self.candidates = candidates
        self.description = description

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
            tempPage.append(self.rankMenu(i, self.candidates[i]['candidate_name'], self.save))
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
        await deferInt(interaction)
        if not self.currentPage == 0:
            self.currentPage -= 1
            self.refreshDropdowns()
            await interaction.edit_original_response(view=self.pages[self.currentPage])
    async def nextCallback(self, interaction:discord.Interaction):
        #respond immeditately, interactions fail if not responded to in 3 seconds
        await deferInt(interaction)
        if not self.currentPage == self.lastPage:
            self.currentPage += 1
            self.refreshDropdowns()
            await interaction.edit_original_response(view=self.pages[self.currentPage])
    async def submitCallback(self, interaction:discord.Interaction):
        #respond immeditately, interactions fail if not responded to in 3 seconds
        await deferInt(interaction)
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
            text = f"{text}\n\nThe current leader is {self.BVIObject.winner}\n\nSee more information at {URL}"
        elif not switch:
            text = "You have already voted in this election"
        else:
            text = "There was a server error. Please try again later."


        
        
        #Send confirmation
        await interaction.edit_original_response(content=text, view=None)
    async def pageCounterCallback(self, interaction: discord.Interaction):
        await deferInt(interaction)


    #used for debugging
    def debugPages(self):
        print("page debug")
        print(self.currentPage)
        print(self.lastPage)
        print(len(self.pages))


#Sent after discord native poll is sent. Clicking the button deletes the poll and makes a STAR poll with that data
class turnToBV(discord.ui.View):
    def __init__(self, bot: commands.bot, message: discord.Message):
        super().__init__(timeout=300)
        self.bot = bot
        self.message:discord.Message = message
        self.btn = Button(label="Click Here to Turn Into a STAR Poll", style=discord.ButtonStyle.primary)
        self.btn.callback = self.callback
        self.add_item(self.btn)


    #when button is pressed get poll data and turn into a star poll
    async def callback(self, interaction: discord.Interaction):
        await deferInt(interaction)
        poll = self.message.poll

        question: str = poll.question
        duration = poll.expires_at

        answers = poll.answers

        for i in range(len(answers)):
            answers[i] = getattr(answers[i].media, "text", None)

        print(f"{question}\n{answers}\n{duration}")

        Translator = BVI.BVWebTranslator()
        Translator.createElection(question, duration, self.message.author.id, answers)

        print(Translator.electJSON)
        await interaction.edit_original_response(view=InitBallot(self.bot, Translator.electJSON, Translator))

        


        

        