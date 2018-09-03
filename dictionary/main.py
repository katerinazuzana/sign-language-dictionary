#######################################################################
#                                                      
# Czech Sign Language Dictionary 
#                                                      
#######################################################################


from tkinter import *
from tkinter import font
from tkinter import ttk
import sqlite3
import os
from categories_frame import CatFrm
from searchentry_frame import EntFrm
from video_frame import VideoFrm
from altoptions_frame import AltsFrm
from shape_select_frame import ShapeSelectFrm, PassiveShapeSelectFrm
from radio_buttons import RadioFrm
from placement_frame import PlacementFrm
from search_engine import SearchEngine


class Dictionary():
    """A Czech Sign Language Dictionary application.
    
    The main frame consists of components:
    'self.entfrm' -- a search entry frame for inserting the word 
                     that will be translated to sign language
    'self.lab' -- a label where the word that has been looked up 
                  in the Dictionary is displayed
    'self.video' -- a large video frame where the translation
                    to sign language is played
    'self.thumbfrm' -- a frame containing thumbnail video frames,
                       the thumbnails are displayed when there is more
                       than one possible translation to sign language
    'self.sep' -- a vertical separator
    'self.catfrm' -- a category-selection frame where a word for
                     translation might be selected from a category
                     or a subcategory of words 
        
    Constants:
    BORDER -- the main frame border
    VIDEO_WIDTH -- width of the canvas where the main video is played
    VIDEO_HEIGHT -- height of the canvas where the main video is played
    THUMB_WIDTH -- width of the thumbnail videos
    THUMB_HEIGHT -- height of the thumbnail videos
    HIGHLIGHT_BORDER -- a highlight thickness of the thumbnail video
                        that is currently being displayed in the large 
                        video frame
    THUMB_PADX -- horizontal spacing of the thumbnail videos
    THUMB_PADY -- space between the main video and the thumbnails
    BGCOLOR -- background color
    """

    BORDER = 40
    VIDEO_WIDTH = 540
    VIDEO_HEIGHT = 310
    THUMB_WIDTH = 160
    THUMB_HEIGHT = 94
    HIGHLIGHT_BORDER = 4
    THUMB_PADX = 10
    THUMB_PADY = 10
    BGCOLOR = 'white'

    def __init__(self, dbpath, vfdir, imgdir):
        """Build the application window.
        
        Arguments:
        dbpath -- [str] the database file path
        vfdir -- [str] path to the directory where video files 
                 with translations to sign language are located
        imgdir -- [str] path to the directory where images are located
        """
        self.dbpath = dbpath
        self.vfdir = vfdir
        self.imgdir = imgdir
        self.thumbs = []   # a list of frames where thumbnail videos live
        self.alts = None   # the frame where alternative options are displayed
                           # when the given word is not found in the database
        self.altsmax = 10  # maximum number of alternative options
        
        # the SearchEngine object provides the logic behind the dictionary app
        self.searchEng = SearchEngine(self.showResult, 
                                      self.dbpath, 
                                      self.vfdir, 
                                      self.altsmax)
        self.makeWidgets()
        
    def makeWidgets(self):
        # build the application window
        self.root = Tk()
        self.root.title('Slovník českého znakového jazyka')
        self.root.minsize(width = 700, height = 700)
        
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # create the main frame
        self.frame = Frame(self.root, bg=self.BGCOLOR, padx=self.BORDER)
        self.frame.grid(column=0, row=0, sticky=N+E+S+W)
                
        self.frame.columnconfigure(0, minsize=self.VIDEO_WIDTH)
#        self.frame.columnconfigure(2, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(3, minsize=self.VIDEO_HEIGHT)
        self.frame.rowconfigure(4, minsize= self.THUMB_HEIGHT +
                                            2 * self.HIGHLIGHT_BORDER +
                                            self.THUMB_PADY +
                                            self.BORDER)
        
        # set font
        appfont = font.Font(family='Helvetica', size=12)
        self.frame.option_add('*Font', appfont)

        # create the search entry frame
        self.entfrm = EntFrm(self.dbpath, 
                             self.searchEng.search,  
                             self.frame, 
                             bg=self.BGCOLOR)
        self.entfrm.grid(column=0, row=0,
                         rowspan=2, 
                         sticky=N+E+W, 
                         pady=(self.BORDER, 0))

        # create a label to display the word
        self.labvar = StringVar()
        self.lab = Label(self.frame, textvariable=self.labvar, 
                                     height=1, 
                                     font=('Helvetica', 20, 'bold'),
                                     bg=self.BGCOLOR,
                                     fg='red2')
        self.lab.grid(column=0, row=2, sticky=N+W+S, pady=0)
        
        # create the main video frame
        self.video = VideoFrm(width=self.VIDEO_WIDTH,
                              height=self.VIDEO_HEIGHT,
                              parent=self.frame)
        self.video.grid(column=0, row=3)
        
        # create a frame for displaying thumbnail videos
        self.thumbfrm = Frame(self.frame, bg=self.BGCOLOR)
        self.thumbfrm.grid(column=0, row=4, 
                           sticky=N+E+S+W,
                           pady=(self.THUMB_PADY, self.BORDER))

        # create a vertical separator
#        self.sep = ttk.Separator(self.frame, orient='vertical')
#        self.sep.grid(row=0, column=1, 
#                      rowspan=5, 
#                      padx=self.BORDER, 
#                      sticky=N+E+S+W)

        # create the notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(column=1, row=0, sticky=N+E+S+W)
        
        # style
        style = ttk.Style()
        style.configure('TNotebook.Tab', padding=(32, 0, 32, 0))
        style.configure('.', font=appfont)
        style.configure('TNotebook', background=self.BGCOLOR)
        style.configure('TNotebook.Tab', background='ghost white')
        # activeTabBg
        style.map('TNotebook.Tab', background=[('selected', self.BGCOLOR)])
        # 'TNotebook': {'congfigure': {'tabmargins': [2, 5, 2, 0] } }

        # create the category-selection frame
        self.catfrm = CatFrm(self.dbpath, 
                             self.searchEng.search, 
                             self.notebook, 
                             bg=self.BGCOLOR, 
                             padx=self.BORDER, 
                             pady=self.BORDER)
        self.catfrm.grid(column=0, row=0, sticky=N+E+S+W) # rowspan=3
        self.notebook.add(self.catfrm, text='Výběr podle kategorií')
        
        # create the sign-input frame
        self.signfrm = Frame(self.notebook, bg=self.BGCOLOR, 
                             padx=self.BORDER)
        self.signfrm.grid(column=0, row=0, sticky=N+E+S+W)
        self.notebook.add(self.signfrm, text='Překlad z ČZJ do ČJ')
        
        # create an active hand shapes offer
        Label(self.signfrm, 
              text='Tvar aktivní ruky', 
              bg=self.BGCOLOR
              ).grid(column=0, row=0, columnspan=2, sticky=W, pady=(20, 3))
        
        self.actshapes = ShapeSelectFrm(self.signfrm, self.imgdir, self.BGCOLOR)
        self.actshapes.grid(column=0, row=1, 
                            columnspan=2, sticky=N+E+S+W, pady=(0, 20))
        
        # create radio-buttons
        self.radiofrm = RadioFrm(self.signfrm, self.imgdir, self.BGCOLOR)
        self.radiofrm.grid(column=0, row=2, 
                           columnspan=2, sticky=N+S+W, pady=(0, 20))
        
        # create canvas for sign-placement input
        Label(self.signfrm, 
              text='Místo artikulace znaku', 
              bg=self.BGCOLOR
              ).grid(column=0, row=3, columnspan=2, sticky=W, pady=(0, 3))
        
        placementfrm = PlacementFrm(self.signfrm)
        placementfrm.grid(column=0, row=4, sticky=W)
        
        # create the Search button
        Button(self.signfrm, 
               text='Vyhledat', 
               command=self.searchEng.signSearch
               ).grid(column=1, row=4, 
                                sticky=E+S, 
                                padx=(15, 0))
    
    def showResult(self, result):
        successFlag, alist = result        
        self.deleteThumbnails()
        if successFlag == True:
            # the word was found
            word, videofile = alist[0]
            self.showVideoAndWord(word, videofile)
            if len(alist) > 1:                
                # there's more than one match
                self.createThumbnails(alist)
        else:
            # the word was not found
            # display alternative options
            self.showNotFound(alist)
        
    def showVideoAndWord(self, word, videofile):
        """Show the word that is being translated and play
        the corresponding video.
        Arguments:
        word -- [string] the word to be displayed
        videofile -- [string] name of the video file
        """
        self.labvar.set(word)
               
        # if there is an alternative-options-frame currently being displayed,
        # destroy it, and create a video-frame
        if self.alts != None:
            self.alts.destroy()
            self.alts = None
            self.video = VideoFrm(width=self.VIDEO_WIDTH,
                                  height=self.VIDEO_HEIGHT,
                                  parent=self.frame)
            self.video.grid(column=0, row=3)        
        # play the video file
        self.video.play(video_source=videofile)
                                
    def createThumbnails(self, find):
        """Create the thumbnail videos.
        
        Arguments:
        find -- [list] a list of 2-tuples (word, videofile) where
                word -- [string] the word that is being translated
                videofile -- [string] name of video file without suffix
        """
        self.thumbfrm.rowconfigure(0, minsize = self.THUMB_HEIGHT + 
                                                2 * self.HIGHLIGHT_BORDER)
        
        for i in range(len(find)):
            self.thumbfrm.columnconfigure(i, minsize = self.THUMB_WIDTH + 
                                                  2 * self.HIGHLIGHT_BORDER +
                                                  self.THUMB_PADX)
            
            # create the thumbnails and collect them in self.thumbs variable
            thumb = VideoFrm(width=self.THUMB_WIDTH,
                             height=self.THUMB_HEIGHT,
                             parent=self.thumbfrm,
                             thumb=True,
                             border=self.HIGHLIGHT_BORDER)
            thumb.grid(column=i, row=0, padx=(0, self.THUMB_PADX))
            self.thumbs.append(thumb)
            thumb.showFirstPic(find[i][1])
            
            # double-click on the thumbnail plays the thumbnail video
            # in the large video frame
            def callback(vf, i):
                return lambda event: self.onThumbClick(vf, i)            
            thumb.canvas.bind('<Double-Button-1>', callback(find[i][1], i))
            
            # when the mouse cursor enters a thumbnail,
            # the thumbnail video is played (in the thumbnail frame)
            def playThumb(i):
                vs = find[i][1]
                return lambda event: self.thumbs[i].play(video_source=vs)
            thumb.canvas.bind('<Enter>', playThumb(i))
        
        # highlight the thumbnail that is currently displayed
        # in the large video frame (i.e. the 1st one)    
        self.thumbs[0].lightOn()
   
    def onThumbClick(self, vf, i):
        """Highlight the clicked-on thumbnail and play its video.
        
        Remove highlighting from the previously highlighted thumbnail.
        Play the video from the clicked-on thumbnail in the large video frame.
        """
        self.thumbs[i].lightOn()
        for thumb in self.thumbs[:i]+self.thumbs[i+1:]:
            thumb.lightOff()   
        self.video.play(video_source=vf)
     
    def deleteThumbnails(self):
        for thumb in self.thumbs:
            thumb.destroy()
        self.thumbs = []

    def showNotFound(self, altoptions):
        if altoptions == []:
            self.labvar.set('Výraz nebyl nalezen')
        else:
            self.labvar.set('Výraz nebyl nalezen - nechtěli jste hledat:')
            # destroy the video frame
            self.video.destroy()
            # if there is an alternative-options-frame currently 
            # being displayed, destroy it
            if self.alts != None:
                self.alts.destroy()
        # create a frame with an offer of alternative options
        self.alts = AltsFrm(altoptions, 
                            self.searchEng.search, 
                            self.BGCOLOR, 
                            self.frame, 
                            bg=self.BGCOLOR)
        self.alts.grid(column=0, row=3, sticky=N+E+S+W)
        
        

if __name__ == '__main__':
    dbpath = os.path.abspath('dict.db')
    vfdir = os.path.abspath('demo_videofiles')
    imgdir = os.path.abspath('demo_images')
    
    Dictionary(dbpath, vfdir, imgdir).root.mainloop()
    
        
