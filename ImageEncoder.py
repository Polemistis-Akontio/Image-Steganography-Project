from Crypto.Cipher import AES
from sympy import randprime
import numpy as np
from numpy import binary_repr
import cv2 as cv
import math
import os
from hashlib import pbkdf2_hmac
import getpass
import struct

testFile = "testfile.txt"
testImage = "testImage.png"

def encrypt(file, encryptionKey):
    
    salt = os.urandom(16) #need a salt to ensure secure encryption against rainbow tables
    
    key32 = pbkdf2_hmac(   #AES requires a 32 bit key, so we use sha256 hash function
        hash_name="sha256",
        password=encryptionKey.encode(),
        salt=salt,
        iterations=100_000,
        dklen=32
        )
    
    with open(file, "rb") as f: #read the file byte by byte
        plaintext = f.read()
    
    cipher = AES.new(key32, AES.MODE_GCM) #make the cipher based on the 32 bit key
    ciphertext, tag = cipher.encrypt_and_digest(plaintext) #encrypt the plaintext, tag is for integrity assurance
    nonce = cipher.nonce
    
    header = struct.pack(">I", len(ciphertext))
    binary_blob = salt + nonce + tag + header + ciphertext #puts all the encryption information except the password into the beginning of cipher
    bit_string = ''.join(f"{byte:08b}" for byte in binary_blob) #converts the bytes to just 0 and 1s
    #print(bit_string)
    
    return bit_string

def encodeImage(testImage, binaryFile):
    
    img = cv.imread(testImage)
    assert img is not None, "Check to make sure you have a valid image path"
    
    rows, columns, channels = img.shape
    totalVals = rows * columns * channels
    
    stepKey = randprime(6, 1000)
    while math.gcd(stepKey, totalVals) != 1: #checks to make sure the key is coprime, to ensure each pixel will only be accessed once
        print(stepKey)
        stepKey = randprime(6, 1000)
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
            print("Missing key: ", i)

    steppedKeyList = list(steppedDict.keys())

    charIndex = 0
    for char in binaryFile:
        #print("Message char: ", char)
        r, c, ch = steppedDict[steppedKeyList[charIndex]]
        string = binary_repr(img[r, c, ch], 8)
        checkValue = string[7]
        #print("Image values: ", img[r, c])
        #print("Last digit of Pixel: ", string[7])
        if char == checkValue:
            #print("Char == checkValue")
            pass
        else:
            #print("Char != checkValue")
            #print("Old String: ", string)
            val = img[r, c, ch]
            if val == 255:
                img[r, c, ch] = val - 1
                #print("Value: ", val)
                #print("New String: ", binary_repr(img[r, c, ch], 8))
            else:
                img[r, c, ch] = val + 1
                #print("Value: ", val)
                #print("New String: ", binary_repr(img[r, c, ch], 8))
        charIndex += 1

    print("StepKey: ", stepKey)
    print("If the image doesn't appear, click the icon on the taskbar")
    cv.imwrite("newSavedImage.png", img, [cv.IMWRITE_PNG_COMPRESSION, 0])
    with open("savedInfo.txt", "w") as file:
        file.write(f"Encoding Key: {stepKey}\n")
        file.write("File saved as: newSavedImage.png")

    original = cv.imread("testImage.png")
    cv.imwrite("testImage.png", original, [cv.IMWRITE_PNG_COMPRESSION, 0]) #makes sure the original image and the altered image are roughly the same file size
    newImage = cv.imread("newSavedImage.png")
    combined = np.hstack((original, img, newImage))
    cv.imshow("side by side", combined)
    cv.waitKey(0)
    

password = getpass.getpass("Enter an Encryption Password(You must remember this to decrypt later): ")

binary = encrypt(testFile, password)
encodeImage(testImage, binary)