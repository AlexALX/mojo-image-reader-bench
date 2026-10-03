import math
import bpy

# 1. Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. White paint material for pips
white_mat = bpy.data.materials.new(name="PipWhite")
white_mat.use_nodes = True
nodes = white_mat.node_tree.nodes
nodes.clear()

output_white = nodes.new(type='ShaderNodeOutputMaterial')
bsdf_white = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf_white.inputs['Base Color'].default_value = (0.98, 0.98, 0.98, 1.0)
bsdf_white.inputs['Roughness'].default_value = 0.2
white_mat.node_tree.links.new(bsdf_white.outputs['BSDF'], output_white.inputs['Surface'])

# 3. Transparent glass material with adjustable IOR
def create_glass_material(name, color_rgba, ior_value=1.01):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')

    bsdf.inputs['Base Color'].default_value = color_rgba

    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.98
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.98

    bsdf.inputs['Roughness'].default_value = 0.015
    # Set IOR exactly to 1.01 as requested
    bsdf.inputs['IOR'].default_value = ior_value

    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat

# 4. Function to create a dice (size 1.2 as modified by user)
def create_classic_dice(name, location, rotation, main_mat, pip_mat):
    size = 1.2
    bpy.ops.mesh.primitive_cube_add(size=size, location=location, rotation=rotation)
    dice = bpy.context.active_object
    dice.name = name
    dice.data.materials.append(main_mat)

    bevel = dice.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.07
    bevel.segments = 4

    d = (size / 2.0) + 0.001
    o = 0.25

    faces_data = [
        # Z+ (1)
        ([(0.0, 0.0, d)], (0, 0, 0)),
        # Z- (6)
        ([(-o, -o, -d), (-o, 0.0, -d), (-o, o, -d), (o, -o, -d), (o, 0.0, -d), (o, o, -d)], (math.pi, 0, 0)),
        # Y+ (2)
        ([(-o, d, -o), (o, d, o)], (-math.pi/2, 0, 0)),
        # Y- (5)
        ([(-o, -d, -o), (o, -d, o), (0.0, -d, 0.0), (-o, -d, o), (o, -d, -o)], (math.pi/2, 0, 0)),
        # X+ (3)
        ([(d, -o, -o), (d, 0.0, 0.0), (d, o, o)], (0, math.pi/2, 0)),
        # X- (4)
        ([(-d, -o, -o), (-d, -o, o), (-d, o, -o), (-d, o, o)], (0, -math.pi/2, 0)),
    ]

    for pips_pos, rot in faces_data:
        for pos in pips_pos:
            bpy.ops.mesh.primitive_circle_add(
                radius=0.065,
                fill_type='NGON',
                location=pos,
                rotation=rot
            )
            pip = bpy.context.active_object
            pip.data.materials.append(pip_mat)
            pip.parent = dice

    bpy.ops.object.select_all(action='DESELECT')
    dice.select_set(True)
    bpy.context.view_layer.objects.active = dice
    bpy.ops.object.shade_smooth()
    return dice

# 5. Colors with IOR 1.01
red_mat = create_glass_material("RedGlass", (0.9, 0.02, 0.05, 1.0), 1.0)
blue_mat = create_glass_material("BlueGlass", (0.02, 0.3, 0.95, 1.0), 1.0)
green_mat = create_glass_material("GreenGlass", (0.02, 0.85, 0.25, 1.0), 1.0)

# 6. Dice placement
create_classic_dice("Blue_Dice", location=(-0.8, -0.25, 0.5), rotation=(-0.3, 0.2, 0.6), main_mat=blue_mat, pip_mat=white_mat)
create_classic_dice("Green_Dice", location=(0.9, -0.2, 0.4), rotation=(0.2, -0.6, 0.4), main_mat=green_mat, pip_mat=white_mat)
create_classic_dice("Red_Dice", location=(-0.3, 1.3, 0.8), rotation=(0.4, 0.3, -0.2), main_mat=red_mat, pip_mat=white_mat)

# 7. Camera
bpy.ops.object.camera_add(location=(4.0, -4.5, 3.0))
camera = bpy.context.active_object
bpy.context.scene.camera = camera

track_target = bpy.data.objects.new("CameraTarget", None)
# Center of the bounding box of the three dice: X=-0.08, Y=0.28, Z=0.53
track_target.location = (0, 0.1, 0.43)
bpy.context.collection.objects.link(track_target)

track_constraint = camera.constraints.new(type='TRACK_TO')
track_constraint.target = track_target
track_constraint.track_axis = 'TRACK_NEGATIVE_Z'
track_constraint.up_axis = 'UP_Y'

# 8. Lighting setup
bpy.ops.object.light_add(type='SUN', location=(8, -4, 6))
sun = bpy.context.active_object
sun.data.energy = 20.5
# Correct way to set sun angle in Blender API (requires radians)
sun.data.angle = math.radians(120)

# Uncommented point lights from your script are left commented out as requested
#bpy.ops.object.light_add(type='POINT', location=(-3, -1, 3))
#fill_light = bpy.context.active_object
#fill_light.data.energy = 250.0

#bpy.ops.object.light_add(type='POINT', location=(1, 3, 4))
#rim_light = bpy.context.active_object
#rim_light.data.energy = 180.0

# 9. Render settings (800x600, Denoising ON)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
scene.cycles.samples = 1024
scene.cycles.use_denoising = True

scene.render.film_transparent = True
scene.render.resolution_x = 800
scene.render.resolution_y = 600

print("Done!")