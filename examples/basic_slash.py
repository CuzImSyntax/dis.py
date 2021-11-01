# This example requires the 'members' privileged intents

import discord
from discord.ext import commands
import random
import typing

#Important!! When using slash commands, arguments should always be typehinted.

description = '''An example bot to showcase the discord.ext.commands extension
module.

There are a number of utility commands being showcased here.'''

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='?', description=description, intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.slash_command(
    description="Adds two numbers together.",
    #Sets the description for the args showing in discord
    arg_descriptions={
        'left': 'The first number to add together.',
        'right': 'The second number to add together.'})
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.reply(left + right)

@bot.slash_command(
    #Makes the slash command a guild command so it is only available in the guilds in the list.
    guilds=[681821783908810752]
)
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""   #When existing, the docstring wil be used as command description.
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        return await ctx.reply('Format has to be in NdN!')

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.reply(result)

@bot.slash_command(
    description='For when you wanna settle the score some other way.',
    arg_descriptions={'choices': 'A list of different choices seperated with a `:`.'})
async def choose(ctx, choices: str):
    await ctx.reply(random.choice(choices.split(":")))

@bot.slash_command()
async def repeat(ctx, times: int, content: str = 'repeating...'):
    """Repeats a message multiple times."""
    for i in range(times):
        try:
            await ctx.reply(content)
        except discord.InteractionResponded:
            #We want to send a followup after one time as you can only reply to an interaction one time.
            await ctx.reply_followup(content)

@bot.slash_command(
    arg_descriptions={'member': 'The member to check.'})
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.reply(f'{member.name} joined in {member.joined_at}')

#Notice! Because of a discord limitation, group callbacks can't be executed alone, the only way to execute them is
#by invoking a subcommand and have invoke_without_command set to False, as it is by default.
@bot.slash_group()
async def cool(ctx):
    """Says if a user is cool.
    In reality this just gives the subcommand getting invoked.
    """

    await ctx.send(f'No, {ctx.invoked_subcommand} is not cool')
    #You can still send normal messages.
    #When there is no response on the interaction discord will raise an error to the user though.


@cool.slash_command(name='bot')
async def _bot(ctx):
    """Is the bot cool?"""
    await ctx.reply('Yes, the bot is cool.')


@bot.slash_command(name="animal",
                   description="Pick your favorite Animal from a given list.",
                   arg_description={"animal": "Choose your favorite animal."})
async def _animal(ctx, animal: typing.Literal["Cat", "Dog", "Lion", "Elephant"]):
    #With a Literal, you can give users choices, to choose from
    await ctx.reply(f"Oh cool, my favorite animal is the {animal} too.")

bot.run("token")
