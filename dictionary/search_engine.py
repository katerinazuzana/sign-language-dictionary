import sqlite3
import os
import math
from difflib import SequenceMatcher
from drawing_canvas import Point


class SearchEngine():

    def __init__(self, dbpath, vfdir, altsmax):
        self.dbpath = dbpath
        self.vfdir = vfdir
        self.altsmax = altsmax
        
        self.allwords = []
        self.showResultFcn = None

        # create a list of video file names for searching with unknown suffix
        # used in findVideoFile() method
        self.vflist = os.listdir(self.vfdir)
        
        self.allsigns = []
        self.signsmax = 10
        self.groups = {1: 'I', 2: 'I', 3: 'I', 4: 'I', 5: 'I', 
                       6: 'II', 7: 'II', 8: 'II', 9: 'III', 10: 'III', 
                       11: 'III', 12: 'IV', 13: 'IV', 14: 'IV', 15: 'III', 
                       16: 'III', 17: 'IV', 18: 'III', 19: 'III', 20: 'IV', 
                       21: 'II', 22: 'V', 23: 'V', 24: 'V', 25: 'V', 
                       26: 'VI', 27: 'VI', 28: 'VII', 29: 'VII', 30: 'VII', 
                       31: 'VII', 32: 'VII', 33: 'VII', 34: 'VII', 35: 'VII',
                       36: 'VIII', 37: 'VIII', 38: 'VIII', 39: 'VIII', 
                       40: 'VIII', 41: 'IX', 42: 'IX', 43: 'IX', 44: 'IX', 
                       45: 'IX', 46: 'IX', 47: 'IX', 48: 'X', 49: 'XI', 
                       50: 'XI', 51: 'XII'}
                       # all the possible 51 hand shapes are divided into 
                       # 12 groups of visually similar shapes (roman nums I-XII)
                       
        self.width = 240    # canvas width
        self.height = 250   # canvas height

    def search(self, lookupword):
        """Search for the given word in the database.        
        Call a function to display the result.
        Arguments:
        lookupword -- [str] the word to be looked up
        Returns:
        None
        """
        with sqlite3.connect(self.dbpath) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT word, videofile FROM translation WHERE \
                            lower(word)=lower(?)', (lookupword,))
            find = cursor.fetchall() # returns a list of tuples
        
        if find != []:
            # the word was found
            find = self.addSuffixes(find)
            # call fct to show the result            
            self.showResultFcn((True, find))
                          
        else:
            # the word was not found
            # search the database for similar words
            altoptions = self.findAltOpts(lookupword)       
            # call fct to show the result            
            self.showResultFcn((False, altoptions))
        
    def findVideoFile(self, videofile):
        """Return the full name of a video file, including suffix.
        
        Arguments:
        videofile -- [str] name of a video file without suffix
        """
        for vf in self.vflist:
            if vf.startswith(videofile + '.'):
                videosource = os.path.join(self.vfdir, vf)
                return videosource

    def addSuffixes(self, alist):
        """Find the full names (including suffix) of the video files
        in a given list and rewrite the videofile names so that they 
        contain a suffix.
        
        Arguments:
        alist [list] -- items take form (word [str], videofile [str])
        """
            
        for i, (word, filename) in enumerate(alist):
            withsuffix = self.findVideoFile(filename)
            alist[i] = (word, withsuffix)
        return alist

    def findAltOpts(self, lookupword):
        """Find words that have the longest common substrings with lookupword. 
        """
        if self.allwords == []:
            # on first call of findAltOpts()
            # create a list of all the words contained in the database
            with sqlite3.connect(self.dbpath) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT word FROM words')
                allwords = cursor.fetchall()
            self.allwords = self.listOfTuplesToList(allwords)
        
        altopts = []    # to collect words that have the longest common
                        # substrings with the lookupword
        lengths = []    # lengths[i] is the length of the longest common
                        # substring of altopts[i] and the lookupword
        for word in self.allwords:
            match = SequenceMatcher(None, 
                                    lookupword, 
                                    word
                                    ).find_longest_match(0, len(lookupword),
                                                         0, len(word))

            if len(altopts) < self.altsmax and match.size >= 3:
                altopts.append(word)
                lengths.append(match.size)
            elif lengths != [] and match.size > lengths[-1]:
                # current word is a better match than the last item of altopts
                # insert the word into altopts and delete the altopts' last item
                for i in range(len(lengths)):
                    if lengths[i] < match.size:
                        index = i
                altopts.insert(index, word)
                lengths.insert(index, match.size)
                del altopts[-1]
                del lengths[-1]
        return altopts

    def listOfTuplesToList(self, listOfTuples):    
        """Convert a list of tuples into a simple list of tuple[0] items."""
        res = []
        for item in listOfTuples:
            res.append(item[0])
        return res
  
    def signSearch(self, *userSign):
        """Search the database for signs similar to the sign from the user 
        input.
        
        Take a list of all the signs in the database, where each item of the
        list contains also information about the sign type and the sign
        components - hand shapes and placement.
        
        Go through all the database signs and for each of them calculate 
        an abstract distance between the sign provided by the user
        and the sign from the database. The distance is measured in a 3D 
        space, where the axes correspond to:
        - active hand's shape
        - sign type
        - sign placement
         
        Along each of the three axes, the distance can take a value from 
        interval [0, 1]. (0 - the components match perfectly, 1 - the 
        components are completely different)
        
        Active Hand Shape dimension:
        There is a set of shapes from the user and a set of shapes from the 
        database. The more these two sets are similar, the shorter the distance
        is. We distinguish the cases where the hand shapes are exactly the same 
        (leading to a shorter distance), and the cases where the shapes are
        similar, i.e. belong to the same group (leads to a longer distance).
        
        Sign Type dimension:
        There are three possible types: 'single hand', 'both the same' and 
        'passive hand'. If the type of the user's sign is the same as the type 
        of the sign from the database, the distance is zero, otherwise it's 1.
        There's one exception: when both the user's and the database signs'
        type is 'passive hand', but the user and the db provide different 
        passive hand shape number (uPassiveShape and dbPassiveShape values), 
        the distance is 0.5.
        
        Sign Placement dimension:
        The placement of a sign is given by an elliptic area on a canvas
        (see drawing_canvas.py). The distance between two signs is calculated
        as a ratio of an area where the two ellipses overlap (counted twice -
        once for each ellipse) to the total area of the ellipses.
        
        After calculating the distance for all the database signs, choose the
        'self.signsmax' number of the closest signs as a result of the search.
        When the search is done, call 'self.showSignsFcn' to display it in 
        the application's 'mainfrm' frame.
        
        Arguments:
        *userSign -- a tuple that unpacks into:
        uActiveShape [tuple of ints] -- describes the shape of the active hand
        uSignType [str] -- a string describing the type of the sign, takes one
                           of the values: 'single hand', 
                                          'both the same', 
                                          'passive hand'
        uPassiveShape [int] -- a number describing the shape of the passive hand
        uPlacement [tuple] -- a tuple of floats of the form 
                              [centerx, centery, a , b, angle]
                              describing the sign's placement
        """
        
        # unpack the user's sign input
        uActiveShape, uSignType, uPassiveShape, uPlacemet = *userSign
        
        uActiveShapes = set(uActiveShapes) # a set of ints
        uShapeGroups = set(self.groups[shape] for shape in uActiveShapes 
                           if shape != 0) # a set of strings
        
        # used for comparing the signs placement
        uRelief = self.getReliefFcn(*uPlacement)
        uArea = self.integrateOverCanvas(uRelief)
        
        
        if self.allsigns == []:
            # create a list of all the signs in the database - a list of tuples:
            # (videofile, activeShape, signType, passiveShape, placement)
            with sqlite3.connect(self.dbpath) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM signs')
                allsigns = cursor.fetchall()

        result = []        
        
        for dbSign in allsigns: 
            # unpack the dbSign's components
            videofile, dbActiveShape, dbSignType, dbPassiveShape, dbPlacemet \
            = *dbSign
            
            # dbActiveShape is a str of comma separated numbers -> change to set
            dbActiveShape = set(int(item) for item in dbActiveShape.split(','))
            dbShapeGroups = set(self.groups[shape] for shape in dbActiveShapes)
            
            # change dbPlacement from str "centerx,centery,a,b,angle" to tuple
            dbPlacement = tuple(float(item) for item in dbPlacement.split(','))
            
            
            # distance in the Active Hand Shape dimension
            actDist = self.calcActDist(uActiveShape, uShapeGroups, 
                                       dbActiveShape, dbShapeGroups)
                        
            # distance in the Sign Type dimension - dbPassiveShape-is type int?
            typeDist = self.calcTypeDist(uSignType, uPassiveShape, 
                                         dbSignType, dbPassiveShape)
            
            # distance in the Sign Placement dimension
            placeDist = self.calcPlaceDist(uRelief, uArea, dbPlacement)
            
            # the total distance
            dist  = math.sqrt(actDist**2 + typeDist**2 + placeDist**2)
             
            result.append((videofile, dist))

        # choose the first 'self.signmax' closest signs
        result = sorted(result, key = lambda x: x[1])
        result = result[:self.signsmax]
        # remove the distance values
        result = self.listOfTuplesToList(result)
        # demo result:
        result = ['bezecke_lyzovani.mp4', 
                  'biatlon.mp4', 
                  'bowling.mp4', 
                  'bolivie.mp4', 
                  'box.mp4', 
                  'cerna_hora.mp4', 
                  'cesko.mp4', 
                  'brazilie_2.mp4']
                  
        # find the words corresponding to individual videofiles
        for i, videofile in enumerate(result):
            with sqlite3.connect(self.dbpath) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT word FROM translation WHERE \
                               videofile=?', (videofile,))
                words = cursor.fetchall()
            text = ', '.join(self.listOfTuplesToList(words))
            result[i] = (text, videofile)
        # add suffixes
        result = addSuffixes(result)
        
        # add success flag
        res = (True, result)
        # show the result
        self.showResultFcn(res)


    def calcActDist(self, uShape, uGroups, dbShape, dbGroups):
        """Calculate the distance between the uSign and the dbSign in the
        Active Hand Shape dimension.
        
        Arguments:
        uShape [set] -- a set of ints describing the shape of the active hand 
                        of the user's sign
        uGroups [set] -- a set of strings describing the hand shape groups 
                         of the user's sign
        dbShape [set] -- a set of ints describing the shape of the active hand 
                        of the dbSign
        dbGroups [set] -- a set of strings describing the hand shape groups 
                         of the dbSign
        
        Returns:
        a distance [float]
        """
    
        if dbActiveShape == uActiveShape:
            # all the same shapes
            actDist = 0
        elif len(dbActiveShape & uActiveShape) >= 1 and \
             len(dbGroups ^ uGroups) == 0:
            # at least one common shape, other similar shapes
            actDist = 0.25
        elif len(dbGroups ^ uGroups) == 0:
            # all similar shapes
            actDist = 0.5
        elif len(dbGroups & uGroups) >= 1:
            # at least one similar shape
            actDist = 0.75
        else:    
            # all completely different shapes
            actDist = 1
        return actDist

    def calcTypeDist(self, uSignType, uPassiveShape, 
                           dbSignType, dbPassiveShape):
        """Calculate the distance between the uSign and the dbSign in the
        Sign Type dimension.
        
        Arguments:
        uSignType [str] -- one of 'single hand', 'both the same', 'passive hand'
        uPassiveShape [int] -- a number describing the shape of the passive hand
        dbSignType [str]-- one of 'single hand', 'both the same', 'passive hand'
        dbPassiveShape [int]-- a number describing the shape of the passive hand
        
        Returns:
        a distance [float] 
        """
        
        if dbSignType != uSignType:
            # different type
            typeDist = 1
        else:
            # the same type
            if dbSignType == 'passive hand':
                if dbPassiveShape == uPassiveShape:
                    # the same shape
                    typeDist = 0
                else:
                    # different shape
                    typeDist = 0.5
            else:
                # the same type other than 'passive hand'
                typeDist = 0
        return typeDist

    def calcPlaceDist(self, uRelief, uArea, dbPlacement):
        """Calculate the distance between the uSign and the dbSign in the
        Placement dimension.
        
        The distance is calculated as a ratio of the overlapping area (counted
        twice - once for each ellipse) to the total area of the ellipses.
        
        Arguments:
        uRelief [function] -- fcn of canvas coords describing the user's ellipse
        uArea [int] -- the area af the user's ellipse
        dbPlacement [list] -- a list of floats of the form 
                              [centerx, centery, a , b, angle]
                              describing the dbSign's placement
                              
        Returns:
        a distance [float] 
        """
        
        # area of the db ellipse
        dbRelief = self.getReliefFcn(*dbPlacement)
        dbArea = self.integrateOverCanvas(dbRelief)
        
        # overlap of the two ellipses
        fcn = lambda x, y: uRelief(x, y) * dbRelief(x, y)
        overlap = self.integrateOverCanvas(fcn)
        
        placeDist = (2 * overlap) / (uArea + dbArea)
        return placeDist

    def integrateOverCanvas(self, fcn):
        """Integrate the function over the canvas area."""
        
        integral = 0
        for x in range(self.width):
            for y in range(self.height):
                integral += fcn(x, y)
        return integral

    def getReliefFcn(self, centerx, centery, a, b, angle):
        """Return a function of canvas coords that describes an elliptic area.
        
        Arguments:
        centerx [float] -- x coord of the elipse center
        centery [float] -- y coord of the elipse center
        a [float] -- major semi-axis length
        b [float] -- minor semi-axis lenght
        angle [float] -- angle of rotation of the ellipse
        
        Returns:
        a function of two float args that returns 1 for points inside 
        the elliptic area, and 0 for points outside of it:
        f(x, y) = 1     for (x, y) inside the ellipse
        f(x, y) = 0     for (x, y) outside the ellipse
        """       
        
        def f(x, y):
            center = Point(centerx, centery)
            point = Point(x, y)
            # angle coord of the point with respect to the ellipse center:
            phi = point.getAngle(center)
            # radial coord of the point with respect to the ellipse center:
            r = abs(point - center)
            # radial coord of the ellipse border at angle phi:
            elRadius = math.sqrt(a**2 * math.cos(phi - angle)**2 + 
                                 b**2 * math.sin(phi - angle)**2)
            
            if r <= elRadius:
                # (x, y) is inside
                return 1
            else:
                # (x, y) is outside
                return 0
        return f
    
        






