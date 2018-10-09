from tkinter import *
from shape_select_frame import ShapeSelectFrm
from radio_buttons import RadioFrm
from placement_frame import PlacementFrm


class SignInputFrm(Frame):
    """A frame for sign input.
    
    The sign that the user wants to be translated from czech sign language 
    to czech is specified by its components: handshapes and sign placement.
    
    SignInputFrm contains widgets:
    - 'self.actshapes' frame for selecting a handshape of the active hand
    - 'self.radiofrm' frame for choosing the type of the sign, and possibly
        also a handshape of the passive hand
    - 'self.placementfrm' frame with a drawing canvas for specifying where 
        the sign is located, and with a Search button that starts a search
        for signs that correspond the best to the sign components specified
        in SignInputFrm
    """
    
    def __init__(self, parent, imgdir, signSearchFcn, canvasSize, **options):
        """Initialize the SignInputFrm object.
        
        Arguments:
            parent: a parent tkinter widget
            imgdir (str): a path to the directory with images
            signSearchFcn: a function that does a search to find the most
                similar signs to the one from the user input
            canvasSize (tuple): a tuple of the form (width (int), height (int))
                defining the size of a canvas that serves to insert the desired
                placement of the sign
        """
        super().__init__(parent, **options)
        self.imgdir = imgdir
        self.signSearchFcn = signSearchFcn
        self.canvasSize = canvasSize
        self.bgcolor = options.get('bg', self['bg'])
        self.verticalSpace = 20   # vertical space between the widgets
        self.makeWidgets()
        self.focus_set()
       
    def makeWidgets(self):
        """Create the 'self.actshapes', 'self.radiofrm' and 
        'self.placementfrm' widgets.
        """
        self.columnconfigure(0, weight=1)  # empty column
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=2)  # empty column
        
        self.rowconfigure(0, weight=1)  # empty row
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)  # empty row
        
        # create an active hand shapes offer
        self.actshapes = ShapeSelectFrm(self, self.imgdir, bg=self.bgcolor)
        self.actshapes.grid(column=1, row=1, 
                            sticky=N+E+S+W, 
                            pady=(0, self.verticalSpace))
        
        # create radio-buttons
        self.radiofrm = RadioFrm(self, self.imgdir, bg=self.bgcolor)
        self.radiofrm.grid(column=1, row=2, 
                           sticky=N+E+S+W, 
                           pady=(0, self.verticalSpace))

        # create canvas for sign-placement input
        self.placementfrm = PlacementFrm(self,
                                         self.imgdir, 
                                         self.canvasSize, 
                                         bg=self.bgcolor)
        self.placementfrm.grid(column=1, row=3, sticky=N+E+S+W)

    def onSearchPress(self):
        """Call 'self.signSearchFcn' to start the search for similar signs."""
        if self.placementfrm.canvas.ellipse:
            # an ellipse object exists
            ellipseParams = (self.placementfrm.canvas.ellipse.center.x, 
                             self.placementfrm.canvas.ellipse.center.y, 
                         abs(self.placementfrm.canvas.ellipse.a), 
                         abs(self.placementfrm.canvas.ellipse.b), 
                             self.placementfrm.canvas.ellipse.angle)
        else:
            # no ellipse was drawn
            ellipseParams = None
        
        signComponents = ((self.actshapes.var1.get(), 
                           self.actshapes.var2.get()), 
                           self.radiofrm.var.get(), 
                           self.radiofrm.passhapes.var1.get(), 
                           ellipseParams)
        self.signSearchFcn(signComponents)
        
