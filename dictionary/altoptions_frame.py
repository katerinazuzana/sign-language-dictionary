import tkinter as tk
import tkinter.font as tkFont


class AltsFrm(tk.Frame):
    """A frame displaying alternative options when the word was not found.

    When the czech expression from user input is not found in the database,
    some alternative expressions are suggested to the user. The alternative
    options are displayed in AltsFrm object, each option in its own label.
    """

    def __init__(self, parent, altoptions, searchfcn, **options):
        """Create a frame with an offer of options.

        Arguments:
            parent: the parent tkinter widget
            altoptions: a list of (str) options
            searchfcn: a function that does the search, takes a str argument
        """
        super().__init__(parent, **options)
        self.altoptions = altoptions
        self.searchfcn = searchfcn
        self.labbgcolor = options.get('bg', self['bg'])
        self.labFont = None
        self.labFontSize = 13
        self.makeWidgets()

    def makeWidgets(self):
        """Create the labels with alternative options."""

        for i in range(len(self.altoptions)):
            lab = tk.Label(self,
                           text=self.altoptions[i],
                           height=1,
                           bg=self.labbgcolor,
                           fg='red2',
                           cursor='hand2')
            lab.grid(column=0, row=i, sticky=tk.W, pady=0)

            if not self.labFont:
                font = tkFont.Font(font=lab['font'])  # current app font
                self.labFont = font.configure(size=self.labFontSize)
            lab.config(font=self.labFont)

            # when a label is clicked on, the corresponding video is played
            def onLabelClick(i):
                return lambda event: self.searchfcn(self.altoptions[i])
            lab.bind('<Button-1>', onLabelClick(i))
