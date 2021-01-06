# Code by: Samuel Losi
# last updated: 04/22/2020

####### Pick Points #######

import cv2
import numpy as np
import edgeDetection as ed

lmb = []
pointsChosen = 5

def drawEdgesOnImgs(formatImgLst,edgePts):
    drawnImgs = []
    for w,img in enumerate(formatImgLst):
        for j,i in edgePts[w]:
            img[i][j][0] = np.uint8(255)
            img[i][j][1] = np.uint8(0)
            img[i][j][2] = np.uint8(0)
        drawnImgs.append(img)
    return drawnImgs

# pre-interface point selection
# inspired by https://www.pyimagesearch.com/2015/03/09/capturing-mouse-click-events-with-python-and-opencv/ 
def mouse_callback(event, x, y, flags, params):
    if event == 1:
        global lmb
        if len(lmb) < pointsChosen:
            lmb.append([(x, y)])
            cv2.destroyAllWindows()

def getPoints(disImg):
    while True:
        for i in range(len(lmb)):
            color = (0, 0, 255)
            cv2.circle(disImg,lmb[i][0],10,color,2)
        cv2.namedWindow('Pick Points!', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('Pick Points!',mouse_callback)
        cv2.imshow('Pick Points!',disImg)
        key = cv2.waitKey(0)
        if key == 27 and len(lmb) == pointsChosen:
            cv2.destroyAllWindows()
            break
        cv2.destroyAllWindows()

def getGenPts(imgLst):
    return getLikePoints(imgLst)

# inspired by https://docs.opencv.org/3.4/d7/d66/tutorial_feature_detection.html
# these are the computer generated similar points
def getLikePoints(imgList):
    img1 = ed.getGrey(imgList[0])
    img2 = ed.getGrey(imgList[1])

    orb = cv2.ORB_create()

    kp1, des1 = orb.detectAndCompute(img1,None)
    kp2, des2 = orb.detectAndCompute(img2,None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    matches = bf.match(des1,des2)

    good = []
    goodPoints = []
    for val,match in enumerate(matches):
        i = match.queryIdx
        j = match.trainIdx
        if not (kp1[i].pt[0] < 200 or kp2[j].pt[0] < 200 or \
                    kp1[i].pt[0] > 600 or kp2[j].pt[0] > 600):
            good.append(match)
            goodPoints.append([kp1[i].pt,kp2[j].pt])
    return goodPoints[:10]