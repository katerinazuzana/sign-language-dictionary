from tkinter import *
import math, cmath


class DrawingCanvas(Canvas):
    """
    """
    def __init__(self, parent, **options):
        """
        """
        super().__init__(parent, **options)
        
        self.settings = {'width': 3, 
                         'outline': 'red', 
                         'fill': 'gray90'}
        
        self.markSize = 3   # half size
        self.markSettings = {'width': 1, 
                             'outline': 'darkgreen', 
                             'fill': 'green'}
        self.markCursors = {'r' : 'right_side', 
                            'tr': 'top_right_corner', 
                            't' : 'top_side', 
                            'tl': 'top_left_corner', 
                            'l' : 'left_side', 
                            'bl': 'bottom_left_corner', 
                            'b' : 'bottom_side',
                            'br': 'bottom_right_corner'}
        
        self.id = None      # id of the item draw on canvas
        self.ellipse = None     # ellipse object
        self.drawMode = True
        self.moveMode = False
        self.scaleMode = False
        self.rotateMode = False

        self.bind('<ButtonPress-1>', self.onPress)
        self.bind('<B1-Motion>', self.onMove)
        self.bind('<ButtonRelease-1>', self.onRelease)
        self.bind('<Double-Button-1>', self.onDoubleClick)
    
    def onPress(self, event):
        self.start = event
        if self.drawMode:
            # remembering the left upper corner of rectangle encapsulating 
            # the ellipse - will be used for calculating the ellipse parameters
            self.leftUpper = event
        elif self.moveMode:
            self.startCoords = self.coords(self.id)
    
    def onMove(self, event):
        if self.drawMode:
            # drawing an ellipse
            if self.id: self.delete(self.id)
            self.id = self.create_oval(self.start.x, self.start.y, 
                                       event.x, event.y, 
                                       **self.settings)
        elif self.moveMode:
            # if mouse is over the ellipse, move the ellipse
            dx, dy = (event.x - self.start.x), (event.y - self.start.y)
            self.move(CURRENT, dx, dy)
            self.start = event
        
    def onRelease(self, event):
        if self.drawMode:
        
            rightLower = event
            self.ellipse = Ellipse(self.leftUpper, rightLower)
            print(self.ellipse)
            
            # convert ellipse representation from oval to polygon
            polygon = self.ovalToPolygon(self.ellipse)
            self.delete(self.id) # delete oval
            self.id = polygon
            
            self.drawMode = False
            self.moveMode = True
            # set cursor: self.ellipse.config
        
        elif self.moveMode:
            endCoords = self.coords(self.id)
            # recalculate the ellipse parameters
            self.ellipse.moved(self.startCoords, endCoords)
            print(self.ellipse)

    def onDoubleClick(self, event):
        """Change mode."""
        if self.coords(CURRENT):
            if self.moveMode: self.switchToScaleMode()
            elif self.scaleMode: self.switchToRotateMode()
            elif self.rotateMode: # switch to move mode
                self.rotateMode = False
                self.moveMode = True
                print('in move mode')
    
    def ovalToPolygon(self, ellipse, steps=40):
        """
        better keep the number of steps a multiple of four
        to ensure precise values for the ellipse parameters
        """
        points = []
        for i in range(steps):
            # calculate the angle for this step
            theta = 2 * math.pi * float(i) / steps

            x = ellipse.centerX + ellipse.a * math.cos(theta)
            y = ellipse.centerY + ellipse.b * math.sin(theta)

            points.append(round(x))
            points.append(round(y))
        
        return self.create_polygon(tuple(points), **self.settings)

    def switchToScaleMode(self):
        self.moveMode = False               
        self.scaleMode = True
        print('in scale mode')
        
        # draw marks
        self.drawMarks()
    
    def switchToRotateMode(self):
        self.scaleMode = False               
        self.rotateMode = True
        print('in rotate mode')

    def drawMarks(self):
        self.marks = {}
        for mark, center in self.ellipse.marks.items():
            markId = self.create_rectangle(center.real - self.markSize, 
                                  center.imag - self.markSize, 
                                  center.real + self.markSize, 
                                  center.imag + self.markSize, 
                                  **self.markSettings)
            self.marks[mark] = markId
            
            def onEnter(mark):
                return lambda ev: self.config(cursor = self.markCursors[mark])
            self.tag_bind(markId, '<Enter>', onEnter(mark))
            
            def onLeave():
                return lambda ev: self.config(cursor = '')
            self.tag_bind(markId, '<Leave>', onLeave())
    


class Ellipse():
    def __init__(self, leftUpper, rightLower):
    
        # calculate the ellipse parameters
        self.centerX = (rightLower.x + leftUpper.x) // 2
        self.centerY = (rightLower.y + leftUpper.y) // 2
        self.a = (rightLower.x - leftUpper.x) // 2
        self.b = (rightLower.y - leftUpper.y) // 2
        self.angle = 0
        
        # calculate positions of scale marks (ellipse not rotated)
        self.marks = {}
        self.marks['r']  = complex(self.centerX + self.a, self.centerY         )
        self.marks['tr'] = complex(self.centerX + self.a, self.centerY - self.b)
        self.marks['t']  = complex(self.centerX         , self.centerY - self.b)
        self.marks['tl'] = complex(self.centerX - self.a, self.centerY - self.b)
        self.marks['l']  = complex(self.centerX - self.a, self.centerY         )
        self.marks['bl'] = complex(self.centerX - self.a, self.centerY + self.b)
        self.marks['b']  = complex(self.centerX         , self.centerY + self.b)
        self.marks['br'] = complex(self.centerX + self.a, self.centerY + self.b)
        
        

    def moved(self, fromCoords, toCoords):
        """Recalculate the parameters after the ellipse has moved."""
        shiftX = toCoords[0] - fromCoords[0]
        shiftY = toCoords[1] - fromCoords[1]            
        self.centerX = self.centerX + shiftX
        self.centerY = self.centerY + shiftY

    def __str__(self):
        return 'Ellipse: centerX = {}, centerY = {}, a = {}, b = {}, angle = {}'.format(self.centerX, self.centerY, self.a, self.b, self.angle)




        
