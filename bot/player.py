from commons import *
from guild_settings import *
from guild_settings import *
from roleClasses import *


class Player:
    def __init__(self, id: int, name: str, guildsettings: GuildSettings):
        self.id = id
        self.name = name
        self.guildsettings = guildsettings

        self.role = None
        self.roleName = None
        self.hasChannel = False
        self.channel = None

        self.dead = False

        self.voting = None

        self.targets = {
            1: None,
            2: None
        }
        


