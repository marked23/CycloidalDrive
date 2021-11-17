import cadquery as cq
from cadquery import exporters

if 'show_object' not in globals():
    def show_object(*args, **kwargs):
        pass

diskRadius    = 25.5
diskThickness =  1.5
hubRadius    = 17.35
hubThickness =  8.0
hubHoleDia        = 13.0
z_plus = (True, True, False)
chamferSize        =  0.2
boltCircleCount  = 10
boltCircleDia    = 30.0
boltCircleHoleDia = 2.5
# thin_face = 2.0


outerDiskRib = (
    cq.Workplane()
    .cylinder(diskThickness + .3, diskRadius, centered=z_plus)
    .faces(">Z")
    .hole(diskRadius * 2 - 4.0)
)

innerDiskRib = (
    cq.Workplane()
    .cylinder(diskThickness + .3, diskRadius-5.5, centered=z_plus)
    .faces(">Z")
    .hole(diskRadius * 2 - 15.0)
)

disk = (
    cq.Workplane()
    .cylinder(diskThickness, diskRadius, centered=z_plus)
    .union(outerDiskRib)
    .union(innerDiskRib)
    .edges(">Z or <Z").chamfer(chamferSize)
)

hub = (
    cq.Workplane()
    .cylinder(hubThickness, hubRadius, centered=z_plus)
)

result = (
    cq.Workplane()
    .add(hub)
    .union(disk)
    .faces(">Z").hole(hubHoleDia)
    .faces(">Z")
    .polygon(boltCircleCount, boltCircleDia, forConstruction=True)
    .vertices().hole(boltCircleHoleDia)
    .edges(">Z or <Z")
    .chamfer(chamferSize)
)



# Displays the result of this script
# show_object(result, options={"alpha": 0.3, "color": (64, 164, 223)})
show_object(result)
# exporters.export(result, 'TorqueHat.stl')
