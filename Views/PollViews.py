#This file contains views relating to polls. Views are objects in the discord API that house buttons and other advanced graphics
import json

import discord
from discord.ui import Button, View
from discord.ext import commands

#TODO have these each created once when a new election is made, not every time a ballot is made

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

#TODO implement cleaner UI for user
#View for message that will initiate ballot casting. This shows title, desc, options, and the cast vote button. This is not the ballot itself
class InitBallot(discord.ui.View):
    def __init__(self, bot: commands.bot, data: dict, BVIObject):
        super().__init__()
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

    #function to send Ballot. Technically all buttons can begin a ballot to avoid frusturations with users who dont understand STAR voting
    async def button_callback(self, interaction:discord.Interaction):
        #respond immeditately, interactions fail if not responded to in 3 seconds
        await interaction.response.defer(ephemeral=True)
        view = Ballot(self.bot, self.title, self.candidates, self.BVIObject)
        await interaction.followup.send(view.description, view= view, ephemeral=True)


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
            await interaction.response.defer(ephemeral=True)
            #save score
            self.save.scores[self.candNum] = self.values[0]
        #keeps option selects persistent in when navigating pages, otherwise it always goes back to X.
        #TODO this function causes pages to turn from blank to X when swiping left to right. Does not affect dropdowns already voted on
        def refreshDefault(self):
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
        super().__init__()
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
        Button(label="▶️", style= discord.ButtonStyle.primary, row=4)]

        self.navButtons[0].callback = self.prevCallback
        self.navButtons[2].callback = self.nextCallback
        self.navButtons[1].callback = self.submitCallback


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


        #This button initiates voting
        self.begin: Button = Button(label="Click Here to Begin Voting", style= discord.ButtonStyle.primary)
        self.begin.callback = self.beginCallback
        self.add_item(self.begin)
                

        

    #Change pages
    #set nav buttons based on what page we are on
    #TODO clean this up and use it
    def setNavs(self, page: int):
        if page == 0:
            navButtons[0].disabled = True
            navButtons[1].disabled = False
            navButtons[2].disabled = True
            navButtons[2].label = ""
        elif page == (len(self.pages) - 1):
            navButtons[0].disabled = False
            navButtons[1].disabled = True
            navButtons[2].disabled = False
            navButtons[2].label = "Submit Ballot"
        else:
            navButtons[0].disabled = False
            navButtons[1].disabled = False
            navButtons[2].disabled = True
            navButtons[2].label = ""


    #callbacks for buttons
    #TODO there is likely a slightly more efficient way to do this
    def refreshDropdowns(self):
        for child in self.pages[self.currentPage].children:
            if isinstance(child, discord.ui.Select):
                child.refreshDefault()
    async def prevCallback(self, interaction:discord.Interaction):
        #respond immeditately, interactions fail if not responded to in 3 seconds
        await interaction.response.defer(ephemeral=True)
        if not self.currentPage == 0:
            self.currentPage -= 1
            self.refreshDropdowns()
            await interaction.edit_original_response(view=self.pages[self.currentPage])
    async def nextCallback(self, interaction:discord.Interaction):
        #respond immeditately, interactions fail if not responded to in 3 seconds
        await interaction.response.defer(ephemeral=True)
        if not self.currentPage == self.lastPage:
            self.currentPage += 1
            self.refreshDropdowns()
            await interaction.edit_original_response(view=self.pages[self.currentPage])
    async def submitCallback(self, interaction:discord.Interaction):
        #respond immeditately, interactions fail if not responded to in 3 seconds
        await interaction.response.defer(ephemeral=True)
        scores = []
        for i in self.save.scores:
            scores.append(translateEmoji(i))
        text = "You voted: \n"
        for i in range(len(self.candidates)):
            text = text + (f"•{self.candidates[i]['candidate_name']}: {self.save.scores[i]} \n")
        
        #TODO implement responses for user already voted and failed to send vote
        switch = self.BVIObject.submitBallot(interaction.user.id, scores)
        await interaction.edit_original_response(content=text, view=None)
            
    async def beginCallback(self, interaction:discord.Interaction):
        #respond immeditately, interactions fail if not responded to in 3 seconds
        await interaction.response.defer(ephemeral=True)
        await interaction.edit_original_response(view=self.pages[0])


    #used for debugging
    def debugPages(self):
        print("page debug")
        print(self.currentPage)
        print(self.lastPage)
        print(len(self.pages))




    
        