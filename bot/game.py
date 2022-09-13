from fileinput import lineno
from cycle import Cycle
import time
import random
from rolelist import *
from player import *
from winconditions import *
from guild_settings import *
import discord
from player import *

# Game class


class Game:
    def __init__(self):
        self.bot = None
        self.guild = None
        self.settings: dict = None
        self.guildsettings: GuildSettings = None
        self.cycle = None
        self.players = []
        self.livingPlayers = []
        self.deadPlayers = []

        self.running = False
        self.gameStarted = False
        self.gameEnded = False
        self.playersWhoWon = []

        self.tick = False
        self.prevPhase = 'day'

        self.updateTimer = 1
    
    def setup(self, settings: GuildSettings):
        self.settings = settings.settings
        self.guildsettings = settings

        self.bot = settings.bot
        self.guild = settings.guild

        self.cycle = Cycle('day', self.settings['cycles'])
        self.updateTimer = self.settings['game']['updateTimer']

    async def channel_setup(self):
        # Delete every channel in the category
        for channel in self.guildsettings.category.channels:
            await channel.delete()

        # Create the basic channels
        # For each channel in the settings
        for channel in self.settings['channels']:# Create the channel
            self.settings['channels'][channel] = await self.guild.create_text_channel(channel, category=self.guildsettings.category)
            # Set the permissions for the channel
            # Hide the channel from everyone
            await self.settings['channels'][channel].set_permissions(self.guild.default_role, read_messages=False, send_messages=False)
            # If the channel is the day channel
            if channel == 'day':
                # Set the description
                await self.settings['channels'][channel].edit(topic='Day 1 - 60 seconds left')
                # Allow the alive role to read and write, but disallow the dead role to write
                await self.settings['channels'][channel].set_permissions(self.settings['roles']['alive'], read_messages=True, send_messages=True)
                await self.settings['channels'][channel].set_permissions(self.settings['roles']['dead'], read_messages=True, send_messages=False, add_reactions=False)
            # If the channel is the dead channel
            elif channel == 'dead':
                # Set the description
                await self.settings['channels'][channel].edit(topic='Dead Chat, for those who have died.')
                # Allow the dead role to read and write, but disallow the alive role to read and write
                await self.settings['channels'][channel].set_permissions(self.settings['roles']['dead'], read_messages=True, send_messages=True, read_message_history=False)
                await self.settings['channels'][channel].set_permissions(self.settings['roles']['alive'], read_messages=False, send_messages=False, read_message_history=False)
            # If the channel is the spectator channel
            elif channel == 'spectator':
                # Set the description
                await self.settings['channels'][channel].edit(topic='Spectator Chat, for those who just want to observe.')
                # Allow the spectator role to read and write
                await self.settings['channels'][channel].set_permissions(self.settings['roles']['spectator'], read_messages=True, send_messages=True)
                # Disallow the alive, dead and player role to read and write, or read the message history
                await self.settings['channels'][channel].set_permissions(self.settings['roles']['alive'], read_messages=False, send_messages=False, read_message_history=False)
                await self.settings['channels'][channel].set_permissions(self.settings['roles']['dead'], read_messages=False, send_messages=False, read_message_history=False)
                await self.settings['channels'][channel].set_permissions(self.settings['roles']['player'], read_messages=False, send_messages=False, read_message_history=False)
            elif channel == 'mafia':
                # Set the description
                await self.settings['channels'][channel].edit(topic='Mafia Chat, to plot and plan murderous acts.')
            elif channel == 'vampires':
                # Set the description
                await self.settings['channels'][channel].edit(topic='Vampire Chat, to plan whom to convert next, may they be town. Or simply to discuss the weather.')
            elif channel == 'coven':
                # Set the description
                await self.settings['channels'][channel].edit(topic='Coven Chat, to act upon thine witchy ways, with thine coven behind thine back.')
            elif channel == 'werewolves':
                # Set the description
                await self.settings['channels'][channel].edit(topic='Werewolf Chat, to discuss the latest gossip, and to plan the next attack.')
            # Allow the spectator role to read every channel, but disallow them to write and react
            await self.settings['channels'][channel].set_permissions(self.settings['roles']['spectator'], read_messages=True, send_messages=False, read_message_history=True, add_reactions=False)

    async def setup_players(self):
        # For each player in self.settings['players']
        for player in self.settings['players']:
            newPlayer = Player(player, self.settings['players'][player], self.guildsettings)
            self.players.append(newPlayer)
            # Give the player the alive role
            await newPlayer.member.add_roles(self.settings['roles']['alive'])
            # Give the player the player role if they don't have it
            if self.settings['roles']['player'] not in newPlayer.member.roles:
                await newPlayer.member.add_roles(self.settings['roles']['player'])

            # Rename the player to their name (self.settings['players'][player])
            # Check if the bot the necessary permissions to do so
            if self.guild.me.guild_permissions.manage_nicknames:
                try:
                    await newPlayer.member.edit(nick=self.settings['players'][player])
                except discord.Forbidden:
                    print('Bot does not have permission to change nicknames')

            # Create the player's private channel and set the permissions for it
            newPlayer.channel = await self.guild.create_text_channel(self.settings['players'][player], category=self.guildsettings.category)
            await newPlayer.channel.set_permissions(self.guild.default_role, read_messages=False, send_messages=False)
            await newPlayer.channel.set_permissions(self.settings['roles']['spectator'], read_messages=True, send_messages=False, read_message_history=True, add_reactions=False)
            await newPlayer.channel.set_permissions(newPlayer.member, read_messages=True, send_messages=True)
            # Change description
            await newPlayer.channel.edit(topic=f'Private channel for {self.settings["players"][player]}. Use /t and write your targets name to target them.')

            # Add the channel to the settings
            self.settings['playerChannels'][self.settings['players'][newPlayer.id]] = newPlayer.channel

    def getPlayer(self, member: discord.Member):
        for player in self.players:
            if player.member == member:
                return player
        return None
    
    def get_player(self, member: discord.Member):
        return self.getPlayer(member)

    async def distribute_roles(self):
        rolelist = getRolelist(len(self.players), self.settings['rolelist'])
        # shuffle the rolelist
        random.shuffle(rolelist)
        # For each player in self.players
        for player in self.players:
            player.setRole(rolelist.pop())
            # If the role has a channel, add the player to the channel
            if player.role.hasChannel:
                # If the player is a mafia, add them to the mafia channel
                if player.role.alignment == 'mafia':
                    # Change the mafia channel's permissions to allow the player to read and write
                    await self.settings['channels']['mafia'].set_permissions(player.member, read_messages=True, send_messages=True)
                    await self.settings['channels']['mafia'].send(f'{player.member.mention} is a {player.role.name}')
                elif player.role.alignment == 'vampire':
                    # Change the vampire channel's permissions to allow the player to read and write
                    await self.settings['channels']['vampires'].set_permissions(player.member, read_messages=True, send_messages=True)
                    await self.settings['channels']['vampires'].send(f'{player.member.mention} is a {player.role.name}')
                elif player.role.alignment == 'werewolf':
                    # Change the werewolf channel's permissions to allow the player to read and write
                    await self.settings['channels']['werewolves'].set_permissions(player.member, read_messages=True, send_messages=True)
                    await self.settings['channels']['werewolves'].send(f'{player.member.mention} is a {player.role.name}')
                elif player.role.alignment == 'coven':
                    # Change the coven channel's permissions to allow the player to read and write
                    await self.settings['channels']['coven'].set_permissions(player.member, read_messages=True, send_messages=True)
                    await self.settings['channels']['coven'].send(f'{player.member.mention} is a {player.role.name}')

    # Update function: Ticks every second
    def update(self):
        # TODO: integrate Day/Night cycle

