
import cadquery as cq

from cadquery import Workplane, Vector, Wire, Location, Shape
from cadquery.cq import T, VectorLike, Union, Tuple

if 'show_object' not in globals():
    def show_object(*args, **kwargs):
        pass

outer_od_radius    = 31
outer_od_thickness = 5
inner_od_radius    = 17.35
inner_od_thickness =  8.0
id_diameter        = 13.0
fillet_size        =  0.2
bolt_circle_count  = 10
bolt_circle_dia    = 30.0
bolt_circle_hole_dia = 2.5
thin_face = 2.0

outerRing = cq.Workplane("XY")
outerRing = outerRing.cylinder(outer_od_thickness, outer_od_radius)
outerRing = outerRing.faces('>Z').workplane()
outerRing = outerRing.hole(54)

cutter = (cq.Workplane("XY")
    .polygon(5, 30, forConstruction=True)
    .vertices().cylinder(5,5)
)

torqueRings = (cq.Workplane("XY")
    .cylinder(5,13)
    .polygon(5, 30, forConstruction=True)
    .vertices()
    .cylinder(5, 7)
    .faces('>Z')
    .workplane()
    .hole(13)
    .cut(cutter)
    .edges('|Z').fillet(1)
)

connectorBlob = (
    cq.Workplane("XY")
    .polygon(5, 48.5, forConstruction=True).vertices()
    .cylinder(5, 4)
)

scallops = cq.Workplane("XY")
scallops = scallops.polygon(nSides=48, diameter=62.4, forConstruction=True).tag("polygon")
scallops = scallops.vertices()
scallops = scallops.cylinder(5, 2.5)

# show_object(cutter)
# show_object(torqueRings)
# show_object(outerRing)
# show_object(connectorBlob)
# show_object(scallops)

result = outerRing.union(connectorBlob).union(torqueRings)
result = result.edges('|Z').fillet(1)
result = result.faces('<Z or >Z').edges().chamfer(.5)
result = result.cut(scallops)
show_object(result)

cq.exporters.export(result, "CycDisk_solid.stl")