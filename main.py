##Copyright 2009-2015 Thomas Paviot (tpaviot@gmail.com)
##
##This file is part of pythonOCC.
##
##pythonOCC is free software: you can redistribute it and/or modify
##it under the terms of the GNU Lesser General Public License as published by
##the Free Software Foundation, either version 3 of the License, or
##(at your option) any later version.
##
##pythonOCC is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU Lesser General Public License for more details.
##
##You should have received a copy of the GNU Lesser General Public License
##along with pythonOCC.  If not, see <http://www.gnu.org/licenses/>.

import math
import numpy as np

from OCC.gp import (gp_Pnt, gp_Sphere, gp_Ax3, gp_Dir, gp_Circ, gp_Ax2,
                    gp_Pnt2d, gp_Dir2d)
from OCC.BRepBuilderAPI import (BRepBuilderAPI_MakeEdge,
                                BRepBuilderAPI_MakeFace,
                                BRepBuilderAPI_MakeWire)
from OCC.TColgp import TColgp_Array2OfPnt
from OCC.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCC.GeomAbs import GeomAbs_C2, GeomAbs_C0, GeomAbs_G1, GeomAbs_G2
from OCC.Geom2d import Geom2d_Line
from OCC.BRepLib import breplib_BuildCurves3d
from OCC.Quantity import Quantity_Color, Quantity_NOC_PINK

from OCC.Display.SimpleGui import init_display

def face(px, py, pz):
    nx, ny = px.shape
    pnt_2d = TColgp_Array2OfPnt(1, nx+1, 1, ny+1)
    for row in range (pnt_2d.LowerRow(), pnt_2d.UpperRow()):
        for col in range (pnt_2d.LowerCol(), pnt_2d.UpperCol()):
            i,j = row-1, col-1
            pnt = gp_Pnt (px[i, j], py[i, j], pz[i, j])
            pnt_2d.SetValue(row, col, pnt)
            print (i, j, px[i, j], py[i, j], pz[i, j])
    
    curve = GeomAPI_PointsToBSplineSurface(pnt_2d, 3, 8, GeomAbs_G2, 0.001).Surface()
    #surface = BRepBuilderAPI_MakeFace(curve, 1e-6)
    #return surface.Face()
    return curve
    
display, start_display, add_menu, add_function_to_menu = init_display()

px = np.linspace (-1, 1, 5) * 10
py = np.linspace (-1, 1, 5) * 10
mesh = np.meshgrid (px, py)
dat1 = mesh[0]**2 / (2*10) + mesh[1]**2 / (2*10)

surf1 = face(*mesh, dat1)
display.DisplayShape(surf1)
    
display.FitAll()
start_display()
    