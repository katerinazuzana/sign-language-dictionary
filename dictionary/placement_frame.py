from tkinter import *
from PIL import Image, ImageTk
import os

class PlacementFrm(Frame):
    def __init__(self, parent, imgdir, bgcolor, **options):
        super().__init__(parent, **options)
        self.bgcolor = bgcolor
        self.hintIconPath = os.path.join(imgdir, 'hint_icon.png')
        
        self.hintSize = 14
        self.hint = None
        self.hintText = 'Klepnutím a tažením nakreslete elipsu.' + \
                        ' Nápovědu zavřete kliknutím na ikonu.'
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
        self.hintButton = Button(self, 
                                 image=self.icon, 
                                 command=self.onHintPress)
        self.hintButton.grid(column=1, row=0, 
                             sticky=W, 
                             padx=(8, 0), pady=(0, 3))
        
        # create a canvas and buttons
        self.canvas = Canvas(self, width=240, 
                                   height=250, 
                                   borderwidth=2, 
                                   relief='groove')
        self.canvas.grid(column=0, row=1, columnspan=2, rowspan=2)        
        Button(self, 
               text='Zrušit', 
               command=self.onDelete
               ).grid(column=2, row=1, sticky=S+W, padx=(15, 0))
        Button(self, 
               text='Vyhledat', 
               command=self.master.onSearchPress
               ).grid(column=2, row=2, sticky=S+W, padx=(15, 0), pady=(8, 0))
    
    def onHintPress(self):
        if not self.hint:
            self.openHint()
        else:
            self.closeHint()
    
    def openHint(self):
        self.hint = Toplevel()
        Message(self.hint, 
             text=self.hintText, 
             width=200, 
             font=('Helvetica', 10),
             bg=self.bgcolor).grid()
        
        xoffset = self.hintButton.winfo_rootx() + self.hintSize
        yoffset = self.hintButton.winfo_rooty() + self.hintSize
        self.hint.geometry('+{}+{}'.format(xoffset, yoffset))
        self.hint.overrideredirect(True)
        
        self.hint.focus_set()
        self.hint.bind('<FocusOut>', lambda: self.closeHint())
    
    def closeHint(self):
        self.hint.destroy()
        self.hint = None
        
    def onDelete(self):
        pass



    
