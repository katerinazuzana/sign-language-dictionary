import tkinter as tk
import tkinter.font as tkFont
from searchentry_frame import EntFrm
from video_frame import VideoFrm
from altoptions_frame import AltsFrm
from scrolled_frame import ScrolledFrame


class MainFrm(tk.Frame):
    """A frame where the search results are displayed.

    MainFrm consists of widgets:
    'self.entfrm' -- a frame with an entry for inserting a word
    'self.lab' -- a label where the word that has been looked up is displayed
    'self.videofrm' -- a large video frame where a video with a sign is played
    'self.thumbfrm' -- a frame containing thumbnail video frames,
                       czech to czech sign language:
                           the thumbnails are displayed when there is more
                           than one possible translation to sign language
                       czech sign language to czech:
                           the signs that are closest to the user input sign
                           are displayed as thumbnail videos
    """

    VIDEO_WIDTH = 540  # width of the canvas where the main video is played
    VIDEO_HEIGHT = 310  # height of the canvas where the main video is played
    THUMB_WIDTH = 160  # width of the thumbnail videos
    THUMB_HEIGHT = 94  # height of the thumbnail videos

    # a highlight thickness of the thumbnail video that is currently being
    # displayed in the large video frame
    HIGHLIGHT_BORDER = 4
    THUMB_PADX = 5  # horizontal spacing of the thumbnail videos
    THUMB_PADY = 35  # space between the main video and the thumbnails

    # the width of the scrollbar used in the frame with thumbnail videos
    SCROLLBAR_WIDTH = 15
    TOP_SPACE = 5  # additional padding at the top of the frame
    LAB_PADY = 20  # space between the label and the main video frame widgets
    LAB_FONT_SIZE = 20  # font size of the label
    LAB_FONT_SIZE_SMALL = 19
    LAB_FONT_SIZE_SMALLEST = 16
    LENGTH_NORMAL_FONT = 33  # max word length for using normal font size
    LENGTH_SMALL_FONT = 37  # max word length for using small font size

    def __init__(self, parent, dbpath, vfdir, imgdir, searchEng, altsmax,
                 border, **options):
        """Initialize a MainFrm object, create the widgets.

        Arguments:
            parent: a parent tkinter widget
            dbpath (str): the database file path
            vfdir (str): a path to the directory with video files
            imgdir (str): a path to the directory with images
            searchEng: an object that provides searching operations
            altsmax (int): number of alternative words shown when the word
                from the user is not found in the database
            border (int): the main window border width
        """
        super().__init__(parent, **options)
        self.dbpath = dbpath
        self.vfdir = vfdir
        self.imgdir = imgdir
        self.searchEng = searchEng
        self.thumbs = []   # a list of frames where thumbnail videos live

        # a frame where alternative options are displayed when the given word
        # is not found in the database
        self.altsfrm = None

        self.altsmax = altsmax
        self.BORDER = border
        self.bgcolor = options.get('bg', self['bg'])
        self.makeWidgets()

    def makeWidgets(self):
        """Create the widgets."""
        self.columnconfigure(0, minsize=self.VIDEO_WIDTH)
        self.rowconfigure(0, weight=1)  # empty row
        self.rowconfigure(1, weight=4)
        self.rowconfigure(3, minsize=self.VIDEO_HEIGHT)
        self.rowconfigure(4,
                          minsize=self.THUMB_HEIGHT +
                          2 * self.HIGHLIGHT_BORDER +
                          self.THUMB_PADY +
                          self.BORDER)

        # create the search entry frame
        self.entfrm = EntFrm(self,
                             self.imgdir,
                             self.searchEng,
                             self.showResult,
                             bg=self.bgcolor)
        self.entfrm.grid(column=0, row=1,
                         sticky=tk.N+tk.E+tk.S+tk.W,
                         pady=(self.BORDER + self.TOP_SPACE, 0))

        # create a label to display the word
        self.labvar = tk.StringVar()
        self.lab = tk.Label(self,
                            textvariable=self.labvar,
                            height=1,
                            bg=self.bgcolor,
                            fg='red2')
        self.lab.grid(column=0, row=2,
                      sticky=tk.N+tk.S+tk.W,
                      pady=(0, self.LAB_PADY))

        # create the main video frame
        self.videofrm = VideoFrm(self,
                                 self.VIDEO_WIDTH,
                                 self.VIDEO_HEIGHT,
                                 self.imgdir)
        self.videofrm.grid(column=0, row=3)

        # frame for displaying thumbnail videos
        self.createThumbFrm()

    def createThumbFrm(self):
        """Create a frame for displaying thumbnail videos."""
        self.thumbfrm = ScrolledFrame(self,
                                      # canvas size:
                                      width=self.VIDEO_WIDTH,
                                      height=self.THUMB_HEIGHT +
                                      2 * self.HIGHLIGHT_BORDER,
                                      orient='horizontal',
                                      bg=self.bgcolor)
        # frame size:
        self.thumbfrm.config(width=self.VIDEO_WIDTH,
                             height=self.THUMB_HEIGHT +
                             2 * self.HIGHLIGHT_BORDER +
                             self.SCROLLBAR_WIDTH)
        self.thumbfrm.grid_propagate(0)

        self.thumbfrm.grid(column=0, row=4,
                           sticky=tk.N+tk.E+tk.S+tk.W,
                           pady=(self.THUMB_PADY, self.BORDER))

    def showResult(self, result):
        """Show the first video in result in large, and possible other videos
        in thumbnails.

        If there's no result found, show an offer of alternative words.

        Arguments:
            result: a 2-tuple of form (boolean-flag, a-list) where a-list
            contains items of form:
                (word (str), video-file (str)) - for boolean-flag True
                alternative-word (str) - for boolean-flag False
        """
        self.deleteThumbnails()

        successFlag, alist = result
        if successFlag is True:
            # the word was found
            # or it was a sign search (that always returns successFlag = True)
            word, videofile = alist[0]
            self.showWordAndVideo(word, videofile)
            if len(alist) > 1:
                # there's more than one match
                # (this is always the case for the sign search)
                self.createThumbnails(alist)
        else:
            # the word was not found
            # display alternative options
            self.showNotFound(alist)

    def showWordAndVideo(self, word, videofile):
        """Show 'word' on 'self.lab' label and play the corresponding video.

        Arguments:
            word (str): the word to be displayed
            videofile (str): name of the video file
        """
        self.labvar.set(word)
        if len(word) <= self.LENGTH_NORMAL_FONT:
            self.setLabFontSize(self.LAB_FONT_SIZE)
        elif len(word) <= self.LENGTH_SMALL_FONT:
            self.setLabFontSize(self.LAB_FONT_SIZE_SMALL)
        else:
            self.setLabFontSize(self.LAB_FONT_SIZE_SMALLEST)

        # if there is an AltsFrm, create a VideoFrm instead of it
        if self.altsfrm is not None:
            self.altsfrm.destroy()
            self.altsfrm = None
            self.videofrm = VideoFrm(self,
                                     self.VIDEO_WIDTH,
                                     self.VIDEO_HEIGHT,
                                     self.imgdir)
            self.videofrm.grid(column=0, row=3)
        # play the video file
        self.videofrm.play(video_source=videofile)

    def createThumbnails(self, find):
        """Create the thumbnail video frames.

        Arguments:
            find (list): a list of 2-tuples (word, videofile) where
                word (str) is the word that is being translated
                videofile (str) is name of video file
        """

        self.thumbfrm.rowconfigure(0,
                                   minsize=self.THUMB_HEIGHT +
                                   2 * self.HIGHLIGHT_BORDER)

        for i in range(len(find)):
            self.thumbfrm.columnconfigure(i,
                                          minsize=self.THUMB_WIDTH +
                                          2 * self.HIGHLIGHT_BORDER +
                                          self.THUMB_PADX)

            # create the thumbnails and collect them in self.thumbs variable
            thumb = VideoFrm(self.thumbfrm.interior,
                             self.THUMB_WIDTH,
                             self.THUMB_HEIGHT,
                             thumb=True,
                             border=self.HIGHLIGHT_BORDER,
                             bg=self.bgcolor)
            thumb.grid(column=i, row=0, padx=(0, self.THUMB_PADX))
            self.thumbs.append(thumb)
            thumb.showFirstPic(find[i][1])

            # double-click on the thumbnail plays the thumbnail video
            # in the large video frame
            def callback(word, vf, i):
                return lambda event: self.onThumbClick(word, vf, i)
            thumb.canvas.bind('<Double-Button-1>', callback(*find[i], i))

            # when the mouse cursor enters a thumbnail,
            # the thumbnail video is played (in the thumbnail frame)
            def playThumb(i):
                vs = find[i][1]
                return lambda event: self.thumbs[i].play(video_source=vs)
            thumb.canvas.bind('<Enter>', playThumb(i))

        # highlight the thumbnail that is currently displayed
        # in the large video frame (i.e. the 1st one)
        self.thumbs[0].lightOn()

    def onThumbClick(self, word, vf, i):
        """Highlight the clicked-on thumbnail and play its video.

        Remove highlighting from the previously highlighted thumbnail.
        Play the video from the clicked-on thumbnail in the large video frame.
        """
        self.thumbs[i].lightOn()
        for thumb in self.thumbs[:i]+self.thumbs[i+1:]:
            thumb.lightOff()
        self.showWordAndVideo(word, vf)

    def deleteThumbnails(self):
        """Delete the thumbnail video frames."""
        for thumb in self.thumbs:
            thumb.destroy()
        self.thumbs = []
        # create a new, empty thumbfrm
        self.thumbfrm.destroy()
        self.createThumbFrm()

    def showNotFound(self, altoptions):
        """Show a 'Not found' notification and possible alternatives."""
        if altoptions == []:
            self.labvar.set('Výraz nebyl nalezen')
        else:
            self.labvar.set('Výraz nebyl nalezen - nechtěli jste hledat:')
            self.setLabFontSize(self.LAB_FONT_SIZE_SMALLEST)
            self.videofrm.destroy()
            if self.altsfrm is not None:
                self.altsfrm.destroy()
        # create a frame with an offer of alternative options
        self.altsfrm = AltsFrm(self,
                               altoptions,
                               self.searchEng,
                               self.showResult,
                               bg=self.bgcolor)
        self.altsfrm.grid(column=0, row=3, sticky=tk.N+tk.E+tk.S+tk.W)

    def showEnterText(self):
        """Prompt the user to enter an expression."""
        self.deleteThumbnails()
        if self.altsfrm is not None:
            self.altsfrm.destroy()
        self.labvar.set('Zadejte výraz, který chcete vyhledat')
        self.setLabFontSize(self.LAB_FONT_SIZE_SMALL)

    def setLabFontSize(self, size):
        """Set font size in 'self.lab'."""
        font = tkFont.Font(font=self.lab['font'])  # get current app font
        font.configure(size=size, weight='bold')  # adjust it
        self.lab.config(font=font)  # use the changed font in the label
