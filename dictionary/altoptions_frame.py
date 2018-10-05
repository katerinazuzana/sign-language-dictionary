from tkinter import *
import tkinter.font as tkFont


class AltsFrm(Frame):
    """A frame where alternative options to the word given 
    by the user are displayed. The AltsFrm object is to be displayed 
    when the search for the word is not successfull.
    Each option is displayed on its own Label.
    """
   
    def __init__(self, altoptions, searchfcn, labbgcolor, parent, **options):
        """Create the labels with the options.
        
        Arguments:
        altoptions -- a list of strings
        searchfcn -- a function that does the search,
                     takes one [str] argument
        labbgcolor -- [str] background color of the labels
        parent -- the parent tkinter widget
        """
        super().__init__(parent, **options)
        self.altoptions = altoptions
        self.searchfcn = searchfcn
        self.labbgcolor = labbgcolor
        
        self.labFont = None
        self.labFontSize = 13
        self.makeWidgets()

    def makeWidgets(self):
        for i in range(len(self.altoptions)):
            lab = Label(self, text=self.altoptions[i],
                              height=1, 
                              bg=self.labbgcolor,
                              fg='red2',
                              cursor='hand2')
            lab.grid(column=0, row=i, sticky=W, pady=0)
            
            if not self.labFont:
                font = tkFont.Font(font=lab['font']) # current application font
                self.labFont = font.configure(size=self.labFontSize)
            lab.config(font=self.labFont)
            
            # when a label is clicked on, the corresponding video is played
            def onLabelClick(i):
                return lambda event: self.searchfcn(self.altoptions[i])
            lab.bind('<Button-1>', onLabelClick(i))


