import numpy as np
import sys, time, os
from optparse import OptionParser

from OCC.Display.SimpleGui import init_display
from OCC.gp import gp_Pnt, gp_Ax1, gp_Ax2, gp_Ax3, gp_Vec, gp_Dir
from OCC.gp import gp_Pln, gp_Lin
from OCC.IntAna import IntAna_IntConicQuad
from OCC.Precision import precision_Angular, precision_Confusion
from OCC.Geom import Geom_Plane, Geom_Surface
from OCC.GeomLProp import GeomLProp_SurfaceTool
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCCUtils.Construct import make_plane, make_line
from OCCUtils.Construct import dir_to_vec, vec_to_dir
from OCCUtils.Common    import project_point_on_plane

def rot_axs (axs, ax, deg):
    axs.Rotate(ax, np.deg2rad(deg))

def def_ax (x, y, z, lx=150, ly=200, dx=0, dy=0, dz=0):
    axs = gp_Ax3 (gp_Pnt(x, y, z), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))
    a_x = gp_Ax1 (gp_Pnt(x, y, z), axs.XDirection())
    a_y = gp_Ax1 (gp_Pnt(x, y, z), axs.YDirection())
    a_z = gp_Ax1 (gp_Pnt(x, y, z), axs.Direction())
    rot_axs (axs, a_x, dx)
    rot_axs (axs, a_y, dy)
    rot_axs (axs, a_z, dz)
    pln = BRepBuilderAPI_MakeFace(
        gp_Pln (axs), -lx/2, lx/2, -ly/2, ly/2
    ).Face()
    return axs, pln

def axs_line (axs):
    p0, dx, dy = axs.Location(), axs.XDirection(), axs.YDirection()
    px = gp_Pnt((gp_Vec(p0.XYZ()) + dir_to_vec(dx)*50 ).XYZ())
    py = gp_Pnt((gp_Vec(p0.XYZ()) + dir_to_vec(dy)*100).XYZ())
    lx = make_line (p0, px)
    ly = make_line (p0, py)
    return lx, ly

def reflect (p0, v0, ax):
    ray = gp_Lin (p0, vec_to_dir(v0))
    intersection = IntAna_IntConicQuad(
        ray, gp_Pln (ax),
        precision_Angular(),
        precision_Confusion()
    )
    p1 = intersection.Point(1)
    vx, vy = gp_Vec(1, 0, 0), gp_Vec(0, 1, 0)
    handle = Geom_Plane(ax)
    handle.D1 (0.5, 0.5, gp_Pnt(), vx, vy)
    vz = vx.Crossed(vy)
    v1 = v0.Mirrored(gp_Ax2(p1, vec_to_dir(vz)))
    return p1, v1

def proj_vec (pln, p, v):
    p0, p1 = p, gp_Pnt((gp_Vec(p.XYZ()) + v).XYZ())
    p2 = project_point_on_plane (pln, p1)
    v2 = gp_Vec (p0, p2)
    return v2

def get_angle (ax, v0, v1):
    p0 = ax.Location()
    dx = ax.XDirection()
    dy = ax.YDirection()
    dz = ax.Direction()
    pl_x = Geom_Plane (p0, dy)
    pl_y = Geom_Plane (p0, dx)
    v0_x = proj_vec (pl_x, p0, v0)
    v1_x = proj_vec (pl_x, p0, v1)
    v0_y = proj_vec (pl_y, p0, v0)
    v1_y = proj_vec (pl_y, p0, v1)
    return v1_x.Angle(v0_x), v1_y.Angle(v0_y)
    
if __name__ == '__main__':
    argvs = sys.argv  
    parser = OptionParser()
    parser.add_option("--px", dest="px", default=0.0, type="float")
    parser.add_option("--dx", dest="dx", default=0.0, type="float")
    parser.add_option("--py", dest="py", default=0.0, type="float")
    parser.add_option("--dy", dest="dy", default=0.0, type="float")
    opt, argc = parser.parse_args(argvs)

    ax, pln = def_ax (0, 0, 0, lx=100, ly=100)    
    m1_ax, m1_pln = def_ax (0,    0, 470, dx=-45)    
    m2_ax, m2_pln = def_ax (0, -250, 470, dx=45, dy=180)    
    wg_ax, wg_pln = def_ax (0, -250, 470+360, lx=100, ly=100, dy=0)  
    
    ax0 = gp_Ax3 (gp_Pnt(opt.px, opt.py, 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))
    rot_axs (ax0, gp_Ax1(ax0.Location(), ax0.XDirection()), opt.dx)
    rot_axs (ax0, gp_Ax1(ax0.Location(), ax0.YDirection()), opt.dy)
    pnt = ax0.Location()
    vec = dir_to_vec (ax0.Direction())

    m1_pnt, m1_vec = reflect (   pnt,    vec, m1_ax)
    m2_pnt, m2_vec = reflect (m1_pnt, m1_vec, m2_ax)
    wg_pnt, wg_vec = reflect (m2_pnt, m2_vec, wg_ax)
    wg_vec.Reverse()
    wg_p = wg_ax.Location()
    print (np.rad2deg(get_angle (wg_ax, wg_vec, dir_to_vec(wg_ax.Direction()))))
    print (wg_pnt.X() - wg_p.X(), wg_pnt.Y() - wg_p.Y())
    
    """
    display, start_display, add_menu, add_function_to_menu = init_display()
    display.DisplayShape (pnt)
    display.DisplayShape (pln)
    display.DisplayShape (m1_pln)
    display.DisplayShape (m2_pln)
    display.DisplayShape (wg_pln)
    display.DisplayShape (axs_line(ax))
    display.DisplayShape (axs_line(m1_ax))
    display.DisplayShape (axs_line(m2_ax))
    display.DisplayShape (axs_line(wg_ax))
    
    display.DisplayVector(   vec*50, pnt)
    display.DisplayVector(m1_vec*50, m1_pnt)
    display.DisplayVector(m2_vec*50, m2_pnt)
    display.DisplayVector(wg_vec*50, wg_pnt)
    display.DisplayVector(dir_to_vec(wg_ax.Direction())*50, wg_ax.Location())
    display.DisplayShape (make_line(   pnt, m1_pnt))
    display.DisplayShape (make_line(m1_pnt, m2_pnt))
    display.DisplayShape (make_line(m2_pnt, wg_pnt))

    display.FitAll()
    start_display()
    """