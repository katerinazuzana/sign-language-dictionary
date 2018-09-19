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
        self.scMarkSettings = {'width': 1, 
                               'outline': 'darkgreen', 
                               'fill': 'green'}
        self.rotMarkSettings = {'fill': 'black'}
        self.scMarkCursors = {'r' : 'right_side', 
                            'tr': 'top_right_corner', 
                            't' : 'top_side', 
                            'tl': 'top_left_corner', 
                            'l' : 'left_side', 
                            'bl': 'bottom_left_corner', 
                            'b' : 'bottom_side',
                            'br': 'bottom_right_corner'}
        
        self.markIds = {}       # mark items drawn on canvas  
        self.id = None          # id of the ellipse draw on canvas
        self.ellipse = None     # ellipse object
        
        self.drawMode = True
        self.scaleMode = False
        self.rotateMode = False

        self.bind('<ButtonPress-1>', self.onPress)
        self.bind('<B1-Motion>', self.onMotion)
        self.bind('<ButtonRelease-1>', self.onRelease)
        self.bind('<Double-Button-1>', self.onDoubleClick)
    
    def onPress(self, event):
        
        if self.drawMode:
            # remember the topleft corner of rectangle encapsulating the ellipse
            self.topLeft = Point(event)
    
    def onMotion(self, event):
        """
        """
        if self.drawMode:
            # draw an ellipse
            if self.id: self.delete(self.id)
            self.id = self.create_oval(self.topLeft.x, self.topLeft.y, 
                                       event.x, event.y, 
                                       **self.settings, 
                                       tags='ellipse')
        
    def onRelease(self, event):
        if self.drawMode:
            
            # create an ellipse object
            bottomRight = Point(event)
            self.ellipse = Ellipse(self.topLeft, bottomRight)
            
            # set cursor
            self.tag_bind('ellipse', '<Enter>', 
                                     lambda ev: self.config(cursor='fleur'))
            self.tag_bind('ellipse', '<Leave>', 
                                     lambda ev: self.config(cursor=''))
            
            # binding that enables moving the ellipse
            self.tag_bind('ellipse', '<ButtonPress-1>', self.startMove)
            
            # change mode
            self.drawMode = False
            self.switchToScaleMode()

    def onDoubleClick(self, event):
        """Change mode."""

        if self.id in self.find_withtag(CURRENT):
            # if mouse is over the ellipse:
            
            if self.scaleMode: self.switchToRotateMode()
            else: self.switchToScaleMode()

    def switchToRotateMode(self):
        self.scaleMode = False               
        self.rotateMode = True
        self.drawMarks(mode='rotate')

    def switchToScaleMode(self):
        self.rotateMode = False               
        self.scaleMode = True
        self.drawMarks(mode='scale')
    
    def drawMarks(self, mode):
        if mode == 'scale':
            createFcn = self.create_rectangle
            settings = self.scMarkSettings
        elif mode == 'rotate':
            createFcn = self.create_oval
            settings = self.rotMarkSettings
    
        for mark, position in self.ellipse.markCoords.items():
            topLeft = position - (self.markSize, self.markSize)
            bottomRight = position + (self.markSize, self.markSize)
            
            markId = createFcn(topLeft.x, topLeft.y, 
                               bottomRight.x, bottomRight.y, 
                               **settings, 
                               tags='marks')
            self.markIds[mark] = markId
            
            if mode == 'scale':
                def onEnter(mark):
                    return lambda ev: self.config(cursor = 
                                                  self.scMarkCursors[mark])
                self.tag_bind(markId, '<Enter>', onEnter(mark))
    
                def onPress(mark):
                    return lambda ev: self.startScale(ev, mark)
                self.tag_bind(markId, '<ButtonPress-1>', onPress(mark))
            
        if mode == 'rotate':
            self.tag_bind('marks', '<Enter>', 
                                   lambda ev: self.config(cursor = 'exchange'))
            self.tag_bind('marks', '<ButtonPress-1>', self.startRotate)
            
        self.tag_bind('marks', '<Leave>', lambda ev: self.config(cursor = ''))
    
    def startMove(self, event):
        self.startPoint = Point(event)
        self.bind('<B1-Motion>', self.doMove)
        self.bind('<ButtonRelease-1>', self.stopMove)
    
    def doMove(self, event):

        # change the ellipse' topLeft and bottomRight points
        self.endPoint = Point(event)
        self.recalcCornersOnMove()
        
        # recalculate the marks' positions
        self.ellipse.calcMarkCoords()
                
        self.redrawItems()
        self.startPoint = Point(event)
    
    def stopMove(self, event):
        # reset binding
        self.bind('<B1-Motion>', self.onMotion)
        self.bind('<ButtonRelease-1>', self.onRelease)
            
    def startScale(self, event, mark):
        
        self.startPoint = Point(event)
        self.movingMark = mark
        
        # make cursor keep the same shape during whole scaling
        # even when it moves out of the mark
        self.config(cursor = self.scMarkCursors[mark])
        self.tag_unbind(self.markIds[mark], '<Leave>')
        
        self.bind('<B1-Motion>', self.doScale)
        self.bind('<ButtonRelease-1>', self.stopScale)
    
    def doScale(self, event):
        
        # change the ellipse' topLeft and bottomRight points
        self.endPoint = Point(event)
        self.recalcCornersOnScale()
        
        # recalculate the marks' positions
        self.ellipse.calcMarkCoords()
        
        self.redrawItems()
        self.startPoint = Point(event)
    
    def stopScale(self, event):

        # reset the cursor shape
        self.config(cursor = '')
        self.tag_bind(self.markIds[self.movingMark], '<Leave>', 
                      lambda ev: self.config(cursor = ''))
        # set the bindings to the initial ones
        self.bind('<B1-Motion>', self.onMotion)
        self.bind('<ButtonRelease-1>', self.onRelease)
    
    def startRotate(self, event):
        
        self.startPoint = Point(event)
        
        # make cursor keep the same shape during whole scaling
        # even when it moves out of the mark
        self.config(cursor = 'exchange')
        self.tag_unbind('marks', '<Leave>')
        
        self.bind('<B1-Motion>', self.doRotate)
        self.bind('<ButtonRelease-1>', self.stopRotate)
    
    def doRotate(self, event):
        
        # calculate the angle difference
        startAngle = self.startPoint.getAngle(self.ellipse.center)
        endAngle = Point(event).getAngle(self.ellipse.center)
        diffAngle = endAngle - startAngle
        
        # update the ellipse' angle and topLeft and bottomRight points
        self.ellipse.changeAngle(diffAngle)
        
        # recalculate the ellipse parameters and the marks' positions
        self.ellipse.calcMarkCoords(mode='rotate')
        
        self.redrawItems()
        self.startPoint = Point(event)
    
    def stopRotate(self, event):

        # reset the cursor shape
        self.config(cursor = '')
        self.tag_bind('marks', '<Leave>', lambda ev: self.config(cursor=''))
        # set the bindings to the initial ones
        self.bind('<B1-Motion>', self.onMotion)
        self.bind('<ButtonRelease-1>', self.onRelease)    
    
    def redrawItems(self):
         
        # redraw the ellipse
        self.delete(self.id)
        if self.ellipse.angle == 0:
            self.id = self.create_oval(self.ellipse.topLeft.x, 
                                   self.ellipse.topLeft.y, 
                                   self.ellipse.bottomRight.x, 
                                   self.ellipse.bottomRight.y, 
                                   **self.settings, 
                                   tags='ellipse')
        else:
            # get a tuple of points covering (densely enough) the ellipse border
            polygonPoints = self.getPolygonPoints()
            # draw the rotated ellipse - as a polygon
            self.id = self.create_polygon(polygonPoints, 
                                      **self.settings, 
                                      tags='ellipse')
        
        # redraw the marks
        if self.scaleMode: mode = 'scale'
        else: mode = 'rotate'
        self.delete('marks')
        self.drawMarks(mode=mode)
    
    def getPolygonPoints(self, steps=80):
        """
        
        better keep the number of steps a multiple of four
        to ensure precise values for the ellipse parameters
        
        Returns:
        a tuple of points' coords: (x0, y0, x1, y1, ...)
        """
        points = []
        for i in range(steps):
            # calculate the angle for this step
            theta = 2 * math.pi * float(i) / steps
            
            # point is of type Point
            point = self.ellipse.center + math.cos(theta) * self.ellipse.a + \
                                          math.sin(theta) * self.ellipse.b
            points.append(point.x)
            points.append(point.y)        
        return tuple(points)
    
    def recalcCornersOnMove(self):
        """Recalculate the coords of the topLeft and bottomRight corners."""

        shift = self.endPoint - self.startPoint
        self.ellipse.topLeft += shift
        self.ellipse.bottomRight += shift
        
    def recalcCornersOnScale(self):
        """Recalculate the coords of the topLeft and bottomRight corners."""
        
        mouseMove = self.endPoint - self.startPoint
        
        # only horizontal movement:                
        if self.movingMark == 'r':
            self.ellipse.bottomRight += mouseMove.projectOn((1, 0))
        elif self.movingMark == 'l':
            self.ellipse.topLeft += mouseMove.projectOn((1, 0))
        
        # only vertical movement:                      
        elif self.movingMark == 't':
            self.ellipse.topLeft += mouseMove.projectOn((0, 1))
        elif self.movingMark == 'b':
            self.ellipse.bottomRight += mouseMove.projectOn((0, 1))
        
        # a corner mark is moving            
        elif self.movingMark == 'tr':
            self.ellipse.topLeft += mouseMove.projectOn((0, 1))
            self.ellipse.bottomRight += mouseMove.projectOn((1, 0))
        elif self.movingMark == 'bl':
            self.ellipse.bottomRight += mouseMove.projectOn((0, 1))
            self.ellipse.topLeft += mouseMove.projectOn((1, 0))    
        elif self.movingMark == 'tl':
            self.ellipse.topLeft += mouseMove
        elif self.movingMark == 'br':
            self.ellipse.bottomRight += mouseMove



class Ellipse():
    def __init__(self, topLeft, bottomRight):
        """
        Arguments:
        topLeft -- [Point]
        bottomRight -- [Point]
        """
    
        self.topLeft = topLeft
        self.bottomRight = bottomRight
        
        self.angle = 0       
        
        # calculate initial positions of scale marks (ellipse not rotated)
        self.markCoords = {}
        self.calcMarkCoords()
    
    def calcParams(self):
        """Calculate the ellipse parameters.
        
        Calculate the 'center', 'a', and 'b' parameters from 
        'topLeft', 'bottomRight', and 'angle'.
        """
        
        self.center = (self.topLeft + self.bottomRight) * 0.5
        self.ab = self.bottomRight - self.center
        
        # unit vector in the direction of a-semiaxis -- tuple: (float, float)
        unitA = (math.cos(self.angle), math.sin(self.angle))
        # unit vector in the direction of b-semiaxis -- tuple
        unitB = (- math.sin(self.angle), math.cos(self.angle))
        self.a = self.ab.projectOn(unitA)
        self.b = self.ab.projectOn(unitB)        
    
    def changeAngle(self, diffAngle):
        
        self.angle = self.angle + diffAngle
        self.a = self.a.rotate(diffAngle)
        self.b = self.b.rotate(diffAngle)
        
        # probably not needed:
        self.topLeft = self.topLeft.rotate(diffAngle, self.center)
        self.bottomRight = self.bottomRight.rotate(diffAngle, self.center)
        
    def calcMarkCoords(self, mode=None):
        """Calculate the coords of the scaling/rotating marks."""
        
        if mode != 'rotate': self.calcParams()
        self.markCoords['r']  = self.center + self.a
        self.markCoords['tr'] = self.center + self.a - self.b
        self.markCoords['t']  = self.center          - self.b
        self.markCoords['tl'] = self.center - self.a - self.b
        self.markCoords['l']  = self.center - self.a
        self.markCoords['bl'] = self.center - self.a + self.b
        self.markCoords['b']  = self.center          + self.b
        self.markCoords['br'] = self.center + self.a + self.b   

    def __str__(self):
        return 'Ellipse: center = {}, a = {}, b = {}, angle = {}'.format(self.center, self.a, self.b, self.angle)



class Point():
    """Class representing a point (a vector) in 2D plane.
    
    """
    def __init__(self, *args):
        
        assert len(args) in (1, 2), \
               "Can't initialize a Point with {}".format(args)
        
        if len(args) == 1:
            event = args[0]
            self.x = event.x
            self.y = event.y
        else:
            x, y = args[0], args[1]
            self.x = x
            self.y = y
    
    def __repr__(self):
        return 'Point({}, {})'.format(self.x, self.y)
    
    def __add__(self, other):
        """Add: self + other."""
        try:
            return Point(self.x + other.x, self.y + other.y)
        except AttributeError:
            return self + Point(*other)

    def __sub__(self, other):
        """Subtract: self - other."""
        try:
            return Point(self.x - other.x, self.y - other.y)
        except AttributeError:
            return self - Point(*other)

    def __iadd__(self, other):
        """Incremental addition."""
        return self + other

    def __mul__(self, other):
        """Multiply the vector by a number, or do a scalar product 
        of two vectors.
        
        The method chooses which operation to perform according to 
        the arguments provided.
        """
        if type(other) in (int, float):
            # multiplication of the vector by a number
            return Point(self.x * other, self.y * other)
        else:
            # scalar product of vectors
            try:
                return self.x * other.x + self.y * other.y
            except AttributeError:
                return self * Point(*other)
    
    def __rmul__(self, other):
        """Right multiplication: other * self."""  
        return self.__mul__(other)

    def projectOn(self, other):
        """Projection of 'self' into a direction of a unit vector 'other'.
        
        Arguments:
        other -- 2-tuple 
        """
        other = Point(*other)
        scalProduct = self.x * other.x + self.y * other.y
        return scalProduct * other
    
    def __complex__(self):
        """Type conversion to a complex number."""
        return self.x + 1j*self.y
    
    def rotate(self, alpha, center=None):
        """Rotate the point by angle alpha around a given center.
        
        Arguments:
        center [Point] - the axis of rotation
        alpha [float] - angle in radians
        """
        if not center: center = Point(0, 0) 
        cSelf = complex(self)
        cCenter = complex(center)
        
        phaseFactor = cmath.exp(alpha*1j)
        cRotatedPoint = phaseFactor * (cSelf - cCenter) + cCenter
        return Point(cRotatedPoint.real, cRotatedPoint.imag)
    
    def getAngle(self, center):
        """Return the point's angel coord with respect to a given center."""
        return cmath.phase(complex(self) - complex(center))



        
