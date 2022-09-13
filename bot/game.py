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
                await self.settings['channels'][channel].set_permissions(self.settings['roles']['dead'], read_messages=True, send_messages=False)
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
            elif channel == 'vampire':
                # Set the description
                await self.settings['channels'][channel].edit(topic='Vampire Chat, to plan whom to convert next, may they be town. Or simply to discuss the weather.')
            # Allow the spectator role to read every channel, but disallow them to write and react
            await self.settings['channels'][channel].set_permissions(self.settings['roles']['spectator'], read_messages=True, send_messages=False, read_message_history=True, add_reactions=False)

    async def setup_players(self):
        # For each player in self.settings['players']
        for player in self.settings['players']:
            


