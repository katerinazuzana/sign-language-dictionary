import sqlite3
import os
import math
import numpy as np
from difflib import SequenceMatcher
from drawing_canvas import Vect
import tools


class SearchEngine():
    """A class that provides the logic behind the dictionary application.

    Methods:
        search(lookupword):
            Look up the word in the database. Call a fcn to display the result.
        signSearch(userSign):
            Search the database for signs similar to the sign from user input.
    """

    def __init__(self, dbpath, vfdir, altsmax, canvasSize):
        """Initialize the attributes.

        Arguments:
            dbpath (str): the database file path
            vfdir (str): a path to the directory with video files
            altsmax (int): maximum number of alternative words
            canvasSize (tuple of ints) : size of DrawingCanvas, (width, height)
        """
        self.dbpath = dbpath
        self.vfdir = vfdir
        self.altsmax = altsmax
        self.allwords = []

        # a function that shows the result of the search in the main frame,
        # the function is assigned in main.py after mainfrm is created
        self.showResultFcn = None

        # create a list of video file names for searching with unknown suffix
        # used in findVideoFile() method
        self.vflist = os.listdir(self.vfdir)

        self.allsigns = []
        self.signsmax = 15
        # all the possible 54 handshapes are divided into
        # 11 groups of visually similar shapes (roman nums I-XI)
        self.groups = {1: 'I', 2: 'I', 3: 'I', 4: 'I', 5: 'I',
                       6: 'II', 7: 'II', 8: 'II', 9: 'III', 10: 'III',
                       11: 'IV', 12: 'IV', 13: 'IV', 14: 'III', 15: 'III',
                       16: 'IV', 17: 'III', 18: 'III', 19: 'IV', 20: 'II',
                       21: 'V', 22: 'V', 23: 'V', 24: 'V', 25: 'V',
                       26: 'V', 27: 'V', 28: 'II', 29: 'VI', 30: 'VI',
                       31: 'VI', 32: 'VI', 33: 'VI', 34: 'VI', 35: 'VI',
                       36: 'VI', 37: 'VII', 38: 'VII', 39: 'VII',
                       40: 'VII', 41: 'VII', 42: 'VII', 43: 'VII', 44: 'VII',
                       45: 'VII', 46: 'VII', 47: 'VII', 48: 'VII', 49: 'VIII',
                       50: 'IX', 51: 'IX', 52: 'X', 53: 'XI', 54: 'XI'}

        # length that fits into the label where czech translation is shown
        self.maxTextLength = 42
        self.canvasWidth, self.canvasHeight = canvasSize

    def search(self, lookupword):
        """Look up the word in the database.

        Arguments:
            lookupword (str): the word to be looked up
        Returns:
            2-tuple: (boolean-success-flag, a-list)
        """
        with sqlite3.connect(self.dbpath) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT word, videofile FROM translation WHERE \
                            lower(word)=lower(?)', (lookupword,))
            find = cursor.fetchall()

        if find != []:
            # the word was found
            find = self.addSuffixes(find)
            return (True, find)

        else:
            # the word was not found
            # search the database for similar words
            altoptions = self.findAltOpts(lookupword)
            return (False, altoptions)

    def findVideoFile(self, videofile):
        """Return the full name of a video file, including suffix.

        Arguments:
            videofile (str): name of a video file without suffix
        """
        for vf in self.vflist:
            if vf.startswith(videofile + '.'):
                videosource = os.path.join(self.vfdir, vf)
                return videosource

    def addSuffixes(self, alist):
        """Add suffixes to the videofiles names in 'alist'.

        Find the full names (including suffix) of the video files
        in 'alist' and rewrite the videofile names so that they
        contain a suffix.

        Arguments:
            alist (list): items take form (word (str), videofile (str))
        """
        for i, (word, filename) in enumerate(alist):
            withsuffix = self.findVideoFile(filename)
            alist[i] = (word, withsuffix)
        return alist

    def findAltOpts(self, lookupword):
        """Search the database for words similar to 'lookupword'.

        Find words that have the longest common substrings with 'lookupword'.
        The maximum number of these words is given by 'self.altsmax'.

        Arguments:
            lookupword (str)

        Returns:
            list: a list of expressions (str) that are closest to 'lookupword'
        """
        if self.allwords == []:
            # on first call of findAltOpts()
            # create a list of all the words contained in the database
            with sqlite3.connect(self.dbpath) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT word FROM words')
                allwords = cursor.fetchall()
            self.allwords = tools.listOfTuplesToList(allwords)

        # to collect words that have the longest common
        # substrings with the lookupword
        altopts = []
        # lengths[i] is the length of the longest common
        # substring of altopts[i] and the lookupword
        lengths = []

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
                # insert the word into altopts and delete the altopts last item
                for i in range(len(lengths)):
                    if lengths[i] < match.size:
                        index = i
                altopts.insert(index, word)
                lengths.insert(index, match.size)
                del altopts[-1]
                del lengths[-1]
        return altopts

    def signSearch(self, userSign):
        """Search the database for signs similar to the sign from user input.

        Take a list of all the signs in the database, where each item of the
        list contains also information about the sign type and the sign
        components - handhapes and placement.

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
        is. We distinguish the cases where the handshapes are exactly the same
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
        (see drawing_canvas.py). The distance is calculated using a ratio
        of an area where the two ellipses overlap to the total area of the
        ellipses. The higher the ratio, the shorter the distance.

        After calculating the distance for all the database signs, choose the
        'self.signsmax' number of the closest signs as a result of the search.
        When the search is done, call 'self.showSignsFcn' to display it in
        the application's 'mainfrm' frame.

        Arguments:
            userSign: a tuple of:
                uActiveShape (tuple of ints): describes the shape of the
                    active hand
                uSignType (str): describes the type of the sign, takes one of
                    the values: 'single hand', 'both the same', 'passive hand'
                uPassiveShape (int): describes the shape of the passive hand
                uPlacement (tuple of floats): describes the sign placement,
                    takes the form of (centerx, centery, a , b, angle)
        """

        # unpack the user's sign input
        uActShape, uSignType, uPassiveShape, uPlacement = userSign

        uActiveShape = set(uActShape)  # a set of ints
        if len(uActiveShape) == 2 and (0 in uActiveShape):
            uActiveShape.remove(0)
        uShapeGroups = set(self.groups[shape] for shape in uActiveShape
                           if shape != 0)  # a set of strings

        if uPlacement:
            # used for comparing the signs placement:
            uReliefFcn = self.getReliefFcn(*uPlacement)
            uRelief = self.getRelief(uReliefFcn)  # numpy array
            uArea = (uRelief == 1).sum()

        if self.allsigns == []:
            # create a list of all the signs in the database - list of tuples:
            # (videofile, activeShape, signType, passiveShape, placement, area)
            with sqlite3.connect(self.dbpath) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT videofile, activeshape, signtype, \
                    passiveshape, placement, area FROM signs')
                allsigns = cursor.fetchall()

        result = []

        for dbSign in allsigns:
            # unpack the dbSign's components
            (videofile, dbActShape, dbSignType, dbPassiveShape, dbPlacement,
                dbArea) = dbSign

            # dbActiveShape is a str of comma separated numbers or None
            if dbActShape:
                dbActiveShape = set(int(item) for item in
                                    dbActShape.split(','))
                dbShapeGroups = set(self.groups[shape] for shape in
                                    dbActiveShape)
            else:
                dbActiveShape = set()
                dbShapeGroups = set()

            # dbPlacement is a str "line#, # of 0s, # of 1s, # of 0s" or None
            if dbPlacement:
                # get numpy array
                dbRelief = self.getDbRelief(dbPlacement)  # numpy array

            # distance in the Active Hand Shape dimension
            actDist = self.calcActDist(uActiveShape, uShapeGroups,
                                       dbActiveShape, dbShapeGroups)

            # distance in the Sign Type dimension
            typeDist = self.calcTypeDist(uSignType, uPassiveShape,
                                         dbSignType, dbPassiveShape)

            # distance in the Sign Placement dimension
            placeDist = 1
            if uPlacement and dbPlacement:
                placeDist = self.calcPlaceDist(uRelief,
                                               uArea,
                                               dbRelief,
                                               dbArea)

            # the total distance
            dist = actDist + typeDist + placeDist
            result.append((videofile, dist))

        # choose the first 'self.signmax' closest signs
        result = sorted(result, key=lambda x: x[1])
        result = result[:self.signsmax]
        # remove the distance values
        result = tools.listOfTuplesToList(result)
        # remove duplicates
        for i in range(len(result)-1, -1, -1):
            if result[i] in result[:i]:
                del result[i]

        # find the words corresponding to individual videofiles
        for i, videofile in enumerate(result):
            with sqlite3.connect(self.dbpath) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT word FROM translation WHERE \
                               videofile=?', (videofile,))
                words = cursor.fetchall()
            wordslist = tools.listOfTuplesToList(words)
            text = ', '.join(wordslist)
            while len(text) > self.maxTextLength:
                del wordslist[-1]
                text = ', '.join(wordslist)
            result[i] = (text, videofile)

        result = self.addSuffixes(result)
        res = (True, result)
        self.showResultFcn(res)

    def calcActDist(self, uShape, uGroups, dbShape, dbGroups):
        """Calculate the distance between the user sign and the db sign in the
        Active Hand Shape dimension.

        Arguments:
            uShape (set of ints): describes active hand shapes of user sign
            uGroups (set of strs): describes the handshape groups of user sign
            dbShape (set of ints): describes the active hand shape of db sign
            dbGroups (set of strs): describes the handshape groups of db sign

        Returns:
            float: a distance
        """

        if dbShape == uShape:
            # all the same shapes
            actDist = 0
        elif len(dbShape & uShape) >= 1 and len(dbGroups ^ uGroups) == 0:
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
        """Calculate the distance between the user sign and the db sign in the
        Sign Type dimension.

        Arguments:
            uSignType (str): the user's sign type, one of:
                'single hand', 'both the same', 'passive hand'
            uPassiveShape (int): describes passive hand shape of user's sign
            dbSignType (str): the database sign type, one of:
                'single hand', 'both the same', 'passive hand'
            dbPassiveShape (int or None): describes pass. hand shape of db sign

        Returns:
            float: a distance
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

    def calcPlaceDist(self, uRelief, uArea, dbRelief, dbArea):
        """Calculate the distance between the user sign and the db sign in the
        Placement dimension.

        Arguments:
            uRelief (numpy.array): describing the user's ellipse
            uArea (int): the area af the user's ellipse
            dbRelief (numpy.array): describing the db ellipse
            dbArea (int): the area af the database ellipse

        Returns:
            float: a distance
        """

        # overlap of the two ellipses
        sumArr = uRelief + dbRelief
        overlap = (sumArr == 2).sum()

        placeDist = 1 - (2 * overlap) / (uArea + dbArea)
        return placeDist

    def getReliefFcn(self, centerx, centery, a, b, angle):
        """Return a function of canvas coords that describes an elliptic area.

        Arguments:
            centerx (float): x coord of the elipse center
            centery (float): y coord of the elipse center
            a (float): major semi-axis length
            b (float): minor semi-axis lenght
            angle (float): angle of rotation of the ellipse

        Returns:
            a function of two float args that returns 1 for points inside
            the elliptic area, and 0 for points outside of it:
                f(x, y) = 1     for (x, y) inside the ellipse
                f(x, y) = 0     for (x, y) outside the ellipse
        """

        def f(x, y):
            center = Vect(centerx, centery)
            point = Vect(x, y)
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

    def getRelief(self, reliefFcn):
        matrix = []
        for y in range(self.canvasHeight):
            row = []
            for x in range(self.canvasWidth):
                row.append(reliefFcn(x, y))
            matrix.append(row)
        return np.array(matrix)

    def getDbRelief(self, dbPlacement):
        placement = [[int(item) for item in line.split(",")] for line
                     in dbPlacement.split(";")]
        # empty matrix
        matrix = [[0] * self.canvasWidth for _ in range(self.canvasHeight)]

        # line number, num of 0s, num of 1s, num of 0s
        for lineNum, n1, n2, n3 in placement:
            matrix[lineNum] = [0] * n1 + [1] * n2 + [0] * n3
        return np.array(matrix)
