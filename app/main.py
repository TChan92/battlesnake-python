import bottle
import os
import sys
# from pprint import pprint

from Snake import Snake
from Map import Map
from utils import *

ourSnakeId = ""
ourName = "CleverNameSnake"
originalDictionary = {}
mapObj = Map()

@bottle.route('/')
def static():
    return "the server is running"


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path,root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    mapObj.game_id = data['game_id']
    mapObj.board_width = data['width']
    mapObj.board_height = data['height']

    # head_url = '%s://%s/static/head.gif' % (
    #     bottle.request.urlparts.scheme,
    #     bottle.request.urlparts.netloc
    # )

    return {
        'color': '#FFA500',
        'taunt': 'TODO Get Taunt Later',
        # 'head_url': head_url,
        'head_url': 'http://via.placeholder.com/300',
        'name': ourName,
        'head_type': "pixel",
        'tail_type': "pixel"
    }

@bottle.post('/move')
def move():
    snakeObj = Snake() 
    data = bottle.request.json
    mapObj.setData(data)
    # pprint(data)
    # True/False for every spot on the board for visited nodes in BFS
    if (len(originalDictionary) < 1):
        generateDictionaryTF(mapObj, originalDictionary)
    turnDictionary = originalDictionary.copy()
    # Remove spots that are completely unavailable
    # Makes list for other snakes by looking at all snakes with name != ours
    for snake in data['snakes']['data']:
        if snake['id'] == data['you']['id']:
            print(snake)
            ourSnake = snake
            snakeObj.ourSnake = ourSnake
            snakeObj.headOfOurSnake = ourSnake['body']['data'][0]
            snakeObj.health = ourSnake['health']
        else:
            snakeObj.otherSnakes.append(snake)

        # If it's the first few turns we want to not remove the tail from nodes that can be removed from the list
        # as the snake extends out in the first 3 turns
        coordsToIterateThrough = snake['body']['data'][:-1]
        if data['turn'] < 2:
            coordsToIterateThrough = snake['body']['data']

        # removes all snake bodies/tail (not head) from list of
        # possible co-ordinates
        for coord in coordsToIterateThrough:
            x = coord['x']
            y = coord['y']
            # removes move directions that are directly onto enemy snakes
            if not turnDictionary.get((x, y), None) is None:
                del turnDictionary[(x, y)]
            
    # dictionary of all 4 directions
    t = (snakeObj.headOfOurSnake['x'], snakeObj.headOfOurSnake['y'])
    directionsCanGo = getDirectionsCanGo(t,
            turnDictionary)
    # dictionary holding all possible directions in form:
    # [direction, heuristicValue]
    directionHeuristics = {}
    removeSnakeCollisions(snakeObj, turnDictionary, directionHeuristics)
    # set collision directions == 5 (Danger)
    currMove = determineMovePriority(directionsCanGo, 
                                     turnDictionary,  
                                     mapObj, 
                                     directionHeuristics, 
                                     snakeObj)
    # danger check should happen after food evaluation

    # send determined move to server
    return {
        'move': currMove,
        # 'taunt': tauntGenerator(mapObj)
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()


if __name__ == '__main__':
    port = '8080'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    bottle.run(application, host=os.getenv('IP', '127.0.0.1'), port=os.getenv('PORT', 8080), debug=True)