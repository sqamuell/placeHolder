# Code by: Samuel Losi
# last updated: 04/27/2020

####### Geometry Construction #######

import cv2
import math
import copy
import pickPoints as pp

# 112 website
def almostEqual(d1, d2, epsilon=10**-7):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

def pairImgPxls(width,moveVals,distoPlane=5):
    uPairs = []
    disToView = moveVals[1]
    for i in range(0,width//2):
        pair = pairUValues(width,i,distoPlane,disToView)
        uPairs.append(pair)
    for i in range(width//2,width):
        pair = pairUValues(width,i,distoPlane,disToView)
        pair[0] += width//2
        pair = pair[::-1]
        uPairs.append(pair)
    return uPairs

def getIntersections(img1UV,img2UV,uPairs,moveVals):
    cen1 = (0,0,0)
    cen2 = movePoint(moveVals,cen1,1)
    centers = [cen1,cen2]
    intersections = []
    for pair in uPairs:
        uValIntersects = findPixelIntersections(pair,img1UV,img2UV,centers,moveVals)
        intersections.extend(uValIntersects)
    return intersections

# pre-interface method of selecting similar points on the image
'''
def calibrateImgs(drawnImgs,imgs):
    callibrated = False
    while not callibrated:
        callibrateImgs = copy.deepcopy(drawnImgs)
        simPts = []
        for i,img in enumerate(callibrateImgs):
            print(f'Please select ({pp.pointsChosen}) calibration points on img{i+1}!')
            pp.lmb = []
            pp.getPoints(img)
            if simPts == []:
                simPts.extend(pp.lmb)
            else:
                for i in range(len(pp.lmb)):
                    simPts[i].extend(pp.lmb[i])
        print('Awesome!')
        print()

        userPts = copy.deepcopy(simPts)

        print("callibrating...")
        print()

        otherPts = pp.getGenPts(imgs)
        simPts.extend(otherPts)

        img1Pts = []
        img2Pts = []
        for pt1,pt2 in simPts:
            img1Pts.append(pt1)
            img2Pts.append(pt2)

        sCoordsI1 = getPointsAndSlopes(img1Pts)
        sCoordsI2 = getPointsAndSlopes(img2Pts)

        extendedImg1 = []
        for point in sCoordsI1:
            newPoint = extendLineToX((0,0,0),point,5)
            extendedImg1.append(newPoint)
        
        extendedImg2 = []
        for point in sCoordsI2:
            newPoint = extendLineToX((0,0,0),point,5)
            extendedImg2.append(newPoint)

        callibrated,moveVals,intersects = triangulateLocation(extendedImg1, extendedImg2)
    return moveVals
'''

def calibrateImgs(img1Pts,img2Pts,imgs):
    otherPts = pp.getGenPts(imgs)
    img1Other = []
    img2Other = []
    for pt1,pt2 in otherPts:
        img1Other.append(pt1)
        img2Other.append(pt2)

    img1Pts.extend(img1Other)
    img2Pts.extend(img2Other)

    sCoordsI1 = getPointsAndSlopes(img1Pts)
    sCoordsI2 = getPointsAndSlopes(img2Pts)

    extendedImg1 = []
    for point in sCoordsI1:
        newPoint = extendLineToX((0,0,0),point,5)
        extendedImg1.append(newPoint)
    
    extendedImg2 = []
    for point in sCoordsI2:
        newPoint = extendLineToX((0,0,0),point,5)
        extendedImg2.append(newPoint)

    callibrated,moveVals,intersects = triangulateLocation(extendedImg1, extendedImg2)
    return moveVals,callibrated

def dif3D(pt1,pt2):
    x1,y1,z1 = pt1
    x2,y2,z2 = pt2
    return ((x2-x1), (y2-y1), (z2-z1))

def dist3d(point1,point2):
    x1,y1,z1 = point1
    x2,y2,z2 = point2
    x = (x2-x1)
    y = (y2-y1)
    z = (z2-z1)
    xyDist = (x**2 + y**2)**0.5
    return (xyDist**2 + z**2)**0.5

def movePoint(moveVals, point, direc):
    xT,yT,zT = moveVals
    x,y,z = point
    x += xT * direc
    y += yT * direc
    z += zT * direc
    return (x,y,z)


def genTestCoords():
    Lu = [(800-200*i) for i in range(5)]
    Lv = [(400-200*i) for i in range(3)]
    L = []
    for u in Lu:
        for v in Lv:
            L.append((u,v))
    return L

def getPointsAndSlopes(points):
    sphereCoords = remapCoords(points)
    # slopes = calcRadialSlopes(sphereCoords)
    return sphereCoords

def remapCoords(UVCoords, UVHeight = 400, UVWidth = 800, radius = 5):
    newCoords = []
    for u,v in UVCoords:
        # account for unintuative flipped pixels
        # v = UVHeight - v
        zOffset = (v / UVHeight) - 0.5
        circZ = (zOffset * math.pi) # changed to pi
        z = radius * math.sin(circZ)
        if almostEqual(z,0): z = 0
        distXY = radius * math.cos(circZ)
        xyOffset = (u / UVWidth) * (2 * math.pi) + (math.pi/2) # changed to pi/2
        x = distXY * math.cos(xyOffset)
        if almostEqual(x,0): x = 0
        y = distXY * math.sin(xyOffset)
        if almostEqual(y,0): y = 0
        newCoords.append((x,y,z))
    return newCoords

# coords = [[600,300],[200,300]]
# print(coords)
# print(remapCoords(coords,400,800))

'''
def calcRadialSlopes(coords, step = 0.5, center = (0,0,0)):
    slopes = []
    for point in coords:
        x,y,z = point
        xS = x * step
        yS = y * step
        zS = z * step
        slopes.append((xS,yS,zS))
    return slopes
'''

def getProjectedPts(slopeLst,numPts=400):
    projPts = []
    for xS,yS,zS in slopeLst:
        ptLst = []
        i = 20
        while len(ptLst) < numPts:
            point = ((xS*i),(yS*i),(zS*i))
            ptLst.append(point)
            i += 1
        projPts.append(ptLst)
    return projPts

def inLine(point,slope,tolerance):
    x,y,z = point
    xS,yS,zS = slope
    i = 0
    lastDist,curDist = abs(x),0
    while True:
        xN,yN,zN = (x - (xS*i)), (y - (yS*i)), (z - (zS*i))
        if abs(yN) < tolerance and abs(zN) < tolerance:
            return True,(xN,yN,zN)
        elif i == 400:
            return False, None
        else:
            i +=1

'''
def avg(L):
    return sum(L)/len(L)
'''

'''
def getAvgPt(newPts):
    xL = []
    yL = []
    zL = []
    for x,y,z in newPts:
        xL.append(x)
        yL.append(y)
        zL.append(z)
    return (avg(xL),avg(yL),avg(zL))
'''

'''
def triangulate(projectedPoints,slopeSL,tolerance = 1):
    intersections = []
    for i,curSlope in enumerate(slopeSL):
        newPts = []
        for j, curPoint in enumerate(projectedPoints[i]):
            cross, loc = inLine(curPoint,curSlope,tolerance)
            if cross == True:
                intersections.append(loc)
                break
    return intersections
'''

# went through a series of iterations for this function
def triangulateLocation(sCImg1,sCImg2,center = (0,0,0)):
    percentInLine = 0.6
    cenImg1 = (0,0,0)
    callibrated = False
    total = len(sCImg1)
    for i in range(len(sCImg1)):
        intersects = []
        passed = 0
        newCoordsImg2 = []
        curMoveVals = dif3D(sCImg1[i],sCImg2[i])
        cenImg2 = movePoint(curMoveVals,cenImg1,1)
        for j in range(len(sCImg1)):
            coord = movePoint(curMoveVals,sCImg2[j],1)
            newCoordsImg2.append(coord)
        for h in range(len(sCImg1)):
            line1 = sCImg1[h],center
            line2 = newCoordsImg2[h],center
            good = find3dIntersection(line1,line2,0.1)
            if good != None:
                passed += 1
                intersects.append(good)
        if passed/total > percentInLine:
            callibrated = True
            return callibrated,curMoveVals,intersects
    return None,None,None

def findCenterPoints(vecs,distToPlane, step = 0.05):
    center1 = (0,0,0)
    x = 0
    while x < distToPlane * 10:
        x += step
        center2 = (x,0,0)

#  from https://www.reddit.com/r/gamedev/comments/463ypv/can_someone_donate_a_2d_line_intersection/
def find2dIntersection(line1,line2):
    x1,y1 = line1[0]
    x2,y2 = line1[1]
    x3,y3 = line2[0]
    x4,y4 = line2[1]
    det12 = x1*y2 - y1*x2
    det34 = x3*y4 - y3*x4
    den = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
    x = (det12*(x3 - x4) - (x1 - x2)*det34) / den
    y = (det12*(y3 - x4) - (y1 - y2)*det34) / den
    return x,y
#  end copied code

def extendLineToX(center,vector,newX):
    x,y,z = center
    xS,yS,zS = vector
    # x = xS*val
    # y = yS*val
    # z = zS*val
    if xS < 0:
        newX *= -1
    val = newX / xS
    y = yS*val
    z = zS*val
    return (newX,y,z)

# made with what I learned from https://www.youtube.com/watch?v=N-qUfr-rz_Y
# code is mine
def find3dIntersection(line1,line2,prox = 1):
    point1 = line1[0]
    point2 = line2[0]

    x1,y1,z1 = point1
    x2,y2,z2 = line1[1]
    x3,y3,z3 = point2
    x4,y4,z4 = line2[1]

    vec1 = (x2-x1,y2-y1,z2-z1)
    vec2 = (x4-x3,y4-y3,z4-z3)

    '''
    vec1[0]*x - vec2[0]*y == point2[0] - point1[0]
    vec1[1]*x - vec2[1]*y == point2[1] - point1[1]
    vec1[2]*x - vec2[2]*y == point2[2] - point1[2]
    '''
    if vec1[0] == 0 or vec1[1] == 0:
        return None

    fac = vec1[0]/vec1[1]

    if vec2[0] - fac*(vec2[1]) == 0:
        return None

    y = ((-1*(vec1[0] - ((fac*vec1[1]))) + -1*((point2[0] - point1[0])
                                               - fac*(point2[1] - point1[1]))) /
                                    (vec2[0] - fac*(vec2[1])))

    x = (point2[1] - point1[1] + vec2[1]*y)/vec1[1]

    if almostEqual(vec1[2]*x - vec2[2]*y, point2[2] - point1[2],prox):
        xpt = point1[0] + (x*vec1[0])
        ypt = point1[1] + (x*vec1[1])
        zpt = point1[2] + (x*vec1[2])
        return (xpt,ypt,zpt)
    else:
        return None

# this bit was hard
'''
def findPixelIntersections(intervals,intDif,ePt1,ePt2,centers,moveVals):
    intersections = []
    used = set()

    # nearest location is at [200,x] and [600,x]; pattern 0,200,400,600,800
    # this means increasing step until then, and dexcresing after
    # angle of view taken - empirical understanding needed
    # we need to break down 0-400 into steps; this can then be mirrored repeativly
    # then the reference points loc inform the step offset
    # a= 10, b=16: offset = 6
    # lets try step = 2^^x

    # think of as a "scan"
    # step changes across image: small - large - small - small - large - small

    for i in range(len(intervals)):
        if i-intDif not in range(len(intervals)):
            continue
        start1 = intervals[i][0]
        end1 = intervals[i][1]
        start2 = intervals[i-intDif][0]
        end2 = intervals[i-intDif][1]
        for point in ePt1:
            if point[0] in range(start1,end1):
                pointSphere,pointSlope = getPointsAndSlopes([point])
                for other in ePt2:
                    if other not in used and other[0] in range(start2,end2) and other[1] <300:
                        otherSphere,otherSlope = getPointsAndSlopes([other])
                        otherPoint = movePoint(moveVals,otherSphere[0],1)
                        # good luck! ^_^
                        line1 = (pointSphere[0],centers[0])
                        line2 = (otherPoint,centers[1])
                        intersect = find3dIntersection(line1,line2,0.001)
                        if intersect != None:
                            used.add(other)
                            intersections.append(intersect)
                            break
    return intersections

def findIntersectionsTest(dif,ePt1,ePt2,centers,moveVals):
    intersections = []
    used = set()
    # range = 0 to 400
    # 
    for i in range(100,300):
        for point in ePt1:
            if point[0] == i:
                for other in ePt2:
                    if other[0] == i - dif:
                        pointSphere,pointSlope = getPointsAndSlopes([point])
                        otherSphere,otherSlope = getPointsAndSlopes([other])
                        otherPoint = movePoint(moveVals,otherSphere[0],1)
                        # good luck! ^_^
                        line1 = (pointSphere[0],centers[0])
                        line2 = (otherPoint,centers[1])
                        intersect = find3dIntersection(line1,line2,0.001)
                        if intersect != None:
                            print(point)
                            used.add(other)
                            intersections.append(intersect)
                            break
    return intersections
'''
# who knew it was that simple
def pairUValues(uDomain,uImg1,disToPln,disToView):
    theta1Deg = ((uImg1/uDomain) * 360) - 90
    theta1Rad = theta1Deg * (math.pi/180)
    h = disToPln * math.tan(theta1Rad)
    theta2Rad = math.atan((h + disToView) / disToPln)
    theta2Deg = theta2Rad / (math.pi/180) + 90
    uImg2 = int((theta2Deg / 360) * uDomain)
    return [uImg2,uImg1]

def genUValues():
    L = [0 + (10 *x) for x in range(41)]
    return L

def findPixelIntersections(pair,img1Pts,img2Pts,centers,moveVals,threshold = 1):
    used = set()
    intersections = []
    cen1 = centers[0]
    cen2 = centers[1]
    uVal1 = pair[0]
    uVal2 = pair[1]
    for pixel1 in img1Pts:
        if pixel1[0] == uVal1 and ((pixel1[0] < 350 and pixel1[0] > 50)
                    or (pixel1[0] < 750 and pixel1[0] > 450)) and pixel1[1] < 200:
            point1 = remapCoords([pixel1])
            for pixel2 in img2Pts:
                if int(pixel2[0]) == uVal2 and pixel2 not in used:
                    point2 = remapCoords([pixel2])
                    point2 = movePoint(moveVals,point2[0],1)
                    line1 = (point1[0],cen1)
                    line2 = (point2,cen2)
                    intersect = find3dIntersection(line1,line2,threshold)
                    if intersect != None:
                        used.add(pixel2)
                        # print(pixel1,pixel2)
                        intersections.append(intersect)
                        break
    return intersections

'''
uImg1Lst = genUValues()

uPairs = []
for uImg1 in uImg1Lst:
    pair = pairUValues(800,uImg1,5,3)
    uPairs.append(pair)
print(uPairs)
'''