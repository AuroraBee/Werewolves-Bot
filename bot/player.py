from commons import *

class Player:
    def __init__(self):
        self.name = 'NULL'
        self.role = None
        self.tag = 'NULL#0000'
        self.id = -1
        self.target = -1
        self.will = ''
        self.notes = ''

    # Function to set the name
    def setName(self, name):
        self.name = name

    def setRole(self, role):
        self.role = role

    def setTag(self, tag):
        self.tag = tag

    def setID(self, id):
        self.id = id

    def setTarget(self, target):
        self.target = target
    
    def setWill(self, will):
        self.will = will

    def setNotes(self, notes):
        self.notes = notes
    
    def getNotes(self):
        return self.notes

    def getWill(self):
        return self.will

    def getName(self):
        return self.name

    def getRole(self):
        return self.role

    def getTag(self):
        return self.tag

    def getID(self):
        return self.id

    def getTarget(self):
        return self.target

    def performAction(self):
        self.role.performAction(self, self.target)

    
def createPlayer(name, tag):
    global id
    player = Player()
    player.setName(name)
    player.setTag(tag)
    player.setID(id)
    id += 1
    return player

