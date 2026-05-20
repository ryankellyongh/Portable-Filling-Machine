import FreeCAD, Part
from FreeCAD import Base
from math import cos, sin, pi

doc = FreeCAD.activeDocument()
if doc is None:
    doc = FreeCAD.newDocument("FillingMachine_Complete")

# --- Create Assembly Container ---
assembly = doc.addObject("App::Part", "FillingMachineAssembly")
assembly.Label = "FillingMachineAssembly"

# --- Parameters ---
housing_size = 60.0
wall_thickness = 3.0
cylinder_diameter = housing_size - 2 * wall_thickness - 4
cylinder_height = 60.0
neck_diameter = 20.0
neck_height = 6.0
cap_height = 10.0
cap_diameter = neck_diameter + 2.0
nozzle_length = 18.0
nozzle_diameter = 10.0
nozzle_neck_diameter = 14.0
nozzle_neck_height = 5.0
snap_groove_count = 2
snap_groove_width = 1.0
snap_groove_spacing = 3.0
side_handle_length = 60.0
side_handle_width = 14.0
side_handle_thickness = 12.0

# --- Positions ---
cyl_x = housing_size / 2
cyl_y = housing_size / 2
cyl_z = wall_thickness + 5
neck_z = cyl_z + cylinder_height
cap_z = neck_z + neck_height

# --- Helper: Add and Register Part ---
def add_part(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    assembly.addObject(obj)
    return obj

# --- Housing ---
housing = Part.makeBox(housing_size, housing_size, cylinder_height + 24, Base.Vector(0, 0, 0))
inner = Part.makeBox(housing_size - 2 * wall_thickness, housing_size - 2 * wall_thickness,
                     cylinder_height + 16, Base.Vector(wall_thickness, wall_thickness, wall_thickness))
housing_shell = housing.cut(inner)

# --- Transparent Fill Window (visual indicator) ---
window_width = 8.0
window_height = cylinder_height + 6
window_thickness = wall_thickness + 0.5
window_x = housing_size / 2 - window_width / 2
window_y = 0  # front face
window_z = wall_thickness + 5

# Create transparent window panel
window_panel = Part.makeBox(window_width, window_thickness, window_height,
                            Base.Vector(window_x, window_y, window_z))
window_obj = add_part(window_panel, "FillWindow")

# Cut hole in housing to expose fluid
window_cut = Part.makeBox(window_width, wall_thickness, window_height,
                          Base.Vector(window_x, window_y, window_z))
housing_shell = housing_shell.cut(window_cut)

# --- Fillet edges ---
fillet_radius = 4.0
vertical_edges = [e for e in housing_shell.Edges if e.Vertexes[0].Point.x == e.Vertexes[1].Point.x and
                  e.Vertexes[0].Point.y == e.Vertexes[1].Point.y and abs(e.Vertexes[0].Point.z - e.Vertexes[1].Point.z) > (cylinder_height + 24) * 0.9]
if vertical_edges:
    housing_shell = housing_shell.makeFillet(fillet_radius, vertical_edges)
housing_obj = add_part(housing_shell, "Housing")

# --- Main Cylinder ---
main_cyl = Part.makeCylinder(cylinder_diameter / 2, cylinder_height, Base.Vector(cyl_x, cyl_y, cyl_z))
main_cyl_obj = add_part(main_cyl, "MainCylinder")

# --- Fill Limit Ring ---
fill_limit_ring_diameter = cylinder_diameter - 4.0
fill_limit_ring_thickness = 1.0
fill_limit_ring_height = 1.5
fill_limit_ring_z = neck_z - neck_height - fill_limit_ring_height - 2.0
outer_ring = Part.makeCylinder(fill_limit_ring_diameter / 2, fill_limit_ring_height,
                               Base.Vector(cyl_x, cyl_y, fill_limit_ring_z))
inner_ring = Part.makeCylinder((fill_limit_ring_diameter / 2) - fill_limit_ring_thickness,
                               fill_limit_ring_height, Base.Vector(cyl_x, cyl_y, fill_limit_ring_z))
fill_ring = outer_ring.cut(inner_ring)
fill_ring_obj = add_part(fill_ring, "FillLimitRing")

# --- Neck ---
neck = Part.makeCylinder(neck_diameter / 2, neck_height, Base.Vector(cyl_x, cyl_y, neck_z))
neck_obj = add_part(neck, "Neck")

# --- Fill Cap ---
cap = Part.makeCylinder(cap_diameter / 2, cap_height, Base.Vector(cyl_x, cyl_y, cap_z))
cap_obj = add_part(cap, "FillCap")

# --- Plunger with O-ring Groove ---
plunger_diameter = cylinder_diameter - 1.2
plunger_length = 10.0
plunger_z = cyl_z + cylinder_height - plunger_length - 6
o_ring_cross_section = 1.5
groove_width = o_ring_cross_section * 1.1
groove_depth = o_ring_cross_section * 0.8
groove_outer = plunger_diameter / 2
groove_inner = groove_outer - groove_depth
o_ring_groove_z = plunger_z + plunger_length / 2 - 1.0
plunger = Part.makeCylinder(plunger_diameter / 2, plunger_length, Base.Vector(cyl_x, cyl_y, plunger_z))
groove_cutter = Part.makeCylinder(groove_outer, groove_width, Base.Vector(cyl_x, cyl_y, o_ring_groove_z))
groove_core = Part.makeCylinder(groove_inner, groove_width, Base.Vector(cyl_x, cyl_y, o_ring_groove_z))
groove = groove_cutter.cut(groove_core)
plunger_with_groove = plunger.cut(groove)
rod_diameter = 4.0
rod_length = cap_height + 18.0
rod_z = plunger_z + plunger_length
rod = Part.makeCylinder(rod_diameter / 2, rod_length, Base.Vector(cyl_x, cyl_y, rod_z))
plunger_assembly = plunger_with_groove.fuse(rod)
plunger_obj = add_part(plunger_assembly, "Plunger")
o_ring_major_radius = plunger_diameter / 2 - groove_depth / 2
o_ring_minor_radius = o_ring_cross_section / 2
o_ring_vector = Base.Vector(cyl_x, cyl_y, o_ring_groove_z + groove_width / 2)
o_ring_shape = Part.makeTorus(o_ring_major_radius, o_ring_minor_radius, o_ring_vector)
o_ring_obj = add_part(o_ring_shape, "PlungerO_Ring")

# --- Nozzle ---
nozzle_z = wall_thickness - 2
nozzle_neck_z = nozzle_z + nozzle_length
nozzle = Part.makeCylinder(nozzle_diameter / 2, nozzle_length, Base.Vector(cyl_x, cyl_y, nozzle_z))
nozzle_neck = Part.makeCylinder(nozzle_neck_diameter / 2, nozzle_neck_height, Base.Vector(cyl_x, cyl_y, nozzle_neck_z))
groove_outer = nozzle_neck_diameter / 2
groove_inner = groove_outer - 1.0
nozzle_groove = Part.makeCylinder(groove_outer, snap_groove_width, Base.Vector(cyl_x, cyl_y, nozzle_neck_z + 2))
nozzle_groove_core = Part.makeCylinder(groove_inner, snap_groove_width, Base.Vector(cyl_x, cyl_y, nozzle_neck_z + 2))
snap_cut = nozzle_groove.cut(nozzle_groove_core)
nozzle_with_groove = nozzle.fuse(nozzle_neck).cut(snap_cut)
nozzle_obj = add_part(nozzle_with_groove, "Nozzle")

# --- Snap-On Nozzle (Side Display) ---
snap_nozzle_x = -18
snap_nozzle_y = cyl_y
snap_nozzle_z = 10
snap_nozzle = Part.makeCylinder(nozzle_diameter / 2, nozzle_length, Base.Vector(snap_nozzle_x, snap_nozzle_y, snap_nozzle_z))
for i in range(snap_groove_count):
    groove_z = snap_nozzle_z + 2 + i * snap_groove_spacing
    outer = Part.makeCylinder(nozzle_diameter / 2, snap_groove_width, Base.Vector(snap_nozzle_x, snap_nozzle_y, groove_z))
    inner = Part.makeCylinder(nozzle_diameter / 2 - 1, snap_groove_width, Base.Vector(snap_nozzle_x, snap_nozzle_y, groove_z))
    snap_nozzle = snap_nozzle.cut(outer.cut(inner))
snap_nozzle_obj = add_part(snap_nozzle, "SnapNozzle")

# ---------- Efficient, toggleable SIDE HANDLE ----------
# HANDLE_MODE: 0 = no handle, 1 = right only, 2 = both sides
HANDLE_MODE = 1

def make_side_handle(side: str):
    if side == 'right':
        hx = housing_size + 5
    elif side == 'left':
        hx = -10
    else:
        return None, None

    hy = (housing_size - side_handle_width) / 2
    hz = (cylinder_height + 24 - side_handle_length) / 2

    # Top connecting bar
    top_bar = Part.makeBox(5, side_handle_width, 4,
                           Base.Vector(housing_size, hy, hz + side_handle_length - 4))

    # Bottom connecting bar
    bottom_bar = Part.makeBox(5, side_handle_width, 4,
                              Base.Vector(housing_size, hy, hz))

    # Slim vertical grip
    grip_bar = Part.makeBox(6, side_handle_width, side_handle_length,
                            Base.Vector(hx, hy, hz))

    hshape = grip_bar.fuse(top_bar).fuse(bottom_bar)

    try:
        hshape = hshape.makeFillet(2.0, hshape.Edges)
    except Exception as e:
        print(f"Fillet error: {e}")

    name = f"SideHandle_{side.capitalize()}"
    return add_part(hshape, name), name

# Create requested handles
created_handle_names = []
if HANDLE_MODE == 1:
    obj, nm = make_side_handle('right')
    if obj: created_handle_names.append(nm)
elif HANDLE_MODE == 2:
    for side in ('right', 'left'):
        obj, nm = make_side_handle(side)
        if obj: created_handle_names.append(nm)
# ---------- End Side Handle ----------

# --- Outlet Valve ---
valve_diameter = 6.0
valve_thickness = 1.5
valve_z = cyl_z + 5
valve = Part.makeCylinder(valve_diameter / 2, valve_thickness, Base.Vector(cyl_x, cyl_y, valve_z))
valve_obj = add_part(valve, "OutletValve")

# --- Internal Tube ---
tube_diameter = 4.0
tube_height = cyl_z + 5
tube = Part.makeCylinder(tube_diameter / 2, tube_height, Base.Vector(cyl_x, cyl_y, nozzle_z))
try:
    tube = tube.makeFillet(0.5, tube.Edges)
except Exception as e:
    print(f"Error applying fillet to internal tube: {e}")
tube_obj = add_part(tube, "InternalTube")

# --- Gasket Under Neck ---
gasket_outer = neck_diameter / 2 + 1.5
gasket_inner = neck_diameter / 2
gasket_thickness = 2.0
gasket_z = neck_z - gasket_thickness - 0.5
outer_ring = Part.makeCylinder(gasket_outer, gasket_thickness, Base.Vector(cyl_x, cyl_y, gasket_z))
inner_core = Part.makeCylinder(gasket_inner, gasket_thickness, Base.Vector(cyl_x, cyl_y, gasket_z))
gasket = outer_ring.cut(inner_core)
gasket_obj = add_part(gasket, "NeckGasket")

# --- Guide Rods ---
plunger_top = plunger_z + plunger_length
guide_rod_radius = 1.5
guide_rod_z = 0.00
guide_rod_top_clearance = 1.0
guide_rod_height = plunger_top - guide_rod_z - guide_rod_top_clearance
guide_rod_distance = (housing_size / 2) - 2.0
rod_angles = [pi/4, 3*pi/4, 5*pi/4, 7*pi/4]
main_cylinder_radius = cylinder_diameter / 2
guide_rod_clearance = 2.0
guide_rod_distance = main_cylinder_radius + guide_rod_clearance
for i, angle in enumerate(rod_angles):
    x = cyl_x + guide_rod_distance * cos(angle)
    y = cyl_y + guide_rod_distance * sin(angle)
    rod = Part.makeCylinder(guide_rod_radius, guide_rod_height, Base.Vector(x, y, guide_rod_z))
    add_part(rod, f"GuideRod_{i+1}")

# --- Base Feet ---
foot_radius = 3.0
foot_height = 2.5
foot_distance = main_cylinder_radius + guide_rod_clearance
foot_positions = []
for angle in rod_angles:
    x = cyl_x + foot_distance * cos(angle)
    y = cyl_y + foot_distance * sin(angle)
    foot_positions.append(Base.Vector(x, y, 0))
for i, pos in enumerate(foot_positions):
    foot = Part.makeCylinder(foot_radius, foot_height, pos)
    add_part(foot, f"BaseFoot_{i+1}")

doc.recompute()

# --- Colors ---
colors = {
    "Housing": (0.85, 0.85, 0.85),        # Light grey
    "MainCylinder": (0.95, 0.95, 0.95),   # Near white
    "Neck": (0.75, 0.75, 0.75),           # Mid grey
    "FillCap": (0.3, 0.3, 0.3),           # Dark grey
    "Plunger": (0.75, 0.75, 0.75),        # Grey
    "PlungerO_Ring": (0.15, 0.15, 0.15),  # Near black
    "Nozzle": (0.75, 0.75, 0.75),         # Grey
    "SnapNozzle": (0.75, 0.75, 0.75),     # Grey
    "OutletValve": (0.75, 0.75, 0.75),    # Grey
    "InternalTube": (0.75, 0.75, 0.75),   # Grey
    "NeckGasket": (0.2, 0.2, 0.2),        # Dark grey
    "BaseFoot_1": (0.3, 0.3, 0.3),        # Dark grey
    "BaseFoot_2": (0.3, 0.3, 0.3),
    "BaseFoot_3": (0.3, 0.3, 0.3),
    "BaseFoot_4": (0.3, 0.3, 0.3),
    "GuideRod_1": (0.7, 0.7, 0.7),        # Silver grey
    "GuideRod_2": (0.7, 0.7, 0.7),
    "FillLimitRing": (0.7, 0.7, 0.7),     # Grey
    "FillWindow": (0.85, 0.95, 1.0),      # Subtle light blue tint
    "SideHandle_Right": (0.3, 0.3, 0.3)   # Dark grey
}

for name, rgb in colors.items():
    try:
        doc.getObject(name).ViewObject.ShapeColor = rgb
    except Exception as e:
        print(f"Error coloring {name}: {e}")

for nm in globals().get("created_handle_names", []):
    try:
        doc.getObject(nm).ViewObject.ShapeColor = (0.3, 0.3, 0.3)
    except Exception as e:
        print(f"Error coloring {nm}: {e}")

try:
    doc.getObject("FillWindow").ViewObject.Transparency = 80
except Exception:
    pass
