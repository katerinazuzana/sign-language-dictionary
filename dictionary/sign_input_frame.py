from tkinter import *
from shape_select_frame import ShapeSelectFrm, PassiveShapeSelectFrm
from radio_buttons import RadioFrm
from placement_frame import PlacementFrm


class SignInputFrm(Frame):

    def __init__(self, parent, imgdir, signSearchFcn, **options):
        super().__init__(parent, **options)
        self.imgdir = imgdir
        self.signSearchFcn = signSearchFcn
        self.bgcolor = options.get('bg', self['bg'])
        self.makeWidgets()
        self.focus_set()
       
    def makeWidgets(self):

        # create an active hand shapes offer
        self.actshapes = ShapeSelectFrm(self, self.imgdir, bg=self.bgcolor)
        self.actshapes.grid(column=0, row=0, 
                            sticky=N+S+W, pady=(0, 20))
        
        # create radio-buttons
        self.radiofrm = RadioFrm(self, self.imgdir, bg=self.bgcolor)
        self.radiofrm.grid(column=0, row=1, 
                           sticky=N+S+W, pady=(0, 20))

        # create canvas for sign-placement input
        placementfrm = PlacementFrm(self,
                                    self.imgdir, 
                                    bg=self.bgcolor)
        placementfrm.grid(column=0, row=2, sticky=W)

    def onSearchPress(self):
    
        signComponents = ((self.actshapes.var1.get(), 
                           self.actshapes.var2.get()), 
                           self.radiofrm.var.get(), 
                           self.radiofrm.passhapes.var1.get(), 
                          (self.placementfrm.canvas.ellipse.center.x, 
                           self.placementfrm.canvas.ellipse.center.y, 
                       abs(self.placementfrm.canvas.ellipse.a), 
                       abs(self.placementfrm.canvas.ellipse.b), 
                           self.placementfrm.canvas.ellipse.angle))

        self.signSearchFcn(*signComponents)
        




