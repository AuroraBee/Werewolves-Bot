# This script contains the discord bot code.

import random
import asyncio
import time
import difflib
from game import *
from guild_settings import *
import discord
from discord import app_commands

# subclasses the discord.Client class
class MitesiClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild = discord.Object(id = '1013481020328251432'))
            self.synced = True
        print('------')
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        await self.change_presence(activity=discord.Game(name='with Mitesi!'))


# load the bot's token
with open('secretConfig/token.txt', 'r') as f:
    token = f.readlines()
token = [x.strip() for x in token]
token = token[0]

# load the bot's config
with open('secretConfig/config.txt', 'r') as f:
    config = f.readlines()
config = [x.strip() for x in config]

discordroles = {}

bot = MitesiClient()
# Command tree
tree = app_commands.CommandTree(bot)
tree.clear_commands(guild = None)

'''
async def update():
    while True:
        game.update()
        await asyncio.sleep(game.updateTimer)


# Command to give the player role to the person who sent the command
@tree.command(name='participate', description='Gives the player role to the person who sent the command', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction):
    await ctx.user.add_roles(discordroles['player'])
    await ctx.response.send_message('You have been given the player role', ephemeral=True)

# Command to remove the player role from the person who sent the command
@tree.command(name='leave', description='Removes the player role from the person who sent the command', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction):
    await ctx.user.remove_roles(discordroles['player'])
    await ctx.response.send_message('You have been removed from the player role', ephemeral=True)
    game.removeParticipant(ctx.user)

# Deferred command to start the game
@tree.command(name='start', description='Starts the game', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction):
    game.start()
    await ctx.response.send_message('Game started!')

# Command to tick the game
@tree.command(name='tick', description='Ticks the game', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction):
    game.update()
    await ctx.response.send_message('Game ticked!')

# Command to loop the game
@tree.command(name='startloop', description='Loops the game', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction):
    # use asyncio to start the game loop
    asyncio.create_task(update())
    await ctx.response.send_message('Game loop started!')
'''

@tree.command(name='setup', description='Sets everything up', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction):
    settings = GuildSettings(bot, ctx.guild)
    await settings.setup()

    # Create a game
    game = Game()
    game.setup(settings)

    # Add the guild to the database
    guilds[ctx.guild_id] = [settings, game]

    await ctx.response.send_message('Successfully set up the game!', ephemeral=True)

# Command to print information about the game
@tree.command(name='info', description='Prints information about the game', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction):
    await ctx.response.send_message(guilds[ctx.guild_id][0].settings, ephemeral=True)

# game.channel_setup() command to set up the channels
@tree.command(name='channel_setup', description='Sets up the channels', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction):
    # Get the guild settings
    game = guilds[ctx.guild_id][1]

    # Set up the channels
    await game.channel_setup()

# Join command with options to join as a player or a spectator
@tree.command(name='join', description='Join the game', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction, spectator: bool = False):
    # Get the users roles
    roles = ctx.user.roles

    # Get the guild settings
    settings = guilds[ctx.guild_id][0].settings
    guildsettings: GuildSettings = guilds[ctx.guild_id][0]

    # If the user already has the player role and is not a spectator
    if settings['roles']['player'] in roles and not spectator:
        guildsettings.add_participant(ctx.user)
        await ctx.response.send_message('You are already a player', ephemeral=True)
        return

    # If the user already has the spectator role and is a spectator
    if settings['roles']['spectator'] in roles and spectator:
        await ctx.response.send_message('You are already a spectator', ephemeral=True)
        return

    # If the user is a spectator and has the player role
    if settings['roles']['player'] in roles and spectator:
        # Remove the player role
        await ctx.user.remove_roles(settings['roles']['player'])
        guildsettings.remove_participant(ctx.user)
        # Add the spectator role
        await ctx.user.add_roles(settings['roles']['spectator'])
        await ctx.response.send_message('You are now a spectator', ephemeral=True)
        return

    # If the user is a player and has the spectator role
    if settings['roles']['spectator'] in roles and not spectator:
        # Remove the spectator role
        await ctx.user.remove_roles(settings['roles']['spectator'])
        # Add the player role
        await ctx.user.add_roles(settings['roles']['player'])
        guildsettings.add_participant(ctx.user)
        await ctx.response.send_message('You are now a player', ephemeral=True)
        return

    # If the player is a spectator
    if spectator:
        # Add the spectator role
        await ctx.user.add_roles(settings['roles']['spectator'])
        await ctx.response.send_message('You are now a spectator', ephemeral=True)
        return
    else:
        # Add the player role
        await ctx.user.add_roles(settings['roles']['player'])
        guildsettings.add_participant(ctx.user)
        await ctx.response.send_message('You are now a player', ephemeral=True)
        return
    
# Leave command to leave the game
@tree.command(name='leave', description='Leave the game', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction):
    # Get the users roles
    roles = ctx.user.roles

    # Get the guild settings
    settings = guilds[ctx.guild_id][0].settings

    # Remove every game related role
    for role in settings['roles']:
        # skip the Game Master role
        if role == settings['roles']['game_master']:
            continue
        if settings['roles'][role] in roles:
            await ctx.user.remove_roles(settings['roles'][role])
    
    guilds[ctx.guild_id][0].remove_participant(ctx.user)
    
    await ctx.response.send_message('You have left the game', ephemeral=True)

# Command to target a player
@tree.command(name='direct_target', description='Target a player by mention', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction, player: discord.Member):
    # Ping the player
    await ctx.response.send_message(f'You have targeted {player.mention}', ephemeral=True)

# Command to target a player
@tree.command(name='t', description='Target a player', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction, player: str):
    # Get the guild settings
    settings = guilds[ctx.guild_id][0].settings
    guildsettings = guilds[ctx.guild_id][0]

    # Get a list of all the players (Dict of ID: normalizedName)
    players: dict = guildsettings.get_participants()
    # Get the player whose name closest matches the input
    # using difflib
    player = difflib.get_close_matches(player, players.values(), n=1, cutoff=0.5)
    # Get the player ID
    # for each key in the dict, if the value matches the player name
    try:
        for key in players:
            if players[key] == player[0]:
                player = key
                break
    except IndexError:
        await ctx.response.send_message('No such player found', ephemeral=True)
        return
    
    # Get the player object
    player = ctx.guild.get_member(player)

    # Ping the player
    await ctx.response.send_message(f'You have targeted {player.mention}', ephemeral=True)

# Command to target a player
@tree.command(name='target', description='Target a player', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction, player: str):
    # Get the guild settings
    settings = guilds[ctx.guild_id][0].settings
    guildsettings = guilds[ctx.guild_id][0]

    # Get a list of all the players (Dict of ID: normalizedName)
    players: dict = guildsettings.get_participants()
    # Get the player whose name closest matches the input
    # using difflib
    player = difflib.get_close_matches(player, players.values(), n=1, cutoff=0.5)
    # Get the player ID
    # for each key in the dict, if the value matches the player name
    try:
        for key in players:
            if players[key] == player[0]:
                player = key
                break
    except IndexError:
        await ctx.response.send_message('No such player found', ephemeral=True)
        return
    
    # Get the player object
    player = ctx.guild.get_member(player)

    # Ping the player
    await ctx.response.send_message(f'You have targeted {player.mention}', ephemeral=True)

# start the bot
bot.run(token)