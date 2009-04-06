#!/usr/bin/env python

## Program:   VMTK
## Module:    $RCSfile: vmtksurfacetransforminteractive.py,v $
## Language:  Python
## Date:      $Date: 2009/01/30 15:52:00 $
## Version:   $Revision: 1.0 $

##   Copyright (c) Luca Antiga, David Steinman. All rights reserved.
##   See LICENCE file for details.

##      This software is distributed WITHOUT ANY WARRANTY; without even 
##      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
##      PURPOSE.  See the above copyright notices for more information.

## Note: this class was contributed by 
##       Hugo Gratama van Andel
##       Academic Medical Centre - University of Amsterdam
##       Dept. Biomedical Engineering  & Physics

import vtk
import sys

from vmtk import vmtkrenderer
from vmtk import pypes

vmtksurfacetransforminteractive = 'vmtkSurfaceTransformInteractive'

class vmtkSurfaceTransformInteractive(pypes.pypeScript):

    def __init__(self):
 
        pypes.pypeScript.__init__(self)
 
        self.Surface = None
        self.TransformedSurface = vtk.vtkPolyData()
        self.ReferenceSurface = None
        self.vmtkRenderer = None
        self.OwnRenderer = 0
 
        self.Actor = None
        self.BoxWidget = None
        self.Matrix4x4 = None
        self.Transform = None
        self.TransformFilter = None
        self.Scaling = 0
 
        self.SetScriptName('vmtksurfacetransforminteractive')
        self.SetScriptDoc('interactively transform a surface to another surface')
        self.SetInputMembers([
            ['Surface','i','vtkPolyData',1,'','the input surface','vmtksurfacereader'],
            ['ReferenceSurface','r','vtkPolyData',1,'','the reference surface','vmtksurfacereader'],
            ['Scaling','scaling','bool',1,'','allow scaling of surface'],            
            ['vmtkRenderer','renderer','vmtkRenderer',1,'','external renderer']
            ])
        self.SetOutputMembers([
            ['Surface','o','vtkPolyData',1,'','the output surface','vmtksurfacewriter'],
            ['Matrix4x4','omatrix4x4','vtkMatrix4x4',1,'','the output transform matrix']
            ])
 
    def KeyPressed(self,object,event):
        key = object.GetKeySym()
        if key != 'space':
            return
        if self.BoxWidget.GetEnabled() != 1:
            return
        self.BoxWidget.GetTransform(self.Transform)
        self.TransformFilter.Update()
 
        self.TransformedSurface.ShallowCopy(self.TransformFilter.GetOutput())
        self.TransformedSurface.Update()
 
        if self.TransformedSurface.GetSource():
            self.TransformedSurface.GetSource().UnregisterAllOutputs()
 
        self.vmtkRenderer.RenderWindow.Render()     
 
    def Display(self):
 
        self.Surface.ComputeBounds()
      	self.BoxWidget.PlaceWidget(self.Surface.GetBounds())
 
      	self.vmtkRenderer.RenderWindowInteractor.Initialize()
 
        self.vmtkRenderer.RenderWindowInteractor.AddObserver("KeyPressEvent", self.KeyPressed)
        self.vmtkRenderer.RenderWindow.Render()
        self.vmtkRenderer.RenderWindowInteractor.Start()
 
    def Execute(self):
 
        if (self.Surface == None):
            self.PrintError('Error: no Surface.')
 
        #if (self.ReferenceSurface == None):
        #    self.PrintError('Error: no Reference Surface.')
 
        if not self.vmtkRenderer:
            self.vmtkRenderer = vmtkrenderer.vmtkRenderer()
            self.vmtkRenderer.Initialize()
            self.OwnRenderer = 1
 
        if self.Transform == None:   
            self.Transform = vtk.vtkTransform()
 
        if self.TransformFilter == None:
            self.TransformFilter= vtk.vtkTransformPolyDataFilter()
 
        self.TransformFilter.SetInput(self.Surface)
        self.TransformFilter.SetTransform(self.Transform)
 
        self.TransformFilter.Update()
        self.TransformFilter.GetOutput().Update()
 
        self.TransformedSurface.ShallowCopy(self.TransformFilter.GetOutput())
        self.TransformedSurface.Update()
 
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInput(self.TransformedSurface)
 
        mapper.ScalarVisibilityOff()
 
        self.Actor = vtk.vtkActor()
        self.Actor.SetMapper(mapper)
        self.Actor.GetProperty().SetColor(1.0, 0.1, 0.1)
        #self.Actor.GetProperty().SetOpacity(0.5)        
        self.vmtkRenderer.Renderer.AddActor(self.Actor)

        if self.ReferenceSurface: 
            mapper2 = vtk.vtkPolyDataMapper()
            mapper2.SetInput(self.ReferenceSurface)
            mapper2.ScalarVisibilityOff()
     
            self.Actor2 = vtk.vtkActor()
            self.Actor2.SetMapper(mapper2)
            self.Actor2.GetProperty().SetColor(1.0, 1.0, 1.0)
            self.Actor2.GetProperty().SetOpacity(0.5)
     
            self.vmtkRenderer.Renderer.AddActor(self.Actor2)        
 
        self.BoxWidget = vtk.vtkBoxWidget()
        self.BoxWidget.SetInteractor(self.vmtkRenderer.RenderWindowInteractor)
        self.BoxWidget.GetFaceProperty().SetColor(0.6,0.6,0.2)
        self.BoxWidget.GetFaceProperty().SetOpacity(0.25)
        self.BoxWidget.ScalingEnabledOff()
        self.BoxWidget.HandlesOff()
 
        if self.Scaling:
            self.BoxWidget.ScalingEnabledOn()
            self.BoxWidget.HandlesOn()
 
        self.OutputText('Press \'i\' to activate the box widget interactor \n')
        self.OutputText('Use the left-mousebutton to rotate the box \n')
        self.OutputText('Use the middle-mouse-button to move the box \n')
        self.OutputText('Press space to move the surface to its new postion \n')
        self.OutputText('Press \'q\' to quit and apply the transform \n')
 
        self.Display()
 
        self.Surface = self.TransformedSurface
 
        self.Matrix4x4 = self.Transform.GetMatrix()
 
        if self.OwnRenderer:
            self.vmtkRenderer.Deallocate()
 
 
if __name__=='__main__':
    main = pypes.pypeMain()
    main.Arguments = sys.argv
    main.Execute()
 
