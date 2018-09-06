import sqlite3
import os
from difflib import SequenceMatcher

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
            match.size
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
  
    def signSearch(self, *args):
        pass



