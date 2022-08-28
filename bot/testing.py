from cycle import Cycle
import time, random
from rolelist import *
from player import *

# Test the Cycle class by creating a new Cycle object and updating it every second.
# Print formatted output to the console.

# Create a new Cycle object.
length = {'day': 10, 'night': 4, 'voting': 4, 'judging': 3}
cycle = Cycle('day', length)

tick = False
prevPhase = 'day'

# List of players. List[Player]
players = []

# Create two new players.
for i in range(2):
    tmpPlayer = createPlayer('Player ' + str(i), 'Player ' + str(i) + '#0000')
    players.append(tmpPlayer)

# Get the rolelist for the current number of players.
rolelist = getRolelist(len(players), '1v1')

# Assign the each player a random role from the rolelist.
# remove the role from the rolelist.
'''for player in players:
    player.setRole(random.choice(rolelist))
    rolelist.remove(player.getRole())'''

# Set Player 1 to Villager
players[0].setRole(Villager())
# Set Player 2 to Werewolf
players[1].setRole(Werewolf())

print('Players:')
for player in players:
    print(player.getName() + ': ' + player.getRole().getName())
print('\n')


game = False

# Update the cycle every second.
while game:
    prevPhase = cycle.getPhase()
    cycle.update()
    
    if cycle.getPhaseChanged() and prevPhase != cycle.getPhase():
        # if new phase is day or night
        if cycle.getPhase() == 'day' or cycle.getPhase() == 'night':
            tick = True
    else:
        tick = False
    
    # print formatted output to the console, detailing if a tick has occurred.
    print('\n' + '-' * 20)
    print('Current phase: ' + cycle.getPhase())
    print('Phase time: ' + str(cycle.getPhaseTime()))
    print('Phase length: ' + str(cycle.getPhaseLength()))
    print('Phase changed: ' + str(cycle.getPhaseChanged()))
    print('Previous phase: ' + prevPhase)
    print('Tick: ' + str(tick))
    print('-' * 20)

    cycle.setPhaseChanged(False)
    time.sleep(1)