# Code by: Samuel Losi
# last updated: 04/28/2020

####### Run Functions & Interface #######


# project takes two 360-degree images, 
# has user define the edges,
# triangulates their position in 3d space,
# constructs 3d geometry from them,
# then displays it in a 3d space

# obviously cmu_112_graphics is from https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
from cmu_112_graphics import *
from tkinter import filedialog
import PIL.Image, PIL.ImageTk
import cv2
import copy
import edgeDetection as ed
import constructGeometry as cg
import pickPoints as pp
import drawGeometry as dg


# I'm sorry for this really ugly code for the interface
# I was pressed for time and it works :)
# inspired by https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
# but i wrote it...clearly
def appStarted(app):
    app.screen = 0
    app.nextScreen = False
    # next button location
    app.nB1 = (1500,550)
    app.nB2 = (app.nB1[0]+50,app.nB1[1]+25)
    # file selection parameters
    app.img1Sel = (700,200)
    app.img2Sel = (700,250)
    app.selBW = 100
    app.selBH = 25
    app.file1 = ''
    app.file2 = ''
    app.img1Push = False
    app.img2Push = False
    app.notReadable = False
    app.imgs = []
    # edge refinement parameters
    app.edgeSelec = (375,100)
    app.sO = 50
    app.drag1 = False
    app.drag2 = False
    app.slider1 = 0
    app.slider2 = 0
    app.sliderStart = app.edgeSelec[0]+847
    app.sliderTop = app.edgeSelec[1]+app.sO
    app.sliderBottom = (app.sliderTop+400)-(2*app.sO)
    app.sliderCen1 = app.sliderBottom
    app.sliderCen2 = app.sliderBottom
    app.slider1Val = 1 #
    app.slider2Val = 0
    app.image = None
    app.edgeImgs = []
    # point selection parameters
    app.img1 = (25,100)
    app.img2 = (875,100)
    app.imgDis1 = None
    app.imgDis2 = None
    app.screen1Loc = []
    app.screen2Loc = []
    app.img1Loc = []
    app.img2Loc = []



def mousePressed(app,event):
    # on next screen press
    if app.screen < 6 and event.x in range(app.nB1[0],app.nB2[0]) and \
                          event.y in range(app.nB1[1],app.nB2[1]) and \
                          (app.screen != 4 or (len(app.img1Loc) == 5 and \
                                                    len(app.img2Loc) == 5)):
        app.nextScreen = True

    # on screen 4
    if app.screen == 4:
        if len(app.screen1Loc) < 5 and event.x in range(app.img1[0],app.img1[0]+800) \
                        and event.y in range(app.img1[1],app.img1[1]+400):
            app.screen1Loc.append((event.x,event.y))
            app.img1Loc.append([event.x-app.img1[0],event.y-app.img1[1]])
        if len(app.screen2Loc) < 5 and event.x in range(app.img2[0],app.img2[0]+800) \
                        and event.y in range(app.img2[1],app.img2[1]+400):
            app.screen2Loc.append((event.x,event.y))
            app.img2Loc.append([event.x-app.img2[0],event.y-app.img2[1]])

    if (app.screen == 2 or app.screen == 3) \
            and event.x in range(app.sliderStart-15,app.sliderStart+6+15) \
            and event.y in range(app.sliderCen1-5,app.sliderCen1+5):
        app.drag1 = True

    if (app.screen == 2 or app.screen == 3) \
            and event.x in range(app.sliderStart+app.sO-15,app.sliderStart+app.sO+6+15) \
            and event.y in range(app.sliderCen2-5,app.sliderCen2+5):
        app.drag2 = True

    if app.screen == 1 and event.x in range(app.img1Sel[0],app.img1Sel[0]+app.selBW) \
                                    and event.y in range(app.img1Sel[1],app.img1Sel[1]+app.selBH):
        app.img1Push = True
    if app.screen == 1 and event.x in range(app.img2Sel[0],app.img2Sel[0]+app.selBW) \
                                    and event.y in range(app.img2Sel[1],app.img2Sel[1]+app.selBH):
        app.img2Push = True




def mouseDragged(app, event):
    if app.drag1 and event.y > app.sliderTop and event.y < app.sliderBottom:
        app.sliderCen1 = event.y
        app.slider1Val = abs(event.y-app.sliderBottom)/(app.sliderBottom-app.sliderTop)
        app.slider1Val = int(app.slider1Val*17)
        if app.slider1Val % 2 == 0:
            app.slider1Val += 1

    if app.drag2 and event.y > app.sliderTop and event.y < app.sliderBottom:
        app.sliderCen2 = event.y
        app.slider2Val = abs(event.y-app.sliderBottom)/(app.sliderBottom-app.sliderTop)
        app.slider2Val = int(app.slider2Val*8)
    
    if app.drag1 or app.drag2:
        blurredImg = ed.blurImg(app.imgLst[app.screen-2],app.slider1Val,app.slider2Val)
        app.edges = ed.cannyEdges(blurredImg)
        app.image = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(app.edges))



def mouseReleased(app,event):
    if app.img1Push == True:
        app.file1 = filedialog.askopenfilename()
        app.img1Push = False
    if app.img2Push == True:
        app.file2 = filedialog.askopenfilename()
        app.img2Push = False
    if app.drag1 == True: 
        app.drag1 = False
    if app.drag2 == True: 
        app.drag2 = False
    if app.nextScreen == True:
        app.screen += 1
        if app.screen == 2:
            try:
                app.imgLst = []
                formatImg1,app.widthImg = ed.formatImage(app.file1)
                app.imgLst.append(formatImg1)
                formatImg2,app.widthImg = ed.formatImage(app.file2)
                app.imgLst.append(formatImg2)
            except:
                app.notReadable = True
                app.screen = 1
        if app.screen == 3 or app.screen == 4:
            app.edgeImgs.append(app.edges)
        if app.screen == 2 or app.screen == 3:
            app.sliderCen1 = app.sliderBottom
            app.sliderCen2 = app.sliderBottom
            app.slider1Val = 1
            app.slider2Val = 0  
            blurredImg = ed.blurImg(app.imgLst[app.screen-2],app.slider1Val,app.slider2Val)
            app.edges = ed.cannyEdges(blurredImg)
            app.image = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(app.edges))
        if app.screen == 4:
            app.edgePts = ed.getPts(app.edgeImgs)
            drawnImgs = pp.drawEdgesOnImgs(app.imgLst,app.edgePts)
            app.imgDis1 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(drawnImgs[0]))
            app.imgDis2 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(drawnImgs[1]))
        if app.screen == 6:
            moveVals,callibrated = cg.calibrateImgs(app.img1Loc,app.img2Loc,app.imgLst)
            if not callibrated:
                app.screen1Loc = []
                app.screen2Loc = []
                app.img1Loc = []
                app.img2Loc = []
                app.screen = 4
            else:
                uPairs = cg.pairImgPxls(app.widthImg,moveVals)
                intersections = cg.getIntersections(app.edgePts[0],app.edgePts[1], \
                                                                    uPairs,moveVals)
                window = dg.construct()
                dg.drawIntersections(window,intersections)
                dg.run()
        app.nextScreen = False



def redrawAll(app, canvas):
        if app.screen == 0:
            drawScreen0(app, canvas)
        elif app.screen == 1:
            drawScreen1(app, canvas)
        elif app.screen == 2 or app.screen == 3:
            drawScreen2(app, canvas)
        elif app.screen == 4:
            drawScreen4(app, canvas)
        elif app.screen == 5:
            drawScreen5(app, canvas)
        elif app.screen == 6:
            drawScreen6(app, canvas)
        if app.screen < 6:
            drawNextButton(app, canvas)



def drawScreen0(app, canvas): # entrance img
    canvas.create_text(app.width/2,app.height/2,text='welcome to placeHolder.',font='TkDefaultFont 14')


def drawScreen1(app, canvas): # image selection
    canvas.create_text(app.width/2,app.height/4,text='choose your 360° imgs',font='TkDefaultFont 12')
    if not app.img1Push: 
        canvas.create_rectangle(app.img1Sel[0],app.img1Sel[1], app.img1Sel[0]+app.selBW,\
                                    app.img1Sel[1]+app.selBH,fill='light grey',width=0)
    else: 
        canvas.create_rectangle(app.img1Sel[0],app.img1Sel[1], app.img1Sel[0]+app.selBW,\
                                    app.img1Sel[1]+app.selBH,outline='black',width=1)
    if not app.img2Push:
        canvas.create_rectangle(app.img2Sel[0],app.img2Sel[1],app.img2Sel[0]+app.selBW, \
                                app.img2Sel[1]+app.selBH,fill='light grey',width=0)
    else:
        canvas.create_rectangle(app.img2Sel[0],app.img2Sel[1],app.img2Sel[0]+app.selBW, \
                                    app.img2Sel[1]+app.selBH,outline='black',width=1)
    canvas.create_text(app.img1Sel[0]+(app.selBW/2),app.img1Sel[1]+(app.selBH/2),text='select img1')
    canvas.create_text(app.img2Sel[0]+(app.selBW/2),app.img2Sel[1]+(app.selBH/2),text='select img2')
    canvas.create_text(app.img1Sel[0]+app.selBW+4,app.img1Sel[1]+(app.selBH/2),text='...'+app.file1[-50:],anchor=W)
    canvas.create_text(app.img2Sel[0]+app.selBW+4,app.img2Sel[1]+(app.selBH/2),text='...'+app.file2[-50:],anchor=W)
    if app.notReadable:
        # canvas.create_rectangle((app.width/2)-70,(app.height/2)+10,(app.width/2)+70, \
        #                         (app.height/2)+30,outline='black',width=1)
        canvas.create_text(app.width/2,(app.height/2)+20,text='...pls select jpgs or pngs',\
                                font='TkDefaultFont 8')



def drawScreen2(app, canvas): # refine image 1 edges
    canvas.create_text(app.width/2,app.height/8,text=f'refine gaussian filter kernal and sigma for img{app.screen-1} edges',font='TkDefaultFont  12')
    canvas.create_image(app.edgeSelec[0],app.edgeSelec[1],image=app.image,anchor=NW)
    # slider bar 1 & 2
    canvas.create_rectangle(app.sliderStart,app.sliderTop,
                            app.sliderStart+6,app.sliderBottom,
                            fill='light grey',width=0)
    canvas.create_rectangle(app.sliderStart+app.sO,app.sliderTop,
                            app.sliderStart+app.sO+6,app.sliderBottom,
                            fill='light grey',width=0)
    # slider 1 & 2
    if not app.drag1: canvas.create_rectangle(app.sliderStart-15,app.sliderCen1-5,
                            app.sliderStart+6+15,app.sliderCen1+5,
                            fill='grey',width=0)
    else: canvas.create_rectangle(app.sliderStart-15,app.sliderCen1-5,
                            app.sliderStart+6+15,app.sliderCen1+5,
                            fill='dark grey',width=0)
    if not app.drag2: canvas.create_rectangle(app.sliderStart+app.sO-15,app.sliderCen2-5,
                            app.sliderStart+app.sO+6+15,app.sliderCen2+5,
                            fill='grey',width=0)
    else: canvas.create_rectangle(app.sliderStart+app.sO-15,app.sliderCen2-5,
                            app.sliderStart+app.sO+6+15,app.sliderCen2+5,
                            fill='dark grey',width=0)
    # values 1 & 2
    canvas.create_text(app.sliderStart+3,app.sliderBottom+(app.sO/2),text=f'{app.slider1Val}')
    canvas.create_text(app.sliderStart+app.sO+3,app.sliderBottom+(app.sO/2),text=f'{app.slider2Val}')
    canvas.create_text(app.sliderStart+3,app.sliderTop-(app.sO/2),text=f'kernal')
    canvas.create_text(app.sliderStart+app.sO+3,app.sliderTop-(app.sO/2),text=f'sigma')



def drawScreen4(app, canvas): # select same points
    canvas.create_text(app.width/2,app.height/8,text='pick (5) similar, ordered points',font='TkDefaultFont 12')
    canvas.create_image(app.img1[0],app.img1[1],image=app.imgDis1,anchor=NW)
    canvas.create_image(app.img2[0],app.img2[1],image=app.imgDis2,anchor=NW)
    drawCircles(app,canvas)


def drawScreen5(app, canvas): # entrance img
    canvas.create_text(app.width/2,app.height/2,text='click next to load the 3d generated roadscape',font='TkDefaultFont 14')


def drawScreen6(app, canvas): # entrance img
    canvas.create_text(app.width/2,app.height/2,text='youre a prick',font='TkDefaultFont 14')


def drawCircles(app,canvas):
    r = 10
    for i,loc in enumerate(app.screen1Loc):
        x,y = loc
        canvas.create_oval(x-r,y-r,x+r,y+r,outline='red',width=3)
        canvas.create_text(x,y-(2*r),text=f'{i+1}',fill='red',font='TkDefaultFont 14')
    for i,loc in enumerate(app.screen2Loc):
        x,y = loc
        canvas.create_oval(x-r,y-r,x+r,y+r,outline='red',width=3)
        canvas.create_text(x,y-(3*r),text=f'{i+1}',fill='red',font='TkDefaultFont 16')


def drawNextButton(app, canvas):
    if not app.nextScreen:
        canvas.create_rectangle(app.nB1[0],app.nB1[1],app.nB2[0],app.nB2[1],fill='light grey',
                            width=0)
    else:
        canvas.create_rectangle(app.nB1[0],app.nB1[1],app.nB2[0],app.nB2[1],outline='black',
                            width=1)
    bCX = (app.nB1[0] + app.nB2[0]) / 2
    bCY = (app.nB1[1] + app.nB2[1]) / 2
    canvas.create_text(bCX,bCY,text='NEXT >')


# size so both images fit!
runApp(width=1700, height=600) 
