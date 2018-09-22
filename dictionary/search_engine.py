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
        self.width = 240    # canvas width
        self.height = 250   # canvas height
        self.showSignsFcn = None

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
            # find the full name (including suffix) of the video files
            # and rewrite the videofile names in the find list so that
            # the videofile now contains a suffix
            for i in range(len(find)):
                withsuffix = self.findVideoFile(find[i][1])
                find[i] = (find[i][0], withsuffix)
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
        """Convert a list of 1-tuples into a simple list."""
        res = []
        for item in listOfTuples:
            res.append(item[0])
        return res
  
    def signSearch(self, *userSign):
        """
        
        
        Active Hand Shape dimension:
        The algorithm doesn't take into account the order of the shapes.
        Explain shape groups
        We distinguish the cases where the hand shapes are the same, 
        and the cases where the shapes are similar, i.e. belong to 
        the same group
        
        When the search is done, call 'self.showSignsFcn' to display the result.
        
        uActiveShape [tuple] - (int, int)
        uSignType [str]
        uPassiveShape [int]
        """
        
        # unpack the user's sign input
        uActiveShape, uSignType, uPassiveShape, uPlacemet = *userSign
        
        uActiveShapes = set(uActiveShapes)
        uShapeGroups = set(self.groups[shape] for shape in uActiveShapes 
                           if shape != 0)
        
        uCenterX, uCenterY, uA, uB, uAngle = *uPlacement
        # area of the ellipse from user input
        uRelief = self.getReliefFcn(*uPlacement)
        uArea = self.integrateOverCanvas(uRelief)
        
        
        if self.allsigns == []:
            # create a list of all the signs in the database - a list of tuples:
            # (videofile, activeShape, signType, passiveShape, placement)
            with sqlite3.connect(self.dbpath) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM signs')
                allsigns = cursor.fetchall() # returns a list of tuples

        result = []        
        
        for dbSign in allsigns: 
            # unpack the dbSign's components
            videofile, dbActiveShape, dbSignType, dbPassiveShape, dbPlacemet \
            = *dbSign
            
            # dbActiveShape is a str of comma separated numbers -> change to set
            dbActiveShape = set(dbActiveShape.split(','))
            dbShapeGroups = set(self.groups[shape] for shape in dbActiveShapes)
            
            # change dbPlacement from string "centerx,centery,a,b,angle" to list
            dbPlacement = dbPlacement.split(',')
            
            
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
        result = self.listOfTuplesToList(result)
        self.showSignsFcn(result)


    def calcActDist(self, uShape, uGroups, dbShape, dbGroups):
    
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
        """return a function of canvas coords that describes the elliptic area
        f(x, y) = 1     for (x, y) inside the ellipse
        f(x, y) = 0     for (x, y) outside the ellipse
        """       
        
        def f(x, y):
            
            center = Point(centerx, centery)
            point = Point(x, y)
            # angle coord of the point with respect to the ellipse center
            phi = point.getAngle(center)
            # radial coord of the point with respect to the ellipse center
            r = abs(point - center)
            # radial coord of the ellipse border at angle phi
            elRadius = math.sqrt(a**2 * math.cos(phi - angle)**2 + 
                                 b**2 * math.sin(phi - angle)**2)
            
            if r <= elRadius:
                # (x, y) is inside
                return 1
            else:
                # (x, y) is outside
                return 0
        return f
    
        






