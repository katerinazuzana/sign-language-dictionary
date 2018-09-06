from tkinter import *
from shape_select_frame import ShapeSelectFrm, PassiveShapeSelectFrm
from radio_buttons import RadioFrm
from placement_frame import PlacementFrm


class SignInputFrm(Frame):

    def __init__(self, parent, bgcolor, imgdir, signSearchFcn, **options):
        
        super().__init__(parent, **options)
        self.bgcolor = bgcolor
        self.imgdir = imgdir
        self.signSearchFcn = signSearchFcn
        self.makeWidgets()
       
    def makeWidgets(self):

        # create an active hand shapes offer
        self.actshapes = ShapeSelectFrm(self, self.imgdir, self.bgcolor)
        self.actshapes.grid(column=0, row=0, 
                            sticky=N+E+S+W, pady=(0, 20))
        
        # create radio-buttons
        self.radiofrm = RadioFrm(self, self.imgdir, self.bgcolor)
        self.radiofrm.grid(column=0, row=1, 
                           sticky=N+S+W, pady=(0, 20))

        # create canvas for sign-placement input
        placementfrm = PlacementFrm(self, 
                                    self.bgcolor, 
                                    bg=self.bgcolor)
        placementfrm.grid(column=0, row=2, sticky=W)

    def onSearchPress(self):
    
        signComponents = ((self.actshapes.sel1, self.actshapes.sel1), 
                          (self.radiofrm.var.get(), 
                           self.radiofrm.passhapes.sel1), 
                          (None,))
        # TODO fetch the ellipse
        self.signSearchFcn(*signComponents)
        




