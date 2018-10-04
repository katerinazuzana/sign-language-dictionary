from tkinter import *
from shape_select_frame import ShapeSelectFrm, PassiveShapeSelectFrm
from radio_buttons import RadioFrm
from placement_frame import PlacementFrm


class SignInputFrm(Frame):

    def __init__(self, parent, imgdir, signSearchFcn, canvasSize, **options):
        super().__init__(parent, **options)
        self.imgdir = imgdir
        self.signSearchFcn = signSearchFcn
        self.canvasSize = canvasSize
        self.bgcolor = options.get('bg', self['bg'])
        self.makeWidgets()
        self.focus_set()
       
    def makeWidgets(self):

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
                            sticky=N+E+S+W, pady=(0, 20))
        
        # create radio-buttons
        self.radiofrm = RadioFrm(self, self.imgdir, bg=self.bgcolor)
        self.radiofrm.grid(column=1, row=2, 
                           sticky=N+E+S+W, pady=(0, 20))

        # create canvas for sign-placement input
        self.placementfrm = PlacementFrm(self,
                                         self.imgdir, 
                                         self.canvasSize, 
                                         bg=self.bgcolor)
        self.placementfrm.grid(column=1, row=3, sticky=N+E+S+W)

    def onSearchPress(self):
    
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

        self.signSearchFcn(*signComponents)
        




