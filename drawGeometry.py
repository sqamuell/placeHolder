    # Code by: Samuel Losi
# last updated:  04/22/20

# code referenced from https://www.youtube.com/watch?v=Hqg4qePJV2U
# formatting for my specific project will take place, as well as gerometry drawing

####### Geometry and 3D Space #######

from pyglet.gl import *
from pyglet.window import key
import math


class Model:

    def __init__(self):
        self.batch = pyglet.graphics.Batch()
    
    # I wrote from here...

    def addTriangle(self,ptL,color):
        x0,z0,y0 = ptL[0]
        x1,z1,y1 = ptL[1]
        x2,z2,y2 = ptL[2]
        self.batch.add(3,GL_TRIANGLES,None,('v3f',(x0,y0,z0, x1,y1,z1, x2,y2,z2, )))

    def addLine(self,point,cen):
        disColor = ('c3f',(1,1,1,0,0,0))
        xC,zC,yC = cen
        x,z,y = point
        self.batch.add(2,GL_LINES,None,('v3f',(x,y,z,xC,yC,zC)),disColor)
        
    def addPoint(self,point):
        disColor = ('c3f',(0,0,0))
        x,z,y = point
        self.batch.add(1,GL_POINTS,None,('v3f',(x,y,x)),disColor)

    # ... to here!

    def draw(self):
        self.batch.draw()

class Player:
    def __init__(self,pos=(0,0,0),rot=(0,0)):
        self.pos = list(pos)
        self.rot = list(rot)

    def mouse_motion(self,dx,dy):
        dx/=8; dy/=8; self.rot[0]+=dy; self.rot[1]-=dx
        if self.rot[0]>90: self.rot[0] = 90
        elif self.rot[0]<-90: self.rot[0] = -90

    def update(self,dt,keys):
        s = dt*10
        rotY = -self.rot[1]/180*math.pi
        dx,dz = s*math.sin(rotY),s*math.cos(rotY)
        if keys[key.W]: self.pos[0]+=dx; self.pos[2]-=dz
        if keys[key.S]: self.pos[0]-=dx; self.pos[2]+=dz
        if keys[key.A]: self.pos[0]-=dz; self.pos[2]-=dx
        if keys[key.D]: self.pos[0]+=dz; self.pos[2]+=dx
        if keys[key.SPACE]: self.pos[1]+=s
        if keys[key.LSHIFT]: self.pos[1]-=s

class Window(pyglet.window.Window):

    def push(self,pos,rot): glPushMatrix(); glRotatef(-rot[0],1,0,0); glRotatef(-rot[1],0,1,0); glTranslatef(-pos[0],-pos[1],-pos[2],)
    def Projection(self): glMatrixMode(GL_PROJECTION); glLoadIdentity()
    def Model(self): glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    def set2d(self): self.Projection(); gluOrtho2D(0,self.width,0,self.height); self.Model()
    def set3d(self): self.Projection(); gluPerspective(70,self.width/self.height,0.05,1000); self.Model()

    def setLock(self,state): self.lock = state; self.set_exclusive_mouse(state)
    lock = False; mouse_lock = property(lambda self:self.lock,setLock)
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.set_minimum_size(300,200)
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        pyglet.clock.schedule(self.update)

        self.model = Model()
        self.player = Player((0.5,1.5,1.5),(-30,0))

    def on_mouse_motion(self,x,y,dx,dy):
        if self.mouse_lock: self.player.mouse_motion(dx,dy)

    def on_key_press(self,KEY,MOD):
        if KEY == key.ESCAPE: self.close()
        elif KEY == key.E: self.mouse_lock = not self.mouse_lock

    def update(self,dt):
        self.player.update(dt,self.keys)

    def on_draw(self):
        self.clear()
        self.set3d()
        self.push(self.player.pos,self.player.rot)
        self.model.draw()
        glPopMatrix()

# I wrote from here...

def construct():
    window = Window(fullscreen=True,caption='3d geometry',resizable=False)
    # niceBlue = (0.5,0.7,1,1)
    # black = (0,0,0,1)
    glClearColor(0,0,0,1)
    glEnable(GL_DEPTH_TEST)
    return window

def addTriangle(window,ptL,color):
    window.model.addTriangle(ptL,color)

def addLine(window, point, center=(0,0,0)):
    window.model.addLine(point,center)

def addPoint(window, point):
    x,y,z = point
    other1 = (x+0.1,y+0.1,z)
    other2 = (x+0.1,y,z+0.1)
    points = [point,other1,other2]
    window.model.addTriangle(points,1)

def drawIntersections(window,intersections):
    for intersect in intersections:
        x,y,z = intersect
        ground = (x,y,-1)
        mid = (0,y,-1)
        addLine(window,intersect,ground)
        addLine(window,mid,ground)
        if x < 0: otherPt = (x-2,y,z)
        else: otherPt = (x+2,y,z)        
        addLine(window,intersect,otherPt)

def run():
    pyglet.app.run()

# ... to here!