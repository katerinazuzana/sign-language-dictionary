from tkinter import *
import tkinter.font as tkFont
import os
from drawing_canvas import DrawingCanvas
import tools


class PlacementFrm(Frame):
    """A frame with a drawing canvas used to specify the sign placement.
    
    PlacementFrm contains widgets:
    - a label with a title
    - 'self.hintIcon' label that shows a window with instructions when 
        pointed to by a mouse
    - 'self.canvas' DrawingCanvas used to specify the sign placement
    - 'delButton' button that deletes what was drawn on the canvas
    - 'searchButton' button that starts a search for signs
    """    
    
    def __init__(self, parent, imgdir, canvasSize, **options):
        """Set constants and create the widgets.
        
        Arguments:
            parent: a parent tkinter widget
            imgdir (str): a path to the directory with images
            canvasSize (tuple): a 2-tuple with width and height of the canvas
        """
        super().__init__(parent, **options)
        self.bgcolor = options.get('bg', self['bg'])
        
        self.hintIconPath = os.path.join(imgdir, 'hint_icon.png')
        self.hintSize = 20
        self.hintText = 'Klepnutím a tažením nakreslete elipsu,'+\
                       ' která bude vyznačovat umístění znaku.'+\
                       ' Elipsu lze myší přesouvat.'+\
                       ' Po dvojkliku na elipsu je možné měnit její velikost.'+\
                       ' Po dalším dvojkliku lze elipsou otáčet.'
        
        self.delIconPath = os.path.join(imgdir, 'del_draw.png')
        self.delIconSize = 32
        self.delButSize = 35
        self.searchIconPath = os.path.join(imgdir, 'search_icon.png')
        self.searchIconSize = 32
        self.searchButWidth = 52
        self.searchButHeight = 35
        
        self.delay = 1000 # how long to wait before button description shows up
        self.caption = None
        self.captFont = None
        self.captFontSize = 10   # font size of the captions/hint message
        self.msgWidth = 100      # width of the caption message widget
        
        self.labPady = 3
        self.hintPadx = 8
        self.delButPadx = 15
        self.searchButPadx = 5
        self.butVertSpace = 7 # vertical space between Delete and Search buttons
        
        self.canvasBorder = 2
        self.canvasWidth, self.canvasHeight = canvasSize
        self.canvasImagePath = os.path.join(imgdir, 'interpreter.png')
        self.makeWidgets()
        
    def makeWidgets(self):
        """Create a title label, a hint icon, a drawing canvas, and buttons."""
        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)
        
        Label(self, 
              text='Místo artikulace znaku', 
              bg=self.bgcolor).grid(column=0, row=0, 
                                    sticky=E, 
                                    pady=(0, self.labPady))

        # create hint icon
        self.icon = tools.getImage(self.hintIconPath, 
                                   width=self.hintSize, 
                                   height=self.hintSize)
        self.hintIcon = Label(self, image=self.icon, bg=self.bgcolor)
        self.hintIcon.grid(column=1, row=0, 
                           sticky=N+W, 
                           padx=(self.hintPadx, 0))
        # when mouse is over the icon, show the hintText
        self.hintIcon.bind('<Enter>', self.showHint)
        self.hintIcon.bind('<Leave>', self.hideHint)
        
        # create a canvas
        self.canvas = DrawingCanvas(self, 
                                    width=self.canvasWidth, 
                                    height=self.canvasHeight, 
                                    borderwidth=self.canvasBorder, 
                                    relief='groove')
        self.canvas.grid(column=0, row=1, columnspan=2, rowspan=2)
        self.image = tools.getImage(self.canvasImagePath, 
                                    width=self.canvasWidth, 
                                    height=self.canvasHeight)
        self.canvas.create_image(2, 2, image=self.image, anchor=NW)        
        
        # create delete button
        self.delImg = tools.getImage(self.delIconPath, 
                                     width=self.delIconSize, 
                                     height=self.delIconSize)
        delButton = Button(self, 
                           image=self.delImg, 
                           command=self.onDelete, 
                           width=self.delButSize, 
                           height=self.delButSize, 
                           bg=self.bgcolor, 
                           activebackground=self.bgcolor, 
                           borderwidth=0, 
                           highlightthickness=0)
        delButton.grid(column=2, row=1, 
                       sticky=S+W, 
                       padx=(self.delButPadx, 0))
        # when mouse is over the button for a while, show a caption
        delButton.bind('<Enter>', lambda ev: self.onButEnter('Smazat'))
        delButton.bind('<Leave>', self.onButLeave)
        
        # create search button
        self.searchImg = tools.getImage(self.searchIconPath, 
                                        width=self.searchIconSize, 
                                        height=self.searchIconSize)
        searchButton = Button(self, 
                              image=self.searchImg, 
                              command=self.master.onSearchPress, 
                              width=self.searchButWidth,
                              height=self.searchButHeight, 
                              bg=self.bgcolor, 
                              activebackground='ghost white', 
                              borderwidth=0, 
                              highlightthickness=2, 
                              highlightbackground='light gray')
        searchButton.grid(column=2, row=2, 
                          sticky=S+W, 
                          padx=(self.searchButPadx, 0), 
                          pady=(self.butVertSpace, 0))
        # when mouse is over the button for a while, show a caption
        searchButton.bind('<Enter>', lambda ev: self.onButEnter('Vyhledat'))
        searchButton.bind('<Leave>', self.onButLeave)
    
    def showHint(self, event):
        """Create a toplevel window with a hint message."""
        self.hint = Toplevel()
        msg = Message(self.hint, 
                      text=self.hintText, 
                      width=140,  # the actual width will be different because 
                                  # the words are not split at the end of line
                      bg=self.bgcolor)
        msg.grid()
        
        # set hint font if not defined yet
        if not self.captFont: self.setCaptFont(msg)
        msg.config(font=self.captFont)
        
        xoffset = self.hintIcon.winfo_rootx() + self.hintSize
        yoffset = self.hintIcon.winfo_rooty() + self.hintSize
        
        width = 150 # approx msg window actual width in pixels
        # ensure that the message window is fully visible -
        # that it doesn't streach beyond the right screen border: 
        if xoffset + width > self.winfo_screenwidth():
            xoffset = self.winfo_screenwidth() - width
        self.hint.geometry('+{}+{}'.format(xoffset, yoffset))
        self.hint.overrideredirect(True)
    
    def hideHint(self, event):
        """Destroy the 'self.hint' window."""
        self.hint.destroy()
        
    def onDelete(self):
        """Delete the ellipse, reset the canvas to its initial state."""
        self.canvas.delete(ALL)
        self.canvas.create_image(2, 2, image=self.image, anchor=NW)
        self.canvas.ellipse = None
        self.canvas.drawMode = True
        self.canvas.moveMode = False
        self.canvas.scaleMode = False
        self.canvas.rotateMode = False

    def onButEnter(self, text):
        """Call the after() method to show a button caption."""
        self.job = self.after(self.delay, lambda: self.showCaption(text))
    
    def onButLeave(self, event):
        """Stop showing the button caption."""
        self.after_cancel(self.job)
        if self.caption: self.hideCaption()
    
    def showCaption(self, text):
        """Create a toplevel window with a caption message."""
        self.caption = Toplevel()
        msg = Message(self.caption, 
                      text=text, 
                      width=self.msgWidth, 
                      bg=self.bgcolor)
        msg.grid()
                
        # set caption font if not defined yet
        if not self.captFont: self.setCaptFont(msg)
        msg.config(font=self.captFont)
        
        # position the window at the right bottom of mouse cursor
        x, y = self.winfo_pointerxy()
        xoffset = x + 10 # x + approx cursor size
        yoffset = y + 11 # y + approx cursor size
        self.caption.geometry('+{}+{}'.format(xoffset, yoffset))
        self.caption.overrideredirect(True)
    
    def hideCaption(self):
        """Destroy the 'self.caption' window."""
        self.caption.destroy()
        self.caption = None 

    def setCaptFont(self, msg):
        """Set the caption font to be the app font with a changed size."""
        font = tkFont.Font(font=msg['font'])  # the application's font
        font.configure(size=self.captFontSize)
        self.captFont = font                  # caption/hint font
    
