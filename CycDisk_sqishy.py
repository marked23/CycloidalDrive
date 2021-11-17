
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


springRing = cq.Workplane("XY")
springRing = springRing.cylinder(outer_od_thickness, 22)
springRing = springRing.faces('>Z').workplane()
springRing = springRing.hole(40)

# show_object(springRing)

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
    # .edges('|Z').fillet(1)
)

torqueRings = (
    torqueRings
    .union(springRing)
    .edges('|Z').fillet(1)
    .faces('<Z or >Z').edges().chamfer(.5)
)

# def _ring2(
#     self: T, 
#     od: float = 10.0, 
#     id: float = 5.0, 
#     height: float = 3.0,
#     centered: Union[bool, Tuple[bool, bool, bool]] = True,
#     combine: bool = True,
#     clean: bool = True,
# ) -> T:
#     """
#     Make a cylinder with a hole in it

#     :param od: the outside diameter of the ring.
#     :param id: the inside diameter of the ring.
#     :param height: the height of the ring.

#     :returns: cq object with the resulting solid selected.

#     This example will create a ring::

#         result = Workplane().ring(10,5,3)
#     """
#     s = (
#         self
#         .cylinder(height, od/2, centered=centered, combine=combine, clean=clean)
#         .faces()
#         .hole(id, None)
#     )

#     return self.eachpoint(lambda: loc: p.moved(loc), True) 

def _makeFlexRing(baseAngle: float = 0.0) -> T:
    s = (
        cq.Workplane('XY')
        .cylinder(5, 26, angle=60)
        .rotate((0,0,0), (0,0,1), -60 )
        .faces('<Z')
        .workplane()
        .hole(50)
        .workplane()
        .cylinder(5, 24, angle=60)
        .rotate((0,0,0), (0,0,1), 30 + baseAngle)
        .faces('<Z')
        .workplane()
        .hole(46)
        # .workplane()
        # .cylinder(5, 22, angle=30 + baseAngle)
        # .faces('>Z')
        # .workplane()
        # .hole(43)
    )
    return s

flexring1 = _makeFlexRing(0)
flexring2 = _makeFlexRing(72)
flexring3 = _makeFlexRing(144)
flexring4 = _makeFlexRing(216)
flexring5 = _makeFlexRing(288)

# show_object(flexring1)
# show_object(flexring2)
# show_object(flexring3)
# show_object(flexring4)
# show_object(flexring5)


# flexrings = (
#     flexring1
#     .union(flexring2)
#     .union(flexring3)
#     .union(flexring4)
#     .union(flexring5)
# )

# show_object(flexrings)

flexringSwitchback = (
    cq.Workplane("XY")

    # the outer one to the right
    .polygon(5, 52.5, forConstruction=True).rotate((0,0,0), (0,0,1), -30)
    .vertices()
    .cylinder(5, 1.5)
    # .faces("<Z")
    # .workplane()
    # .polygon(5, 52.5, forConstruction=True).rotate((0,0,0), (0,0,1), -30)
    # .vertices()
    # .hole(1.5)

    # the outer one to the left
    .polygon(5, 49.0, forConstruction=True).rotate((0,0,0), (0,0,1), 30)
    .vertices()
    .cylinder(5, 1.5)
    # .faces("<Z")
    # .workplane()
    # .polygon(5, 49.0, forConstruction=True).rotate((0,0,0), (0,0,1), 30)
    # .vertices()
    # .hole(1.5)

    # the inner one to the right
    .polygon(5, 45.5, forConstruction=True).rotate((0,0,0), (0,0,1), -30)
    .vertices()
    .cylinder(5, 1.5)
    # .faces("<Z")
    # .workplane()
    # .polygon(5, 45.5, forConstruction=True).rotate((0,0,0), (0,0,1), -30)
    # .vertices()
    # .hole(1.5)
    .combine()    
)
# show_object(flexringSwitchback)

fullFlexRing = (
    flexringSwitchback
    .union(flexring1)
    .union(flexring2)
    .union(flexring3)
    .union(flexring4)
    .union(flexring5)
)

# show_object(fullFlexRing)

# connectorBlob = (
#     cq.Workplane("XY")
#     .polygon(5, 48.5, forConstruction=True).vertices()
#     .cylinder(5, 4)
# )

scallops = cq.Workplane("XY")
scallops = scallops.polygon(nSides=48, diameter=62.4, forConstruction=True).tag("polygon")
scallops = scallops.vertices()
scallops = scallops.cylinder(5, 2.5)

# show_object(cutter)
# show_object(torqueRings)
# show_object(outerRing)
# show_object(connectorBlob)
# show_object(scallops)

result = outerRing.union(torqueRings) 
result = result.union(fullFlexRing)
# result = result.edges('|Z').fillet(1)
# result = result.faces('<Z or >Z').edges().chamfer(.5)
result = result.cut(scallops)
show_object(result)

cq.exporters.export(result, "CycDisk_squishy.stl")