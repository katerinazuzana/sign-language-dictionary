"""video_frame module

classes:
VideoFrm -- a frame where a video is played
MyVideoCapture -- capture a video source
"""

from tkinter import *
import cv2
import PIL.Image, PIL.ImageTk


class VideoFrm(Frame):
    """A frame containing a Canvas tkinter widget for playing a video. 
    A VideoFrm is used for both the large video frame and the thumbnail
    videos.   
    """
   
    def __init__(self, parent, width, height, thumb=False, 
                 border=0, **options):
        """Create the self.canvas widget.
        
        Arguments:
        parent -- the parent tkinter widget
        width -- [int] the width of the canvas
        height -- [int] the height of the canvas
        Keyword arguments:
        thumb -- [bool] a boolean flag indicating whether 
                 the VideoFrm object is used 
                 as the large video screen (thumb=False) 
                 or as a thumbnail video (thumb=True)
                 (default False)
        border -- [int] a highlight thickness of the thumbnail video
                  (default 0)
        """
        super().__init__(parent, **options)
        self.thumb = thumb
        if self.thumb: self.light = False  # a boolean flag showing whether
                                   # the thumbnail is currently highlighted
        self.border = border
        
        # create a canvas for displaying the video
        self.width = width
        self.height = height
        self.canvas = Canvas(self, width=self.width, 
                                   height=self.height, 
                                   highlightthickness=0)
        self.canvas.grid(column=0, row=0, padx=self.border, pady=self.border)
        self.canvas.config(bg='black')
        # canvas center coords
        self.centerX =  int(self.width / 2) + self.border
        self.centerY =  int(self.height / 2) + self.border

    def play(self, video_source):
        """Start playing video from the video source.
        
        Arguments:
        video_source -- [str] a path to the video file to be played
        """
        self.video = MyVideoCapture(video_source)
        self.update(video_source)
    
    def update(self, video_source):
        """Get a frame from the video source and display it on self.canvas.
        
        After it is called once, the update method will be automatically
        called every self.video.delay milliseconds until there are no frames
        left in the video source.
        """
        ret, frame = self.video.getFrame()
        if ret:
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
                                     anchor=CENTER)
            # after delay, call self.update method again   
            self.after(self.video.delay, lambda: self.update(video_source))
        else:
            # there are no more frames in the video source
            self.showFirstPic(video_source)
            if self.thumb == False:
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
        """Draw a highlighting border around the canvas."""
        
        if not self.light:
            self.light = True
            self.canvas.config(highlightthickness=self.border, 
                               highlightbackground='red')
            self.canvas.grid(column=0, row=0, padx=0, pady=0)
    
    def lightOff(self):
        """Remove the highlighting border from around the canvas."""
        
        if self.light:
            self.light = False
            self.canvas.config(highlightthickness=0)
            self.canvas.grid(column=0, row=0, 
                             padx=self.border, pady=self.border)
    
    def showFirstPic(self, video_source):
        """Display the first frame from the video source on self.canvas.
        
        Arguments:
        video_source -- [str] a path to the video file
        """
        vid = MyVideoCapture(video_source)
        ret, frame = vid.getFrame()                    
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
                                 anchor=CENTER)   
       
    def drawReplayArrow(self):
        """Draw a replay arrow over the video on self.canvas
        to indicate that the video may be replayed.
        """
        # darken the video screen
        transparentRect = self.canvas.create_rectangle(0, 0, self.width,
                                                       self.height,
                                                       fill='black',
                                                       stipple='gray25')
        color = 'ghost white'
        thickness = 3
        # draw the arc
        perimeter = 20
        x0 = self.centerX - perimeter
        y0 = self.centerY - perimeter
        x1 = self.centerX + perimeter
        y1 = self.centerY + perimeter
        arc = self.canvas.create_arc(x0, y0, x1, y1, start=0, extent=300,
                                     style=ARC, width=thickness,
                                     outline=color)
        # draw the arrow head    
        arrowhead = (self.centerX + perimeter, self.centerY)
        a = 8
        point1 = (arrowhead[0]-a-2, arrowhead[1]-a+2)
        point2 = (arrowhead[0]+a, arrowhead[1]-a)
            
        line1 = self.canvas.create_line(point1[0], point1[1], arrowhead[0],
                                        arrowhead[1], width=thickness+1,
                                        fill=color)
        line2 = self.canvas.create_line(point2[0], point2[1], arrowhead[0],
                                        arrowhead[1], width=thickness,
                                        fill=color)
    

class MyVideoCapture:
    """An object capturing a video source using an OpenCV VideoCapture."""
    
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
            ret, frame = self.vid.read()
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        return (False, None)


