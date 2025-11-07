from Crypto.Cipher import AES
from sympy import randprime
import numpy as np
from numpy import binary_repr
import cv2 as cv
import time
import math

testFile = "testfile.txt"
testImageWEBP = "testImage.webp"
#imageKey = randprime(6, 100)#must be prime number, otherwise when iterating through the pixels it'll loop and skip values
#imageKey = 37
testBinary = "01001000 01010100 01010100 01010000 01010011 00100000 01101011 01100101 01100101 01110000 01110011 00100000 01100100 01100001 01110100 01100001 00100000 01110011 01100101 01100011 01110101 01110010 01100101 00101110"


def encrypt():
    
    return
    
def parseImage():
    
    return

def encodeImage(testImage, binaryFile):
    
    img = cv.imread(testImage)
    assert img is not None, "Check to make sure you have a valid image path"
    
    rows, columns, channels = img.shape
    totalVals = rows * columns * channels
    
    stepKey = randprime(6, 100)
    while math.gcd(stepKey, totalVals) != 1: #checks to make sure the key is coprime, to ensure each pixel will only be accessed once
        print(stepKey)
        stepKey = randprime(6, 100)
        print(stepKey)
    
    valueDict = {}
    count = 0
    for px in range(0, rows): #puts each BGR value into a corresponding key, left to right, top to bottom
        for px2 in range(0, columns):
            for value in range(0, channels):
                valueDict[count] = [px, px2, value]
                count += 1
    
    steppedDict = {}
    
    keyList = list(valueDict.keys())
    
    visitedCount = 0
    index = 0
    
    while visitedCount < len(keyList): #creates the steppedDict, which uses the prime step 
        key = keyList[index % len(keyList)]
        if key not in steppedDict:
            steppedDict[key] = valueDict[key]
            index += stepKey
            visitedCount += 1
        else:
            print("value already found", key)
            break
    
    for i in range(totalVals):
        if i not in steppedDict: #double checks to make sure there aren't any keys missing from steppedDict
            print(i)


    for key in steppedDict:
        r, c, ch = steppedDict[key]
        print(binary_repr(img[r, c, ch], 8))     


    #print(valueDict)
    #cv.imshow('', img)
    #cv.waitKey(0)
    
    
encodeImage(testImageWEBP, testBinary)