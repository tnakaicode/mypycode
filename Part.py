import os, path
from abc import abstractmethod
from collections import MutableMapping

from OCC.Graphic3d import Graphic3d_NOM_ALUMINIUM
from OCC.TopoDS import TopoDS_Shape, TopoDS_Vertex
from OCC.StlAPI import StlAPI_Writer
from OCC.AIS import AIS_Shape
from OCC.gp import gp_Pnt
from OCCUtils.Construct import make_vertex, make_line, make_box

# FileIO libraries:
from OCC.STEPCAFControl import STEPCAFControl_Writer
from OCC.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Interface import Interface_Static_SetCVal
from OCC.IFSelect import IFSelect_RetDone
from OCC.TDF import TDF_LabelSequence
from OCC.TCollection import TCollection_ExtendedString
from OCC.TDocStd import Handle_TDocStd_Document
from OCC.XCAFApp import XCAFApp_Application
from OCC.XCAFDoc import (XCAFDoc_DocumentTool_ShapeTool,
                         XCAFDoc_DocumentTool_ColorTool,
                         XCAFDoc_DocumentTool_LayerTool,
                         XCAFDoc_DocumentTool_MaterialTool)

class Base(MutableMapping, object):
    """
    Base container class from which other base classes are derived from.
    This is a an abstract base class and should not be used directly by users.

    Notes
    -----
    When properly defined in inherited functions, this class should behave like
    a dictionary.

    As this class inherits from MutableMapping, any class inherting from
    AirconicsBase must also define the abstract methods of Mutable mapping,
    i.e. __setitem__, __getitem__, __len__, __iter__, __delitem__
    """
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def __str__(self, *args, **kwargs):
        pass

    @abstractmethod
    def Display(self, *args, **kwargs):
        pass

    @abstractmethod
    def Write(self, *args, **kwargs):
        pass

    @abstractmethod
    def Build(self, *args, **kwargs):
        pass

class Part (Base):
    def __init__(self, parts={}, construct_geometry=False, *args, **kwargs):
        # Set the components dictionary (default empty)
        self._Parts = {}
        for name, part in parts.items():
            self.__setitem__(name, part)

        # Set all kwargs as attributes
        for key, value in kwargs.items():
            self.__setattr__(key, value)

        self.construct_geometry = construct_geometry

        if self.construct_geometry:
            self.Build()
        else:
            print("Skipping geometry construction for {}".format(
                type(self).__name__))

    def __getitem__(self, name):
        return self._Parts[name]

    def __setitem__(self, name, part):
        """Note no error checks done here: users responsible for content
        of this class"""
        self._Parts[name] = part

    def __delitem__(self, name):
        del self._Parts[name]

    def __iter__(self):
        return iter(self._Parts)

    def __len__(self):
        return len(self._Parts)

    def __str__(self):
        """Overloads print output to display the names of components in
        the object instance"""
        output = str(self.keys())   # Note self.keys are self._Parts.keys
        return output

    def AddPart(self, part, name=None):
        if name is None:
            # set a default name:
            name = 'part_' + str(len(self))
        self.__setitem__(name, part)

    def Build(self):
        print("Attempting to construct {} geometry...".format(type(self).__name__))

    def Display(self, context, material=Graphic3d_NOM_ALUMINIUM, color=None):
        for name, component in self.items():
            try:
                component.Display(context, material, color)
            except AttributeError:
                # We are probably dealing with a core pythonocc shape:
                try:
                    context.DisplayShape(component)
                except:
                    print("Could not display shape type {}: skipping".format(
                        type(component)))
    
    def Write(self, filename, single_export=True):
        """Writes the Parts contained in this instance to file specified by
        filename.

        One file is produced, unless single_export is False when one file
        is written for each Part.

        Parameters
        ---------
        filename : string
        
        single_export : bool
            returns a single output file if true, otherwise writes one file
            per part

        Returns
        -------
        status : list
            The flattened list of error codes returned by writing each part

        Notes
        -----
        * Calls the .Write method belonging to each Part

        See Also
        --------
        AirconicsBase
        """
        path, ext = os.path.splitext(filename)
        status = []
        print (single_export)
        
        if single_export:
            shapes = []
            for partname, part in self.items():
                shapes.append(part)
            status.append(export_STEPFile(shapes, filename))
        else:
            # not complete 
            for name, part in self.items():
                f = path + '_' + name + ext
                print (f)
                status.append(Part.Write(f, single_export=True))
        return status

def export_STEPFile(shapes, filename):
    """Exports a .stp file containing the input shapes

    Parameters
    ----------
    shapes : list of TopoDS_Shape
        Shapes to write to file

    filename : string
        The output filename
    """
    # initialize the STEP exporter
    step_writer = STEPControl_Writer()
    Interface_Static_SetCVal("write.step.schema", "AP214") # Use default?

    # transfer shapes
    for shape in shapes:
        step_writer.Transfer(shape, STEPControl_AsIs)

    status = step_writer.Write(filename)

    assert(status == IFSelect_RetDone)
    return status

if __name__ == "__main__":
    from OCC.Display.SimpleGui import init_display
    display, start_display, add_menu, add_function_to_menu = init_display()

    p0 = make_vertex (gp_Pnt(0, 0, 0))
    p1 = make_vertex (gp_Pnt(0, 0, 1))
    p2 = make_vertex (gp_Pnt(0, 1, 1))
    
    shape = Part ()
    shape["line_1"] = make_line (p0, p1) 
    shape["line_2"] = make_line (p1, p2) 
    shape["line_3"] = make_line (p2, p0)
    shape.Display (display)
    shape.Write ("lines.stp", True)

    display.FitAll()
    start_display()