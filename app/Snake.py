import json
# from SnakeStates import SnakeState

    
class Snake(object):
    def __init__(self):
        # self.curState = SnakeState()
        self.currTaunt = 'meow'
        self.ourSnake = {}
        self.headOfOurSnake = None
        self.ourSnake = None
        self.otherSnakes = []
        self.health = 0
        return