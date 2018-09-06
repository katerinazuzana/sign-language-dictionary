from tkinter import *

class PlacementFrm(Frame):
    def __init__(self, parent, bgcolor, **options):
        super().__init__(parent, **options)
        self.bgcolor = bgcolor
        self.makeWidgets()
        
    def makeWidgets(self):
        self.rowconfigure(1, weight=1)
        
        Label(self, 
              text='Místo artikulace znaku', 
              bg=self.bgcolor
              ).grid(column=0, row=0, columnspan=2, sticky=W, pady=(0, 3))
        
        self.canvas = Canvas(self, width=240, 
                                   height=250, 
                                   borderwidth=2, 
                                   relief='groove')
        self.canvas.grid(column=0, row=1, rowspan=2)
        
        Button(self, 
               text='Zrušit', 
               command=self.onDelete,
               ).grid(column=1, row=1, sticky=S+W, padx=(15, 0))
        
        Button(self, 
               text='Vyhledat', 
               command=self.master.onSearchPress,
               ).grid(column=1, row=2, sticky=S+W, padx=(15, 0), pady=(8, 0))
        
    def onDelete(self):
        pass
    
