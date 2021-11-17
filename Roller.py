if 'show_object' not in globals():
    def show_object(*args, **kwargs):
        pass

import cadquery as cq

thickness = 5
od = 9 
chamferSize = 0.3
holeDia = 3.3
cskDia = 7
cskAngle = 90

part = (
    cq.Workplane("XY")
    .cylinder(thickness, od/2)
    .faces(">Z").chamfer(chamferSize)
    .faces(">Z")
    .cskHole(holeDia, cskDia, cskAngle)
    .faces("<Z").chamfer(chamferSize)
)

show_object(part)

cq.exporters.export(part, 'Roller.stl')
