#archive of views that were decided against, copying some code from them may still be useful but these classes shouldnt be used

#Message for one candidate
class refinedBallot(discord.ui.View):
    def __init__(self, candidate):
        super().__init__()

        self.candidate = candidate

        self.candLabel = Button(label=candidate['candidate_name'])
        self.dropdown = self.rankMenu()

        self.add_item(self.candLabel)
        self.add_item(self.dropdown)

    #TODO this could use some minor optimizations
    class rankMenu(discord.ui.Select):
        def __init__(self):
            #integer that refers to the candidate. (if a candidate is the 4th object in the candidate list, the 4th object in the dropdown list will refer to it)
            options = []
            rankLabels = ["0", "1", "2", "3", "4", "5"]
            for i in range(len(rankLabels)):
                if i == 0:
                    options.append(discord.SelectOption(label=rankLabels[i], default=True))
                else:
                    options.append(discord.SelectOption(label=rankLabels[i]))
            super().__init__(placeholder="Score from 0-5", min_values=0, max_values=1, options=options)

        #called when option is selected
        async def callback(self, interaction: discord.Interaction):
            #this line seems to do nothing, but discord doesnt consider the interaction responded without it
            await interaction.response.defer(ephemeral=True)
            print(self.values[0])


#View for the message that the user will use to vote
#discord limits items in UI and this greatly exceeds it
class Ballot(discord.ui.View):
    #class for a dropdown menu
    class rankMenu(discord.ui.Select):
        def __init__(self, candidate:int):
            #integer that refers to the candidate. (if a candidate is the 4th object in the candidate list, the 4th object in the dropdown list will refer to it)
            self.candidate = candidate
            options = []
            rankLabels = ["0", "1", "2", "3", "4", "5"]
            for i in range(len(rankLabels)):
                if i == 0:
                    options.append(discord.SelectOption(label=rankLabels[i], default=True))
                else:
                    options.append(discord.SelectOption(label=rankLabels[i]))
            super().__init__(placeholder="Score from 0-5", min_values=0, max_values=1, options=options)
        
        #called when option is selected
        async def callback(self, interaction: discord.Interaction):
            #this line seems to do nothing, but discord doesnt consider the interaction responded without it
            await interaction.response.defer(ephemeral=True)
            print(self.values[0])
  
    def __init__(self, bot:commands.bot, title:str, candidates: list):
        super().__init__()

        self.bot = bot

        self.title = title
        self.candidates = candidates

        dropdowns = []

        for i in range(len(candidates)):
            self.candidates[i].callback = self.wrongButton
            self.add_item(self.candidates[i])
            dropdowns.append(self.rankMenu(i))
            self.add_item(dropdowns[i])


        self.castVote = Button(label="Submit Ballot", style=discord.ButtonStyle.primary)
        self.castVote.callback = self.submitBallot

        self.add_item(self.castVote)

    async def submitBallot(self, interaction:discord.Interaction):
        
        print(self.dropdown.values)

    async def wrongButton(self, interaction:discord.Interaction):
        await interaction.response.defer()