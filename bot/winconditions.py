from roleClasses import *
from commons import *

'''
Input: list of roles.
Output: True/False
Description: This function returns True if the game is won, False otherwise.
'''
def isWon(players):
    # Check if the game is won
    # Is there only one role left?
    if len(players) <= 1:
        return True
    # Is there only one alignment left?
    alignments = {}
    for player in players:
        x = player.role.alignment
        if x in alignments:
            alignments[x] += 1
        else:
            alignments[x] = 1
    if len(alignments) == 1:
        return True
    
    return False
