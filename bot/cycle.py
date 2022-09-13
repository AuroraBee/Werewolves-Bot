import time

class Cycle:
    def __init__(self, phase, length = {'day': 60, 'night': 40, 'voting': 40, 'judging': 15}):
        self.phase = phase
        self.length = length
        self.lastTime = time.time()
        self.phaseTime = 0
        self.phase_length = length[phase]
        self.phaseChanged = False
    
    def update(self):
        self.phaseTime = time.time() - self.lastTime
        if self.phaseTime > self.phase_length:
            self.phaseTime = 0
            self.lastTime = time.time()
            self.phase = self.nextPhase()
            self.phase_length = self.length[self.phase]
            self.phaseChanged = True

    def nextPhase(self):
        # if the phase is day, move to voting
        if self.phase == 'day':
            return 'voting'
        # if the phase is voting or judging, move to night
        elif self.phase == 'voting' or self.phase == 'judging':
            return 'night'
        # if the phase is night, move to day
        elif self.phase == 'night':
            return 'day'
        else:
            print('Error: invalid phase')
            return 'day'

    def getPhase(self):
        return self.phase

    def getPhaseTime(self):
        return self.phaseTime

    def getPhaseLength(self):
        return self.phase_length

    def getPhaseChanged(self):
        return self.phaseChanged

    def setPhase(self, phase):
        self.phase = phase
        self.phase_length = self.length[phase]
        self.phaseTime = 0
        self.lastTime = time.time()
        self.phaseChanged = True

    def setPhaseTime(self, phaseTime):
        self.phaseTime = phaseTime
        self.lastTime = time.time() - phaseTime
        self.phaseChanged = True

    def setPhaseLength(self, phaseLength):
        self.phase_length = phaseLength
        self.phaseTime = 0
        self.lastTime = time.time()
        self.phaseChanged = True

    def setPhaseChanged(self, phaseChanged):
        self.phaseChanged = phaseChanged

