#!/usr/bin/python
#Orange Widget developped by Michael ORTEGA Apr, 2015.

"""
<name>SpaceTime</name>
<icon>OWUTSpaceTime_icons/OWUTSpaceTime.svg</icon>
<description>Display 2D time oriented paths </description>
<priority>31</priority>
"""

import Orange
import math
from OWWidget import *
import OWGUI
import zlib
import datetime
from PyQt4.QtOpenGL                 import *

import sys
tmpSettings = QSettings()
path = str(tmpSettings.value("ut-path/path","unknown").toString()+"/Visualization/UTToolsVisualization/OWUTSpaceTime_libs")
sys.path.append(path)

from dateutil    import parser as _par
import geoMath as _gM

try:
    from OpenGL import GL,GLU,GLUT
except ImportError:
    print "PyOpenGL must be installed to run this widget."


class OWUTSpaceTime(OWWidget):
    settingsList = ['config']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
        
            try:
                from OpenGL import GL,GLU,GLUT
            except ImportError:
                print "PyOpenGL must be installed to run this widget."
                self.label       = OWGUI.label(self.controlArea,self,"PyOpenGL must be installed to run this widget.\nhttps://pypi.python.org/pypi/PyOpenGL")
                return 
                
            #controls
            self.boxSettings    = OWGUI.widgetBox(self.controlArea, "Columns Selection", addSpace=True)
            self.paths_times    = OWGUI.comboBox(self.boxSettings, self, None,"Timestamps")
            self.paths_ids      = OWGUI.comboBox(self.boxSettings, self, None,"Path IDs")
            self.paths_X        = OWGUI.comboBox(self.boxSettings, self, None,"X Coordinate")
            self.paths_Y        = OWGUI.comboBox(self.boxSettings, self, None,"Y Coordinate")

            #infos
            self.boxInfos       = OWGUI.widgetBox(self.controlArea, "Infos", addSpace=True)
            self.nb_paths       = OWGUI.label(self.boxInfos,self,"Nb Paths: ")
                        
            #OpenGL Area
            tabs = OWGUI.tabWidget(self.mainArea)
            tab = OWGUI.createTabPage(tabs, "OpenGL Context")
            self.ogl = Paths(self)
            self.ogl.setMouseTracking(True)
            
            tab.layout().addWidget(self.ogl)
            
            OWGUI.button(self.controlArea, self, 'Display Paths', callback=self.compute)
        else:
            self.boxSettings = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(self.boxSettings, self,"Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def compute(self):
        o = self.ogl
        
        if self.data: 
            #indices in data table
            dates    = self.paths_times.currentIndex()
            ids     = self.paths_ids.currentIndex()
            X       = self.paths_X.currentIndex()
            Y       = self.paths_Y.currentIndex()
        
            #list all the paths
            paths = []
            for line in self.data:
                if not line[ids] in paths:
                    paths.append(line[ids])
            self.nb_paths.setText("Nb Paths: "+str(len(paths)))
                
            #filling the paths
            o.paths = []
            for i in range(len(paths)):
                o.paths.append([])
            
            max_x = -float("inf")
            max_y = -float("inf")
            min_x = float("inf")
            min_y = float("inf")
            
            min_date = datetime.datetime(2100,2,11,15,0)
            max_date = datetime.datetime(1900,2,11,0,0)
            
            for line in self.data:
                i = paths.index(line[ids])
                d = _par.parse(line[dates].value)
                if d > max_date:
                    max_date = d
                elif d < min_date:
                    min_date = d
                x = float(line[X].value)
                y = float(line[Y].value)
                
                o.paths[i].append([x,d,y])
                
                if      x > max_x:   max_x = x
                elif    x < min_x:   min_x = x
                if      y > max_y:   max_y = y
                elif    y < min_y:   min_y = y
                            
                                        
            o.center    = [(max_x+min_x)/2.0,(max_y+min_y)/2.0]
            v_size       = (max_y-min_y)/2.0
            distance    = v_size/(math.tan((o.camera.v_angle)*math.pi/180.0/2.0))
            
            time_height = v_size/(max_date - min_date).total_seconds()

            o.size = [max_x-min_x,v_size,max_y-min_y]
            print o.size

            for i in range(len(o.paths)):
                for j in range(len(o.paths[i])):
                    Y = (o.paths[i][j][1] - min_date).total_seconds()*time_height
                    o.paths[i][j] = [o.paths[i][j][0]-o.center[0],Y,o.paths[i][j][2]-o.center[1]]
            

        o.camera.position   = [0,0,distance]
        o.camera.viewPoint  = [0,0,0]
        o.camera.up         = [0,1,0]        
        o.camera.near       = distance/100.
        o.camera.far        = distance*4     
                       
        self.ogl.initializeGL()                
        self.ogl.updateGL()
        self.boxSettings.update()

    def setData(self, data, id=None):
        self.data = data
        if self.data != None:
            self.paths_times.clear()
            self.paths_ids.clear()
            self.paths_X.clear()
            self.paths_Y.clear()
        
            for d in self.data.domain:
                self.paths_times.addItem(str(d.name))
                self.paths_ids.addItem(str(d.name))
                self.paths_X.addItem(str(d.name))
                self.paths_Y.addItem(str(d.name))
                
            self.paths_times.setCurrentIndex(0)
            self.paths_ids.setCurrentIndex(1)
            self.paths_X.setCurrentIndex(2)
            self.paths_Y.setCurrentIndex(3)
        return

def mainOWUTOpenGL(data):
    return null


class Camera:
    "Parametres extrinseques de la camera OpenGL"
    def __init__(self,l):
        self.position 		= l[0:3]
        self.viewPoint 		= l[3:6]
        self.up				= l[6:9]
        self.v_angle		= 20.
        self.near			= 0.001
        self.far			= 20.
        self.ray            = [0,0,0]
        
    def rayFromCursor(self,c,ws):
        """ ws is the window ratio W/H """
        print "cursor",c
        height = 2*self.near*math.tan((self.v_angle*math.pi/180.0)/2.0)
        width  = height*ws

        up = [x*height for x in self.up]
        
        direction_n = _gM.normalize([x-y for x,y in zip(self.viewPoint,self.position)])
        direction = [x*self.near for x in direction_n] 

        left = _gM.cross(self.up,direction_n)
        left = [x*width for x in left]
        
        pt = [cp+d+u/2.0+l/2.0 for cp,d,u,l in zip(self.position,direction,up,left)]
        pt = [x-u*c[1]-l*c[0] for x,u,l in zip(pt,up,left)]
        res = _gM.normalize([x-y for x,y in zip(pt,self.position)])
        self.ray = res
        return res
        
        
class Paths(QGLWidget):
    """Widget for drawing paths"""
    
    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(500, 500)
        self.window_size    = [500,500]
        self.clear_color    = [0.5,0.5,0.5,1]
        self.paths          = []
        self.center         = [0,0]
        self.size           = [1,1,1]
        self.cursor         = [0,0]
        self.mode           = "normal"
        self.camera         = Camera([0,0,10,0,0,0,0,1,0])
        self.min_date       = datetime.date.today()
        self.max_date       = datetime.date.today()
        self.closest_path    = -1
        self.index_in_closest_path = -1


    ###################################
    ## COMPUTATIONS
    
    
    def closestPath(self,x,y):
        self.closest_path = -1
        min_dist = float("inf")
        
        ray = self.camera.rayFromCursor(self.cursor,self.window_size[0]/float(self.window_size[1]))
                
        for p in range(len(self.paths)):
            for i in range(len( self.paths[p])):
                pt = self.paths[p]
                A = _gM.projectPointOnLine(pt[i],self.camera.position,ray)
                dA = _gM.distance3DSquared(pt[i],A)
                if dA < min_dist:
                    self.closest_path = p
                    min_dist = dA
                    self.index_in_closest_path = i
          

    ###################################
    ## DISPLAY
    
    def drawFrame(self):
        
        GL.glBegin(GL.GL_LINES)
        
        GL.glColor(1,1,1,1)
        GL.glVertex(-1000,0,0)
        GL.glVertex(1000,0,0)
        GL.glVertex(0,-0,0)
        GL.glVertex(0,1000,0)
        GL.glVertex(0,0,-1000)
        GL.glVertex(0,0,1000)
         
        GL.glEnd()
        
    def drawCube(self):
        GL.glBegin(GL.GL_LINES)
        
        GL.glColor(1,1,1,1)

        #bottom
        GL.glVertex(-self.size[0]/2.0,0,-self.size[2]/2.0)
        GL.glVertex(-self.size[0]/2.0,0,self.size[2]/2.0)

        GL.glVertex(-self.size[0]/2.0,0,self.size[2]/2.0)
        GL.glVertex(self.size[0]/2.0,0,self.size[2]/2.0)

        GL.glVertex(self.size[0]/2.0,0,self.size[2]/2.0)
        GL.glVertex(self.size[0]/2.0,0,-self.size[2]/2.0)

        GL.glVertex(self.size[0]/2.0,0,-self.size[2]/2.0)
        GL.glVertex(-self.size[0]/2.0,0,-self.size[2]/2.0)
        
        #top
        GL.glVertex(-self.size[0]/2.0,self.size[1],-self.size[2]/2.0)
        GL.glVertex(-self.size[0]/2.0,self.size[1],self.size[2]/2.0)

        GL.glVertex(-self.size[0]/2.0,self.size[1],self.size[2]/2.0)
        GL.glVertex(self.size[0]/2.0,self.size[1],self.size[2]/2.0)

        GL.glVertex(self.size[0]/2.0,self.size[1],self.size[2]/2.0)
        GL.glVertex(self.size[0]/2.0,self.size[1],-self.size[2]/2.0)

        GL.glVertex(self.size[0]/2.0,self.size[1],-self.size[2]/2.0)
        GL.glVertex(-self.size[0]/2.0,self.size[1],-self.size[2]/2.0)
        
        #sides
        GL.glVertex(-self.size[0]/2.0,0,-self.size[2]/2.0)
        GL.glVertex(-self.size[0]/2.0,self.size[1],-self.size[2]/2.0)
        
        GL.glVertex(-self.size[0]/2.0,0,self.size[2]/2.0)
        GL.glVertex(-self.size[0]/2.0,self.size[1],self.size[2]/2.0)
        
        GL.glVertex(self.size[0]/2.0,0,self.size[2]/2.0)
        GL.glVertex(self.size[0]/2.0,self.size[1],self.size[2]/2.0)
        
        GL.glVertex(self.size[0]/2.0,0,-self.size[2]/2.0)
        GL.glVertex(self.size[0]/2.0,self.size[1],-self.size[2]/2.0)
        
        GL.glEnd()
        
    def displayPaths(self):

        if len(self.paths) > 0:
            GL.glColor(0,1,0,1)
            
            target_point = [0,0,0]
            if self.index_in_closest_path != -1:
                target_point = self.paths[self.closest_path][self.index_in_closest_path]
            
            points_of_target = []
            for i in range(len(self.paths)):
                done = False
                GL.glLineWidth(4)
                GL.glBegin(GL.GL_LINE_STRIP)
                for pt in self.paths[i]:
                    if pt[1] > target_point[1] and done == False:
                        points_of_target.append(pt)
                        done = True
                        GL.glVertex(*pt)
                        GL.glEnd()
                        GL.glLineWidth(1)    
                        GL.glBegin(GL.GL_LINE_STRIP)
                        GL.glVertex(*pt)
                    else:
                        GL.glVertex(*pt)
                GL.glEnd()
                
            GL.glLineWidth(1)
            
            GL.glColor(0,0,0,1)
            for p in self.paths:
                GL.glBegin(GL.GL_LINE_STRIP)
                for pt in p:
                    GL.glVertex([pt[0],0,pt[2]])
                GL.glEnd()
            
            GL.glColor(0.1,0.1,0.1,1)
            GL.glBegin(GL.GL_LINES)
            for p in self.paths:
                pt = p[0]
                GL.glVertex(*pt)
                GL.glVertex([pt[0],0,pt[2]])
                pt = p[-1]
                GL.glVertex(*pt)
                GL.glVertex([pt[0],0,pt[2]])

            GL.glEnd()
            
            
            
            GL.glBegin(GL.GL_LINES)
            for pt in points_of_target:
                GL.glVertex(*pt)
                GL.glVertex(pt[0],0,pt[2])                
            GL.glEnd()
            
        
    def paintGL(self):  
        """Drawing routine"""
        self.resizeGL(*self.window_size)

        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glLoadIdentity()
         
        GLU.gluLookAt(  self.camera.position[0],self.camera.position[1],self.camera.position[2],
                        self.camera.viewPoint[0],self.camera.viewPoint[1],self.camera.viewPoint[2],
                        self.camera.up[0],self.camera.up[1],self.camera.up[2])    
                        
        #self.drawFrame()
        self.drawCube()
        self.displayPaths()
        
        GL.glFlush()

    def resizeGL(self, w, h):
        """Resize the GL window"""

        GL.glViewport(0, 0, w, h)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(self.camera.v_angle,float(w)/float(h),self.camera.near,self.camera.far)
        self.window_size = [w,h]
        
        GL.glMatrixMode(GL.GL_MODELVIEW)

    def initializeGL(self):
        """Initialize GL"""

        # set viewing projection
        GL.glClearColor(*self.clear_color)
        GL.glClearDepth(1.0)
     
    #######################
    ## INTERACTIONS     
    
    def mousePressEvent(self,event):
        if event.button() == 2:
            self.mode = "rotation"
        elif event.button() == 4:
            self.mode = "translation"
        else:
            print "something"
            
        self.cursor = [event.x()/float(self.window_size[0]),event.y()/float(self.window_size[1])]
        print self.cursor
       
    def wheelEvent(self,event):
        direction = [x-y for x,y in zip(self.camera.viewPoint,self.camera.position)]
        self.camera.position 	= [t+math.copysign(0.01,event.delta()/float(self.window_size[0]))*k for t,k in zip(self.camera.position,direction)]
        self.glDraw()       
        pass
            
    def mouseReleaseEvent(self,event):
        self.mode = "normal"
        
    def mouseMoveEvent(self,event):
        depX = event.x()/float(self.window_size[0])-self.cursor[0]
        depY = event.y()/float(self.window_size[1])-self.cursor[1]

        if self.mode == "rotation":
            
            #from left to right -> 2PI
            q = _gM.quaternion(depX*3.1415*2,[0,1,0])
            self.camera.position = _gM.rotatePointWithPivot(self.camera.position,q,self.camera.viewPoint)
            self.camera.direction = _gM.normalize([t-k for t,k in zip(self.camera.viewPoint,self.camera.position)])
            right = _gM.cross(self.camera.direction,[0,1,0])
            self.camera.up = _gM.normalize(_gM.cross(right,self.camera.direction))
            
            #from down to up -> PI
            s = _gM.cross(self.camera.direction,self.camera.up)
            q = _gM.quaternion(depY*3.1415,_gM.normalize(s))
            self.camera.position = _gM.rotatePointWithPivot(self.camera.position,q,self.camera.viewPoint)
            self.camera.direction = _gM.normalize([t-k for t,k in zip(self.camera.viewPoint,self.camera.position)])
            right = _gM.cross(self.camera.direction,[0,1,0])
            self.camera.up = _gM.normalize(_gM.cross(right,self.camera.direction))
            
            
        elif self.mode == "translation":
            direction = _gM.normalize([x-y for x,y in zip(self.camera.viewPoint,self.camera.position)])
            d = math.sqrt(_gM.distance3DSquared(self.camera.position,self.camera.viewPoint))
            v = [-depX*d*t + depY*d*k for t,k in zip(_gM.cross(direction,self.camera.up),self.camera.up)]
            self.camera.position 	= [t+k for t,k in zip(self.camera.position,v)]
            self.camera.viewPoint 	= [t+k for t,k in zip(self.camera.viewPoint,v)]	

        else: #No specific mode
            self.closestPath(event.x(),event.y())
            
        self.cursor = [event.x()/float(self.window_size[0]),event.y()/float(self.window_size[1])]
        self.glDraw()
