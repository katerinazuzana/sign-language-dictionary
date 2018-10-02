from tkinter import *
from PIL import Image, ImageTk
import os
from drawing_canvas import DrawingCanvas


class PlacementFrm(Frame):
    def __init__(self, parent, imgdir, **options):
        super().__init__(parent, **options)
        self.bgcolor = options.get('bg', self['bg'])
        
        self.hintIconPath = os.path.join(imgdir, 'hint_icon.png')
        self.delIconPath = os.path.join(imgdir, 'del_icon.png')
        self.delIconSize = 30
        self.searchIconPath = os.path.join(imgdir, 'search_icon.png')
        self.searchIconSize = 40
        self.delay = 1000 # how long to wait before button description shows up
        self.caption = None
        self.captFont = ('Helvetica', 10)
        
        self.hintSize = 14
        self.hintText = 'Klepnutím a tažením nakreslete elipsu,'+\
                       ' která bude vyznačovat umístění znaku.'+\
                       ' Elipsu lze myší přesouvat.'+\
                       ' Po dvojkliku na elipsu je možné měnit její velikost.'+\
                       ' Po dalším dvojkliku lze elipsou otáčet.'
        self.makeWidgets()
        
    def makeWidgets(self):
        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)
        
        Label(self, 
              text='Místo artikulace znaku', 
              bg=self.bgcolor
              ).grid(column=0, row=0, sticky=W, pady=(0, 3))
        
        # create hint icon
        with Image.open(self.hintIconPath) as img:
            img = img.resize((self.hintSize, self.hintSize), Image.LANCZOS)
            self.icon = ImageTk.PhotoImage(img)
        self.hintIcon = Label(self, image=self.icon)
        self.hintIcon.grid(column=1, row=0, 
                           sticky=W, 
                           padx=(8, 0))
        # when mouse is over the icon, show the hintText
        self.hintIcon.bind('<Enter>', self.showHint)
        self.hintIcon.bind('<Leave>', self.hideHint)
        
        # create a canvas
        self.canvas = DrawingCanvas(self, 
                                    width=240, 
                                    height=250, 
                                    borderwidth=2, 
                                    relief='groove')
        self.canvas.grid(column=0, row=1, columnspan=2, rowspan=2)        
        
        # create delete button
        with Image.open(self.delIconPath) as img:
            img = img.resize((self.delIconSize, self.delIconSize), 
                             Image.LANCZOS)
            self.delImg = ImageTk.PhotoImage(img)
        delButton = Button(self, 
                           image=self.delImg, 
                           command=self.onDelete)
        delButton.grid(column=2, row=1, sticky=S+W, padx=(15, 0))       
        # when mouse is over the button for a while, show a caption
        delButton.bind('<Enter>', lambda ev: self.onButEnter('Zrušit'))
        delButton.bind('<Leave>', self.onButLeave)
        
        # create search sign button
        with Image.open(self.searchIconPath) as img:
            img = img.resize((self.searchIconSize, self.searchIconSize), 
                             Image.LANCZOS)
            self.searchImg = ImageTk.PhotoImage(img)
        searchButton = Button(self, 
               image=self.searchImg, 
               command=self.master.onSearchPress)
        searchButton.grid(column=2, row=2, 
                          sticky=S+W, 
                          padx=(15, 0), pady=(8, 0))
        
        # when mouse is over the button for a while, show a caption
        searchButton.bind('<Enter>', lambda ev: self.onButEnter('Vyhledat'))
        searchButton.bind('<Leave>', self.onButLeave)
    
    def showHint(self, event):
        self.hint = Toplevel()
        Message(self.hint, 
                text=self.hintText, 
                width=150, 
                font=self.captFont,
                bg=self.bgcolor).grid()
        
        xoffset = self.hintIcon.winfo_rootx() + self.hintSize
        yoffset = self.hintIcon.winfo_rooty() + self.hintSize
        self.hint.geometry('+{}+{}'.format(xoffset, yoffset))
        self.hint.overrideredirect(True)
    
    def hideHint(self, event):
        self.hint.destroy()
        
    def onDelete(self):
        self.canvas.delete(ALL)
        self.canvas.ellipse = None
        self.canvas.drawMode = True
        self.canvas.moveMode = False
        self.canvas.scaleMode = False
        self.canvas.rotateMode = False

    def onButEnter(self, text):
        self.job = self.after(self.delay, lambda: self.showCaption(text))
    
    def onButLeave(self, event):
        self.after_cancel(self.job)
        if self.caption: self.hideCaption()
    
    def showCaption(self, text):
        self.caption = Toplevel()
        Message(self.caption, 
                text=text, 
                width=100, 
                font=self.captFont,
                bg=self.bgcolor).grid()
        
        x, y = self.winfo_pointerxy()
        xoffset = x + 10 # x + approx cursor size
        yoffset = y + 11 # y + approx cursor size
        self.caption.geometry('+{}+{}'.format(xoffset, yoffset))
        self.caption.overrideredirect(True)
    
    def hideCaption(self):
        self.caption.destroy()
        self.caption = None 

    
