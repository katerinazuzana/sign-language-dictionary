from tkinter import *
from searchentry_frame import EntFrm
from video_frame import VideoFrm
from altoptions_frame import AltsFrm


class MainFrm(Frame):
    """A frame where the results of searching are displayed.
    
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
    
    Constants:
    VIDEO_WIDTH -- width of the canvas where the main video is played
    VIDEO_HEIGHT -- height of the canvas where the main video is played
    THUMB_WIDTH -- width of the thumbnail videos
    THUMB_HEIGHT -- height of the thumbnail videos
    HIGHLIGHT_BORDER -- a highlight thickness of the thumbnail video
                        that is currently being displayed in the large 
                        video frame
    THUMB_PADX -- horizontal spacing of the thumbnail videos
    THUMB_PADY -- space between the main video and the thumbnails
    """
    
    VIDEO_WIDTH = 540
    VIDEO_HEIGHT = 310
    THUMB_WIDTH = 160
    THUMB_HEIGHT = 94
    HIGHLIGHT_BORDER = 4
    THUMB_PADX = 10
    THUMB_PADY = 10
    
    def __init__(self, parent, dbpath, vfdir, imgdir, searchfcn, 
                 altsmax, border, **options):
        super().__init__(parent, **options)

        self.dbpath = dbpath
        self.vfdir = vfdir
        self.imgdir = imgdir
        self.searchfcn = searchfcn
        self.thumbs = []   # a list of frames where thumbnail videos live
        self.alts = None   # the frame where alternative options are displayed
                           # when the given word is not found in the database
        self.altsmax = altsmax
        self.BORDER = border
        self.bgcolor = options.get('bg', self['bg'])

        self.makeWidgets()

    def makeWidgets(self):
        self.columnconfigure(0, minsize=self.VIDEO_WIDTH)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(3, minsize=self.VIDEO_HEIGHT)
        self.rowconfigure(4, minsize= self.THUMB_HEIGHT +
                                      2 * self.HIGHLIGHT_BORDER +
                                      self.THUMB_PADY +
                                      self.BORDER)

        # create the search entry frame
        self.entfrm = EntFrm(self.dbpath, 
                             self.searchfcn,  
                             self, 
                             self.imgdir, 
                             bg=self.bgcolor)
        self.entfrm.grid(column=0, row=0,
                         rowspan=2, 
                         sticky=N+E+W, 
                         pady=(self.BORDER, 0))

        # create a label to display the word
        self.labvar = StringVar()
        self.lab = Label(self, 
                         textvariable=self.labvar, 
                         height=1, 
                         font=('Helvetica', 20, 'bold'),
                         bg=self.bgcolor,
                         fg='red2')
        self.lab.grid(column=0, row=2, sticky=N+W+S, pady=0)
        
        # create the main video frame
        self.video = VideoFrm(width=self.VIDEO_WIDTH,
                              height=self.VIDEO_HEIGHT,
                              parent=self)
        self.video.grid(column=0, row=3)
        
        # create a frame for displaying thumbnail videos
        self.thumbfrm = Frame(self, bg=self.bgcolor)
        self.thumbfrm.grid(column=0, row=4, 
                           sticky=N+E+S+W,
                           pady=(self.THUMB_PADY, self.BORDER))

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
                                  parent=self)
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
                            self.searchfcn, 
                            self.bgcolor, 
                            self, 
                            bg=self.bgcolor)
        self.alts.grid(column=0, row=3, sticky=N+E+S+W)
    
    def showEnterText(self):
        self.deleteThumbnails()
        self.video.destroy()
        if self.alts != None:
            self.alts.destroy()
        self.labvar.set('Zadejte výraz, který chcete vyhledat')

    def showResult(self, result):
        """
        """
        
        






