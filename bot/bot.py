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

bot = MitesiClient()
# Command tree
tree = app_commands.CommandTree(bot)
tree.clear_commands(guild = None)

async def loop(guildID):
    game = guilds[guildID][1]
    while True:
        await asyncio.sleep(game.updateTimer)
        game.update()

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
    game = guilds[ctx.guild_id][1]
    response = '```'
    # send game stats: daycount, time in day, players, running, prev phase
    response += '\nGame stats:\n'
    response += 'Day: ' + str(game.cycle.dayCount) + '\n'
    response += 'Time in day: ' + str(game.cycle.phaseTime) + '\n'
    response += 'Players: ' + str(game.players) + '\n'
    response += 'Running: ' + str(game.running) + '\n'
    response += 'Previous phase: ' + str(game.prevPhase) + '\n\n'

    # also send information about each player
    # send player stats: name, death status, dying, voting, targets, rolename
    response += 'Player stats:\n'
    for player in game.players:
        response += 'Name: ' + str(player.name) + '\n'
        response += 'Dead: ' + str(player.dead) + '\n'
        response += 'Dying: ' + str(player.dying) + '\n'
        response += 'Voting: ' + str(player.voting) + '\n'
        response += 'Targets: ' + str(player.targets) + '\n'
        response += 'Role: ' + str(player.roleName) + '\n\n'
    response += '```'

    await ctx.response.send_message(response, ephemeral=True)

# game.channel_setup() command to set up the channels
@tree.command(name='channel_setup', description='Sets up the channels', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction):
    game = guilds[ctx.guild_id][1]
    # Set up the channels
    await game.channel_setup()

@tree.command(name='player_setup', description='Sets up the players', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction):
    game = guilds[ctx.guild_id][1]
    # Set up the channels
    await game.setup_players()

# Join command with options to join as a player or a spectator
@tree.command(name='join', description='Join the game', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction, spectator: bool = False):
    # Get the users roles
    roles = ctx.user.roles

    # Get the guild settings
    settings = guilds[ctx.guild_id][0].settings
    guildsettings: GuildSettings = guilds[ctx.guild_id][0]
    game = guilds[ctx.guild_id][1]

    # If the game is running, don't let them join
    if game.running and not spectator:
        await ctx.response.send_message('The game is already running!', ephemeral=True)
        return
    elif game.running and spectator:
        # Let them join as a spectator
        await ctx.user.add_roles(settings['roles']['spectator'])
        await ctx.response.send_message('You have joined as a spectator.', ephemeral=True)
        return

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
    game = guilds[ctx.guild_id][1]

    # Get the game master role
    game_master = settings['roles']['game master']

    # If the game is running and the user is a player, set them to dying
    if game.running and settings['roles']['player'] in roles:
        # Set the player to dying
        game.get_player(ctx.user).kill()
        # Send a leave message in #day
        await settings['channels']['day'].send(f'{ctx.user.mention} has left the game!')
    
    # Remove read and write permissions from the channels
    for channel in settings['channels'].values():
        try:
            await channel.set_permissions(ctx.user, overwrite=None)
        except:
            pass

    # Remove every game related role, except the game master role
    for role in roles:
        if role != game_master:
            # Make sure the role is a game role
            if role in settings['roles'].values():
                await ctx.user.remove_roles(role)
    
    guilds[ctx.guild_id][0].remove_participant(ctx.user)
    
    await ctx.response.send_message('You have left the game', ephemeral=True)

# Command to target a player
@tree.command(name='direct_target', description='Target a player by mention', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction, player: discord.Member):
    game = guilds[ctx.guild_id][1]

    # Get the user's Player object and set the target
    await game.get_player(ctx.user).set_target(player)

    await ctx.response.send_message(f'You have targeted {player.mention}', ephemeral=True)

# Command to target a player
@tree.command(name='t', description='Target a player (shorthand)', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction, player: str):
    # Get the guild settings
    settings = guilds[ctx.guild_id][0].settings
    guildsettings = guilds[ctx.guild_id][0]
    game = guilds[ctx.guild_id][1]

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
    
    # Get the user's Player object and set the target
    await game.get_player(ctx.user).set_target(player)

    # Ping the player
    await ctx.response.send_message(f'You have targeted {player.mention}', ephemeral=True)

# Command to target a player
@tree.command(name='target', description='Target a player', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction, player: str):
    # Get the guild settings
    settings = guilds[ctx.guild_id][0].settings
    guildsettings = guilds[ctx.guild_id][0]
    game = guilds[ctx.guild_id][1]

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

    # Get the user's Player object and set the target
    await game.get_player(ctx.user).set_target(player)

    # Ping the player
    await ctx.response.send_message(f'You have targeted {player.mention}', ephemeral=True)

# Command to vote for a player
@tree.command(name='vote', description='Vote for a player', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction, player: str):
    # Get the guild settings
    settings = guilds[ctx.guild_id][0].settings
    guildsettings = guilds[ctx.guild_id][0]
    game = guilds[ctx.guild_id][1]

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

    # Get the user's Player object and set the target
    await game.get_player(ctx.user).set_vote(player)

    # Ping the player
    await ctx.response.send_message(f'You have voted for {player.mention}', ephemeral=True)

# Command to run loop()
@tree.command(name='run', description='Run the game', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction):
    # Get the guild settings
    settings = guilds[ctx.guild_id][0].settings
    guildsettings = guilds[ctx.guild_id][0]
    game = guilds[ctx.guild_id][1]

    # Get the game master role
    game_master = settings['roles']['game master']

    # If the user is not the game master
    if game_master not in ctx.user.roles:
        await ctx.response.send_message('You are not the game master', ephemeral=True)
        return

    # If the game is already running
    if game.running:
        await ctx.response.send_message('The game is already running', ephemeral=True)
        return

    # Start the game
    game.running = True
    await ctx.response.send_message('The game has started', ephemeral=True)

    # Run the game loop
    await loop(ctx.guild_id)

# Command to distribute roles
@tree.command(name='distribute', description='Distribute roles', guild = discord.Object(id = '1013481020328251432'))
async def self(ctx: discord.Interaction):
    # Get the guild settings
    settings = guilds[ctx.guild_id][0].settings
    guildsettings: GuildSettings = guilds[ctx.guild_id][0]
    game: Game = guilds[ctx.guild_id][1]

    # Get the game master role
    game_master = settings['roles']['game master']

    # If the user is not the game master
    if game_master not in ctx.user.roles:
        await ctx.response.send_message('You are not the game master', ephemeral=True)
        return

    # If the game is already running
    if game.running:
        await ctx.response.send_message('The game is already running', ephemeral=True)
        return

    # Distribute the roles
    await game.distribute_roles()

    # Send a message to each player
    for player in game.players:
        await player.send_private(f'You are a {player.role}')

    await ctx.response.send_message('The roles have been distributed', ephemeral=True)

# start the bot
bot.run(token)