# This example requires the 'message_content' privileged intent to function.
import datetime
import os
import traceback

import discord
from discord import TextStyle
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('TOKEN')

# The guild in which this slash command will be registered.
# It is recommended to have a test guild to separate from your "production" bot
TEST_GUILD = discord.Object(id=918037457277161492)


class CandidateScorecardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='0', style=discord.ButtonStyle.grey, custom_id='persistent_view:0')
    async def zero(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Make sure to update the message with our updated selves
        self.reset_all_buttons()
        button.style = discord.ButtonStyle.blurple
        button.disabled = True
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='1', style=discord.ButtonStyle.grey, custom_id='persistent_view:1')
    async def one(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Make sure to update the message with our updated selves
        self.reset_all_buttons()
        button.style = discord.ButtonStyle.blurple
        button.disabled = True
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='2', style=discord.ButtonStyle.grey, custom_id='persistent_view:2')
    async def two(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Make sure to update the message with our updated selves
        self.reset_all_buttons()
        button.style = discord.ButtonStyle.blurple
        button.disabled = True
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='3', style=discord.ButtonStyle.grey, custom_id='persistent_view:3', row=1)
    async def three(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Make sure to update the message with our updated selves
        self.reset_all_buttons()
        button.style = discord.ButtonStyle.blurple
        button.disabled = True
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='4', style=discord.ButtonStyle.grey, custom_id='persistent_view:4', row=1)
    async def four(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Make sure to update the message with our updated selves
        self.reset_all_buttons()
        button.style = discord.ButtonStyle.blurple
        button.disabled = True
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='5', style=discord.ButtonStyle.grey, custom_id='persistent_view:5', row=1)
    async def five(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Make sure to update the message with our updated selves
        self.reset_all_buttons()
        button.style = discord.ButtonStyle.blurple
        button.disabled = True
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

    @discord.ui.button(label='Submit', style=discord.ButtonStyle.green, custom_id='persistent_view:green')
    async def submitballot(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ballot submitted :)")


class BallotView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


class EmbedVote(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Vote', style=discord.ButtonStyle.green, custom_id='persistent_view:vote')
    async def vote(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Make sure to update the message with our updated selves
        await interaction.response.send_message("Score these candidates on a 0 to 5 scale.\nCandidate Name",
                                                view=BallotView(), ephemeral=True)


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
    async def editcandidates1(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Need to make sure only the creator can edit the embed.
        # if (interaction.user == message.user):
        await interaction.response.send_modal(STARVotingCandidateEdit())

    @discord.ui.button(label='Edit Candidates 2', style=discord.ButtonStyle.blurple,
                       custom_id='persistent_view:editcandidates2')
    async def editcandidates2(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Need to make sure only the creator can edit the embed.
        # if (interaction.user == message.user):
        await interaction.response.send_modal(STARVotingCandidateEdit())


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


class STARVotingBot(commands.Bot):
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


bot = STARVotingBot()
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
                    "???? Red Party         ???? Green Party" \
             "\n\n\n???? Orange Party      ???? Blue Party" \
             "\n\n\n???? Yellow Party      ???? Purple Party" \
                    "```"
    return party_list


@bot.command()
@commands.is_owner()
async def star(ctx: commands.Context, *args):
    """Creates an embed for a STAR voting election.
        args:
            ElectionTitle: Title of the election
            Days: Number of days the election will last.
            Candidates: As many candidates as you want. Using both firstname and lastname requires "Jane Doe"
        example:
            .star "What is the best color?" 5 Blue Red Green Yellow Purple Orange
    """
    # The first argument should be the election title.
    electionTitle = args[0]
    # Get how many days the STAR Voting election will last and set an end date.
    now = datetime.datetime.now()
    days = int(args[1])
    endDate = now + datetime.timedelta(days)
    endDate = endDate.strftime("%A, %B %d, %Y  %H:%M:%S")  # Example: Friday September 16, 2022  18:10:11
    # Set the candidates into their own variable.
    candidateTuple = args[2:]
    candidates = str(candidateTuple)
    # Pretty print the candidates
    #candidates_prettified = prettify_candidates(candidates)

    # Using block quotes via "> " or ">>> " looks nice so maybe use it for the formatting of values.

    # Create the instructions for the embed.
    star_voting_instructions = "See the image below for instructions \non how a STAR voting election works! " \
                               "\nThen click on Vote and fill out your ballot!"
    embedVar = discord.Embed(
        title=electionTitle, description=star_voting_instructions,
        color=0x336EFF, timestamp=now
    )
    embedVar.add_field(name="End Date", value=f"This election will end in {days} days on\n{endDate}", inline=False)

    #for x in args[2:]:
    # Add candidates under their respective parties, if the parties exist.
    # Adding so many parties may visually clutter the embed,
    # especially with emojis to represent color or symbols of each party.
    # Might want to save labeling by party until once the voter clicks on the button to vote.
    embedVar.add_field(name="???? Red Party", value=f"> {candidates}", inline=True)
    embedVar.add_field(name="???? Orange Party", value=f"> {candidates}", inline=True)
    embedVar.add_field(name="???? Yellow Party", value=f"> {candidates}", inline=True)
    embedVar.add_field(name="???? Green Party", value=f"> {candidates}", inline=True)
    embedVar.add_field(name="???? Blue Party", value=f"> {candidates}", inline=True)
    embedVar.add_field(name="???? Purple Party", value=f"> {candidates}", inline=True)

    embedVar.add_field(name="Current Vote Count:", value="#ofvotes", inline=False)

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

    await ctx.send(embed=embedVar)
    await ctx.send(view=EmbedEdit(), ephemeral=True)
    await ctx.send(view=EmbedVote())


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
    bar_graph_padding_char = '???'
    for candidate, score in candidates_scores.items():
        bar_graph_percentage = (float(score) / total_score)
        bar_graph_padding_length = bar_graph_percentage * bar_graph_length
        bar_graph_empty_padding_length = bar_graph_length - bar_graph_padding_length
        # await ctx.send(f"{bar_graph_percentage}\t{bar_graph_padding_length}\t{bar_graph_empty_padding_length}")
        # await ctx.send(f"{candidate :{padding_char}<{candidate_padding_length}}|????????????????????????????????????????????????????????????| {score}")
        await ctx.send(
            f"{str(candidate) :{padding_char}<{candidate_padding_length}}|{' ':{bar_graph_padding_char}<{bar_graph_padding_length}}{' ':{padding_char}>{bar_graph_empty_padding_length}}| {score}")


bot.run(token)
