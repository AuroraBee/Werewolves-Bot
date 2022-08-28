from roleClasses import *
from commons import *
import math, random
from winconditions import *

# This is the file to define the rolelists for the bot.


# RoleCodes list: code: ClassName
# The role codes are as follows:
roleCodes = {
    'vil': 'Villager',
    'were': 'Werewolf',
    'seer': 'Seer',
    'witch': 'Witch',
    'hunter': 'Hunter',
    'ga': 'GuardianAngel',
    'sk': 'SerialKiller',
    'doc': 'Doctor',
    'sher': 'Sheriff',
    'inv': 'Investigator',
    'jest': 'Jester'
}

rolelists = {
    '1v1': [
        'vil',
        'were',
    ],
    'default': [
        # 4 villagers to 1 wolf
        'vil', 'vil', 'vil', 'vil',
        'were'
    ],
    'wonTest': [
        'vil', 'vil', 'vil', 'vil'
    ],
}

def codeToClass(code):
    # This returns the class that the code defines
    return roleDictionary[roleCodes[code]]

def adjustRolelist(playerNumber, rolelistName):
    # This adjust the rolelist to the number of players, preserving ratios
    ratios = {}
    for role in rolelists[rolelistName]:
        if role in ratios:
            ratios[role] += 1
        else:
            ratios[role] = 1
    
    # Normalize the ratios
    total = 0
    for role in ratios:
        total += ratios[role]
    for role in ratios:
        ratios[role] /= total

    # Create the new rolelist
    newRolelist = []
    # for each unique role in the rolelist
    for role in set(rolelists[rolelistName]):
        # for each player
        for i in range(math.ceil(playerNumber * ratios[role])):
            newRolelist.append(role)
    
    # make sure the new rolelist has a length equal to the number of players
    while len(newRolelist) < playerNumber:
        newRolelist.append(newRolelist[0])
    # if it is longer, remove a villager, if there is one
    if len(newRolelist) > playerNumber and 'vil' in newRolelist:
        newRolelist.remove('vil')
    # if there is no villager, remove a random role
    elif len(newRolelist) > playerNumber:
        newRolelist.remove(random.choice(newRolelist))

    # Return the new rolelist
    return newRolelist

def getRolelist(playerNumber, rolelistName):
    # This returns the rolelist for the given number of players
    rolelist = adjustRolelist(playerNumber, rolelistName)
    # shuffle the rolelist
    random.shuffle(rolelist)
    return [codeToClass(code)() for code in rolelist]

