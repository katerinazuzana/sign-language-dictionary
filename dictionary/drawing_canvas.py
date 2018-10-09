from tkinter import *
import math, cmath


class DrawingCanvas(Canvas):
    """A canvas used to select an eliptic area on the background picture.
    
    An ellipse can be draw on the canvas. The ellipse can then be moved, 
    resized and rotated.
    """
    
    def __init__(self, parent, **options):
        super().__init__(parent, **options)
        self.settings = {'width': 3,          # ellipse settings
                         'outline': 'red', 
                         'fill': 'gray90'}
        
        self.markSize = 3   # half side of a square, or a radius
        self.scMarkSettings = {'width': 1, 
                               'outline': 'darkgreen', 
                               'fill': 'green'}
        self.rotMarkSettings = {'width': 1, 
                                'fill': 'black'}
                                
        self.markNames = ['r', 'tr', 't', 'tl', 'l', 'bl', 'b', 'br']
        self.cursorShapes = ['right_side', 
                             'top_right_corner', 
                             'top_side', 
                             'top_left_corner', 
                             'left_side', 
                             'bottom_left_corner', 
                             'bottom_side',
                             'bottom_right_corner']
        self.numShapes = len(self.cursorShapes)
        
        self.markIds = {}     # mark items drawn on canvas  
        self.id = None     # id of the ellipse draw on canvas
        self.ellipse = None     # ellipse object
        
        self.drawMode = True
        self.scaleMode = False
        self.rotateMode = False

        self.bind('<ButtonPress-1>', self.onPress)
        self.bind('<B1-Motion>', self.onMotion)
        self.bind('<ButtonRelease-1>', self.onRelease)
        self.bind('<Double-Button-1>', self.onDoubleClick)
    
    def onPress(self, event):
        """Remember the topleft corner of a rect. encapsulating the ellipse."""
        if self.drawMode:
            self.topLeft = Vect(event)
    
    def onMotion(self, event):
        """Draw an ellipse according to the mouse movement."""
        if self.drawMode:
            # draw an ellipse
            if self.id: self.delete(self.id)
            self.id = self.create_oval(self.topLeft.x, 
                                       self.topLeft.y, 
                                       event.x, event.y, 
                                       **self.settings, 
                                       tags='ellipse')
        
    def onRelease(self, event):
        """Create an Ellipse object and set the ellipse bindings."""
        if self.drawMode: 
            # create an ellipse object
            bottomRight = Vect(event)
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
        """On ellipse double-click, change the mode between scale and rotate."""
        if self.id in self.find_withtag(CURRENT):
            # if mouse is over the ellipse:  
            if self.scaleMode: self.switchToRotateMode()
            else: self.switchToScaleMode()

    def switchToRotateMode(self):
        """Switch to rotate mode and redraw the marks accordingly."""
        self.scaleMode = False               
        self.rotateMode = True
        self.delete('marks')
        self.drawMarks(mode='rotate')

    def switchToScaleMode(self):
        """Switch to scale mode and redraw the marks accordingly."""   
        self.rotateMode = False               
        self.scaleMode = True
        self.delete('marks')
        self.drawMarks(mode='scale')
    
    def drawMarks(self, mode):
        """Draw the scaling/rotation marks of the ellipse and 
        set the corresponding bindings.
        
        Arguments:
            mode (str): takes a value of 'scale' or 'rotate' to diferentiate 
                between scaling and rotating marks
        """
        if mode == 'scale':
            createFcn = self.create_rectangle
            settings = self.scMarkSettings
            # update the dict with cursor shapes according to current angle
            self.calcShapesDict()
            
        elif mode == 'rotate':
            createFcn = self.create_oval
            settings = self.rotMarkSettings
    
        for mark, position in self.ellipse.markCoords.items():
            # draw the mark
            topLeft = position - (self.markSize, self.markSize)
            bottomRight = position + (self.markSize, self.markSize)  
            markId = createFcn(topLeft.x, topLeft.y, 
                               bottomRight.x, bottomRight.y, 
                               **settings, 
                               tags='marks')
            self.markIds[mark] = markId
            
            if mode == 'scale':
                # change the cursor shape when over the mark
                def onEnter(mark):
                    return lambda ev: self.config(cursor= 
                                                  self.scMarkCursors[mark])
                self.tag_bind(markId, '<Enter>', onEnter(mark))
                # on mark press start scaling of the ellipse
                def onPress(mark):
                    return lambda ev: self.startScale(ev, mark)
                self.tag_bind(markId, '<ButtonPress-1>', onPress(mark))
            
        if mode == 'rotate':
            # set the cursor shape over the rotation marks
            self.tag_bind('marks', '<Enter>', 
                                   lambda ev: self.config(cursor='exchange'))
            # on mark press start rotation of the ellipse
            self.tag_bind('marks', '<ButtonPress-1>', self.startRotate)
            
        self.tag_bind('marks', '<Leave>', lambda ev: self.config(cursor=''))
    
    def calcShapesDict(self):
        """Calculate the dictionary with cursor shapes according to 
        current angle of the ellipse.
        
        These cursor shapes are used over the scaling marks.
        There are 'self.numShapes'=8 different directions in which the 
        mouse cursor arrow can point. When the ellipse is in a rotated 
        position, the cursor shapes are rotated as well, so that for 
        example the top-most mark still gets the up-pointing cursor.
        """
        
        # divide the full 2pi angle into 'self.numShapes' number of segments
        # and find out in which segment the ellipse angle resides
        segmentSize = 2*math.pi / self.numShapes   # pi/4
        segmentNumber = (self.ellipse.angle + segmentSize/2) // segmentSize
                        # (angle + pi/8) // (pi/4)
        
        # create a shifted list of shapes, where all the shapes are shifted 
        # with respect to the initial 'self.cursorShapes' list by the number 
        # of positions equal to the segmentNumber
        rotatedShapes = []
        for i in range(self.numShapes):
            shape = self.cursorShapes[int((i - segmentNumber) % self.numShapes)]
            rotatedShapes.append(shape)
            
        self.scMarkCursors = dict(zip(self.markNames, rotatedShapes))
    
    def startMove(self, event):
        """Remember the start point and set bindings to move the ellipse."""
        self.startPoint = Vect(event)
        self.bind('<B1-Motion>', self.doMove)
        self.bind('<ButtonRelease-1>', self.stopMove)
    
    def doMove(self, event):
        """Recalculate the ellipse parameters and redraw the items on canvas."""
        endPoint = Vect(event)
        shift = endPoint - self.startPoint
        self.ellipse.recalcCornersOnMove(shift)
        self.ellipse.calcMarkCoords()
                
        self.redrawItems()
        self.startPoint = Vect(event)
    
    def stopMove(self, event):
        """Reset the bindings to state before moving the ellipse."""
        self.bind('<B1-Motion>', self.onMotion)
        self.bind('<ButtonRelease-1>', self.onRelease)
            
    def startScale(self, event, mark):
        """Remember the start point and the mark that is being dragged. 
        Set the bindings.
        """
        self.startPoint = Vect(event)
        self.movingMark = mark
        
        # make cursor keep the same shape during whole scaling
        # even when it moves out of the mark
        self.config(cursor = self.scMarkCursors[mark])
        self.tag_unbind(self.markIds[mark], '<Leave>')
        
        self.bind('<B1-Motion>', self.doScale)
        self.bind('<ButtonRelease-1>', self.stopScale)
    
    def doScale(self, event):
        """Recalculate the ellipse parameters and redraw the items on canvas."""
        endPoint = Vect(event)
        mouseMove = endPoint - self.startPoint
        self.ellipse.recalcCornersOnScale(mouseMove, self.movingMark)
        self.ellipse.calcMarkCoords()
        
        self.redrawItems()
        self.startPoint = Vect(event)
    
    def stopScale(self, event):
        """Reset cursor shape and bindings to state before scaling."""
        # reset the cursor shape
        self.config(cursor='')
        self.tag_bind(self.markIds[self.movingMark], '<Leave>', 
                      lambda ev: self.config(cursor=''))
        # set the bindings to the initial ones
        self.bind('<B1-Motion>', self.onMotion)
        self.bind('<ButtonRelease-1>', self.onRelease)
    
    def startRotate(self, event):
        """Remember the start point and set the bindings."""    
        self.startPoint = Vect(event)
        
        # make the cursor keep the same shape during the rotation
        # even when it moves out of the mark
        self.config(cursor = 'exchange')
        self.tag_unbind('marks', '<Leave>')
        
        self.bind('<B1-Motion>', self.doRotate)
        self.bind('<ButtonRelease-1>', self.stopRotate)
    
    def doRotate(self, event):
        """Recalculate the ellipse parameters and redraw the items on canvas."""
        # calculate the angle difference
        startAngle = self.startPoint.getAngle(self.ellipse.center)
        endAngle = Vect(event).getAngle(self.ellipse.center)
        diffAngle = endAngle - startAngle
        
        # update the parameters of the ellipse
        self.ellipse.changeAngle(diffAngle)
        self.ellipse.calcMarkCoords()
        
        self.redrawItems()
        self.startPoint = Vect(event)
    
    def stopRotate(self, event):
        """Reset cursor shape and bindings to state before rotation."""
        # reset the cursor shape
        self.config(cursor='')
        self.tag_bind('marks', '<Leave>', lambda ev: self.config(cursor=''))
        # set the bindings to the initial ones
        self.bind('<B1-Motion>', self.onMotion)
        self.bind('<ButtonRelease-1>', self.onRelease)    
    
    def redrawItems(self):
        """Redraw the ellipse and the scaling/rotation marks.
        
        If the angle of the ellipse rotation is zero (i.e. the ellipse 
        is horizontal) draw it as an oval, otherwise draw it as a polygon.
        """
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
    
    def getPolygonPoints(self, steps=100):
        """Get coordinates of points placed around the ellipse border.
        
        Arguments:
            steps (int): the number of points (default 100)
        Returns:
            a tuple of points' coords: (x0, y0, x1, y1, ...)
        """
        points = []
        for i in range(steps):
            # the angle for this step
            theta = 2 * math.pi * float(i) / steps
            
            point = self.ellipse.center + math.cos(theta) * self.ellipse.a + \
                                          math.sin(theta) * self.ellipse.b
            points.append(point.x)
            points.append(point.y)        
        return tuple(points)    
    

class Ellipse():
    """A class that keeps track of the parameters defining position and 
    size of an ellipse, as well as positions of the scale/rotate marks.
    
    Attributes:
        topLeft (Vect): top left point of rectangle encapsulating the ellipse
        bottomRight (Vect): bottom right point of the rectangle
        angle (float): angle of rotation of the ellipse (its major axis)
            in the (x, y) coord system of the canvas; 
            takes values from interval [0, 2 pi)
        center (Vect): the center of the ellipse
        a (Vect): major semi-axis
        b (Vect): minor semi-axis
        markCoords (dict): a dictionary of form {mark-name: mark-position}
            where: mark-name (str), mark-position (Vect)
    """
    
    def __init__(self, topLeft, bottomRight):
        """Initialize an ellipse object.
        
        At the time of creation, the ellipse is horizontal (the major 
        axis parallel to the x-axis of the canvas).
        
        Arguments:
            topLeft (Vect): top left point of rect. encapsulating the ellipse
            bottomRight (Vect): bottom right point of the rectangle
        """
    
        self.topLeft = topLeft
        self.bottomRight = bottomRight
        self.angle = 0
        self.markCoords = {}
        
        # calculate initial values of parameters and positions of marks
        self.calcMarkCoords()
    
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
    
    def calcParams(self):
        """Calculate the ellipse parameters.
        
        Calculate the 'center', 'a', and 'b' parameters 
        from 'topLeft', 'bottomRight', and 'angle'.
        """
        self.center = (self.topLeft + self.bottomRight) / 2
        ab = self.bottomRight - self.center # ab = self.a + self.b
        
        # direction of major and minor axes
        dirA = Vect(math.cos(self.angle), math.sin(self.angle))
        dirB = Vect(- math.sin(self.angle), math.cos(self.angle))
        
        self.a = ab.projectOn(dirA)
        self.b = ab.projectOn(dirB)        
    
    def recalcCornersOnMove(self, shift):
        """Recalculate the coords of the topLeft and bottomRight corners 
        when the ellipse has been moved.
        
        Arguments:
            shift (Vect): a vector by which the ellipse has been moved
        """
        self.topLeft += shift
        self.bottomRight += shift
        
    def recalcCornersOnScale(self, mouseMove, movingMark):
        """Recalculate the coords of the topLeft and bottomRight corners 
        when the ellipse has been scaled.
        
        Arguments:
            mouseMove (Vect): a vector by which the mouse cursor has been moved
            movingMark (str): name of the mark that has beed dragged
        """
        
        # movement parallel to the major axis                
        if movingMark == 'r':
            self.bottomRight += mouseMove.projectOn(self.a)
        elif movingMark == 'l':
            self.topLeft += mouseMove.projectOn(self.a)
        
        # movement parallel to the minor axis                      
        elif movingMark == 't':
            self.topLeft += mouseMove.projectOn(self.b)
        elif movingMark == 'b':
            self.bottomRight += mouseMove.projectOn(self.b)
        
        # a corner mark is moving            
        elif movingMark == 'tr':
            self.topLeft += mouseMove.projectOn(self.b)
            self.bottomRight += mouseMove.projectOn(self.a)
        elif movingMark == 'bl':
            self.bottomRight += mouseMove.projectOn(self.b)
            self.topLeft += mouseMove.projectOn(self.a)    
        elif movingMark == 'tl':
            self.topLeft += mouseMove
        elif movingMark == 'br':
            self.bottomRight += mouseMove
    
    def changeAngle(self, diffAngle):
        """Update the 'angle', 'topLeft', and 'bottomRight' parameters 
        when the ellipse has been rotated.
        
        Arguments:
            diffAngle (float): angle by which the ellipse has been rotated
        """
        self.angle = (self.angle + diffAngle) % (2 * math.pi)
        self.topLeft = self.topLeft.rotate(diffAngle, self.center)
        self.bottomRight = self.bottomRight.rotate(diffAngle, self.center)  

    def __str__(self):
        return 'Ellipse: center = {}, a = {}, b = {}, angle = {}'.format(
                self.center, self.a, self.b, self.angle)


class Vect():
    """A class representing a vector in 2D plane.
    
    A vector may be regarded as representing a point in plane as well. 
    (the point = endpoint of the vector)
    
    Attributes:
        x (float): x coordinate
        y (float): y coordinate
    """
    
    def __init__(self, *args):
        """Initialize a Vect object.
        
        Arguments:
            *args: may be either 
                one argument - i.e. an object that has some
                               'x' and 'y' attributes
                or two arguments - i.e. the x and y coords
        """
        assert len(args) in (1, 2), \
               "Can't initialize a Vect with {}".format(args)
        
        if len(args) == 1:
            event = args[0]
            self.x = event.x
            self.y = event.y
        else:
            x, y = args[0], args[1]
            self.x = x
            self.y = y
    
    def __add__(self, other):
        """Add 'self' and 'other'.
         
        'other' might be of type Vect, 2-tuple.
        """
        try:
            return Vect(self.x + other.x, self.y + other.y)
        except AttributeError:
            return self + Vect(*other)

    def __sub__(self, other):
        """Subtract 'other' from 'self'.
        
        'other' might be of type Vect, 2-tuple.
        """
        try:
            return Vect(self.x - other.x, self.y - other.y)
        except AttributeError:
            return self - Vect(*other)

    def __iadd__(self, other):
        """Incremental addition."""
        return self + other

    def __mul__(self, other):
        """Multiply the 'self' vector by a number 'other'."""
        return Vect(self.x * other, self.y * other)
    
    def __rmul__(self, other):
        """Right multiplication: other * self."""  
        return self * other

    def __truediv__(self, other):
        """Division of the 'self' vector by the number 'other'."""
        return Vect(self.x / other, self.y / other)

    def __complex__(self):
        """Type conversion to a complex number."""
        return self.x + 1j*self.y
    
    def __abs__(self):
        """Return the length of the vector."""
        return abs(complex(self))

    def __repr__(self):
        return 'Vect({}, {})'.format(self.x, self.y)
    
    def scalProd(self, vect):
        """Return a scalar product with another vector."""
        return self.x * vect.x + self.y * vect.y

    def projectOn(self, vect):
        """Othogonal projection of 'self' into the direction of 'vect'.
        
        Arguments:
            vect (Vect) 
        """
        unitVect = vect / abs(vect)
        scalProduct = self.scalProd(unitVect)
        return scalProduct * unitVect
    
    def getAngle(self, origin):
        """Return the angel coordinate of a point repesented by 'self' vector
        with respect to a given origin."""
        
        return cmath.phase(complex(self) - complex(origin)) % (2 * math.pi)
    
    def rotate(self, alpha, center=None):
        """Rotate the point represented by 'self' vector by angle alpha 
        around a given center.
        
        Arguments:
            alpha (float): angle in radians
            center (Vect): the axis of rotation (default is None),
                if not provided, the axis eventually defaults to Vect(0, 0)
        """
        if not center: center = Vect(0, 0) 
        cSelf = complex(self)
        cCenter = complex(center)
        
        phaseFactor = cmath.exp(alpha*1j)
        cRotatedPoint = phaseFactor * (cSelf - cCenter) + cCenter
        return Vect(cRotatedPoint.real, cRotatedPoint.imag)

