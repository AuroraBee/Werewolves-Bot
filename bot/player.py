from commons import *
from guild_settings import *
from roleClasses import *


class Player:
    def __init__(self, id: int, name: str, guildsettings: GuildSettings):
        self.id = id
        self.member = guildsettings.guild.get_member(id)
        self.name = name
        self.guildsettings = guildsettings

        self.role: BaseRole = None
        self.roleName = None
        self.channel: discord.TextChannel = None

        self.dead = False
        self.dying = False

        self.voting = None

        self.targets = {
            1: None,
            2: None
        }
    
    async def send(self, message):
        if self.channel and message:
            await self.channel.send(message)
    
    async def send_private(self, message):
        if self.member and message:
            await self.member.send(message)
    
    # Function to set the role of the player
    def setRole(self, role: BaseRole):
        self.role = role
        self.roleName = role.name

    # Function to target a player
    async def set_target(self, target: discord.Member, number: int = 1):
        # Get the player object of the target
        targetPlayer = guilds[self.guildsettings.guild.id][1].getPlayer(target)
        if targetPlayer:
            self.targets[number] = targetPlayer
        else:
            await self.send(f'Could not find player {target.name}.')
    
    # Function to vote for a player
    async def set_vote(self, target: discord.Member):
        # Get the player object of the vote
        targetPlayer = guilds[self.guildsettings.guild.id][1].getPlayer(target)
        if targetPlayer:
            self.voting = targetPlayer
        else:
            await self.send(f'Could not find player {target.name}.')

    def kill(self):
        self.dying = True

    def revive(self):
        self.dead = False
        self.dying = False
    
    def update(self):
        if self.dying:
            self.dead = True
            self.dying = False

    # Function to perform the action of the role
    async def performAction(self):
        if (self.dead): return
        response = await self.role.performAction(self, self.targets, guilds[self.guildsettings.guild.id][1].prevPhase)
        # Send the response to the players channel
        await self.send(response)
        # Reset the targets
        self.targets = {
            1: None,
            2: None
        }

    def getRole(self):
        return self.role

    def getRoleName(self):
        return self.roleName

    def getChannel(self):
        return self.channel

    def getTargets(self):
        return self.targets

    def getVoting(self):
        return self.voting

    def isDead(self):
        return self.dead

    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def getMember(self):
        return self.member




