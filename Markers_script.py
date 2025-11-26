import maya.cmds as cmds
import math

# ---------- Parameters (tweak these) ----------
count = 12                 # number of hour markers
cube_w = 0.2               # cube width (X)
cube_h = 0.05              # cube height (Y)
cube_d = 0.9               # cube depth (Z) - full thickness
y_offset = 0.05            # vertical offset above the clock face
group_name = "markers_grp"
clock_name = "clock_face_geo"   # change if your clock mesh uses a different name
# ------------------------------------------------

# Ensure clock exists
if not cmds.objExists(clock_name):
    cmds.error("Clock face object '%s' not found. Rename your mesh or change clock_name." % clock_name)

# compute clock radius from bounding box
bbox = cmds.xform(clock_name, q=True, ws=True, boundingBox=True)
xmin, ymin, zmin, xmax, ymax, zmax = bbox
half_x = (xmax - xmin) / 2.0
half_z = (zmax - zmin) / 2.0
radius = max(half_x, half_z)

# placement radius: put cube center at radius - cube_d/2 (so cube is inside and outer face sits on rim)
placement_radius = radius - (cube_d / 2.0)

if placement_radius <= 0:
    cmds.error("Computed placement_radius <= 0 (%.3f). Reduce cube_d or check clock size." % placement_radius)

# create/clean group
if cmds.objExists(group_name):
    # delete existing children (keeps the group)
    children = cmds.listRelatives(group_name, children=True, type='transform') or []
    if children:
        cmds.delete(children)
else:
    cmds.group(empty=True, name=group_name)

# create markers inside the rim
for i in range(count):
    angle_deg = i * (360.0 / count)
    angle_rad = math.radians(angle_deg)

    x = math.sin(angle_rad) * placement_radius
    z = math.cos(angle_rad) * placement_radius

    marker_name = "marker_%02d" % (i + 1)
    marker = cmds.polyCube(name=marker_name, w=cube_w, h=cube_h, d=cube_d)[0]

    # place center at computed position and Y offset
    cmds.xform(marker, ws=True, translation=(x, y_offset, z))

    # rotate to point outward
    cmds.xform(marker, ws=True, rotation=(0.0, angle_deg, 0.0))

    cmds.parent(marker, group_name)

    # freeze transforms for tidy channel box (optional)
    cmds.makeIdentity(marker, apply=True, t=1, r=1, s=1, n=0)

print("Placed %d markers inside '%s' (clock radius: %.3f -> placement: %.3f)." %
      (count, clock_name, radius, placement_radius))
