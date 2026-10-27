"""Stage 1 (물질 혼합실) and stage 2 (빛과 열의 방) sprites.

Usage:
  blender -b --factory-startup --python stage12_props.py -- <props_dir> [names...]
Writes <props_dir>/<file>.png and <props_dir>/source/<file>.blend.
- Stations/objects: two 192px cells, before | after (discovered, quiz solved, done or inspected).
- Pickups (flour, baking, vinegar, key): one 192px cell.
- The stage 1 lab bench is two tiles wide: 384x192 cells.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Matrix, Vector
import prop_kit as K

WOOD, DARKWOOD, STEEL, SLATE, DARK = "#caab7e", "#5b4857", "#aebccb", "#2d455f", "#1e2b3d"


def tilt_frame(center, angle_deg):
    return Matrix.Translation(Vector(center)) @ Matrix.Rotation(math.radians(angle_deg), 4, "X")


def steel():
    return K.principled(STEEL, 0.3, 0.8)


def lamp_mat(on, off_color="#ffb04a", on_color="#5bf0c9"):
    c = on_color if on else off_color
    return K.principled(c, 0.3, emit=c, emit_str=3 if on else 2.4)


def bench(top=WOOD, body=DARKWOOD, top_z=0.3, half=(0.48, 0.25)):
    K.box("BenchBody", (0, 0, top_z / 2 - 0.01), (half[0] - 0.03, half[1] - 0.03, top_z / 2 - 0.01), K.principled(body, 0.65), 0.012)
    K.box("BenchTop", (0, 0, top_z), (half[0], half[1], 0.025), K.principled(top, 0.55), 0.012)
    K.box("BenchTrim", (0, -half[1] - 0.003, top_z - 0.005), (half[0], 0.006, 0.02), K.principled("#9e745c", 0.5))
    K.box("BenchPlinth", (0, 0, 0.02), (half[0] - 0.02, half[1] - 0.02, 0.02), K.principled(DARK, 0.7))
    return top_z + 0.025


def bubbles(prefix, center, count, spread, mat, z0, rise):
    x, y = center
    for i in range(count):
        a = i * 2.39996
        r = spread * math.sqrt((i + 0.5) / count)
        K.sphere(f"{prefix}{i}", (x + r * math.cos(a), y + r * math.sin(a) * 0.6, z0 + rise * ((i * 7) % count) / count),
                 0.012 + 0.008 * (i % 3), mat, segs=10)


# ================================================================= STAGE 1
def lab(solved):
    """Two-tile mixing bench: flour, baking soda, vinegar and a mixing beaker that fizzes once solved."""
    base = bench(half=(0.95, 0.27))
    G = K.glass()
    # Flour bowl, baking soda jar, vinegar bottle
    K.cyl("Bowl", (-0.7, -0.02, base + 0.04), 0.1, 0.08, K.principled("#e8e2d8", 0.5), r2=0.07)
    K.sphere("Flour", (-0.7, -0.02, base + 0.075), (0.085, 0.085, 0.035), K.principled("#fbf6ea", 0.8))
    K.cyl("Jar", (-0.42, 0.04, base + 0.08), 0.07, 0.16, G, 0.015)
    K.cyl("Soda", (-0.42, 0.04, base + 0.05), 0.062, 0.09, K.principled("#f2eefc", 0.8))
    K.cyl("JarLid", (-0.42, 0.04, base + 0.17), 0.075, 0.025, K.principled("#9c87be", 0.5))
    K.cyl("Vinegar", (0.62, 0.06, base + 0.12), 0.06, 0.24, G, 0.02)
    K.cyl("VinegarLiquid", (0.62, 0.06, base + 0.09), 0.052, 0.17, K.principled("#f4e6b0", 0.1, emit="#f4e6b0", emit_str=0.2))
    K.cyl("VinegarCap", (0.62, 0.06, base + 0.255), 0.03, 0.04, K.principled("#4a8eb0", 0.5))
    K.box("VinegarLabel", (0.62, -0.002, base + 0.11), (0.045, 0.003, 0.04), K.principled("#67a9c8", 0.5))
    # Test-tube rack
    K.box("Rack", (0.32, 0.1, base + 0.05), (0.13, 0.04, 0.008), K.principled("#776a68", 0.6))
    K.box("RackBase", (0.32, 0.1, base + 0.006), (0.13, 0.05, 0.006), K.principled("#776a68", 0.6))
    for i, c in enumerate(("#91dce4", "#d8ac72", "#a9aad5")):
        x = 0.23 + i * 0.09
        K.cyl(f"Tube{i}", (x, 0.1, base + 0.08), 0.022, 0.16, G)
        K.cyl(f"TubeLiquid{i}", (x, 0.1, base + 0.035), 0.018, 0.06, K.principled(c, 0.3))
    # Mixing beaker in the middle: baking soda + vinegar fizz after the quiz
    K.cyl("Beaker", (0.0, -0.02, base + 0.11), 0.11, 0.22, G)
    K.cyl("Mix", (0.0, -0.02, base + 0.04), 0.1, 0.07, K.principled("#e8f4f8", 0.4))
    if solved:
        foam = K.principled("#ffffff", 0.6, emit="#e8fbff", emit_str=0.6)
        K.cyl("FoamColumn", (0.0, -0.02, base + 0.14), 0.095, 0.14, foam)
        for i, (dx, dy, r) in enumerate(((0, 0, 0.07), (0.06, -0.03, 0.05), (-0.06, -0.02, 0.05), (0.02, 0.05, 0.045), (-0.03, -0.07, 0.04))):
            K.sphere(f"Foam{i}", (dx, -0.02 + dy, base + 0.23 + (i % 2) * 0.02), r, foam, segs=14)
        K.sphere("Spark", (0.0, -0.02, base + 0.36), (0.03, 0.03, 0.03), K.principled("#ffd786", 0.3, emit="#ffd786", emit_str=3), segs=6)
    K.sphere("Lamp", (0.85, -0.275, 0.2), (0.03, 0.018, 0.03), lamp_mat(solved))


def flour(_):
    sack = K.principled("#f0dcc0", 0.8)
    K.sphere("Sack", (0, 0, 0.2), (0.22, 0.17, 0.2), sack, segs=24)
    K.cyl("Neck", (0, 0, 0.42), 0.07, 0.08, sack, r2=0.1)
    K.torus("Tie", (0, 0, 0.4), 0.075, 0.015, K.principled("#a88868", 0.7))
    K.box("Band", (0, -0.16, 0.22), (0.17, 0.02, 0.05), K.principled("#e8c48f", 0.6), rot=(math.radians(8), 0, 0))
    K.sphere("Spill", (0.14, -0.14, 0.01), (0.12, 0.07, 0.015), K.principled("#fbf6ea", 0.9))
    K.scale_all(1.2)


def baking(_):
    K.cyl("Tub", (0, 0, 0.17), 0.17, 0.34, K.principled("#d6c8ef", 0.45), 0.02)
    K.cyl("Lid", (0, 0, 0.36), 0.18, 0.05, K.principled("#9c87be", 0.45), 0.015)
    K.box("Label", (0, -0.165, 0.17), (0.11, 0.012, 0.08), K.principled("#f1eafb", 0.6), 0.008)
    K.box("LabelStripe", (0, -0.178, 0.17), (0.08, 0.004, 0.02), K.principled("#634a8e", 0.5))
    K.sphere("Scoop", (0.18, -0.12, 0.03), (0.06, 0.04, 0.03), K.principled("#f6f2ff", 0.8))
    K.scale_all(1.2)


def vinegar(_):
    G = K.glass("#e8fbff")
    K.cyl("Bottle", (0, 0, 0.2), 0.12, 0.4, G, 0.04)
    K.cyl("Liquid", (0, 0, 0.16), 0.105, 0.3, K.principled("#f0e2a8", 0.1, emit="#f0e2a8", emit_str=0.25))
    K.cyl("Shoulder", (0, 0, 0.44), 0.11, 0.08, G, r2=0.045)
    K.cyl("Cap", (0, 0, 0.5), 0.05, 0.07, K.principled("#4a8eb0", 0.45), 0.01)
    K.box("Label", (0, -0.118, 0.2), (0.09, 0.008, 0.08), K.principled("#67a9c8", 0.5), 0.006)
    K.box("LabelMark", (0, -0.128, 0.2), (0.03, 0.004, 0.04), K.principled("#e2fdff", 0.5))
    K.scale_all(1.2)


def key(_):
    gold = K.principled("#ffd36a", 0.25, 0.9, emit="#ffcf5a", emit_str=0.6)
    km = tilt_frame((0, 0, 0.3), 70)
    K.place(K.torus("Bow", (-0.14, 0, 0), 0.085, 0.03, gold), km)
    K.place(K.cyl("Shaft", (0.08, 0, 0), 0.025, 0.36, gold, rot=(0, math.radians(90), 0)), km)
    K.place(K.box("Tooth1", (0.2, -0.04, 0), (0.018, 0.04, 0.02), gold), km)
    K.place(K.box("Tooth2", (0.12, -0.035, 0), (0.016, 0.035, 0.02), gold), km)
    K.place(K.sphere("Gem", (-0.14, 0, 0.02), 0.035, K.principled("#5be0c9", 0.2, emit="#5be0c9", emit_str=2)), km)
    K.scale_all(1.5)


def terminal(found):
    K.box("Base", (0, 0.04, 0.03), (0.22, 0.16, 0.03), K.principled(DARK, 0.6), 0.01)
    K.rod("Post", (0, 0.06, 0.06), (0, 0.06, 0.3), 0.04, steel())
    tm = tilt_frame((0, 0.02, 0.45), 65)
    K.place(K.box("Body", (0, 0, 0), (0.3, 0.2, 0.04), K.principled("#213b52", 0.45, 0.3), 0.02), tm)
    scr = K.principled("#9ffff0" if found else "#6feee5", 0.3, emit="#6feee5", emit_str=1.6 if found else 0.9)
    K.place(K.box("Screen", (0, 0.01, 0.042), (0.25, 0.15, 0.004), scr), tm)
    ink = K.principled("#0e4751", 0.5)
    if found:
        for i in range(3):
            K.place(K.box(f"Line{i}", (-0.03, 0.08 - i * 0.06, 0.048), (0.17 - i * 0.03, 0.012, 0.002), ink), tm)
    else:  # big question mark
        K.place(K.torus("QTop", (0, 0.05, 0.048), 0.05, 0.016, ink, rot=(0, 0, 0)), tm)
        K.place(K.box("QStem", (0.0, -0.03, 0.048), (0.016, 0.03, 0.003), ink), tm)
        K.place(K.cyl("QDot", (0.0, -0.1, 0.048), 0.018, 0.006, ink), tm)
        K.place(K.box("QMask", (-0.03, 0.02, 0.05), (0.035, 0.03, 0.004), scr), tm)
    K.box("Keyboard", (0, -0.13, 0.33), (0.16, 0.05, 0.012), K.principled("#768da8", 0.5), 0.006, rot=(math.radians(20), 0, 0))


def poster(found):
    for x in (-0.18, 0.18):
        K.rod(f"Leg{x}", (x, 0.08, 0.0), (x * 0.9, 0.04, 0.6), 0.016, K.principled("#7b6a67", 0.6))
    pm = tilt_frame((0, 0.02, 0.42), 76)
    K.place(K.box("Frame", (0, 0, 0), (0.22, 0.26, 0.018), K.principled("#8f785c", 0.5), 0.01), pm)
    K.place(K.box("Paper", (0, 0, 0.02), (0.19, 0.23, 0.004), K.principled("#f6edc9", 0.6)), pm)
    K.place(K.box("Red", (0, 0.15, 0.026), (0.15, 0.03, 0.002), K.principled("#ff9d9d", 0.5)), pm)
    K.place(K.box("Teal", (0, 0.07, 0.026), (0.15, 0.03, 0.002), K.principled("#6fcdd5", 0.5)), pm)
    K.place(K.cyl("Warn", (-0.07, -0.07, 0.026), 0.07, 0.004, K.principled("#f2b232", 0.5), verts=3), pm)
    for i in range(3):
        K.place(K.box(f"Line{i}", (0.08, -0.03 - i * 0.05, 0.026), (0.07, 0.008, 0.002), K.principled("#947d64", 0.5)), pm)
    if found:
        K.place(K.cyl("Check", (0.13, -0.17, 0.03), 0.05, 0.008, K.principled("#5be0c9", 0.4, emit="#5be0c9", emit_str=1.5)), pm)


def board(found):
    for x in (-0.28, 0.28):
        K.rod(f"Leg{x}", (x, 0.06, 0.0), (x, 0.06, 0.55), 0.016, K.principled("#73655f", 0.6))
        K.box(f"Foot{x}", (x, 0.06, 0.012), (0.03, 0.1, 0.012), K.principled("#73655f", 0.6))
    bm = tilt_frame((0, 0.03, 0.42), 76)
    K.place(K.box("Board", (0, 0, 0), (0.32, 0.18, 0.02), K.principled("#2d455f", 0.5), 0.012), bm)
    K.place(K.box("Rim", (0, 0, 0.012), (0.3, 0.16, 0.012), K.principled("#9ec1df", 0.5)), bm)
    K.place(K.box("Surface", (0, 0, 0.025), (0.28, 0.14, 0.004), K.principled("#2d455f", 0.5)), bm)
    note_glow = 1.2 if found else 0.0
    K.place(K.box("Note1", (-0.06, 0.08, 0.03), (0.18, 0.015, 0.002), K.principled("#f4d585", 0.5, emit="#f4d585", emit_str=note_glow)), bm)
    for i in range(2):
        K.place(K.box(f"Note{i + 2}", (-0.1 + i * 0.02, 0.02 - i * 0.06, 0.03), (0.14 - i * 0.03, 0.012, 0.002), K.principled("#e9f2fa", 0.5)), bm)
    for i, c in enumerate(("#ff9d9d", "#6fcdd5", "#f4d585")):
        K.place(K.cyl(f"Magnet{i}", (0.17, 0.08 - i * 0.06, 0.035), 0.022, 0.012, K.principled(c, 0.4, emit=c, emit_str=1.5 if found else 0)), bm)
    K.box("Tray", (0, -0.03, 0.27), (0.24, 0.04, 0.01), K.principled("#9ec1df", 0.5))


def crate(found):
    wood = K.principled("#885f42", 0.7)
    plank = K.principled("#deb283", 0.65)
    K.box("Crate", (0, 0, 0.17), (0.3, 0.22, 0.17), wood, 0.012)
    for z in (0.07, 0.17, 0.27):
        K.box(f"Plank{z}", (0, -0.222, z), (0.29, 0.006, 0.035), plank, 0.004)
    K.box("Cross", (0, -0.232, 0.17), (0.035, 0.006, 0.17), K.principled("#5d3f2f", 0.7))
    if found:  # open lid with supplies inside
        K.box("Lid", (0, 0.27, 0.42), (0.3, 0.02, 0.15), wood, 0.01, rot=(math.radians(-15), 0, 0))
        K.box("Inside", (0, 0, 0.33), (0.27, 0.19, 0.005), K.principled("#4a3226", 0.8))
        K.cyl("Flask", (-0.12, -0.02, 0.38), 0.05, 0.1, K.glass(), 0.01)
        K.box("Goggles", (0.08, -0.04, 0.36), (0.09, 0.04, 0.02), K.principled("#5be0c9", 0.3, emit="#5be0c9", emit_str=1.2), 0.01)
        K.point_light((0, -0.1, 0.45), 1.2, (0.6, 1, 0.9), 0.05)
    else:
        K.box("Lid", (0, 0, 0.345), (0.31, 0.23, 0.02), plank, 0.01)
        K.box("LidBand", (0, 0, 0.368), (0.31, 0.04, 0.006), K.principled("#61412e", 0.7))


# ================================================================= STAGE 2
def observe(done):
    base = bench(top="#e6b582", body="#aa784e")
    # Candle (left) and alcohol lamp (right): both give off light and heat when burning
    K.cyl("Dish", (-0.2, 0.0, base + 0.008), 0.08, 0.016, steel())
    K.cyl("Candle", (-0.2, 0.0, base + 0.09), 0.05, 0.15, K.principled("#fbf3e2", 0.45), 0.008, verts=24)
    K.cyl("CandleWick", (-0.2, 0.0, base + 0.18), 0.006, 0.025, K.principled("#1d1712", 0.9), verts=8)
    G = K.glass("#f3e3c8")
    K.cyl("Lamp", (0.2, 0.0, base + 0.055), 0.09, 0.11, G, 0.02)
    K.cyl("Fuel", (0.2, 0.0, base + 0.035), 0.08, 0.06, K.principled("#b8d9e8", 0.1, emit="#b8d9e8", emit_str=0.2))
    K.cyl("LampNeck", (0.2, 0.0, base + 0.125), 0.032, 0.03, K.principled("#c69a55", 0.35, 0.8))
    K.cyl("LampWick", (0.2, 0.0, base + 0.15), 0.008, 0.025, K.principled("#2a2018", 0.9), verts=8)
    if done:
        K.flame("CandleFlame", (-0.2, 0.0, base + 0.19), 1.3)
        K.flame("LampFlame", (0.2, 0.0, base + 0.16), 1.4, outer="#ff9a3a")
    # Observation notebook
    K.box("Notebook", (0.0, -0.16, base + 0.01), (0.1, 0.07, 0.008), K.principled("#f6edc9", 0.6), rot=(0, 0, math.radians(-8)))
    K.box("NoteLine", (0.0, -0.16, base + 0.02), (0.07, 0.008, 0.002), K.principled("#6a423c", 0.6), rot=(0, 0, math.radians(-8)))


def sensor_post(name_color):
    K.cyl("Base", (0, 0.02, 0.03), 0.24, 0.06, K.principled(SLATE, 0.5, 0.4), 0.012, verts=32)
    K.rod("Post", (0, 0.04, 0.06), (0, 0.04, 0.32), 0.04, steel())
    K.torus("Collar", (0, 0.04, 0.32), 0.05, 0.014, K.principled(name_color, 0.4))


def light(done):
    sensor_post("#79dce3")
    # Solar-cell dish tilted up toward the light
    dm = tilt_frame((0, 0.02, 0.42), 35)
    K.place(K.cyl("Dish", (0, 0, 0), 0.22, 0.04, K.principled("#233c55", 0.4, 0.4), 0.01), dm)
    cell = K.principled("#78ebd2" if done else "#32516b", 0.25, 0.3, emit="#78ebd2" if done else None, emit_str=1.4 if done else 0)
    for i in range(3):
        for j in range(3):
            K.place(K.box(f"Cell{i}{j}", (-0.1 + i * 0.1, -0.1 + j * 0.1, 0.024), (0.042, 0.042, 0.004), cell), dm)
    K.sphere("Sun", (0, 0.04, 0.68), 0.05, K.principled("#fff2a0", 0.3, emit="#ffe070", emit_str=3.5 if done else 0.4), segs=16)
    K.rod("SunRod", (0, 0.06, 0.48), (0, 0.04, 0.63), 0.008, steel())
    if done:
        for i in range(6):
            a = math.radians(i * 60)
            K.rod(f"Ray{i}", (0.07 * math.cos(a), 0.04 + 0.07 * math.sin(a) * 0.5, 0.68 + 0.07 * math.sin(a) * 0.5),
                  (0.12 * math.cos(a), 0.04 + 0.12 * math.sin(a) * 0.5, 0.68 + 0.12 * math.sin(a) * 0.5), 0.008, K.glow("#ffe070", 3))


def heat(done):
    sensor_post("#f1a293")
    K.box("Housing", (0, 0.02, 0.45), (0.2, 0.12, 0.13), K.principled("#534354", 0.5, 0.3), 0.025)
    coil = K.principled("#ff7a3a", 0.4, emit="#ff6a2a", emit_str=3) if done else K.principled("#6a5a5a", 0.4, 0.7)
    for i in range(4):
        K.torus(f"Coil{i}", (0, -0.11, 0.38 + i * 0.045), 0.08, 0.012, coil, rot=(0, 0, 0))
    K.box("Grill", (0, -0.105, 0.45), (0.14, 0.004, 0.1), K.principled("#2a2030", 0.6))
    # Thermometer on the side
    G = K.glass("#fff2dc")
    K.cyl("Thermo", (0.27, 0.0, 0.42), 0.025, 0.36, G)
    K.sphere("Bulb", (0.27, 0.0, 0.24), 0.035, K.principled("#e0483c", 0.3, emit="#e0483c", emit_str=0.6))
    lvl = 0.26 if done else 0.06
    K.cyl("Mercury", (0.27, 0.0, 0.25 + lvl / 2), 0.013, lvl, K.principled("#e0483c", 0.3, emit="#e0483c", emit_str=0.6))
    if done:
        K.point_light((0, -0.3, 0.45), 2.0, (1, 0.6, 0.3), 0.05)
        wave = K.glow("#ffb07a", 1.8)
        for i in range(3):
            K.rod(f"Wave{i}", (-0.1 + i * 0.1, -0.16, 0.6), (-0.08 + i * 0.1, -0.16, 0.7), 0.01, wave)


def relay(done):
    K.cyl("Base", (0, 0.02, 0.04), 0.36, 0.08, K.principled("#3c3b64", 0.5, 0.4), 0.012, verts=6)
    K.cyl("Tower", (0, 0.02, 0.3), 0.15, 0.44, K.principled("#4a4878", 0.45, 0.4), 0.02, verts=6)
    K.cyl("Top", (0, 0.02, 0.54), 0.17, 0.04, K.principled("#c3b0ff", 0.4, 0.5), 0.01, verts=6)
    # Three link rings for observe / light / heat
    for i, c in enumerate(("#f7b876", "#7ce9e2", "#ffa18c")):
        K.torus(f"Link{i}", (0, 0.02, 0.18 + i * 0.11), 0.155, 0.014,
                K.principled(c, 0.3, emit=c, emit_str=2.4) if done else K.principled("#505276", 0.5))
    sm = tilt_frame((0, -0.13, 0.36), 80)
    K.place(K.box("Panel", (0, 0, 0), (0.1, 0.13, 0.01), K.principled("#2a2a48", 0.5), 0.008), sm)
    mark = K.principled("#64e9be", 0.3, emit="#64e9be", emit_str=1.8) if done else K.principled("#e3d8ff", 0.4, emit="#c8b6ff", emit_str=0.8)
    if done:
        K.place(K.box("Check1", (-0.025, -0.02, 0.013), (0.03, 0.01, 0.003), mark, rot=(0, 0, math.radians(-45))), sm)
        K.place(K.box("Check2", (0.025, 0.01, 0.013), (0.055, 0.01, 0.003), mark, rot=(0, 0, math.radians(50))), sm)
    else:
        K.place(K.box("Diamond", (0, 0, 0.013), (0.045, 0.045, 0.003), mark, rot=(0, 0, math.radians(45))), sm)
    K.sphere("Beacon", (0, 0.02, 0.6), 0.045, lamp_mat(done, "#c8b6ff", "#64e9be"))


def bot(inspected):
    """Firebot: the stage 2 mascot with a little flame on its antenna."""
    white = K.principled("#e8f6f5", 0.35)
    teal = K.principled("#66c4d2", 0.4, 0.3)
    K.cyl("Pad", (0, 0, 0.02), 0.18, 0.04, K.principled("#2a3d4a", 0.6, 0.3), 0.01)
    K.sphere("Glow", (0, 0, 0.1), (0.07, 0.07, 0.03), K.glow("#ffd58c", 2.5))
    K.sphere("Body", (0, 0, 0.26), (0.17, 0.15, 0.15), white)
    K.sphere("Belly", (0, -0.12, 0.25), (0.08, 0.04, 0.06), K.principled("#ffd58c", 0.4))
    for s in (-1, 1):
        K.sphere(f"Arm{s}", (0.19 * s, -0.02, 0.27), (0.045, 0.045, 0.07), teal)
    K.sphere("Head", (0, 0, 0.48), (0.2, 0.17, 0.15), K.principled("#b0eeea", 0.35))
    K.sphere("Face", (0, -0.075, 0.48), (0.155, 0.1, 0.1), K.principled("#173247", 0.2))
    eye = K.principled("#9dffc8" if inspected else "#7ff6ff", 0.3, emit="#9dffc8" if inspected else "#7ff6ff", emit_str=3)
    for s in (-1, 1):
        if inspected:
            K.sphere(f"Eye{s}", (0.055 * s, -0.172, 0.49), (0.032, 0.012, 0.014), eye, segs=12)
        else:
            K.sphere(f"Eye{s}", (0.055 * s, -0.172, 0.49), (0.026, 0.012, 0.034), eye, segs=12)
    K.box("Mouth", (0, -0.175, 0.44), (0.03, 0.006, 0.006), K.principled("#dd9d83", 0.5))
    K.cyl("Antenna", (0, 0, 0.66), 0.012, 0.08, K.principled("#ffd58c", 0.4))
    K.flame("AntennaFlame", (0, 0, 0.68), 1.6 if inspected else 1.2)
    K.scale_all(1.3)


def archive2(inspected):
    body = K.principled("#80674c", 0.6)
    # Open-front bookcase: sides, back and top only, so the books show
    for x in (-0.39, 0.39):
        K.box(f"Side{x}", (x, 0.05, 0.32), (0.02, 0.18, 0.32), body, 0.006)
    K.box("Back", (0, 0.21, 0.32), (0.38, 0.015, 0.31), K.principled("#51696c", 0.6))
    K.box("Bottom", (0, 0.05, 0.05), (0.38, 0.17, 0.03), body)
    K.box("Plinth", (0, 0.05, 0.02), (0.41, 0.19, 0.02), K.principled(DARK, 0.7))
    for z in (0.22, 0.44):
        K.box(f"Board{z}", (0, 0.04, z), (0.38, 0.16, 0.012), K.principled("#dfc9a0", 0.6))
    colors = ("#e0584f", "#ffcf5a", "#5aa8ff", "#9bdfae", "#c0c1ff", "#f29a6b", "#5be0c9")
    for row, z in enumerate((0.23, 0.45)):
        for i in range(7):
            h = 0.13 + 0.03 * ((i + row) % 3)
            K.box(f"Book{row}{i}", (-0.3 + i * 0.09, 0.06, z + h / 2 + 0.012), (0.035, 0.11, h / 2), K.principled(colors[(i + row * 3) % 7], 0.6), 0.004)
    K.box("Drawer", (0, -0.13 - (0.12 if inspected else 0), 0.11), (0.35, 0.02, 0.08), K.principled("#dfc9a0", 0.6), 0.008)
    K.box("Pull", (0, -0.155 - (0.12 if inspected else 0), 0.11), (0.06, 0.008, 0.012), K.principled("#c69a55", 0.35, 0.8))
    if inspected:
        K.box("DrawerInside", (0, -0.17, 0.15), (0.33, 0.1, 0.005), K.principled("#4a3a2a", 0.8))
        K.box("GlowCard", (0.05, -0.18, 0.2), (0.1, 0.004, 0.06), K.principled("#9bdfae", 0.4, emit="#9bdfae", emit_str=2), rot=(math.radians(-20), 0, 0))
    K.box("Top", (0, 0.05, 0.645), (0.41, 0.19, 0.015), K.principled("#5a4636", 0.6), 0.006)


# name: (builder, file, tiles, states)
SPECS = {
    "lab": (lab, "s1-mixing-bench", 2, (False, True)),
    "flour": (flour, "s1-flour", 1, (False,)),
    "baking": (baking, "s1-baking-soda", 1, (False,)),
    "vinegar": (vinegar, "s1-vinegar", 1, (False,)),
    "key": (key, "s1-key", 1, (False,)),
    "terminal": (terminal, "s1-terminal", 1, (False, True)),
    "poster": (poster, "s1-poster", 1, (False, True)),
    "board": (board, "s1-board", 1, (False, True)),
    "crate": (crate, "s1-crate", 1, (False, True)),
    "observe": (observe, "s2-observe-bench", 1, (False, True)),
    "light": (light, "s2-light-sensor", 1, (False, True)),
    "heat": (heat, "s2-heat-sensor", 1, (False, True)),
    "relay": (relay, "s2-relay", 1, (False, True)),
    "bot": (bot, "s2-firebot", 1, (False, True)),
    "archive": (archive2, "s2-archive", 1, (False, True)),
}

if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:]
    out_dir = argv[0]
    names = argv[1:] or list(SPECS)
    os.makedirs(os.path.join(out_dir, "source"), exist_ok=True)
    for name in names:
        build, f, tiles, states = SPECS[name]
        K.build_sheet(build, os.path.join(out_dir, f + ".png"), os.path.join(out_dir, "source", f + ".blend"),
                      tiles=tiles, states=states)
