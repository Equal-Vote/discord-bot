# This example requires the 'message_content' privileged intent to function.
import datetime
import threading
import os
import traceback

import requests
import discord
from discord import TextStyle
from discord.ext import commands
from dotenv import load_dotenv
import heapq

import json

load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')
jwt_secret_key = os.getenv('JWT_SECRET_KEY')
jwt_token = os.getenv('JWT_TOKEN')

# The guild in which this slash command will be registered.
# It is recommended to have a test guild to separate from your "production" bot
TEST_GUILD = discord.Object(id=918037457277161492)

class CandidateScorecardView(discord.ui.View):
    def __init__(self):
        self.score_chosen = -1
        super().__init__(timeout=None)

    @discord.ui.button(label='0', style=discord.ButtonStyle.grey, custom_id='persistent_view:0')
    async def zero(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Make sure to update the message with our updated selves
        self.reset_all_buttons()
        self.score_chosen = 0
        button.style = discord.ButtonStyle.blurple
        button.disabled = True
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='1', style=discord.ButtonStyle.grey, custom_id='persistent_view:1')
    async def one(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Make sure to update the message with our updated selves
        self.reset_all_buttons()
        self.score_chosen = 1
        button.style = discord.ButtonStyle.blurple
        button.disabled = True
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='2', style=discord.ButtonStyle.grey, custom_id='persistent_view:2')
    async def two(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Make sure to update the message with our updated selves
        self.reset_all_buttons()
        self.score_chosen = 2
        button.style = discord.ButtonStyle.blurple
        button.disabled = True
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='3', style=discord.ButtonStyle.grey, custom_id='persistent_view:3', row=1)
    async def three(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Make sure to update the message with our updated selves
        self.reset_all_buttons()
        self.score_chosen = 3
        button.style = discord.ButtonStyle.blurple
        button.disabled = True
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='4', style=discord.ButtonStyle.grey, custom_id='persistent_view:4', row=1)
    async def four(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Make sure to update the message with our updated selves
        self.reset_all_buttons()
        self.score_chosen = 4
        button.style = discord.ButtonStyle.blurple
        button.disabled = True
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='5', style=discord.ButtonStyle.grey, custom_id='persistent_view:5', row=1)
    async def five(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Make sure to update the message with our updated selves
        self.reset_all_buttons()
        self.score_chosen = 5
        button.style = discord.ButtonStyle.blurple
        button.disabled = True
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='Prev', style=discord.ButtonStyle.grey, custom_id='persistent_view:prev')
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Make sure to update the message with our updated selves
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='Next', style=discord.ButtonStyle.grey, custom_id='persistent_view:next')
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=self)

    def reset_all_buttons(self):
        self.zero.style = discord.ButtonStyle.grey
        self.one.style = discord.ButtonStyle.grey
        self.two.style = discord.ButtonStyle.grey
        self.three.style = discord.ButtonStyle.grey
        self.four.style = discord.ButtonStyle.grey
        self.five.style = discord.ButtonStyle.grey
        self.zero.disabled = False
        self.one.disabled = False
        self.two.disabled = False
        self.three.disabled = False
        self.four.disabled = False
        self.five.disabled = False


class SubmitBallotView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Submit Ballot 🗳', style=discord.ButtonStyle.green, custom_id='persistent_view:submit_ballot')
    async def submitballot(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ballot submitted to the void :)", ephemeral=True)


class BallotView(discord.ui.View, ):
    def __init__(self):
        super().__init__(timeout=None)


class EmbedVote(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Vote', style=discord.ButtonStyle.green, custom_id='persistent_view:vote')
    async def vote(self, interaction: discord.Interaction, button: discord.ui.Button):
        message_sent = await interaction.send("```candidate_name\n```", ephemeral=True)
        #await interaction.response.send_message(view=CandidateScorecardView(), ephemeral=True)
        #await interaction.followup.send("Complete your ballot by clicking the emoji corresponding to the score you would give the candidate.")
        #for candidate in args:
        #    message_sent = await ctx.send(candidate)
        #    await message_sent.add_reaction('0️⃣')
        #    await message_sent.add_reaction('1️⃣')
        #    await message_sent.add_reaction('2️⃣')
        #    await message_sent.add_reaction('3️⃣')
        #    await message_sent.add_reaction('4️⃣')
        #    await message_sent.add_reaction('5️⃣')
        #await interaction.response.send_message("Score these candidates on a 0 to 5 scale.\nCandidate Name",
        #                                        view=CandidateScorecardView(), ephemeral=True)
        # Webhooks
        #await interaction.followup.send("Score these candidates on a 0 to 5 scale.\nCandidate Name",
        #                                view=CandidateScorecardView(), ephemeral=True)


class EmbedEdit(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Edit Description', style=discord.ButtonStyle.blurple,
                       custom_id='persistent_view:editdescription')
    async def editdescription(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Need to make sure only the creator can edit the embed.
        # if (interaction.user == message.user):
        await interaction.response.send_modal(STARVotingDescriptionEdit())

    @discord.ui.button(label='Edit End Date', style=discord.ButtonStyle.blurple,
                       custom_id='persistent_view:editenddate')
    async def editenddate(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Need to make sure only the creator can edit the embed.
        # if (interaction.user == message.user):
        await interaction.response.send_modal(STARVotingEndDateEdit())

    @discord.ui.button(label='Edit Candidates', style=discord.ButtonStyle.blurple,
                       custom_id='persistent_view:editcandidates1')
    async def editcandidates(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Need to make sure only the creator can edit the embed.
        # if (interaction.user == message.user):
        await interaction.response.send_modal(STARVotingCandidateNameEdit())


class STARVotingElectionSetup(discord.ui.Modal, title='New STAR Voting Election'):
    # Our modal classes MUST subclass `discord.ui.Modal`,
    # but the title can be whatever you want.

    # This will be a short input, where the user can enter their name
    # It will also have a placeholder, as denoted by the `placeholder` kwarg.
    # By default, it is required and is a short-style input which is exactly
    # what we want.
    # for candidate in range(number_of_candidates):
    candidate1 = discord.ui.TextInput(
        label='Candidate Name',
        placeholder='Harry Potter',
    )
    candidate2 = discord.ui.TextInput(
        label='Candidate Name',
        placeholder='Ron Weasley',
    )
    candidate3 = discord.ui.TextInput(
        label='Candidate Name',
        placeholder='Hermione Granger',
        required=False,
    )
    candidate4 = discord.ui.TextInput(
        label='Candidate Name',
        placeholder='Draco Malfoy',
        required=False,
    )
    candidate5 = discord.ui.TextInput(
        label='Candidate Name',
        placeholder='Hedwig',
        required=False,
    )

    # Five candidates seems to be the maximum amount I can fit on one modal.

    # This is a longer, paragraph style input, where user can submit feedback Unlike the name, it is not required. If
    # filled out, however, it will only accept a maximum of 300 characters, as denoted by the `max_length=300` kwarg.
    # feedback = discord.ui.TextInput(label='What do you think of this new feature?',style=discord.TextStyle.long,
    # placeholder='Type your feedback here...',required=False,max_length=300,)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message('Starting a new election...', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_tb(error.__traceback__)


class STARVotingDescriptionEdit(discord.ui.Modal, title='Edit the Description'):
    descriptionEditBox = discord.ui.TextInput(
        label='Description',
        style=TextStyle.long,
    )

    # default=defaultText,

    async def on_submit(self, interaction: discord.Interaction):
        URL = "https://star-vote.herokuapp.com/API/Elections"
        election = requests.get(URL)
        response = requests.post(URL, json = new_election_obj, cookies = {"custom_id_token": jwt_token})
        await interaction.response.send_message('Starting a new election...', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_tb(error.__traceback__)


class STARVotingEndDateEdit(discord.ui.Modal, title='Edit the End Date'):
    days = discord.ui.TextInput(
        label='Days'
    )
    hours = discord.ui.TextInput(
        label='Hours'
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message('Starting a new election...', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_tb(error.__traceback__)


class STARVotingCandidateEdit(discord.ui.Modal, title='Edit the Candidates'):
    # Our modal classes MUST subclass `discord.ui.Modal`,
    # but the title can be whatever you want.

    # This will be a short input, where the user can enter their name
    # It will also have a placeholder, as denoted by the `placeholder` kwarg.
    # By default, it is required and is a short-style input which is exactly
    # what we want.
    # for candidate in range(number_of_candidates):
    candidate1 = discord.ui.TextInput(
        label='Candidate Name',
        placeholder='Harry Potter',
    )
    candidate2 = discord.ui.TextInput(
        label='Candidate Name',
        placeholder='Ron Weasley',
    )
    candidate3 = discord.ui.TextInput(
        label='Candidate Name',
        placeholder='Hermione Granger',
        required=False,
    )
    candidate4 = discord.ui.TextInput(
        label='Candidate Name',
        placeholder='Draco Malfoy',
        required=False,
    )
    candidate5 = discord.ui.TextInput(
        label='Candidate Name',
        placeholder='Hedwig',
        required=False,
    )

    # Five candidates seems to be the maximum amount I can fit on one modal.

    # This is a longer, paragraph style input, where user can submit feedback Unlike the name, it is not required. If
    # filled out, however, it will only accept a maximum of 300 characters, as denoted by the `max_length=300` kwarg.
    # feedback = discord.ui.TextInput(label='What do you think of this new feature?',style=discord.TextStyle.long,
    # placeholder='Type your feedback here...',required=False,max_length=300,)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message('Starting a new election...', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_tb(error.__traceback__)

class STARVotingCandidateNameEdit(discord.ui.Modal, title='Edit Candidates Names'):
    descriptionEditBox = discord.ui.TextInput(
        label='Candidates',
        placeholder='Harry Potter, Ron Weasley, Hermione Granger, Draco Malfoy, Hedwig',
        style=TextStyle.long,
    )

    async def on_submit(self, interaction: discord.Interaction):
        election_id = None
        # Get the election ID that was saved to the embed by getting the embed from the history of this channel.
        messages = [mess async for mess in interaction.message.channel.history(limit=3)]
        for message in messages:
            for embed in message.embeds:
                for field in embed.fields:
                    if field.name == "Election ID":
                        election_id = field.value
                        break

        # Add the election ID to the URL so that we can send the correct get request.
        URL = "https://star-vote.herokuapp.com/API/Election/"
        URL += str(election_id)
        # Get the election from star-vote.
        draft_election_response = requests.get(URL, cookies = {"custom_id_token": jwt_token})

        # Display all the election data.
        print("\ndraft_election_response")
        print(draft_election_response)
        print("\ndraft_election_response.text")
        print(draft_election_response.text)
        draft_election_json = json.loads(draft_election_response.text)
        draft_election_response_election = draft_election_json["election"]
        print("\ndraft_election_response_election")
        print(draft_election_response_election)
        draft_election_response_races = draft_election_response_election["races"]
        print("\ndraft_election_response_races")
        print(draft_election_response_races)
        draft_election_response_race = draft_election_response_races[0]
        print("\ndraft_election_response_race")
        print(draft_election_response_race)
        draft_election_response_candidates = draft_election_response_race["candidates"]
        print("\ndraft_election_response_candidates")
        print(draft_election_response_candidates)

        # Send a message to the person who edited the candidates with the values they provided.
        await interaction.response.send_message(f'Starting a new election... {self.descriptionEditBox}', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_tb(error.__traceback__)


class BetterVotingBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('.'), intents=intents)

    async def setup_hook(self) -> None:
        # Register the persistent view for listening here.
        # Note that this does not send the view to any message.
        # In order to do this you need to first send a message with the View, which is shown below.
        # If you have the message_id you can also pass it as a keyword argument, but for this example
        # we don't have one.
        self.add_view(CandidateScorecardView())

    async def on_ready(self):
        await bot.tree.sync(guild=TEST_GUILD)
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


bot = BetterVotingBot()
# All this method does is copy your defined global commands (so ones without a guild or guilds kwarg,
# or without the @app_commands.guilds() decorator) to the specified guild within the CommandTree.
# When you use this method you must sync afterward still, you can refer to
# when_to_sync.md (located at https://gist.github.com/AbstractUmbra/a9c188797ae194e592efe05fa129c57f) for details there.
bot.tree.copy_global_to(guild=TEST_GUILD)


@bot.command()
@commands.is_owner()
async def onecandidate(ctx: commands.Context):
    """Starts a persistent view."""
    # In order for a persistent view to be listened to, it needs to be sent to an actual message.
    # Call this method once just to store it somewhere.
    # In a more complicated program you might fetch the message_id from a database for use later.
    # However this is outside of the scope of this simple example.
    # Set ephemeral to True so only the user can see the message.
    await ctx.send("Score this candidate on a 0 to 5 scale.", view=CandidateScorecardView(), ephemeral=True)


@bot.command()
@commands.is_owner()
async def threecandidates(ctx: commands.Context):
    """Starts a persistent view."""
    await ctx.send("Score these candidates on a 0 to 5 scale.")
    await ctx.send("Candidate Name", view=CandidateScorecardView(), ephemeral=True)
    await ctx.send("Candidate Name", view=CandidateScorecardView(), ephemeral=True)
    await ctx.send("Candidate Name", view=CandidateScorecardView(), ephemeral=True)


@bot.command()
@commands.is_owner()
async def displayoutput(ctx: commands.Context):
    """Displays the results of the election in the form of a crude bar graph"""
    await ctx.send(
        "Results:\n:black_large_square:        :black_medium_square:        :purple_square:\n:black_large_square: :white_large_square: :black_medium_square: :white_medium_square: :purple_square:\n:black_large_square: :white_large_square: :black_medium_square: :white_medium_square: :purple_square:\n:black_large_square: :white_large_square: :black_medium_square: :white_medium_square: :purple_square:\n:black_large_square: :white_large_square: :black_medium_square: :white_medium_square: :purple_square:")


@bot.hybrid_group(fallback="get")
async def starvote(ctx, number_of_candidates):
    await ctx.send(f"Showing integer: {number_of_candidates}")


@starvote.command()
async def create(ctx, number_of_candidates):
    await ctx.send(f"Created integer: {number_of_candidates}")


""" 
A command that takes in the list of candidates and returns a string that makes it easier to read in the Embed.
Useless now that I know what inline-ing does.
"""
def prettify_candidates(candidate: tuple) -> str:
    # Red, Orange, Yellow, Green, Blue, Purple, Brown, Black, White
    # How else can we display candidates in a column?
    # We can use 3 ticks for multi-line printing.
    # Just use different fields with inlines
    party_list =        "```" \
                    "🔴 Red Party         🟢 Green Party" \
             "\n\n\n🟠 Orange Party      🔵 Blue Party" \
             "\n\n\n🟡 Yellow Party      🟣 Purple Party" \
                    "```"
    return party_list


@bot.command()
@commands.is_owner()
async def new_star_embed(ctx: commands.Context, *args):
    """Creates an embed for a STAR voting election.
        Arguments:
            ElectionID: The ID of the election that STAR Vote generates.
            ElectionTitle: Title of the election. (e.g. NewElection or "New Election")
            Days: Number of days the election will last.
            Candidates: As many candidates as you want. (e.g. JaneDoe or "Jane Doe")
        Example:
            .star "What is the best color?" 5 Blue Red Green Yellow Purple Orange
    """
    # The first argument should be the election title.
    electionID = args[0]
    # The first argument should be the election title.
    electionTitle = args[1]
    now = datetime.datetime.now()
    # Set the candidates into their own variable.
    candidateTupleofTuples = args[3:]
    print(args)
    candidateTuple = candidateTupleofTuples[0]
    # stuff that wasn't working idk
    #candidateTuple = ()
    #for candidate in args[2:]:
    #    candidateTuple = (candidateTuple + candidate)
    candidates = str(candidateTuple)
    # Pretty print the candidates
    #candidates_prettified = prettify_candidates(candidates)

    # Using block quotes via "> " or ">>> " looks nice so maybe use it for the formatting of values.


    # Create the instructions for the embed.
    # Add further instructions depending on if this is an emoji election or star.vote election.
    star_voting_instructions = "Click on the image below for instructions \non how a STAR voting election works! "
    if (electionID != None):
        star_voting_instructions += "\nThen click on Vote and fill out your ballot!"
    else:
        star_voting_instructions += "\nThen fill out one number emoji for each candidate.\nThe highest value you give will be accepted."

    embedVar = discord.Embed(
        title=electionTitle, description=star_voting_instructions,
        color=0x336EFF, timestamp=now
    )
    embedVar.add_field(name="End Date", value=f"This election will end on\n{args[2]}", inline=False)

    #for x in args[2:]:
    # Add candidates under their respective parties, if the parties exist.
    # Adding so many parties may visually clutter the embed,
    # especially with emojis to represent color or symbols of each party.
    # Might want to save labeling by party until once the voter clicks on the button to vote.
    embedVar.add_field(name="🔴 Red Party", value=f"> {candidates}", inline=True)
    embedVar.add_field(name="🟠 Orange Party", value=f"> {candidates}", inline=True)
    embedVar.add_field(name="🟡 Yellow Party", value=f"> {candidates}", inline=True)
    embedVar.add_field(name="🟢 Green Party", value=f"> {candidates}", inline=True)
    embedVar.add_field(name="🔵 Blue Party", value=f"> {candidates}", inline=True)
    embedVar.add_field(name="🟣 Purple Party", value=f"> {candidates}", inline=True)
    vote_count = 0
    embedVar.add_field(name="Current Vote Count:", value=vote_count, inline=False)
    if (electionID != None):
        embedVar.add_field(name="Election ID", value=electionID, inline=False)

    # Set the large image that displays.
    image_simple_ballot = "https://d3n8a8pro7vhmx.cloudfront.net/unifiedprimary/pages/494/attachments/original/1632368538/STAR_Ballot.jpg?1632368538"
    image_full_ballot = "https://assets.nationbuilder.com/unifiedprimary/pages/452/attachments/original/1653962149/How_Does_STAR_Voting_Work_.jpg?1653962149"
    image_white_logo = "https://d3n8a8pro7vhmx.cloudfront.net/unifiedprimary/pages/452/attachments/original/1587524244/Screen_Shot_2020-04-14_at_9.44.07_PM.png?1587524244"
    image_youtube_logo = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT_tWyoQGuNM-f5Th0u8BaZf2JMaiI_xV0abw&usqp=CAU"
    image_star_checked_logo = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRUm3ihBLqL9BCrtoWEWmvliV_sXJyTs_Nh-A&usqp=CAU"
    image_star_voting_square = "https://scontent-ort2-1.xx.fbcdn.net/v/t1.6435-9/94473292_704672340291749_1317799311915876352_n.png?_nc_cat=100&ccb=1-7&_nc_sid=174925&_nc_ohc=9iepT07okusAX9oUFy4&_nc_ht=scontent-ort2-1.xx&oh=00_AT9-8vtH4rDYMyz-hiD08zyvPajynLAlufcJnGupOxnJ3g&oe=634C61D5"
    # The thumbnail might add too much visual clutter if there are emojis used (for party names).
    embedVar.set_thumbnail(url=image_star_voting_square)
    embedVar.set_image(url=image_full_ballot)

    # We could set the author but I don't want the poll creator's user name to be
    # the first thing people read at the top of the modal, since it's not important.
    #embedVar.set_author(name=ctx.author)

    # Set the footer
    # ctx.author would give full_username#1234, ctx.author.id would give the user's id from the COPY ID developer tool.
    # ctx.author.display_name would give a nickname if they have one, otherwise their full_username without the #1234
    # ctx.author.avatar & ctx.author.display_avatar fucks up the UI and display a link as the author.
    # ctx.author.guild_avatar displays as None if you don't have a server specific picture.
    embedVar.set_footer(text=f"Election created by {ctx.author.display_name}")

    print("New STAR Embed Created at " + args[2])
    await ctx.send(embed=embedVar)
    await ctx.send(view=EmbedEdit(), ephemeral=True)
    if (electionID != None):
        await ctx.send(view=EmbedVote())
    else:
        print("About to have the bot send a message for each candidate.")
        for candidate in candidateTuple:
            print("Creating message and voting reactions for: " + candidate)
            #await ctx.send("‎") # whitespace padding
            # output_candidate = await ctx.send("> ```" + candidate + "```\n\n")
            output_candidate = await ctx.send("# " + candidate)
            reactions = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
            for emoji in reactions:
                await output_candidate.add_reaction(emoji)
        await checkIfElectionIsFinished(ctx, args[2])


# Get how many days the STAR Voting election will last and set an end date.
def set_the_election_end_date(current_datetime, current_arg, args) -> tuple[str, int]:
    now = current_datetime
    seconds = 0
    minutes = 0
    hours = 0
    days = 0
    weeks = 0
    current_arg = current_arg
    print(args)
    for word in args[current_arg:]:
        if str(word).isnumeric():
            continue
        if word == "seconds":
            current_arg += 1
            seconds = int(args[current_arg])
        elif word == "minutes":
            current_arg += 1
            minutes = int(args[current_arg])
        elif word == "hours":
            current_arg += 1
            hours = int(args[current_arg])
        elif word == "days":
            current_arg += 1
            days = int(args[current_arg])
        elif word == "weeks":
            current_arg += 1
            weeks = int(args[current_arg])
        else:
            break
        current_arg += 1
    end_date = now + datetime.timedelta(seconds=seconds, minutes=minutes, hours=hours, days=days, weeks=weeks)
    end_date = end_date.strftime("%A, %B %d, %Y  %H:%M:%S")  # Example: Friday September 16, 2022  18:10:11
    return end_date, current_arg


@bot.command()
@commands.is_owner()
async def new_star_election(ctx: commands.Context, *args):
    URL = "https://star-vote.herokuapp.com/API/Elections"
    election_creator_id = ctx.author.id
    print("Election creator id: " + str(election_creator_id))
    election_name = args[0]
    days = int(args[1])
    print("Duration of Election: " + args[1] + " Days")
    candidates = args[2:]
    candidate_list = []
    for candidate in candidates:
        print("Candidate: " + candidate)
        new_candidate_obj = { "candidate_name": candidate}
        candidate_list.append(new_candidate_obj)
    new_race_obj = {
                       "title": election_name,
                       "voting_method": "STAR",
                       "num_winners": 1,
                       "candidates": candidate_list
                   }
    race_list = [new_race_obj]
    new_authentication_obj = {
                                 "voter_id": False,
                                 "email": True
                             }
    new_election_settings_obj = {
                                    "voter_access": "open",
                                    "voter_authentication": new_authentication_obj
                                }
    new_election_obj = {
                          "Election":
                          {
                            "title": election_name,
                            "owner_id": str(election_creator_id),
                            "state": "draft",
                            "races": race_list,
                            "settings": new_election_settings_obj,
                            "auth_key": jwt_secret_key
                          }
                       }

    # need to create a separate token for every user that votes, but those tokens don't need to be stored.
    response = requests.post(URL, json = new_election_obj, cookies = {"custom_id_token": jwt_token})
    print("response.url: " + response.url + "\n")
    print("response.status_code: " + str(response.status_code) + "\n")
    print("response.text: " + response.text + "\n")
    print("\n\n")

    response_data = json.loads(response.text)
    election_id = response_data["election"]["election_id"]

    await new_star_embed(ctx, election_id, election_name, days, candidates)

@bot.command()
@commands.is_owner()
async def list_star_candidates(ctx: commands.Context, *args):
    candidate_scores = dict()
    for candidate in args:
        message_sent = await ctx.send("```" + candidate + "\n```", ephemeral=True)
        candidate_scores[candidate] = 0
        await message_sent.add_reaction('0️⃣')
        await message_sent.add_reaction('1️⃣')
        await message_sent.add_reaction('2️⃣')
        await message_sent.add_reaction('3️⃣')
        await message_sent.add_reaction('4️⃣')
        await message_sent.add_reaction('5️⃣')
        #reaction = await bot.wait_for(['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣'], message_sent, )
        #await ctx.send("You responded with {}".format(reaction.emoji))

    print("Finished displaying candidates.")
    print("Candidate_scores dict:")
    for candidate in candidate_scores:
        print("\tCandidate: " + candidate + "    Score: " + str(candidate_scores[candidate]))

    def checkReaction(reaction, user):
        print("User: " + str(user))
        print("ctx.author: " + str(ctx.author))
        #print("Reaction.message: " + str(reaction.message))
        print("Reaction.message.content: " + str(reaction.message.content[3:-4]))
        return True

    score = 0
    print("Waiting for reaction now.")
    reaction_add, reactor = await bot.wait_for('reaction_add', check=checkReaction)
    print("Reaction added to one of the candidates.")
    print("Reaction_add.emoji: " + reaction_add.emoji)
    #reaction_remove = await bot.wait_for('reaction_remove', check=checkReaction)
    if reaction_add.emoji == '0️⃣':
        score = 0
    elif reaction_add.emoji == '1️⃣':
        score = 1
    elif reaction_add.emoji == '2️⃣':
        score = 2
    elif reaction_add.emoji == '3️⃣':
        score = 3
    elif reaction_add.emoji == '4️⃣':
        score = 4
    elif reaction_add.emoji == '5️⃣':
        score = 5

    candidate_scores[reaction_add.message.content[3:-4]] = score
    print("Updated candidate_scores dict:")
    for candidate in candidate_scores:
        print("\tCandidate: " + candidate + "    Score: " + str(candidate_scores[candidate]))

    thing = await ctx.send(view=SubmitBallotView())

@bot.command()
@commands.is_owner()
async def results(ctx: commands.Context, *args):
    """Creates a bar chart showing score count for each candidate. Proof of concept."""
    await ctx.send(f"Proof of concept to show score count for each candidate just using text.")

    # Create a dictionary linking candidates to their scores.
    candidates_scores = {}
    prev_key = "nothing"
    for count, value in enumerate(args):
        if count % 2 == 0:
            candidates_scores[value] = None
            prev_key = value
        else:
            candidates_scores[prev_key] = value

    # Sum up all the scores from each candidate and display it.
    total_score = 0.0
    for score in candidates_scores.values():
        total_score += float(score)
    await ctx.send(f"The sum of all candidate scores was {total_score}")

    # Print out the dict in a bar graph.
    padding_char = ' '
    candidate_padding_length = 8.0
    bar_graph_length = 20.0
    bar_graph_padding_char = '█'
    for candidate, score in candidates_scores.items():
        bar_graph_percentage = (float(score) / total_score)
        bar_graph_padding_length = bar_graph_percentage * bar_graph_length
        bar_graph_empty_padding_length = bar_graph_length - bar_graph_padding_length
        # await ctx.send(f"{bar_graph_percentage}\t{bar_graph_padding_length}\t{bar_graph_empty_padding_length}")
        # await ctx.send(f"{candidate :{padding_char}<{candidate_padding_length}}|████████████████████| {score}")
        await ctx.send(
            f"{str(candidate) :{padding_char}<{candidate_padding_length}}|{' ':{bar_graph_padding_char}<{bar_graph_padding_length}}{' ':{padding_char}>{bar_graph_empty_padding_length}}| {score}")

@bot.command()
async def new_star_election_using_emojis(ctx: commands.Context, *args):
    print("args: ", args)
    election_creator_id = ctx.author.id
    print("Election creator id: " + str(election_creator_id))
    election_name = args[0]
    # Get how many days the STAR Voting election will last and set an end date.
    now = datetime.datetime.now()
    current_arg = 1
    end_date, arg_count = set_the_election_end_date(now, current_arg, args)
    print("End Date: ", end_date)
    # print("Arg Count: ", arg_count)
    # print("Duration of Election: " + args[1] + " Days")
    candidates = args[arg_count:]
    candidate_list = []
    for candidate in candidates:
        print("Candidate: " + candidate)
        new_candidate_obj = { "candidate_name": candidate}
        candidate_list.append(new_candidate_obj)
    election_id = None

    await new_star_embed(ctx, election_id, election_name, end_date, candidates)


# This function runs periodically every hour
async def checkIfElectionIsFinished(ctx: commands.Context, election_end_time: str):
    now = datetime.datetime.now()
    date_time_format = "%A, %B %d, %Y  %H:%M:%S"
    election_end_datetime = datetime.datetime.strptime(election_end_time, date_time_format)
    current_date = now.strftime(date_time_format)  # Example: Friday September 16, 2022  18:10:11
    print("Current Date =", current_date)

    if now > election_end_datetime:  # check if the current time has past the end time
        print('Calculating Election Results')
        await ctx.send("### *The election has finished*.")
        await calculateElectionResultsFromEmojis(ctx)
    else:
        threading.Timer(1, checkIfElectionIsFinished, [ctx, election_end_time]).start()

async def calculateElectionResultsFromEmojis(ctx):
    #bot.owner_id is my id or whoever added the bot

    # Collect the message of each candidate.
    print(ctx.channel.name)
    list_of_bot_messages = []
    print("Channel History Loop")
    # will break if there are embedded messages posted after the poll options
    async for message in ctx.channel.history(limit=100):
        if message.author.bot and message.embeds:
            break
        elif message.author.bot and not message.embeds:
            list_of_bot_messages.append(message)

    candidate_list = await get_candidates_from_messages(list_of_bot_messages)
    vote_count = await count_each_index_of_scores(list_of_bot_messages)
    multiplied_indexes = await calculate_for_each_index_of_score(vote_count)
    total_scores = await calculate_total_scores(multiplied_indexes)
    await ctx.send("\n## Final Results")
    for index, candidate in enumerate(vote_count):
        print("### Candidate: " + candidate_list[index] + " was scored...")
        await ctx.send("### Candidate: " + candidate_list[index] + " was scored...")
        for score_index, score in enumerate(candidate):
            print(str(score_index) + "  -  " + str(score) + " times.")
            await ctx.send(str(score_index) + "  -  " + str(score) + " times.")
        print("### Final Score: " + str(total_scores[index]))
        await ctx.send("### Final Score: " + str(total_scores[index]))
    print("# Top 2 Runoff")
    await ctx.send("# Top 2 Runoff")
    top_2_candidates_index = [total_scores.index(i) for i in heapq.nlargest(2, total_scores)]
    print("### " + candidate_list[top_2_candidates_index[0]] + " with a score of " + str(total_scores[top_2_candidates_index[0]]))
    print("### " + candidate_list[top_2_candidates_index[1]] + " with a score of " + str(total_scores[top_2_candidates_index[1]]))
    await ctx.send("### " + candidate_list[top_2_candidates_index[0]] + " with a score of " + str(total_scores[top_2_candidates_index[0]]))
    await ctx.send("### " + candidate_list[top_2_candidates_index[1]] + " with a score of " + str(total_scores[top_2_candidates_index[1]]))
    await calculate_runoff_winner(ctx, list_of_bot_messages)


async def get_candidates_from_messages(list_of_bot_messages):
    candidate_list = []
    for message in list_of_bot_messages:
        if len(message.content) > 2 and message.content[0] == "#" and message.content[1] == " ":
            candidate_list.append(message.content.replace("#", "").strip())
    print("\nCandidate List", candidate_list)
    return candidate_list


# TODO: make safe against duplicate votes
async def count_each_index_of_scores(list_of_bot_messages):
    # Reprint the candidate and their total score
    number_of_candidates = 2
    vote_count = [[0] * 6 for _ in range(number_of_candidates)]
    current_candidate = 0
    for message in list_of_bot_messages:
        reactions = message.reactions
        # move to the next message if the reactions list is empty
        if not reactions:
            continue
        print()
        print(reactions)
        print("current_candidate: ", current_candidate)
        for index, reaction in enumerate(reactions):
            vote_count[current_candidate][index] = (reaction.count-1)
        current_candidate += 1
    print("\nVote Count")
    print(vote_count)
    return vote_count


async def calculate_for_each_index_of_score(vote_count):
    number_of_candidates = 2
    multiplied_indexes = [[0] * 6 for _ in range(number_of_candidates)]
    for i in range(number_of_candidates):
        for index, count in enumerate(vote_count[i]):
            multiplied_indexes[i][index] = index * count
    print("\nMultiplied Indexes")
    print(multiplied_indexes)
    return multiplied_indexes


async def calculate_total_scores(multiplied_indexes):
    number_of_candidates = 2
    total_scores = [0] * number_of_candidates
    for index, candidate in enumerate(multiplied_indexes):
        print("index:", index)
        print("candidate", candidate)
        candidate_total_score = 0
        for score in candidate:
            print("score", score)
            candidate_total_score += score
        print(total_scores)
        print(candidate_total_score)
        total_scores[index] = candidate_total_score
    print(total_scores)
    return total_scores


async def calculate_runoff_winner(ctx, list_of_bot_messages):
    print("\nReactions")
    user_to_preference_dict = {}
    for message in list_of_bot_messages:
        #print("if " + str(message.content) + "...")
        reactions = message.reactions
        if len(reactions) < 6:
            continue
        for i in reversed(range(6)):
            reaction = message.reactions[i]
            users = [user async for user in reaction.users()]
            print(users)
            for user in users:
                if user.bot:
                    continue
                if user.name not in user_to_preference_dict:
                    user_to_preference_dict[user.name] = message.content
            #await ctx.send(reaction.users())
            #users = await reaction.users().flatten()
            #print('\n'.join(map(str, users)))
            #await ctx.channel.send('\n'.join(map(str, users)))

bot.run(discord_token)
