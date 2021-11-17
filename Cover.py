from typing import Tuple
import cadquery as cq
from cadquery import exporters
from cadquery import Face, Compound, Shell, Solid
from cadquery.occ_impl.geom import Vector
# from cq_warehouse.fastener import ExternalThread, Thread
from math import sin, cos, tan, radians, pi, degrees, sqrt


if 'show_object' not in globals():
    def show_object(*args, **kwargs):
        pass

outer_od_radius    = 66.5 / 2
outer_od_thickness =  8.0
thin_face          =  1.5
race_rim           =  0.3
inner_od_radius    = 55.0
inner_od_thickness =  5.0
id_diameter        = 35.5
z_plus = (True, True, False)
fillet_size        =  0.2
bolt_circle_count  = 6
bolt_circle_dia    = 59.0
bolt_circle_hole_dia = 4.5

# It's a function that returns a function
# Oh! There's that 't' that's always hanging around.
def helix(r0, r_eps, p, h, d=0, frac=1e-2):
    """ parametricCurve takes a Func<float, (float,float,float)> as its parameter """
    def func(t):
        """parametricCurve will call this 400 times, with values of t from 0 to 1."""
        if t>frac and t<1-frac: # if we're in the middle part of the thread
            z = h*t + d         # make the thread full-scale
            r = r0+r_eps
        elif t<=frac:                       # if we're in the beginning of the thread
            z = h*t + d*sin(pi/2 *t/frac)   # ramp-up the thread, with t
            r = r0 + r_eps*sin(pi/2 *t/frac)
        else:
            z = h*t - d*sin(2*pi - pi/2*(1-t)/frac)    # if we're near the end of the thread
            r = r0 - r_eps*sin(2*pi - pi/2*(1-t)/frac) # ramp-down the thread, as t approaches

        x = r*sin(-2*pi/(p/h)*t)
        y = r*cos(2*pi/(p/h)*t)

        log( f"{t=:8.2f}    {x=:8.2f}    {y=:8.2f}    {z=:8.2f}")

        return x,y,z

    return func

def thread(radius, pitch, height, d, radius_eps, aspect= 10):
    maxD = 10
    e1_bottom = (cq.Workplane("XY")
        .parametricCurve(helix(radius,0,pitch,height,-d), maxDeg=maxD).val()
    )
    e1_top = (cq.Workplane("XY")
        .parametricCurve(helix(radius,0,pitch,height,d), maxDeg=maxD).val()
    )

    e2_bottom = (cq.Workplane("XY")
        .parametricCurve(helix(radius,radius_eps,pitch,height,-d/aspect), maxDeg=maxD).val()
    )
    e2_top = (cq.Workplane("XY")
        .parametricCurve(helix(radius,radius_eps,pitch,height,d/aspect), maxDeg=maxD).val()
    )

    f1 = Face.makeRuledSurface(e1_bottom, e1_top)
    f2 = Face.makeRuledSurface(e2_bottom, e2_top)
    f3 = Face.makeRuledSurface(e1_bottom, e2_bottom)
    f4 = Face.makeRuledSurface(e1_top, e2_top)

    sh = Shell.makeShell([f1,f2,f3,f4])
    rv = Solid.makeSolid(sh)

    return rv

# class ExternalThreadSplineless(Thread):
#     """ Create a thread object used in a bolt """

#     @property
#     def thread_radius(self) -> float:
#         """ The center of the thread radius or pitch radius """
#         return self.min_radius - self.h_parameter / 4

#     @property
#     def external_thread_core_radius(self) -> float:
#         """ The radius of an internal thread object used to size an appropriate hole """
#         if self.hollow:
#             value = self.major_diameter / 2 - 7 * self.h_parameter / 8
#         else:
#             value = None
#         return value

#     def thread_profile(self) -> cq.Workplane:
#         """
#         Generate a 2D profile of a single external thread based on this diagram:
#         https://en.wikipedia.org/wiki/ISO_metric_screw_thread#/media/File:ISO_and_UTS_Thread_Dimensions.svg
#         """

#         # Note: starting the thread profile at the
#         # origin will result in inconsistent results when
#         # sweeping and extracting the outer edges
#         thread_profile = (
#             cq.Workplane("XZ")
#             .moveTo(self.thread_radius / 2, 0)
#             .lineTo(self.min_radius - self.h_parameter / 12, 0)
#             .lineTo(self.min_radius, self.pitch / 8)
#             # .spline(
#             #     [(self.min_radius, self.pitch / 8)],
#             #     tangents=[
#             #         (0, 1, 0),
#             #         (
#             #             sin(radians(90 - self.thread_angle / 2)),
#             #             cos(radians(90 - self.thread_angle / 2)),
#             #         ),
#             #     ],
#             #     includeCurrent=True,
#             # )
#             .lineTo(self.major_diameter / 2, 7 * self.pitch / 16)
#             .lineTo(self.major_diameter / 2, 9 * self.pitch / 16)
#             .lineTo(self.min_radius, 7 * self.pitch / 8)
#             .lineTo(self.min_radius - self.h_parameter / 12, self.pitch)
#             # .spline(
#             #     [(self.min_radius - self.h_parameter / 12, self.pitch)],
#             #     tangents=[
#             #         (
#             #             -sin(radians(90 - self.thread_angle / 2)),
#             #             cos(radians(90 - self.thread_angle / 2)),
#             #         ),
#             #         (0, 1, 0),
#             #     ],
#             #     includeCurrent=True,
#             # )
#             .lineTo(self.thread_radius / 2, self.pitch)
#             .close()
#         )
#         return thread_profile

#     def prepare_revolve_wires(self, thread_wire) -> Tuple:
#         if self.hollow:
#             inner_wires = [
#                 cq.Wire.makeCircle(
#                     radius=self.major_diameter / 2 - 7 * self.h_parameter / 8,
#                     center=cq.Vector(0, 0, 0),
#                     normal=cq.Vector(0, 0, 1),
#                 )
#             ]
#         else:
#             inner_wires = []
#         return (thread_wire, inner_wires)



outer_cylinder = (
    cq.Workplane()
    .cylinder(outer_od_thickness, outer_od_radius, centered=z_plus)
    .faces(">Z")
    .hole(52, outer_od_thickness - thin_face)
    .faces(">Z")
    .hole(id_diameter)
    .faces(">Z")
    .polygon(bolt_circle_count, bolt_circle_dia, forConstruction=True)
    .vertices()
    .hole(bolt_circle_hole_dia)
    .rotate((0,0,0), (0,0,1), 15)
    .faces(">Z")
    .polygon(bolt_circle_count, bolt_circle_dia, forConstruction=True)
    .vertices()
    .hole(bolt_circle_hole_dia)
)

# parameters for slotting tool
angle_rotate = 45
slotter_od = (bolt_circle_dia + bolt_circle_hole_dia) / 2
slotter_id = (bolt_circle_dia - bolt_circle_hole_dia) / 2

# cylinder to represent the inner edge of the slotting tool
inner_slotter = (
    cq.Workplane()
    .cylinder(23, slotter_id)
)
# show_object(inner_slotter)

# Create a solid to use as a custom hole-punch
slotting_tool = (
    cq.Workplane()
    # another cylinder, as a pie piece,
    # to represent the outer edge of the slot
    .cylinder(20, slotter_od, Vector(0,0,1), angle=angle_rotate)
    .rotate((0,0,0), (0,0,1), -angle_rotate)
    .cut(toCut=inner_slotter)
)
# show_object(slotting_tool)

outer_cylinder = (
    outer_cylinder
    .faces(">Z")
    # I'm not sure how to syntax this:
    # for x in range(7):
    #     .cut(slotter)
    #     .rotate((0,0,0), (0,0,1), 60)
    # So instead I'm inlining:
    .cut(slotting_tool)
    .rotate((0,0,0), (0,0,1), 60)
    .cut(slotting_tool)
    .rotate((0,0,0), (0,0,1), 60)
    .cut(slotting_tool)
    .rotate((0,0,0), (0,0,1), 60)
    .cut(slotting_tool)
    .rotate((0,0,0), (0,0,1), 60)
    .cut(slotting_tool)
    .rotate((0,0,0), (0,0,1), 60)
    .cut(slotting_tool)
    .rotate((0,0,0), (0,0,1), 60)
)
#show_object(outer_cylinder)

# add the thin id rim
outer_cylinder = (
    outer_cylinder
    .faces("<Z")
    .cylinder(thin_face + race_rim, (id_diameter/2) + 1, centered=z_plus)
    .hole(id_diameter)
)
#show_object(outer_cylinder)

# fillet both sides
outer_cylinder = (
    outer_cylinder
    .faces("<Z or >Z")
    .edges()
    .fillet(fillet_size)
)
#show_object(outer_cylinder)

# Parameters for thread
p = 1.0                   # Pitch: 1mm
h = outer_od_thickness-2  # Height: somewhat less than the thickness
r = outer_od_radius       # Radius: same as od

# make a helix, then cast(?) it as a workplane
# wire = cq.Wire.makeHelix(pitch=p, height=h, radius=r)
# helix = cq.Workplane(obj=wire)

# # Thread result: A 2D shape swept along a helix.
# sl_thread = (
#     ExternalThread(
#     major_diameter=(outer_od_radius * 2 + 1.6),
#     pitch=p,
#     length=h,
#     hand="right",
#     hollow=True,
#     simple=False)
#     .cq_object
# )

# sl_thread = (
#     sl_thread
#     .translate((0,0,1))
# )

# show_object(sl_thread) #, options={"color": (140, 120, 150)})

radius = outer_od_radius
pitch = p
height = outer_od_thickness - 2
d = pitch/2.001     # width of the thread chord
radius_eps = .5
eps=1e-3

th1 = thread(
    radius - eps,   #   radius minus a little bit
    pitch,          #
    height,         #   4
    d,              #   depletion? portion of circle where thread fades is pitch/4?
    radius_eps)     #       note: underscore   (epsilon? that's all I need... abbreviations in some other language.)
# th2  =thread(radius-1+eps,pitch,height,d,-radius_eps)

th1 = (
    th1
    .translate((0,0,1))
)

# show_object(th1)

# Add the thread to the part.
#  I'm not sure if I'm supposed to .add() or .union()
#  or .combine() or some other method.  I want to
#  merge the two objects together, where they
#  intersect, and discard the unnecessary edges.
result = (
    outer_cylinder
    .union(Compound.makeCompound([th1]))
    # .workplane()
    # .edges(">Z")  # ValueError: If multiple objects selected,
    # .chamfer(.25) # they all must be planar faces.
)

show_object(result)
# show_object(outer_cylinder, options={"color": (140, 120, 15)})
# show_object(thread) # re-render thread, for contrast

exporters.export(result, 'Cover6.stl')
