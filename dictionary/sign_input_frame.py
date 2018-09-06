from tkinter import *
from shape_select_frame import ShapeSelectFrm, PassiveShapeSelectFrm
from radio_buttons import RadioFrm
from placement_frame import PlacementFrm


class SignInputFrm(Frame):

    def __init__(self, parent, bgcolor, imgdir, searchfcn, **options):
        
        super().__init__(parent, **options)
        self.bgcolor = bgcolor
        self.imgdir = imgdir
        self.searchfcn = searchfcn
        self.makeWidgets()
       
    def makeWidgets(self):

        # create an active hand shapes offer
        self.actshapes = ShapeSelectFrm(self, self.imgdir, self.bgcolor)
        self.actshapes.grid(column=0, row=0, 
                            columnspan=2, sticky=N+E+S+W, pady=(0, 20))
        
        # create radio-buttons
        self.radiofrm = RadioFrm(self, self.imgdir, self.bgcolor)
        self.radiofrm.grid(column=0, row=1, 
                           columnspan=2, sticky=N+S+W, pady=(0, 20))
        
        # create canvas for sign-placement input
        Label(self, 
              text='Místo artikulace znaku', 
              bg=self.bgcolor
              ).grid(column=0, row=2, columnspan=2, sticky=W, pady=(0, 3))
        
        placementfrm = PlacementFrm(self)
        placementfrm.grid(column=0, row=3, sticky=W)
        
        # create the Search button
        Button(self, 
               text='Vyhledat', 
               command=self.searchfcn
               ).grid(column=1, row=3, 
                                sticky=E+S, 
                                padx=(15, 0))

