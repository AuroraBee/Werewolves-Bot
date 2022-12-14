from cycle import Cycle
from commons import *

# Base class for roles.
class BaseRole:
    def __init__(self, name = 'Villager', description = 'A simple villager', alignment = 'town', strength = 0, immunity = 0, bypasses = {'admin': True}, phases = []):
        self.name = name
        self.description = description
        self.alignment = alignment
        self.strength = strength
        self.immunity = immunity
        self.tempImmunity = 0
        self.bypasses = bypasses
        self.phases = phases
        self.hasMultipleTargets = False
        self.votingCount = 1
        self.hasChannel = False
        # priority is used to determine the order in which the roles perform their actions
        # higher priority roles perform their actions first
        self.priority = 1
        self.val = 0

    # Function to perform the action of the role.
    def action(self, player, target):
        return "This role has no action."

    # Function to determine if a given attack can kill this role.
    def canDieFrom(self, attack):
        if attack['source'] in self.bypasses:
            return self.bypasses[attack['source']]
        else:
            return attack['value'] > self.immunity + self.tempImmunity

    # Function to perform the action of the role.
    # targets is a dict of {1: target1, 2: target2}
    def performAction(self, player, targets: dict, phase):
        if (self.dead): return
        # if the current phase is in the phases list, perform the action
        if phase in self.phases:
            return self.action(player, targets)
        else:
            print('{} cannot perform action in phase {}'.format(self.name, phase))
            return None
    
    def getName(self):
        return self.name

    def getDescription(self):
        return self.description

    def getAlignment(self):
        return self.alignment

    def getStrength(self):
        return self.strength

    def getImmunity(self):
        return self.immunity + self.tempImmunity

    def getBypasses(self):
        return self.bypasses

    def getPhases(self):
        return self.phases

    def setTempImmunity(self, value):
        self.tempImmunity = value


# Class: Werewolf
# A werewolf.
class Werewolf(BaseRole):
    def __init__(self):
        super().__init__()
        self.name = 'Werewolf'
        self.description = 'Kill all those who oppose you to win!'
        self.alignment = 'werewolf'
        self.strength = 2
        self.immunity = 1
        self.bypasses = {'admin': True}
        self.phases = ['night']
        self.hasChannel = True

    def action(self, player, target):
        # If the target can be killed, kill them.
        if self.canKillTarget(target):
            target.kill()
            return True
        else:
            print("Cant kill target.")
            return False

    def canKillTarget(self, target):
        return target.role.canDieFrom({'source': self.alignment, 'value': self.strength})

# Add the Werewolf role to the roleDictionary
roleDictionary['Werewolf'] = Werewolf

# Class: Villager
# A simple villager.
class Villager(BaseRole):
    def __init__(self):
        super().__init__()

    # The Villager doesnt do anything, so it just returns.
    def performAction(self, player, target):
        return True

roleDictionary['Villager'] = Villager