import logging
import os

import vtk, ctk, qt

import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

import numpy as np

# If needed install libraries before imporing. If already installed, just import it.
try:
  import pyvista as pv
except ModuleNotFoundError:
  slicer.util.pip_install("pyvista")
  import pyvista as pv

try:
  import pymeshfix as mf
except ModuleNotFoundError:
  slicer.util.pip_install("pymeshfix")
  import pymeshfix as mf

#
# MeshVolumeComparison
#

class MeshVolumeComparison(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "MeshVolumeComparison"  # TODO: make this more human readable by adding spaces
        self.parent.categories = ["Quantification"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["Paolo Zaffino (Magna Graecia University of Catanzaro (Italy))", "Michela Desito (Magna Graecia University of Catanzaro (Italy))", "Maria Francesca Spadea (Karlsruher Intitute of Technology (Germany))"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#MeshVolumeComparison">module documentation</a>.
"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """
                                          """

#
# MeshVolumeComparisonWidget
#

class MeshVolumeComparisonWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Close mesh section
        closeMeshCollapsibleButton = ctk.ctkCollapsibleButton()
        closeMeshCollapsibleButton.text = "Close open mesh"
        self.layout.addWidget(closeMeshCollapsibleButton)

        closeMeshFormLayout = qt.QFormLayout(closeMeshCollapsibleButton)

        #
        # Open model selector
        #
        self.openModelSelector = slicer.qMRMLNodeComboBox()
        self.openModelSelector.nodeTypes = ["vtkMRMLModelNode"]
        self.openModelSelector.selectNodeUponCreation = True
        self.openModelSelector.addEnabled = False
        self.openModelSelector.removeEnabled = False
        self.openModelSelector.noneEnabled = False
        self.openModelSelector.showHidden = False
        self.openModelSelector.showChildNodeTypes = False
        self.openModelSelector.setMRMLScene( slicer.mrmlScene )
        self.openModelSelector.setToolTip( "Select the open model" )
        closeMeshFormLayout.addRow("Open model: ", self.openModelSelector)

        #
        # Close model selector
        #

        self.outputModelSelector = slicer.qMRMLNodeComboBox()
        self.outputModelSelector.nodeTypes = ["vtkMRMLModelNode"]
        self.outputModelSelector.selectNodeUponCreation = True
        self.outputModelSelector.addEnabled = True
        self.outputModelSelector.removeEnabled = True
        self.outputModelSelector.noneEnabled = True
        self.outputModelSelector.showHidden = False
        self.outputModelSelector.showChildNodeTypes = False
        self.outputModelSelector.setMRMLScene( slicer.mrmlScene )
        self.outputModelSelector.setToolTip( "Select or create the model to store the closed model" )
        closeMeshFormLayout.addRow("Closed model: ", self.outputModelSelector)

        #
        # Volume difference quantification Button
        #
        self.closeButton = qt.QPushButton("Close model")
        self.closeButton.toolTip = "Close the selected model"
        self.closeButton.enabled = False
        closeMeshFormLayout.addRow(self.closeButton)


        ####### Volume difference Section
        volumeDifferenceCollapsibleButton = ctk.ctkCollapsibleButton()
        volumeDifferenceCollapsibleButton.text = "Difference quantification"
        self.layout.addWidget(volumeDifferenceCollapsibleButton)

        volumeDifferenceFormLayout = qt.QFormLayout(volumeDifferenceCollapsibleButton)

        #
        # Model A selector
        #
        self.modelASelector = slicer.qMRMLNodeComboBox()
        self.modelASelector.nodeTypes = ["vtkMRMLModelNode"]
        self.modelASelector.selectNodeUponCreation = True
        self.modelASelector.addEnabled = False
        self.modelASelector.removeEnabled = False
        self.modelASelector.noneEnabled = False
        self.modelASelector.showHidden = False
        self.modelASelector.showChildNodeTypes = False
        self.modelASelector.setMRMLScene( slicer.mrmlScene )
        self.modelASelector.setToolTip( "Select the model A" )
        volumeDifferenceFormLayout.addRow("Model A: ", self.modelASelector)

        #
        # Model B selector
        #
        self.modelBSelector = slicer.qMRMLNodeComboBox()
        self.modelBSelector.nodeTypes = ["vtkMRMLModelNode"]
        self.modelBSelector.selectNodeUponCreation = True
        self.modelBSelector.addEnabled = False
        self.modelBSelector.removeEnabled = False
        self.modelBSelector.noneEnabled = False
        self.modelBSelector.showHidden = False
        self.modelBSelector.showChildNodeTypes = False
        self.modelBSelector.setMRMLScene( slicer.mrmlScene )
        self.modelBSelector.setToolTip( "Select the model B" )
        volumeDifferenceFormLayout.addRow("Model B: ", self.modelBSelector)

        # Volume Difference QLabel
        self.QLabelVolumeDifference = qt.QLabel("")
        volumeDifferenceFormLayout.addRow("Volume difference = ", self.QLabelVolumeDifference)

        #
        # Volume difference quantification Button
        #
        self.differenceButton = qt.QPushButton("Compute A-B volume difference")
        self.differenceButton.toolTip = "Compute the volume difference"
        self.differenceButton.enabled = False
        volumeDifferenceFormLayout.addRow(self.differenceButton)


        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = MeshVolumeComparisonLogic()

        # Connections
        self.closeButton.connect('clicked(bool)', self.onCloseButton)
        self.openModelSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onCloseSelect)
        self.outputModelSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onCloseSelect)

        self.differenceButton.connect('clicked(bool)', self.onDifferenceButton)
        self.modelASelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onDifferenceSelect)
        self.modelBSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onDifferenceSelect)

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def cleanup(self):
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def onDifferenceSelect(self):
        self.differenceButton.enabled = self.modelASelector.currentNode() and self.modelBSelector.currentNode()

    def onCloseSelect(self):
        self.closeButton.enabled = self.openModelSelector.currentNode() and self.outputModelSelector.currentNode()


    def onDifferenceButton(self):
        """
        Run processing when user clicks "Apply" button.
        """
        with slicer.util.tryWithErrorDisplay("Failed to compute results.", waitCursor=True):
            # Compute output
            volumeDifference = self.logic.computeVolumeDifference(self.modelASelector.currentNode().GetName(), self.modelBSelector.currentNode().GetName())
            self.QLabelVolumeDifference.setText("%.1f" % volumeDifference)

    def onCloseButton(self):
        """
        Run processing when user clicks "Apply" button.
        """
        with slicer.util.tryWithErrorDisplay("Failed to compute results.", waitCursor=True):
            # Compute output
            self.logic.closeMesh(self.openModelSelector.currentNode().GetName(), self.outputModelSelector.currentNode().GetName())


    def onSceneStartClose(self, caller, event):
        """
        Called just before the scene is closed.
        """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event):
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()


    def setParameterNode(self, inputParameterNode):
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if inputParameterNode:
            self.logic.setDefaultParameters(inputParameterNode)

        # Unobserve previously selected parameter node and add an observer to the newly selected.
        # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
        # those are reflected immediately in the GUI.
        if self._parameterNode is not None and self.hasObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode):
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        self._parameterNode = inputParameterNode
        if self._parameterNode is not None:
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

        # Initial GUI update
        self.updateGUIFromParameterNode()

    def initializeParameterNode(self):
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())


    def updateGUIFromParameterNode(self, caller=None, event=None):
        """
        This method is called whenever parameter node is changed.
        The module GUI is updated to show the current state of the parameter node.
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return


#
# MeshVolumeComparisonLogic
#

class MeshVolumeComparisonLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self):
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """

        ScriptedLoadableModuleLogic.__init__(self)

    def setDefaultParameters(self, parameterNode):
        """
        Initialize parameter node with default settings.
        """
        if not parameterNode.GetParameter("Threshold"):
            parameterNode.SetParameter("Threshold", "100.0")
        if not parameterNode.GetParameter("Invert"):
            parameterNode.SetParameter("Invert", "false")

    def computeVolumeDifference(self, modelAName, modelBName):
        modelANode = slicer.util.getNode(modelAName)
        modelA_pv = pv.PolyData(modelANode.GetPolyData())

        modelBNode = slicer.util.getNode(modelBName)
        modelB_pv = pv.PolyData(modelBNode.GetPolyData())

        return modelA_pv.volume - modelB_pv.volume

    def closeMesh(self, openMeshName, closedMeshName):
        modelNode = slicer.util.getNode(openMeshName)
        model_pv = pv.PolyData(modelNode.GetPolyData())

        meshfix = mf.MeshFix(model_pv.triangulate())
        holes = meshfix.extract_holes()
        meshfix.repair(verbose=True)

        fixedModelNode = slicer.util.getNode(closedMeshName)
        fixedModelNode.SetAndObservePolyData(meshfix.mesh.extract_surface())

#
# MeshVolumeComparisonTest
#

class MeshVolumeComparisonTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_MeshVolumeComparison1()

    def test_MeshVolumeComparison1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")

        # Get/create input data

        import SampleData
        registerSampleData()
        inputVolume = SampleData.downloadSample('MeshVolumeComparison1')
        self.delayDisplay('Loaded test data set')

        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertEqual(inputScalarRange[0], 0)
        self.assertEqual(inputScalarRange[1], 695)

        outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        threshold = 100

        # Test the module logic

        logic = MeshVolumeComparisonLogic()

        # Test algorithm with non-inverted threshold
        logic.process(inputVolume, outputVolume, threshold, True)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], threshold)

        # Test algorithm with inverted threshold
        logic.process(inputVolume, outputVolume, threshold, False)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], inputScalarRange[1])

        self.delayDisplay('Test passed')
