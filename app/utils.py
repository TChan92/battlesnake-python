# Used around getDirectionsCanGo() function
SAFE_KILL = 1  # ToDo (cut off the other snake)
FOOD = 2  # complete
OPEN = 3  # complete
NEXT_TO_WALL = 4  # ToDo (use current position in relation to map size)
DANGER = 5  # complete (have to move head-to-head with another snake)
CERTAIN_DEATH = 6  # surrounded by walls (never pick)

# tauntList = ['with', 'Jeff', 'prepare', 'for', 'death!', 'Wrestle']

RIGHT = 'right'
LEFT = 'left'
UP = 'up'
DOWN = 'down'


def containsDirection(direction, directions):
    result = False

    for dir in directions:
        if dir == direction:
            result = True
            continue

    return result


def detectWallRidingKill(mapObj, snakeObj, dirsThatHaveMax, directionHeuristics):
    headOfOurSnake = snakeObj.headOfOurSnake

    headX = headOfOurSnake['x']
    headY = headOfOurSnake['y']

    # detect whether our snake is one row/column away from the wall and riding along
    # wall scenarios:
    # 1. top wall
    # 2. right wall
    # 3. bottom wall
    # 4. left wall
    nearTopWall = headY == 1
    nearBottomWall = headY == mapObj.board_height - 2
    nearRightWall = headX == mapObj.board_width - 2
    nearLeftWall = headX == 1

    nearTopOrBottomWall = nearTopWall or nearBottomWall
    nearRightOrLeftWall = nearRightWall or nearLeftWall

    if (nearTopOrBottomWall or nearRightOrLeftWall):

        # check whether it is riding parallel to the wall
        rightTopWallRiding = nearTopWall and containsDirection(RIGHT, dirsThatHaveMax)
        leftTopWallRiding = nearTopWall and containsDirection(LEFT, dirsThatHaveMax)

        downRightWallRiding = nearRightWall and containsDirection(DOWN, dirsThatHaveMax)
        upRightWallRiding = nearRightWall and containsDirection(UP, dirsThatHaveMax)

        leftBottomWallRiding = nearBottomWall and containsDirection(LEFT, dirsThatHaveMax)
        rightBottomWallRiding = nearBottomWall and containsDirection(RIGHT, dirsThatHaveMax)

        upLeftWallRiding = nearLeftWall and containsDirection(UP, dirsThatHaveMax)
        downLeftWallRiding = nearLeftWall and containsDirection(DOWN, dirsThatHaveMax)

        isTopWallRiding = rightTopWallRiding or leftTopWallRiding
        isRightWallRiding = downRightWallRiding or upRightWallRiding
        isBottomWallRiding = leftBottomWallRiding or rightBottomWallRiding
        isLeftWallRiding = upLeftWallRiding or downLeftWallRiding

        isWallRiding = isTopWallRiding or isRightWallRiding or isBottomWallRiding or isLeftWallRiding

        if isWallRiding:
            topWallY = headY - 1
            rightWallX = headX + 1
            bottomWallY = headY + 1
            leftWallX = headX - 1

            for otherSnake in snakeObj.otherSnakes:
                otherSnakeHead = otherSnake['body']['data'][0]
                otherSnakeHeadX = otherSnakeHead['x']
                otherSnakeHeadY = otherSnakeHead['y']

                otherSnakeInitialLength = len(otherSnake['body']['data']) == 1
                otherSnakeRightRiding = otherSnakeInitialLength
                otherSnakeLeftRiding = otherSnakeInitialLength
                otherSnakeUpRiding = otherSnakeInitialLength
                otherSnakeDownRiding = otherSnakeInitialLength

                if len(otherSnake['body']['data']) > 1:
                    otherSnakeNeck = otherSnake['body']['data'][1]
                    otherSnakeNeckX = otherSnakeNeck['x']
                    otherSnakeNeckY = otherSnakeNeck['y']

                    otherSnakeRightRiding = otherSnakeNeckX == otherSnakeHeadX - 1
                    otherSnakeLeftRiding = otherSnakeNeckX == otherSnakeHeadX + 1
                    otherSnakeUpRiding = otherSnakeNeckY == otherSnakeHeadY + 1
                    otherSnakeDownRiding = otherSnakeNeckY == otherSnakeHeadY - 1

                potentialSafeKillMove = ''

                if rightTopWallRiding and otherSnakeRightRiding and (
                        otherSnakeHeadX <= headX and otherSnakeHeadY == topWallY):
                    potentialSafeKillMove = RIGHT
                elif leftTopWallRiding and otherSnakeLeftRiding and (
                        otherSnakeHeadX >= headX and otherSnakeHeadY == topWallY):
                    potentialSafeKillMove = LEFT
                elif downRightWallRiding and otherSnakeDownRiding and (
                        otherSnakeHeadX == rightWallX and otherSnakeHeadY <= headY):
                    potentialSafeKillMove = DOWN
                elif upRightWallRiding and otherSnakeUpRiding and (
                        otherSnakeHeadX == rightWallX and otherSnakeHeadY >= headY):
                    potentialSafeKillMove = UP
                elif leftBottomWallRiding and otherSnakeLeftRiding and (
                        otherSnakeHeadX >= headX and otherSnakeHeadY == bottomWallY):
                    potentialSafeKillMove = LEFT
                elif rightBottomWallRiding and otherSnakeRightRiding and (
                        otherSnakeHeadX <= headX and otherSnakeHeadY == bottomWallY):
                    potentialSafeKillMove = RIGHT
                elif upLeftWallRiding and otherSnakeUpRiding and (
                        otherSnakeHeadX == leftWallX and otherSnakeHeadY >= headY):
                    potentialSafeKillMove = UP
                elif downLeftWallRiding and otherSnakeDownRiding and (
                        otherSnakeHeadX == leftWallX and otherSnakeHeadY <= headY):
                    potentialSafeKillMove = DOWN

                # if potential cut off move is defined set the heuristic value
                if potentialSafeKillMove != '':
                    setHeuristicValue(directionHeuristics, potentialSafeKillMove, SAFE_KILL)
                    continue


def determineMovePriority(directionsCanGo,
                          turnDictionary,
                          mapObj,
                          directionHeuristics,
                          snakeObj):
    headOfOurSnake = snakeObj.headOfOurSnake
    headOfOurSnake = (snakeObj.headOfOurSnake['x'],snakeObj.headOfOurSnake['y'])
    ourSnake = snakeObj.ourSnake
    currMove = "up"
    # Set heuristic values if they need to be found
    # sets collisions to == CERTAIN_DEATH
    if len(directionsCanGo) >= 2:
        maxSpaces = 0
        maxSpacesDir = 'up'
        dirsAndValues = {}
        # find direction that gives largest/most open area
        for dir in directionsCanGo:
            availableSpotNodes = turnDictionary.copy()
            rootNode = directionalCoordinate(dir, headOfOurSnake)
            temp = bfs(rootNode, availableSpotNodes)
            dirsAndValues[dir] = temp
            if (temp > maxSpaces):
                maxSpaces = temp
                maxSpacesDir = dir
        dirsThatHaveMax = []
        for dir in dirsAndValues:
            if dirsAndValues[dir] == maxSpaces:
                dirsThatHaveMax.append(dir)
        # multiple directions have the best heuristic value
        if len(dirsThatHaveMax) == 1:
            currMove = maxSpacesDir
        # check for nearest food since we have established there is open space
        else:
            # Here we have multiple choices which offer the same amount 
            # of spaces
            if ourSnake['health'] < 50 or ourSnake['length'] < (1.5 * mapObj.board_width):
                print("Getting food")
                # First look at the direction that offers the closest food
                foodDir = getClosestFood(dirsThatHaveMax,
                                         headOfOurSnake,
                                         mapObj.food,
                                         turnDictionary.copy(),
                                         generateDictionaryTuple(mapObj)
                                         )
            else:
                foodDir = None
            if foodDir == None:
                # TODO need to change to space filling algorithm
                buttFirstDir = ButtFirstSearch(dirsThatHaveMax,
                                               headOfOurSnake,
                                               ourSnake['body']['data'][-1],
                                               turnDictionary.copy(),
                                               generateDictionaryTuple(mapObj)
                                               )

                # WE NEED TO CHANGE THIS......
                wallHumpDir = None
                if buttFirstDir == None:
                    # currMove = dirsThatHaveMax[random.randint(0, len(dirsThatHaveMax) - 1)]
                    wallHumpDir = wallHump(dirsThatHaveMax, headOfOurSnake,
                                           turnDictionary.copy())
                    # if directionHeuristics[wallHumpDir] != DANGER:
                    setHeuristicValue(directionHeuristics, wallHumpDir, FOOD)
                else:
                    # if directionHeuristics[wallHumpDir] != DANGER:
                    setHeuristicValue(directionHeuristics, buttFirstDir, OPEN)
            # We are able to get to food. Change heuristic from OPEN to FOOD
            elif ourSnake['health'] < 50 or ourSnake['length'] < (1.5 * mapObj.board_width):
                print("Getting food")
                # if directionHeuristics[foodDir] != DANGER:
                setHeuristicValue(directionHeuristics, foodDir, FOOD)
            # Remove any that are dangerous
            detectWallRidingKill(mapObj, snakeObj, dirsThatHaveMax, directionHeuristics)
            populateMissingHeuristics(directionHeuristics, headOfOurSnake,
                                      turnDictionary)
            currMove = getMinimalHeuristicValue(directionHeuristics)
    elif len(directionsCanGo) == 1:
        currMove = directionsCanGo[0]
    else:
        currMove = 'up'
    return currMove


def removeItemFromDictionary(key, dictionary):
    if not dictionary.get(key, None) is None:
        del dictionary[key]


# gives number for co-ord, ex (0, 0) top L
def directionalCoordinate(direction, withRespectTo):
    # x = withRespectTo['x']
    x = withRespectTo[0]
    # y = withRespectTo['y']
    y = withRespectTo[1]
    if (direction == 'up'):
        return (x, y - 1)
    elif (direction == 'down'):
        return (x, y + 1)
    elif (direction == 'right'):
        return (x + 1, y)
    elif (direction == 'left'):
        return (x - 1, y)


def removeSnakeCollisions(snakeObj, turnDictionary, heuristics):
    ourSnake = snakeObj.ourSnake
    otherSnakes = snakeObj.otherSnakes
    # Our snakes head
    head = ourSnake['body']['data'][0]
    # ----- Other Snakes (Where head is going to go)/ Head collision detection ----
    for snake in otherSnakes:
        # Check if we're longer, if so continue
        if len(snake['body']['data']) < len(ourSnake['body']['data']):
            continue

        # Else, we have to check if we'd run into them and avoid those 
        # directions
        dirsCouldCollideIn(snakeObj, snake, heuristics, turnDictionary)


def dirsCouldCollideIn(ourSnakeObj,
                       otherSnakeObj,
                       dirHeuristic,
                       turnDictionary):
    dirsOurSnakeCanGo = getDirectionsCanGo(ourSnakeObj.headOfOurSnake, turnDictionary)
    dirsOtherSnakeCanGo = getDirectionsCanGo(otherSnakeObj['body']['data'][0], turnDictionary)
    numberOfMovesTheyHave = len(dirsOtherSnakeCanGo)

    for ourDir in dirsOurSnakeCanGo:
        ourCoord = directionalCoordinate(ourDir, ourSnakeObj.headOfOurSnake)
        for theirDirs in dirsOtherSnakeCanGo:
            theirCoord = directionalCoordinate(theirDirs, otherSnakeObj['body']['data'][0])
            if ourCoord == theirCoord:
                if numberOfMovesTheyHave > 1:
                    setHeuristicValue(dirHeuristic, ourDir, DANGER)
                elif numberOfMovesTheyHave == 1:
                    setHeuristicValue(dirHeuristic, ourDir, CERTAIN_DEATH,
                                      turnDictionary, ourCoord)


def getDirectionsCanGo(snakeHead, turnDictionary):
    head = snakeHead
    canGo = []
    # x = head['x']
    print(head)
    x = head[0]
    y = head[1]
    # y = head['y']
    right = (x + 1, y)
    left = (x - 1, y)
    up = (x, y - 1)
    down = (x, y + 1)
    if right in turnDictionary.keys():
        canGo.append('right')
    if left in turnDictionary.keys():
        canGo.append('left')
    if up in turnDictionary.keys():
        canGo.append('up')
    if down in turnDictionary.keys():
        canGo.append('down')
    return canGo


def getUnvisitedNeighbor(node, otherNodes):
    # print(node)
    # print(otherNodes)
    # x = node['x']
    # y = node['y']
    x = node[0]
    y = node[1]
    right = (x + 1, y)
    left = (x - 1, y)
    up = (x, y - 1)
    down = (x, y + 1)
    # right = {'x': x + 1, 'y': y}
    # left = {'x': x - 1, 'y':y}
    # up = {'x': x, 'y': y - 1}
    # down = {'x': x, 'y': y + 1}
    if right in otherNodes.keys() and otherNodes[right] == False:
        return right
    elif left in otherNodes.keys() and otherNodes[left] == False:
        return left
    elif up in otherNodes.keys() and otherNodes[up] == False:
        return up
    elif down in otherNodes.keys() and otherNodes[down] == False:
        return down
    else:
        return None


def bfs(rootNode, otherNodes):
    queue = []
    queue.append(rootNode)
    otherNodes[rootNode] = True
    room = 0
    while len(queue) > 0:
        node = queue.pop(0)
        child = getUnvisitedNeighbor(node, otherNodes)
        while not child == None:
            otherNodes[child] = True
            queue.append(child)
            child = getUnvisitedNeighbor(node, otherNodes)
            room = room + 1

    return room


def determineDirection(node, head):
    if list(head)[1] - list(node)[1] == 1:
        return "up"
    if list(head)[1] - list(node)[1] == -1:
        return "down"
    if list(head)[0] - list(node)[0] == 1:
        return "left"
    if list(head)[0] - list(node)[0] == -1:
        return "right"
    # if head['y'] - node['y'] == 1:
    #     return "up"
    # if head['y'] - node['y'] == -1:
    #     return "down"
    # if head['x'] - node['x'] == 1:
    #     return "left"
    # if head['x'] - node['x'] == -1:
    #     return "right"


def getClosestFood(dirsFromHead, head, foods, otherNodes, parentDictionary):
    queue = []
    queue.append(head)
    # queue.append((head['x'], head['y']))
    otherNodes[tuple(head)] = True
    print(foods['data'])
    food_dict = foods['data']
    foods = []
    for food in food_dict:
        foods.append((food['x'], food['y']))
    while len(queue) > 0:
        node = queue.pop(0)
        if node in foods:
            while not (parentDictionary[node] == head):
                node = parentDictionary[node]
            if determineDirection(node, head) in dirsFromHead:
                return determineDirection(node, head)
        childNode = getUnvisitedNeighbor(node, otherNodes)
        while not childNode == None:
            parentDictionary[childNode] = node
            otherNodes[childNode] = True
            queue.append(childNode)
            childNode = getUnvisitedNeighbor(node, otherNodes)


# our snake chases its own Tail
def ButtFirstSearch(dirsFromHead, head, tail, otherNodes, parentDictionary):
    queue = []
    queue.append(head)
    # queue.append((head['x'], head['y']))
    otherNodes[tuple(head)] = True
    while len(queue) > 0:
        node = queue.pop(0)
        if list(node) == tail:
            while not (parentDictionary[node] == head):
                node = parentDictionary[node]
            if determineDirection(node, head) in dirsFromHead:
                return determineDirection(node, head)
        childNode = getUnvisitedNeighbor(node, otherNodes)
        while not childNode == None:
            parentDictionary[childNode] = node
            otherNodes[childNode] = True
            queue.append(childNode)
            childNode = getUnvisitedNeighbor(node, otherNodes)


def getSpacesAround(dir, start, otherNodes):
    count = 0
    while (getUnvisitedNeighbor(
            directionalCoordinate(dir, start), otherNodes) is not None):
        count += 1
    return count


# This can probably be cleaned up and written better, 
# but the basic idea is to get spaces with 2 edges first otherwise 1
def wallHump(dirsFromHead, head, otherNodes):
    dirMap = {}
    for dir in dirsFromHead:
        dirMap[dir] = len(
            getDirectionsCanGo(directionalCoordinate(dir, head), otherNodes))  # getSpacesAround(dir, start, otherNodes)
    for dir in dirMap:
        if dirMap[dir] == 1:  # 2:
            return dir
    for dir in dirMap:
        if dirMap[dir] == 2:  # 1:
            return dir
    for dir in dirMap:
        if dirMap[dir] == 3:  # 3:
            return dir


def populateMissingHeuristics(directionHeuristics, snakeHead, dictionary):
    dirs = getDirectionsCanGo(snakeHead, dictionary)
    for dire in dirs:
        if not dire in directionHeuristics.keys():
            setHeuristicValue(directionHeuristics, dire, OPEN)

    return


def generateDictionaryTuple(mapObj):
    tempDictionary = {}
    for y in xrange(mapObj.board_height):
        for x in xrange(mapObj.board_width):
            tempDictionary[(x, y)] = ()
    return tempDictionary


def generateDictionaryTF(mapObj, originalDictionary):
    for y in xrange(mapObj.board_height):
        for x in xrange(mapObj.board_width):
            originalDictionary[(x, y)] = False


# For setting the heuristic entries, we only assign higher values
def setHeuristicValue(heuristic, key, value, turnDict=None, coord=None):
    if value == CERTAIN_DEATH:
        # print "Removing CERTAIN_DEATH spots from the turnDict and heuristic"
        removeItemFromDictionary(coord, turnDict)
        # del heuristic[key]
    if heuristic.get(key, None) is None:
        heuristic[key] = value
    elif heuristic[key] < value:
        heuristic[key] = value


def strictlySetHeuristicValue(heuristic, key, value, turnDict=None, coord=None):
    heuristic[key] = value
    return


def getMinimalHeuristicValue(heuristic):
    minVal = CERTAIN_DEATH
    minDir = ''
    for direc in heuristic:
        if heuristic[direc] < minVal:
            minVal = heuristic[direc]
            minDir = direc
    print "heuristics"
    print heuristic
    print "min dir"
    print minDir
    return minDir


# def tauntGenerator(mapObj):
#     # currentTaunt = tauntList.pop(0)
#     # tauntList.append(currentTaunt)
#     return tauntList[mapObj.turn % 6]
