# Code by: Samuel Losi
# last updated: 04/22/2020

####### Edge Detection #######

import cv2
import numpy as np

def displayImage(img):
    cv2.imshow('preview!', img)
    key = cv2.waitKey(0)
    cv2.destroyAllWindows()

# resizes img
def formatImage(image,height=400):
    img = cv2.imread(image)
    width = int((height/len(img)) * len(img[0]))
    dim = (width,height)
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    return cv2.resize(img,dim),width

def blurImg(img,knl,sigma):
    return cv2.GaussianBlur(img,(knl,knl),sigma)

def getGrey(img):
    return cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

# uses canny edge detection to recolor image for Hough Line method
def cannyEdges(img):
    gray = getGrey(img)
    return cv2.Canny(gray,50,150,apertureSize=3)

# pre-interface method for selecting kernal and sigma for edge detection
'''
def getEdgeImgs(formatImgLst):
    num = 1
    edgeImgs = []
    for img in formatImgLst:
        print(f'Applying gaussian filter to img{num}!')
        while True:
            print(f'Please input kernal size (must be odd)...',end='')
            kernalSize = int(input())
            print(f'Please input sigma value...',end='')
            sigma = int(input())
            blurredImg = blurImg(img,kernalSize,sigma)
            edges = cannyEdges(blurredImg)
            displayImage(edges)
            print(f'Do the edges with kernal size: {kernalSize}, and sigma: {sigma}, look good?')
            print('If so, type "y"...',end='')
            passed = input()
            if passed == 'y':
                edgeImgs.append(edges)
                num += 1
                print('Very nice!')
                print()
            else: 
                print("That's ok! Please try again")
                print()
                continue
            break
    return edgeImgs
'''
def getPts(edgeImgs):
    edgePts = []
    for img in edgeImgs:
        whitePixs = []
        for i in range(int(len(img)*0.75)):
            for j in range(len(img[0])):
                if img[i][j] != 0:
                    whitePixs.append((j,i))
        edgePts.append(whitePixs)
    return edgePts
    
# from https://www.cs.cmu.edu/~112/notes/notes-efficiency.html
def merge(edgePoints, start1, start2, end):
    index1 = start1
    index2 = start2
    length = end - start1
    aux = [None] * length
    for i in range(length):
        if ((index1 == start2) or
            ((index2 != end) and (edgePoints[index1][0] > edgePoints[index2][0]))):
            aux[i] = edgePoints[index2]
            index2 += 1
        else:
            aux[i] = edgePoints[index1]
            index1 += 1
    for i in range(start1, end):
        edgePoints[i] = aux[i - start1]

def mergeSortViaWidth(edgePoints):
    n = len(edgePoints)
    step = 1
    while (step < n):
        for start1 in range(0, n, 2*step):
            start2 = min(start1 + step, n)
            end = min(start1 + 2*step, n)
            merge(edgePoints, start1, start2, end)
        step *= 2
    return edgePoints