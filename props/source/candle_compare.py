"""Build the stage-3 candle comparison bench and render it as a 2-frame sprite sheet.
Usage: blender -b --factory-startup --python candle_compare.py -- <out_png> [<blend_out>]
Frame 0 = before the experiment (wicks only), frame 1 = done (left flame small, right flame big).
"""
import bpy, bmesh, sys, math, os
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
BLEND = argv[1] if len(argv) > 1 else None
CELL = 192  # 4x of the 48px display size

scene = bpy.context.scene
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)

def hexrgb(h, a=1.0):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (*c, a)

def principled(name, color, rough=0.6, metal=0.0, emit=None, emit_str=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = hexrgb(color)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = hexrgb(emit)
        b.inputs["Emission Strength"].default_value = emit_str
    return m

def glass_mat(name, tint):
    # Stylized glass: transparent centre, tinted rim (reads well at sprite size)
    m = bpy.data.materials.new(name)
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

def emission_mat(name, color, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = hexrgb(color)
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m

M = {
    "top": principled("WoodTop", "#e3b77c", 0.55),
    "wood": principled("WoodBody", "#8b6247", 0.7),
    "trim": principled("Trim", "#c69a55", 0.4, 0.6),
    "dark": principled("Dark", "#3b2c25", 0.8),
    "wax": principled("Wax", "#fbf3e2", 0.45),
    "wick": principled("Wick", "#1d1712", 0.9),
    "dish": principled("Dish", "#aeb9c0", 0.25, 0.9),
    "glass": glass_mat("Glass", "#d9f6ff"),
    "tagA": principled("TagA", "#f2c46d", 0.5),
    "tagB": principled("TagB", "#5be0c9", 0.4),
    "bubble": principled("Bubble", "#c9fff4", 0.1, emit="#8ff7e6", emit_str=1.2),
    "liquid": principled("Liquid", "#7fe3ff", 0.1, emit="#5fd2f0", emit_str=0.4),
    "flame": emission_mat("Flame", "#ff8a1f", 3.0),
    "core": emission_mat("FlameCore", "#ffe7a0", 4.0),
}

def add(prim, name, loc, scale=(1, 1, 1), mat=None, bevel=0.0, **kw):
    getattr(bpy.ops.mesh, prim)(location=loc, **kw)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    if mat:
        ob.data.materials.append(mat)
    if bevel:
        mod = ob.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        mod.limit_method = "ANGLE"
    bpy.ops.object.shade_smooth() if prim in ("primitive_cylinder_add", "primitive_uv_sphere_add") else None
    return ob

# ---- Bench (1 unit = one 38px tile) ----
TOP_Z = 0.36
add("primitive_cube_add", "Cabinet", (0, 0, TOP_Z / 2 - 0.02), (0.50, 0.25, TOP_Z / 2 - 0.02), M["wood"], 0.012)
add("primitive_cube_add", "Top", (0, 0, TOP_Z), (0.56, 0.30, 0.025), M["top"], 0.012)
add("primitive_cube_add", "TrimFront", (0, -0.302, TOP_Z - 0.006), (0.56, 0.006, 0.02), M["trim"])
add("primitive_cube_add", "Plinth", (0, 0.0, 0.025), (0.52, 0.27, 0.025), M["dark"])
for i, x in enumerate((-0.25, 0.25)):
    add("primitive_cube_add", f"Door{i}", (x, -0.252, 0.17), (0.215, 0.006, 0.12), M["dark"], 0.004)
    add("primitive_cube_add", f"DoorFace{i}", (x, -0.258, 0.17), (0.20, 0.004, 0.108), M["wood"], 0.004)
    add("primitive_cube_add", f"Handle{i}", (x + (0.15 if x < 0 else -0.15), -0.266, 0.2), (0.012, 0.008, 0.04), M["trim"])
# Labels "가" (yellow) and "나" (teal) on the front trim
add("primitive_cube_add", "TagA", (-0.25, -0.31, 0.29), (0.07, 0.006, 0.028), M["tagA"], 0.006)
add("primitive_cube_add", "TagB", (0.25, -0.31, 0.29), (0.07, 0.006, 0.028), M["tagB"], 0.006)

# ---- Candles and jars ----
JAR_R, JAR_H = 0.19, 0.42
base = TOP_Z + 0.025
flames = {}
for side, x in (("A", -0.25), ("B", 0.25)):
    cx = x - (0.03 if side == "B" else 0.0)
    add("primitive_cylinder_add", f"Dish{side}", (cx, 0.0, base + 0.008), (0.075, 0.075, 0.008), M["dish"], vertices=32)
    add("primitive_cylinder_add", f"Candle{side}", (cx, 0.0, base + 0.016 + 0.07), (0.045, 0.045, 0.07), M["wax"], 0.008, vertices=24)
    wick_top = base + 0.016 + 0.14 + 0.025
    add("primitive_cylinder_add", f"Wick{side}", (cx, 0.0, wick_top - 0.0125), (0.006, 0.006, 0.0125), M["wick"], vertices=8)
    # Glass jar: open-bottom cylinder with a rounded closed top
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=JAR_R, depth=JAR_H, location=(x, 0, base + JAR_H / 2))
    jar = bpy.context.active_object
    jar.name = f"Jar{side}"
    bm = bmesh.new(); bm.from_mesh(jar.data)
    bottom = [f for f in bm.faces if f.normal.z < -0.9]
    bmesh.ops.delete(bm, geom=bottom, context="FACES_ONLY")
    bm.to_mesh(jar.data); bm.free()
    jar.data.materials.append(M["glass"])
    bv = jar.modifiers.new("Bevel", "BEVEL"); bv.width = 0.05; bv.segments = 5; bv.limit_method = "ANGLE"
    so = jar.modifiers.new("Solid", "SOLIDIFY"); so.thickness = 0.012
    bpy.ops.object.shade_smooth()
    # Flame objects (toggled per frame)
    size = 1.15 if side == "A" else 1.9
    fl = add("primitive_uv_sphere_add", f"Flame{side}", (cx, 0, wick_top + 0.035 * size), (0.022 * size, 0.022 * size, 0.05 * size), M["flame"], segments=16, ring_count=8)
    co = add("primitive_uv_sphere_add", f"Core{side}", (cx, 0, wick_top + 0.022 * size), (0.011 * size, 0.011 * size, 0.024 * size), M["core"], segments=12, ring_count=6)
    bpy.ops.object.light_add(type="POINT", location=(cx, -0.02, wick_top + 0.05 * size))
    li = bpy.context.active_object; li.name = f"Glow{side}"
    li.data.energy = 1.2 * size * size; li.data.color = (1.0, 0.72, 0.4); li.data.shadow_soft_size = 0.02
    flames[side] = (fl, co, li)

# Oxygen source in jar B: small flask with bubbling liquid
fx = 0.25 + 0.09
add("primitive_cylinder_add", "FlaskB", (fx, 0.03, base + 0.05), (0.045, 0.045, 0.05), M["glass"], 0.01, vertices=24)
add("primitive_cylinder_add", "LiquidB", (fx, 0.03, base + 0.03), (0.038, 0.038, 0.028), M["liquid"], vertices=24)
for i, (dx, dz, r) in enumerate(((0.0, 0.13, 0.018), (-0.05, 0.2, 0.014), (0.03, 0.26, 0.012), (-0.09, 0.3, 0.016), (0.05, 0.34, 0.01), (-0.02, 0.37, 0.012))):
    add("primitive_uv_sphere_add", f"Bubble{i}", (fx + dx - 0.04, -0.02, base + dz), (r, r, r), M["bubble"], segments=12, ring_count=6)

# ---- Camera, light, render ----
TILT = math.radians(54)
AIM = Vector((0, 0, 0.3))
bpy.ops.object.camera_add(location=AIM + 6 * Vector((0, -math.sin(TILT), math.cos(TILT))), rotation=(TILT, 0, 0))
cam = bpy.context.active_object
cam.data.type = "ORTHO"
cam.data.ortho_scale = 1.32
scene.camera = cam

bpy.ops.object.light_add(type="SUN", rotation=(math.radians(30), math.radians(-14), math.radians(-20)))
sun = bpy.context.active_object; sun.data.energy = 3.6; sun.data.angle = math.radians(8)
world = bpy.data.worlds.new("W"); scene.world = world; world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = hexrgb("#9fc6d3"); bg.inputs["Strength"].default_value = 0.9

# No floor shadow: the game draws its own ellipse shadow under every station.

scene.render.engine = "CYCLES"
scene.cycles.samples = 96
scene.cycles.use_denoising = True
scene.render.film_transparent = True
scene.cycles.film_transparent_glass = True
scene.render.resolution_x = scene.render.resolution_y = CELL
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
try:
    scene.view_settings.view_transform = "Standard"
except TypeError as e:
    print("view transform:", e)
scene.view_settings.look = "None"

# Thin dark outline to match the game's flat style
try:
    scene.render.use_freestyle = True
    scene.render.line_thickness_mode = "ABSOLUTE"
    scene.render.line_thickness = 2.6
    ls = scene.view_layers[0].freestyle_settings.linesets[0]
    ls.select_by_visibility = True
    ls.select_silhouette = True; ls.select_border = False; ls.select_crease = False
    ls.linestyle.color = hexrgb("#16232b")[:3]
    ls.linestyle.alpha = 0.85
except Exception as e:
    print("freestyle off:", e)

def set_lit(on):
    for fl, co, li in flames.values():
        fl.hide_render = co.hide_render = li.hide_render = not on

tmp = os.path.splitext(OUT)[0]
frames = []
for i, lit in enumerate((False, True)):
    set_lit(lit)
    path = f"{tmp}_f{i}.png"
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(path)
    px = np.array(img.pixels[:], dtype=np.float32).reshape(CELL, CELL, 4)
    a = px[..., 3]
    a[a < 0.06] = 0.0          # drop faint ambient-occlusion haze from the shadow catcher
    px[:2] = 0; px[-2:] = 0; px[:, :2] = 0; px[:, -2:] = 0  # clean cell borders
    frames.append(px)
    bpy.data.images.remove(img)
    os.remove(path)

sheet = np.concatenate(frames, axis=1)
out = bpy.data.images.new("sheet", CELL * 2, CELL, alpha=True)
out.pixels = sheet.ravel()
out.filepath_raw = OUT
out.file_format = "PNG"
out.save()
print("SAVED", OUT)
if BLEND:
    set_lit(True)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("BLEND", BLEND)
