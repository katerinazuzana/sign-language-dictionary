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
#            polygon = self.ovalToPolygon(self.ellipse)
#            self.delete(self.id) # delete oval
#            self.id = polygon
            
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
        
        self.drawMarks()
    
    def switchToRotateMode(self):
        self.scaleMode = False               
        self.rotateMode = True
        print('in rotate mode')

    def drawMarks(self):
        self.marks = {}     # pictures drawn on canvas
        for mark, center in self.ellipse.markCoords.items():
            markId = self.create_rectangle(center.real - self.markSize, 
                                  center.imag - self.markSize, 
                                  center.real + self.markSize, 
                                  center.imag + self.markSize, 
                                  **self.markSettings, 
                                  tags='marks')
            self.marks[mark] = markId
            
            def onEnter(mark):
                return lambda ev: self.config(cursor = self.markCursors[mark])
            self.tag_bind(markId, '<Enter>', onEnter(mark))
            
            self.tag_bind(markId, '<Leave>', 
                          lambda ev: self.config(cursor = ''))
    
            def onPress(mark):
                return lambda ev: self.startScale(ev, mark)
            self.tag_bind(markId, '<ButtonPress-1>', onPress(mark))

    def startScale(self, event, mark):
        self.scaleFrom = event
        self.start = event
        self.movingMark = mark
        
        # cursor keep the same shape during whole scaling
        # even when it moves out of the mark
        self.config(cursor = self.markCursors[mark])
        self.tag_unbind(self.marks[mark], '<Leave>')
        
        self.bind('<B1-Motion>', self.doScale)
        self.bind('<ButtonRelease-1>', self.stopScale)
    
    def doScale(self, event):
        
        # recalculate the marks' positions
        self.recalcCornerMarks(event)
        self.ellipse.recalcMiddleMarks()
            
        # redraw the marks
        self.delete('marks')
        self.drawMarks()
        
        # redraw the ellipse
        self.delete(self.id)
        topLeftPoint = (self.ellipse.markCoords['tl'].real, 
                        self.ellipse.markCoords['tl'].imag)
        bottomRightPoint = (self.ellipse.markCoords['br'].real, 
                            self.ellipse.markCoords['br'].imag)
        self.id = self.create_oval(*topLeftPoint, 
                                   *bottomRightPoint, 
                                   **self.settings)
        self.tag_lower(self.id) # draw the ellipse under the marks
        
        self.start = event
    
    def stopScale(self, event):
        self.scaleTo = event
        # recalculate the ellipse parameters
        
        # reset the cursor shape
        self.config(cursor = '')
        self.tag_bind(self.marks[self.movingMark], '<Leave>', 
                          lambda ev: self.config(cursor = ''))
        # set the bindings to the initial ones
        self.bind('<B1-Motion>', self.onMove)
        self.bind('<ButtonRelease-1>', self.onRelease)
        
    def recalcCornerMarks(self, event):
        """Recalculate the coordinates of the corner marks."""
        mouseMoveX = event.x - self.start.x
        mouseMoveY = event.y - self.start.y        
        
        # only horizontal movement:                
        if self.movingMark == 'r':
            for m in ('tr', 'br'):
                self.ellipse.markCoords[m] += complex(mouseMoveX, 0)
        elif self.movingMark == 'l':
            for m in ('tl', 'bl'):
                self.ellipse.markCoords[m] += complex(mouseMoveX, 0)
        
        # only vertical movement:                      
        elif self.movingMark == 't':
            for m in ('tl', 'tr'):
                self.ellipse.markCoords[m] += complex(0, mouseMoveY)
        elif self.movingMark == 'b':
            for m in ('bl', 'br'):
                self.ellipse.markCoords[m] += complex(0, mouseMoveY)
        
        else:
            # a corner mark is moving
            moves = [(0         , mouseMoveY), 
                     (mouseMoveX,          0), 
                     (mouseMoveX, mouseMoveY)]
            
            if self.movingMark == 'tr':
                order = ('tl', 'br', 'tr')
            elif self.movingMark == 'bl':
                order = ('br', 'tl', 'bl')     
            elif self.movingMark == 'tl':
                order = ('tr', 'bl', 'tl')
            elif self.movingMark == 'br':
                order = ('bl', 'tr', 'br')

            for m, move in zip(order, moves):
                self.ellipse.markCoords[m] += complex(*move)



class Ellipse():
    def __init__(self, leftUpper, rightLower):
    
        # calculate the ellipse parameters
        self.centerX = (rightLower.x + leftUpper.x) // 2
        self.centerY = (rightLower.y + leftUpper.y) // 2
        self.a = (rightLower.x - leftUpper.x) // 2
        self.b = (rightLower.y - leftUpper.y) // 2
        self.angle = 0
        
        # calculate initial positions of scale marks (ellipse not rotated)
        self.markCoords = {}
        self.markCoords['r']  = complex(self.centerX + self.a, 
                                        self.centerY         )
        self.markCoords['tr'] = complex(self.centerX + self.a, 
                                        self.centerY - self.b)
        self.markCoords['t']  = complex(self.centerX         , 
                                        self.centerY - self.b)
        self.markCoords['tl'] = complex(self.centerX - self.a, 
                                        self.centerY - self.b)
        self.markCoords['l']  = complex(self.centerX - self.a, 
                                        self.centerY         )
        self.markCoords['bl'] = complex(self.centerX - self.a, 
                                        self.centerY + self.b)
        self.markCoords['b']  = complex(self.centerX         , 
                                        self.centerY + self.b)
        self.markCoords['br'] = complex(self.centerX + self.a, 
                                        self.centerY + self.b)
        
    def recalcMiddleMarks(self):
        """Recalculate the coors of the middle marks."""
        for m in ('r', 't', 'l', 'b'):
            c1, c2 = self.getCorners(m)
            self.markCoords[m] = (self.markCoords[c1] + self.markCoords[c2]) / 2
            self.markCoords[m] = complex(int(round(self.markCoords[m].real)), 
                                         int(round(self.markCoords[m].imag)))
        
    def getCorners(self, middle):
        """Return corner marks' names corresponding to a given middle mark."""
        if middle in ('r', 'l'):
            return 't' + middle, 'b' + middle
        if middle in ('t', 'b'):
            return middle + 'r', middle + 'l'

    def moved(self, fromCoords, toCoords):
        """Recalculate the parameters after the ellipse has moved."""
        shiftX = toCoords[0] - fromCoords[0]
        shiftY = toCoords[1] - fromCoords[1]            
        self.centerX = self.centerX + shiftX
        self.centerY = self.centerY + shiftY
    


    def __str__(self):
        return 'Ellipse: centerX = {}, centerY = {}, a = {}, b = {}, angle = {}'.format(self.centerX, self.centerY, self.a, self.b, self.angle)




        
