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
        self.rotMarkSettings = {'width': 1, 
                                'outline': 'black', 
                                'fill': 'black'}
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
            # remember the topleft corner of rectangle encapsulating the ellipse
            self.topLeft = event
    
    def onMove(self, event):
        """
        """
        if self.drawMode:
            # draw an ellipse
            if self.id: self.delete(self.id)
            self.id = self.create_oval(self.start.x, self.start.y, 
                                       event.x, event.y, 
                                       **self.settings, 
                                       tags='ellipse')
        elif self.moveMode:
            if self.id in self.find_withtag('ellipse'):
                # if ellipse is under mouse cursor:
                
                # change the ellipse' topLeft and bottomRight points
                self.recalcCornersOnMove(event)
                
                # recalculate the marks' positions
                self.ellipse.calcMarkCoords()
                
                # redraw the ellipse
                self.delete(self.id)
                self.id = self.create_oval(self.ellipse.topLeft.x, 
                                           self.ellipse.topLeft.y, 
                                           self.ellipse.bottomRight.x, 
                                           self.ellipse.bottomRight.y, 
                                           **self.settings, 
                                           tags='ellipse')
                
                # redraw the marks
                self.delete('marks')
                self.drawMarks(mode='scale')
                
                # reset start point
                self.start = event
        
    def onRelease(self, event):
        if self.drawMode:
            
            # create an ellipse object
            bottomRight = event
            self.ellipse = Ellipse(Point(self.topLeft), Point(bottomRight))
            
            # convert ellipse representation from oval to polygon
#            polygon = self.ovalToPolygon(self.ellipse)
#            self.delete(self.id) # delete oval
#            self.id = polygon
            
            # set cursor
            self.tag_bind('ellipse', '<Enter>', 
                                     lambda ev: self.config(cursor='fleur'))
            self.tag_bind('ellipse', '<Leave>', 
                                     lambda ev: self.config(cursor=''))
            
            # change mode
            self.drawMode = False
            self.moveMode = True
            self.switchToScaleMode()

    def recalcCornersOnMove(self, event):
        """Recalculate the coords of the topLeft and bottomRight corners."""

        shift = Point(event) - Point(self.start)
        self.ellipse.topLeft += shift
        self.ellipse.bottomRight += shift

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
            settings = self.scMarkSettings
        elif mode == 'rotate':
            settings = self.rotMarkSettings
    
        for mark, position in self.ellipse.markCoords.items():
            topLeft = position - (self.markSize, self.markSize)
            bottomRight = position + (self.markSize, self.markSize)
            
            markId = self.create_rectangle(topLeft.x, topLeft.y, 
                                           bottomRight.x, bottomRight.y, 
                                           **settings, 
                                           tags='marks')
            self.markIds[mark] = markId
            
            def onEnter(mark):
                return lambda ev: self.config(cursor = self.scMarkCursors[mark])
            self.tag_bind(markId, '<Enter>', onEnter(mark))
            
            self.tag_bind(markId, '<Leave>', 
                          lambda ev: self.config(cursor = ''))
    
            def onPress(mark):
                return lambda ev: self.startScale(ev, mark)
            self.tag_bind(markId, '<ButtonPress-1>', onPress(mark))

    def startScale(self, event, mark):
        
        self.start = event
        self.movingMark = mark
        
        # make cursor keep the same shape during whole scaling
        # even when it moves out of the mark
        self.config(cursor = self.scMarkCursors[mark])
        self.tag_unbind(self.markIds[mark], '<Leave>')
        
        self.bind('<B1-Motion>', self.doScale)
        self.bind('<ButtonRelease-1>', self.stopScale)
    
    def doScale(self, event):
        
        # change the ellipse' topLeft and bottomRight points
        self.recalcCornersOnScale(event)
        
        # recalculate the marks' positions
        self.ellipse.calcMarkCoords()
                
        # redraw the ellipse
        self.delete(self.id)
        self.id = self.create_oval(self.ellipse.topLeft.x, 
                                   self.ellipse.topLeft.y, 
                                   self.ellipse.bottomRight.x, 
                                   self.ellipse.bottomRight.y, 
                                   **self.settings, 
                                   tags='ellipse')
        
        # redraw the marks
        self.delete('marks')
        self.drawMarks(mode='scale')
        
        # reset start point
        self.start = event
    
    def stopScale(self, event):

        # reset the cursor shape
        self.config(cursor = '')
        self.tag_bind(self.markIds[self.movingMark], '<Leave>', 
                      lambda ev: self.config(cursor = ''))        
        # set the bindings to the initial ones
        self.bind('<B1-Motion>', self.onMove)
        self.bind('<ButtonRelease-1>', self.onRelease)
    
    def ovalToPolygon(self, ellipse, steps=40):
        """
        better keep the number of steps a multiple of four
        to ensure precise values for the ellipse parameters
        """
        points = []
        for i in range(steps):
            # calculate the angle for this step
            theta = 2 * math.pi * float(i) / steps

            x = ellipse.center.x + ellipse.a * math.cos(theta)
            y = ellipse.center.y + ellipse.b * math.sin(theta)

            points.append(round(x))
            points.append(round(y))
        
        return self.create_polygon(tuple(points), **self.settings)
        
    def recalcCornersOnScale(self, event):
        """Recalculate the coords of the topLeft and bottomRight corners."""
        
        mouseMove = Point(event) - Point(self.start)
        
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
        
        # calculate initial positions of scale marks (ellipse not rotated)
        self.markCoords = {}
        self.calcMarkCoords()
    
    def calcParams(self):
        """Calculate the ellipse parameters."""
        
        self.center = (self.topLeft + self.bottomRight) // 2
        self.ab = self.bottomRight - self.center
        self.a = self.ab.projectOn((1, 0))
        self.b = self.ab.projectOn((0, 1))
        self.angle = 0
        
    def calcMarkCoords(self):
        """Calculate the coords of the scaling/rotating marks."""
        
        self.calcParams()
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
    
    The coordinates of the point are integers.
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
            self.x = int(x)
            self.y = int(y)
    
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

    def __floordiv__(self, other):
        return Point(self.x // other, self.y // other)

    def __mul__(self, other):
        """Multiply the vector by a number, or do a scalar product 
        of two vectors.
        
        The method chooses which operation to perform according to 
        the arguments provided.
        """
        if type(other) in (int, float):
            # multiplication of the vector by a number
            return Point(round(self.x * other), round(self.y * other))
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
        """Projection of self on other."""
        return (self * Point(*other)) * Point(*other)
    



        
