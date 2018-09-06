from tkinter import *
from PIL import Image, ImageTk
import os

class PlacementFrm(Frame):
    def __init__(self, parent, imgdir, bgcolor, **options):
        super().__init__(parent, **options)
        self.bgcolor = bgcolor
        
        self.hintIconPath = os.path.join(imgdir, 'hint_icon.png')
        self.delIconPath = os.path.join(imgdir, 'del_icon.png')
        self.delIconSize = 30
        self.searchIconPath = os.path.join(imgdir, 'search_icon.png')
        self.searchIconSize = 40
        
        self.hintSize = 14
        self.hintText = 'Klepnutím a tažením nakreslete elipsu.' + \
                        ' Tady bude další instrukce.'
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
        self.hintIcon.bind('<Enter>', self.openHint)
        self.hintIcon.bind('<Leave>', self.closeHint)
        
        # create a canvas
        self.canvas = Canvas(self, width=240, 
                                   height=250, 
                                   borderwidth=2, 
                                   relief='groove')
        self.canvas.grid(column=0, row=1, columnspan=2, rowspan=2)        
        
        # create delete button
        with Image.open(self.delIconPath) as img:
            img = img.resize((self.delIconSize, self.delIconSize), 
                             Image.LANCZOS)
            self.delImg = ImageTk.PhotoImage(img)
        Button(self, 
               image=self.delImg, 
               command=self.onDelete
               ).grid(column=2, row=1, sticky=S+W, padx=(15, 0))
        
        # create search sign button
        with Image.open(self.searchIconPath) as img:
            img = img.resize((self.searchIconSize, self.searchIconSize), 
                             Image.LANCZOS)
            self.searchImg = ImageTk.PhotoImage(img)
        Button(self, 
               image=self.searchImg, 
               command=self.master.onSearchPress
               ).grid(column=2, row=2, sticky=S+W, padx=(15, 0), pady=(8, 0))
    
    def openHint(self, event):
        self.hint = Toplevel()
        Message(self.hint, 
             text=self.hintText, 
             width=150, 
             font=('Helvetica', 10),
             bg=self.bgcolor).grid()
        
        xoffset = self.hintIcon.winfo_rootx() + self.hintSize
        yoffset = self.hintIcon.winfo_rooty() + self.hintSize
        self.hint.geometry('+{}+{}'.format(xoffset, yoffset))
        self.hint.overrideredirect(True)
    
    def closeHint(self, event):
        self.hint.destroy()
        
    def onDelete(self):
        pass



    
