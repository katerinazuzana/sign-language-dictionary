"""video_frame module

classes:
    VideoFrm: a frame where a video is played
    MyVideoCapture: class capturing a video source
"""


import tkinter as tk
import cv2
import PIL.Image
import PIL.ImageTk
import os
import tools


class VideoFrm(tk.Frame):
    """A frame with a canvas widget for playing a video.

    A VideoFrm is used for both the large video screen and the thumbnail
    videos.
    """

    def __init__(self, parent, width, height, imgdir=None, thumb=False,
                 border=0, **options):
        """Initialize a VideoFrm object. Create a 'self.canvas' widget.

        Arguments:
            parent: the parent tkinter widget
            width (int): the width of the canvas
            height (int): the height of the canvas
            imgdir (str): a path to the directory with images (default is None)
            thumb (bool): a boolean flag indicating whether the VideoFrm
                object is used as the large video screen (thumb=False),
                or as a thumbnail video (thumb=True), (default is False)
            border (int): a highlight thickness of the thumbnail video
                (default is 0)
        """
        super().__init__(parent, **options)
        self.thumb = thumb
        self.border = border
        self.bgcolor = options.get('bg', self['bg'])
        self.job = None  # keeps reference to a job scheduled with after call

        if imgdir:
            self.replayArrowPath = os.path.join(imgdir, 'replay_arrow.png')
            self.arrowSize = 35

        # create a canvas for displaying the video
        self.width = width
        self.height = height
        self.canvas = tk.Canvas(self,
                                width=self.width,
                                height=self.height,
                                highlightthickness=self.border,
                                highlightbackground=self.bgcolor)
        self.canvas.grid(column=0, row=0)
        self.canvas.config(bg='black')
        # canvas center coords
        self.centerX = int(self.width / 2) + self.border
        self.centerY = int(self.height / 2) + self.border

    def play(self, video_source):
        """Start playing video from the video source.

        Arguments:
            video_source (str): a path to the video file to be played
        """
        if self.job:
            self.after_cancel(self.job)
        self.video = MyVideoCapture(video_source)
        self.update(video_source)

    def update(self, video_source):
        """Get a frame from the video source and display it on 'self.canvas'.

        After it is called once, the update method will be automatically
        called every 'self.video.delay' milliseconds until there are no frames
        left in the video source.
        """
        flag, frame = self.video.getFrame()
        if flag:
            # there is a frame in the video source
            img = PIL.Image.fromarray(frame)
            # resize the image
            newwidth = self.width
            newheight = int(self.video.height * newwidth / self.video.width)
            img = img.resize((newwidth, newheight), PIL.Image.BILINEAR)

            # display the image on the canvas
            self.image = PIL.ImageTk.PhotoImage(img)
            self.canvas.delete('all')
            self.canvas.create_image(self.centerX,
                                     self.centerY,
                                     image=self.image,
                                     anchor=tk.CENTER)
            # after delay, call self.update method again
            self.job = self.after(self.video.delay,
                                  lambda: self.update(video_source))
        else:
            # there are no more frames in the video source
            self.showFirstPic(video_source)
            if not self.thumb:
                # the object is the large video, not a thumbnail
                # draw a replay arrow and replay the video on a mouse click
                self.drawReplayArrow()
                self.canvas.bind('<Button-1>', (lambda event: self.onVideoClick
                                                (video_source)))

    def onVideoClick(self, video_source):
        """Replay the video."""
        self.play(video_source)
        # unbind Button-1 event so that the video is replayed only
        # on the first click
        self.canvas.unbind('<Button-1>')

    def lightOn(self):
        """Highlight the canvas."""
        self.canvas.config(highlightbackground='red')

    def lightOff(self):
        """Remove the highlighting from the canvas."""
        self.canvas.config(highlightbackground=self.bgcolor)

    def showFirstPic(self, video_source):
        """Display the first frame from the video source on self.canvas.

        Arguments:
            video_source (str): a path to the video file
        """
        vid = MyVideoCapture(video_source)
        flag, frame = vid.getFrame()
        img = PIL.Image.fromarray(frame)
        # resize the image
        newwidth = self.width
        newheight = int(vid.height * newwidth / vid.width)
        img = img.resize((newwidth, newheight), PIL.Image.BILINEAR)
        # display the image on the canvas
        self.image = PIL.ImageTk.PhotoImage(img)
        self.canvas.create_image(self.centerX,
                                 self.centerY,
                                 image=self.image,
                                 anchor=tk.CENTER)

    def drawReplayArrow(self):
        """Draw a replay arrow over the video on self.canvas
        to indicate that the video may be replayed.
        """
        # darken the video screen
        self.canvas.create_rectangle(0, 0,
                                     self.width,
                                     self.height,
                                     fill='black',
                                     stipple='gray25')
        self.arrow = tools.getImage(self.replayArrowPath,
                                    width=self.arrowSize,
                                    height=self.arrowSize)
        self.canvas.create_image(self.centerX,
                                 self.centerY,
                                 image=self.arrow,
                                 anchor=tk.CENTER)


class MyVideoCapture:
    """A class capturing a video source using an OpenCV VideoCapture."""

    def __init__(self, video_source):
        # open the video source
        self.vid = cv2.VideoCapture(video_source)

        # get the video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.delay = 20

    def __del__(self):
        """Release the video source when the object is destroyed."""
        if self.vid.isOpened():
            self.vid.release()

    def getFrame(self):
        """Return a tuple of a boolean success flag and the current frame."""
        if self.vid.isOpened():
            flag, frame = self.vid.read()
            if flag:
                return (flag, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (flag, None)
        return (False, None)
