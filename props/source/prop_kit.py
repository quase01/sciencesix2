"""Shared Blender setup for the game's station sprites.

Every prop uses the same camera, light, outline and size so they read as one set:
- 1 Blender unit = one 38px game tile
- 192px render cell, drawn in game at 48px (4x)
- orthographic camera tilted 54 degrees, aimed at z=0.3
A sheet has two cells side by side: [before | done/inspected].
"""
import bpy, bmesh, math, os
import numpy as np
from mathutils import Vector

CELL = 192


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def hexrgb(h, a=1.0):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (*c, a)


_mats = {}


def principled(color, rough=0.6, metal=0.0, emit=None, emit_str=0.0):
    key = ("p", color, rough, metal, emit, emit_str)
    if key in _mats and _mats[key].name in bpy.data.materials:
        return _mats[key]
    m = bpy.data.materials.new(f"P_{color}")
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = hexrgb(color)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = hexrgb(emit)
        b.inputs["Emission Strength"].default_value = emit_str
    _mats[key] = m
    return m


def glass(tint="#d9f6ff"):
    """Stylized glass: clear centre, tinted rim. Reads well at sprite size."""
    m = bpy.data.materials.new("Glass")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    mix = nt.nodes.new("ShaderNodeMixShader")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    gl = nt.nodes.new("ShaderNodeBsdfPrincipled")
    gl.inputs["Base Color"].default_value = hexrgb(tint)
    gl.inputs["Roughness"].default_value = 0.08
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.22
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = 0.03
    mr.inputs["To Max"].default_value = 0.65
    nt.links.new(lw.outputs["Facing"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], mix.inputs["Fac"])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(gl.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def glow(color, strength=2.5):
    m = bpy.data.materials.new(f"E_{color}")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = hexrgb(color)
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


def _finish(ob, name, mat, bevel, smooth):
    ob.name = name
    bpy.ops.object.transform_apply(scale=True)
    if mat:
        ob.data.materials.append(mat)
    if bevel:
        mod = ob.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        mod.limit_method = "ANGLE"
    if smooth:
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40))
        except Exception:
            bpy.ops.object.shade_smooth()
    return ob


def box(name, loc, half, mat, bevel=0.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.scale = half
    return _finish(ob, name, mat, bevel, False)


def cyl(name, loc, r, h, mat, bevel=0.0, rot=(0, 0, 0), verts=32, r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=h, location=loc, rotation=rot)
    return _finish(bpy.context.active_object, name, mat, bevel, True)


def sphere(name, loc, scale, mat, segs=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=max(6, segs // 2), location=loc)
    ob = bpy.context.active_object
    ob.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3
    return _finish(ob, name, mat, 0, True)


def torus(name, loc, major, minor, mat, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, location=loc, rotation=rot,
                                     major_segments=40, minor_segments=12)
    return _finish(bpy.context.active_object, name, mat, 0, True)


def open_jar(name, loc, r, h, mat, round_top=0.05):
    """Glass cylinder with the bottom face removed and a rounded closed top."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=r, depth=h, location=(loc[0], loc[1], loc[2] + h / 2))
    ob = bpy.context.active_object
    ob.name = name
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.normal.z < -0.9], context="FACES_ONLY")
    bm.to_mesh(ob.data); bm.free()
    ob.data.materials.append(mat)
    if round_top:
        bv = ob.modifiers.new("Bevel", "BEVEL"); bv.width = round_top; bv.segments = 5; bv.limit_method = "ANGLE"
    so = ob.modifiers.new("Solid", "SOLIDIFY"); so.thickness = 0.01
    bpy.ops.object.shade_smooth()
    return ob


def rod(name, p1, p2, r, mat, verts=12):
    """Cylinder from point p1 to point p2 (tripod legs, frames, pipes)."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d.length, location=(p1 + p2) / 2)
    ob = bpy.context.active_object
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    return _finish(ob, name, mat, 0, True)


def flame(name, loc, size, outer="#ff8a1f", inner="#ffe7a0"):
    """Teardrop flame made of two emissive ellipsoids (same look as the candle bench)."""
    x, y, z = loc
    sphere(name, (x, y, z + 0.035 * size), (0.022 * size, 0.022 * size, 0.05 * size), glow(outer, 3.0), segs=16)
    sphere(name + "Core", (x, y, z + 0.022 * size), (0.011 * size, 0.011 * size, 0.024 * size), glow(inner, 4.0), segs=12)
    return point_light((x, y - 0.03, z + 0.05 * size), 1.2 * size * size, (1.0, 0.72, 0.4), 0.02)


def remove_cap(ob, top=True):
    """Delete the top (or bottom) cap of a cylinder, e.g. an open water tub."""
    bm = bmesh.new(); bm.from_mesh(ob.data)
    sign = 1 if top else -1
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.normal.z * sign > 0.9], context="FACES_ONLY")
    bm.to_mesh(ob.data); bm.free()
    return ob


def place(ob, matrix):
    """Move an object built at the origin into a tilted frame (panels, gauges, screens)."""
    ob.matrix_world = matrix @ ob.matrix_world
    return ob


def scale_all(s):
    """Uniformly enlarge everything around the ground origin (small props like the robot)."""
    for ob in bpy.data.objects:
        if ob.parent is None and ob.type in {"MESH", "CURVE", "LIGHT"}:
            ob.location = ob.location * s
            if ob.type == "LIGHT":
                ob.data.energy *= s * s
            else:
                ob.scale = ob.scale * s


def tube(name, points, radius, mat):
    """Bezier tube through the given points (rubber hoses, cables)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 4
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(points) - 1)
    for bp, p in zip(sp.bezier_points, points):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    ob = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(ob)
    cu.materials.append(mat)
    return ob


def point_light(loc, energy, color=(1, 1, 1), size=0.03):
    bpy.ops.object.light_add(type="POINT", location=loc)
    li = bpy.context.active_object
    li.data.energy = energy
    li.data.color = color
    li.data.shadow_soft_size = size
    return li


def stage(ortho=1.32, aim_z=0.3, world="#9fc6d3", tiles=1):
    """Camera, sun, world and render settings shared by every prop."""
    scene = bpy.context.scene
    tilt = math.radians(54)
    aim = Vector((0, 0, aim_z))
    bpy.ops.object.camera_add(location=aim + 6 * Vector((0, -math.sin(tilt), math.cos(tilt))), rotation=(tilt, 0, 0))
    cam = bpy.context.active_object
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = ortho * tiles  # wide props keep the same pixels per tile
    scene.camera = cam

    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(30), math.radians(-14), math.radians(-20)))
    sun = bpy.context.active_object
    sun.data.energy = 3.6
    sun.data.angle = math.radians(8)
    w = bpy.data.worlds.new("W")
    scene.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = hexrgb(world)
    bg.inputs["Strength"].default_value = 0.9

    scene.render.engine = "CYCLES"
    scene.cycles.samples = 96
    scene.cycles.use_denoising = True
    scene.render.film_transparent = True
    scene.cycles.film_transparent_glass = True
    scene.render.resolution_x = CELL * tiles
    scene.render.resolution_y = CELL
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    try:
        scene.view_settings.view_transform = "Standard"
    except TypeError as e:
        print("view transform:", e)
    scene.view_settings.look = "None"
    try:
        scene.render.use_freestyle = True
        scene.render.line_thickness_mode = "ABSOLUTE"
        scene.render.line_thickness = 2.6
        fs = scene.view_layers[0].freestyle_settings
        ls = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("LineSet")
        if ls.linestyle is None:  # an empty factory scene has no line style
            ls.linestyle = bpy.data.linestyles.new("LineStyle")
        ls.select_by_visibility = True
        ls.select_silhouette = True
        ls.select_border = False
        ls.select_crease = False
        ls.linestyle.color = hexrgb("#16232b")[:3]
        ls.linestyle.alpha = 0.85
    except Exception as e:
        print("freestyle off:", e)


def render_cell(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(path)
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bpy.data.images.remove(img)
    os.remove(path)
    a = px[..., 3]
    a[a < 0.06] = 0.0  # drop faint haze
    px[:2] = 0; px[-2:] = 0; px[:, :2] = 0; px[:, -2:] = 0  # clean cell borders
    return px


def save_sheet(cells, out_png):
    sheet = np.concatenate(cells, axis=1)
    img = bpy.data.images.new("sheet", sheet.shape[1], sheet.shape[0], alpha=True)
    img.pixels = sheet.ravel()
    img.filepath_raw = out_png
    img.file_format = "PNG"
    img.save()
    print("SAVED", out_png)


def build_sheet(build, out_png, blend_path=None, world="#9fc6d3", tiles=1, states=(False, True)):
    """build(done: bool) adds the prop to an empty scene. Renders one cell per state, e.g. [before | done].
    tiles=2 renders a cell two tiles wide; states=(False,) renders a single-state sprite (pickups)."""
    cells = []
    for done in states:
        reset()
        _mats.clear()
        build(done)
        stage(world=world, tiles=tiles)
        cells.append(render_cell(os.path.splitext(out_png)[0] + f"_tmp{int(done)}.png"))
        if done == states[-1] and blend_path:
            bpy.ops.wm.save_as_mainfile(filepath=blend_path)
            print("BLEND", blend_path)
    save_sheet(cells, out_png)
