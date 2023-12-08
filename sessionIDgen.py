import random



def generateID(num):
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

    originNum = 0
    result = ''
    while(originNum < num):
        selectedNum = (random.randint(1, len(characters)))
        result += characters[selectedNum]
        originNum += 1
    return result

