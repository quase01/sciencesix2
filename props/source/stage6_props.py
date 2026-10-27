"""Stage 6 (생태계 복구 대작전) station sprites — wood, leaves and sunlight.

Usage:
  blender -b --factory-startup --python stage6_props.py -- <props_dir> [sort impact action final forestLog coralLog futureLog]
Writes <props_dir>/<file>.png (two 192px cells: before | done or visited) and <props_dir>/source/<file>.blend.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Matrix, Vector
import prop_kit as K

WORLD = "#cfdcbc"  # soft daylight green
FILES = {
    "sort": "s6-sort-station",
    "impact": "s6-eco-monitor",
    "action": "s6-carbon-choices",
    "final": "s6-earth-core",
    "forestLog": "s6-forest-log",
    "coralLog": "s6-coral-log",
    "futureLog": "s6-future-sign",
}

WOOD, DARKWOOD, LEAF, MOSS, STONE = "#b5875a", "#6a4a32", "#5fae5a", "#3f7a45", "#8a8f80"


def tilt_frame(center, angle_deg):
    return Matrix.Translation(Vector(center)) @ Matrix.Rotation(math.radians(angle_deg), 4, "X")


def lamp_mat(on, off_color="#ffb04a", on_color="#9dff8a"):
    c = on_color if on else off_color
    return K.principled(c, 0.3, emit=c, emit_str=3 if on else 2.4)


def bench(top=WOOD, body=DARKWOOD, top_z=0.3, half=(0.48, 0.25)):
    K.box("BenchBody", (0, 0, top_z / 2 - 0.01), (half[0] - 0.03, half[1] - 0.03, top_z / 2 - 0.01), K.principled(body, 0.7), 0.012)
    K.box("BenchTop", (0, 0, top_z), (half[0], half[1], 0.025), K.principled(top, 0.6), 0.012)
    K.box("BenchTrim", (0, -half[1] - 0.003, top_z - 0.005), (half[0], 0.006, 0.02), K.principled(MOSS, 0.6))
    K.box("BenchPlinth", (0, 0, 0.02), (half[0] - 0.02, half[1] - 0.02, 0.02), K.principled("#3a3328", 0.8))
    return top_z + 0.025


def fir(name, loc, h, green):
    """Little Korean fir: trunk plus three stacked cones."""
    x, y, z = loc
    K.cyl(f"{name}Trunk", (x, y, z + h * 0.12), h * 0.07, h * 0.24, K.principled("#5a3d28", 0.8))
    mat = K.principled(green, 0.7)
    for i, (r, zz) in enumerate(((0.32, 0.35), (0.25, 0.58), (0.17, 0.8))):
        K.cyl(f"{name}Cone{i}", (x, y, z + h * zz), h * r, h * 0.32, mat, r2=0.0, verts=10)


# ---------------------------------------------------------------- 연소 분류 관측소
def sort(done):
    base = bench()
    # Two trays: combustion (flame) and non-combustion (lightning bolt)
    for s, col, name in ((-1, "#e0703a", "Burn"), (1, "#4aa8ff", "NoBurn")):
        x = 0.26 * s
        K.box(f"Tray{name}", (x, -0.02, base + 0.02), (0.17, 0.13, 0.02), K.principled("#4a3a2a", 0.7), 0.01)
        K.box(f"TrayRim{name}", (x, -0.02, base + 0.042), (0.17, 0.13, 0.004), K.principled(col, 0.5))
        sm = tilt_frame((x, 0.12, base + 0.13), 75)
        K.place(K.box(f"Sign{name}", (0, 0, 0), (0.1, 0.07, 0.012), K.principled("#f3ead2", 0.6), 0.008), sm)
        if name == "Burn":
            K.place(K.sphere("SignFlame", (0, -0.005, 0.016), (0.03, 0.045, 0.006), K.principled(col, 0.4, emit=col, emit_str=1.2)), sm)
        else:
            K.place(K.box("Bolt1", (-0.01, 0.015, 0.016), (0.01, 0.03, 0.004), K.principled(col, 0.4, emit=col, emit_str=1.2), rot=(0, 0, math.radians(-25))), sm)
            K.place(K.box("Bolt2", (0.01, -0.015, 0.016), (0.01, 0.03, 0.004), K.principled(col, 0.4, emit=col, emit_str=1.2), rot=(0, 0, math.radians(-25))), sm)
        K.rod(f"SignPost{name}", (x, 0.13, base), (x, 0.13, base + 0.09), 0.012, K.principled(DARKWOOD, 0.7))
    # Situation cards: a stack of unknowns before, sorted into the trays after
    cards = [("#e0703a", -1), ("#e0703a", -1), ("#e0703a", -1), ("#4aa8ff", 1)]
    for i, (c, side) in enumerate(cards):
        if done:
            x = 0.26 * side + (i % 3 - 1) * 0.06 * (1 if side < 0 else 0)
            K.box(f"Card{i}", (x, -0.03, base + 0.05 + i * 0.004), (0.045, 0.06, 0.004), K.principled(c, 0.55), rot=(0, 0, math.radians(-10 + i * 7)))
        else:
            K.box(f"Card{i}", (0.0, -0.06, base + 0.008 + i * 0.008), (0.045, 0.06, 0.004), K.principled("#f3ead2", 0.6), rot=(0, 0, math.radians(-12 + i * 8)))
    if not done:
        K.sphere("Question", (0.0, -0.06, base + 0.07), (0.025, 0.025, 0.03), K.principled("#ffdb96", 0.4, emit="#ffcf6a", emit_str=1.5))
    K.sphere("Lamp", (0.0, 0.17, base + 0.03), (0.03, 0.03, 0.025), lamp_mat(done))


# ---------------------------------------------------------------- 기후·생태계 관측소
def impact(done):
    base = bench(top="#9fb4b0", body="#35525a")
    # Diorama: Korean fir forest (left) and coral reef pool (right)
    green = LEAF if done else "#8a7a52"
    K.box("Soil", (-0.25, 0.0, base + 0.02), (0.19, 0.16, 0.02), K.principled("#5a4a32", 0.8), 0.01)
    fir("FirA", (-0.31, 0.04, base + 0.04), 0.3, green)
    fir("FirB", (-0.19, -0.04, base + 0.04), 0.24, green)
    pool = K.cyl("Pool", (0.25, -0.01, base + 0.04), 0.17, 0.08, K.glass("#d7f3ff"))
    K.remove_cap(pool, top=True)
    K.cyl("Sea", (0.25, -0.01, base + 0.03), 0.16, 0.05, K.principled("#3a8fb8", 0.15, emit="#3a8fb8", emit_str=0.2 if done else 0.05))
    coral = ("#ff7a7a", "#ffb04a", "#ff8ac8") if done else ("#ece8e0", "#e2ddd2", "#f2efe8")  # bleached before
    for i, (dx, dy, h) in enumerate(((-0.06, 0.02, 0.09), (0.03, -0.04, 0.07), (0.07, 0.04, 0.1))):
        m = K.principled(coral[i], 0.6)
        K.cyl(f"Coral{i}", (0.25 + dx, -0.01 + dy, base + 0.06 + h / 2), 0.016, h, m)
        K.sphere(f"CoralTip{i}", (0.25 + dx, -0.01 + dy, base + 0.06 + h), 0.026, m, segs=10)
    # Data screen at the back: rising CO2 graph
    K.box("Stand", (0, 0.18, base + 0.08), (0.03, 0.02, 0.08), K.principled(DARKWOOD, 0.7))
    mm = tilt_frame((0, 0.19, base + 0.25), -12)
    K.place(K.box("Screen", (0, 0, 0), (0.14, 0.03, 0.1), K.principled("#24323a", 0.5), 0.01), mm)
    scr = K.principled("#9ff0d8", 0.3, emit="#9ff0d8", emit_str=1.2) if done else K.principled("#2e3e46", 0.4, emit="#2e3e46", emit_str=0.5)
    K.place(K.box("Display", (0, -0.032, 0), (0.12, 0.003, 0.08), scr), mm)
    bar = K.principled("#1e5a46" if done else "#ff6a5a", 0.5, emit=None if done else "#ff6a5a", emit_str=0 if done else 1.5)
    for i, h in enumerate((0.02, 0.035, 0.05, 0.065)):
        K.place(K.box(f"Bar{i}", (-0.075 + i * 0.05, -0.036, -0.06 + h), (0.015, 0.002, h), bar), mm)


# ---------------------------------------------------------------- 탄소 줄이기 선택 제어기
def action(done):
    K.box("Panel", (0, 0.03, 0.2), (0.44, 0.2, 0.2), K.principled("#3a7553", 0.55, 0.2), 0.02)
    K.box("Plinth", (0, 0.03, 0.02), (0.45, 0.21, 0.02), K.principled("#2a3a30", 0.8))
    pm = tilt_frame((0, -0.04, 0.42), 25)
    K.place(K.box("Deck", (0, 0, 0), (0.44, 0.19, 0.025), K.principled(WOOD, 0.6), 0.012), pm)
    # Three choices: bicycle, light switch (lights off), bus
    pad_on = K.principled("#9dff8a", 0.3, emit="#7cf06a", emit_str=1.6)
    pad_off = K.principled("#6a7a6e", 0.6)
    for i, x in enumerate((-0.29, 0.0, 0.29)):
        K.place(K.cyl(f"Pad{i}", (x, -0.02, 0.03), 0.11, 0.015, pad_on if done else pad_off), pm)
        K.place(K.sphere(f"Lamp{i}", (x, 0.13, 0.035), (0.022, 0.022, 0.015), lamp_mat(done, "#ff6a5a")), pm)
    ink = K.principled("#2a3a30", 0.5)
    # bicycle
    for s in (-1, 1):
        K.place(K.torus(f"Wheel{s}", (-0.29 + 0.045 * s, -0.02, 0.07), 0.035, 0.007, ink, rot=(math.radians(90), 0, 0)), pm)
    K.place(K.rod("Frame", Vector((-0.335, -0.02, 0.07)), Vector((-0.27, -0.02, 0.1)), 0.006, K.principled("#e0583c", 0.5)), pm)
    K.place(K.rod("Frame2", Vector((-0.245, -0.02, 0.07)), Vector((-0.27, -0.02, 0.1)), 0.006, K.principled("#e0583c", 0.5)), pm)
    # light bulb (switched off = good choice)
    K.place(K.sphere("Bulb", (0.0, -0.02, 0.09), 0.045, K.principled("#fff6d8", 0.3)), pm)
    K.place(K.cyl("BulbBase", (0.0, -0.02, 0.045), 0.022, 0.03, K.principled("#9aa0a6", 0.3, 0.8)), pm)
    # bus
    K.place(K.box("Bus", (0.29, -0.02, 0.075), (0.075, 0.035, 0.04), K.principled("#ffcf5a", 0.5), 0.01), pm)
    K.place(K.box("BusWindows", (0.29, -0.056, 0.085), (0.06, 0.002, 0.015), K.principled("#4aa8ff", 0.3)), pm)
    # Leaf emblem on top: lights up when all choices are made
    leaf = K.principled(LEAF, 0.5, emit="#9dff8a", emit_str=2.0 if done else 0.0)
    K.rod("LeafStem", (0, 0.2, 0.45), (0, 0.2, 0.55), 0.01, K.principled(MOSS, 0.6))
    K.sphere("Leaf", (0.0, 0.2, 0.6), (0.06, 0.02, 0.09), leaf)


# ---------------------------------------------------------------- 지구 수호자 중앙 제어기
def final(done):
    K.cyl("Base", (0, 0.02, 0.05), 0.42, 0.1, K.principled(STONE, 0.7), 0.015, verts=8)
    K.cyl("Moss", (0, 0.02, 0.105), 0.36, 0.015, K.principled(MOSS, 0.8), verts=8)
    K.cyl("Pedestal", (0, 0.02, 0.17), 0.14, 0.13, K.principled(WOOD, 0.6), 0.02)
    K.torus("GoldRing", (0, 0.02, 0.23), 0.15, 0.012, K.principled("#e8c060", 0.3, 0.8))
    # Globe: dull and hazy before, bright and green after
    sea = K.principled("#3a8fd8", 0.35, emit="#3a8fd8", emit_str=0.8) if done else K.principled("#6a7a8a", 0.5)
    land = K.principled("#5fd068", 0.5, emit="#5fd068", emit_str=0.6) if done else K.principled("#8a7a5a", 0.7)
    G = (0, 0.02, 0.42)
    K.sphere("Globe", G, 0.17, sea, segs=32)
    for i, (az, el, s) in enumerate(((200, 20, 0.08), (250, -15, 0.06), (300, 30, 0.07), (160, -25, 0.05), (330, -10, 0.05))):
        a, e = math.radians(az), math.radians(el)
        d = Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))
        c = Vector(G) + d * 0.155
        blob = K.sphere(f"Land{i}", (0, 0, 0), (s, s, 0.03), land, segs=16)
        K.place(blob, Matrix.Translation(c) @ Vector((0, 0, 1)).rotation_difference(d).to_matrix().to_4x4())
    if not done:  # smoky haze around the globe
        haze = K.principled("#b0a898", 0.8, emit="#b0a898", emit_str=0.1)
        for i in range(5):
            a = math.radians(i * 72 + 20)
            K.sphere(f"Haze{i}", (0.2 * math.cos(a), 0.02 + 0.2 * math.sin(a), 0.5 + 0.05 * (i % 2)), 0.05, haze, segs=12)
    else:
        halo = K.glow("#e1ffba", 2.0)
        K.torus("OrbitA", G, 0.23, 0.008, halo, rot=(math.radians(70), 0, math.radians(20)))
        K.torus("OrbitB", G, 0.23, 0.008, halo, rot=(math.radians(70), 0, math.radians(-40)))
        K.sphere("Star", (0, 0.02, 0.66), (0.04, 0.02, 0.04), K.principled("#ffe39b", 0.3, emit="#ffd860", emit_str=3.5), segs=6)
        K.point_light((0, -0.25, 0.45), 3.0, (0.85, 1.0, 0.75), 0.06)
    for i in range(4):
        a = math.radians(45 + i * 90)
        K.sphere(f"Lamp{i}", (0.33 * math.cos(a), 0.02 + 0.33 * math.sin(a), 0.13), 0.028, lamp_mat(done))


# ---------------------------------------------------------------- 숲의 관찰 기록
def forestLog(visited):
    for x in (-0.2, 0.2):
        K.rod(f"Leg{x}", (x, 0.1, 0.0), (x * 0.9, 0.04, 0.55), 0.018, K.principled(DARKWOOD, 0.7))
    sm = tilt_frame((-0.02, 0.0, 0.4), 72)
    K.place(K.box("Board", (0, 0, 0), (0.24, 0.17, 0.02), K.principled(WOOD, 0.6), 0.01), sm)
    K.place(K.box("Paper", (-0.06, 0.0, 0.024), (0.13, 0.14, 0.004), K.principled("#f3ead2", 0.6)), sm)
    for i in range(4):
        K.place(K.box(f"Line{i}", (-0.06, 0.09 - i * 0.05, 0.03), (0.09, 0.006, 0.002), K.principled("#6a5a42", 0.6)), sm)
    leaf = K.principled(LEAF, 0.5, emit="#9dff8a", emit_str=1.5 if visited else 0.0)
    K.place(K.sphere("PinnedLeaf", (0.14, 0.04, 0.03), (0.04, 0.065, 0.01), leaf), sm)
    K.place(K.sphere("Pin", (0.14, 0.1, 0.04), 0.012, K.principled("#e0483c", 0.4)), sm)
    if visited:
        K.place(K.cyl("Stamp", (0.14, -0.08, 0.03), 0.035, 0.006, K.principled("#9dff8a", 0.4, emit="#7cf06a", emit_str=1.6)), sm)
    K.cyl("Pot", (0.33, -0.08, 0.05), 0.07, 0.1, K.principled("#b0603a", 0.7), r2=0.055)
    fir("PotFir", (0.33, -0.08, 0.1), 0.3, LEAF)


# ---------------------------------------------------------------- 산호초 연구 노트
def coralLog(visited):
    K.box("Stand", (0, 0.04, 0.12), (0.36, 0.17, 0.12), K.principled(DARKWOOD, 0.7), 0.012)
    tank = K.box("Tank", (0, 0.04, 0.38), (0.32, 0.14, 0.14), K.glass("#d7f3ff"))
    K.box("BackWall", (0, 0.17, 0.38), (0.3, 0.005, 0.12), K.principled("#2a6f9a", 0.4, emit="#3ab8e8", emit_str=0.9 if visited else 0.1))
    K.box("Sand", (0, 0.04, 0.26), (0.3, 0.125, 0.02), K.principled("#c9b98a", 0.8))
    for y in (-0.1, 0.18):
        K.box(f"Rim{y}", (0, y, 0.52), (0.33, 0.012, 0.012), K.principled("#2a3a40", 0.5))
    colors = ("#ff7a7a", "#ffb04a", "#ff8ac8", "#a8f0d8")
    for i, (x, h) in enumerate(((-0.2, 0.12), (-0.08, 0.16), (0.06, 0.1), (0.18, 0.14))):
        m = K.principled(colors[i], 0.6)
        K.cyl(f"Coral{i}", (x, 0.06, 0.28 + h / 2), 0.016, h, m)
        K.sphere(f"CoralTip{i}", (x, 0.06, 0.28 + h), 0.03, m, segs=10)
    K.sphere("Fish", (0.0, 0.0, 0.4), (0.04, 0.015, 0.025), K.principled("#ffb04a", 0.5))
    # Clipboard leaning on the stand
    cm = tilt_frame((0.25, -0.15, 0.12), 70)
    K.place(K.box("Clipboard", (0, 0, 0), (0.08, 0.1, 0.008), K.principled(WOOD, 0.6)), cm)
    K.place(K.box("Note", (0, -0.01, 0.01), (0.065, 0.08, 0.003), K.principled("#f3ead2", 0.6)), cm)
    if visited:
        K.point_light((0, -0.1, 0.45), 2.0, (0.6, 0.9, 1.0), 0.05)


# ---------------------------------------------------------------- 미래 생태계 안내판
def futureLog(visited):
    K.cyl("Base", (0, 0.03, 0.03), 0.28, 0.06, K.principled(STONE, 0.7), 0.012, verts=24)
    K.cyl("Grass", (0, 0.03, 0.065), 0.25, 0.012, K.principled(MOSS, 0.8), verts=24)
    K.rod("Post", (-0.12, 0.08, 0.07), (-0.12, 0.08, 0.55), 0.022, K.principled(DARKWOOD, 0.7))
    sm = tilt_frame((-0.12, 0.04, 0.5), 68)
    K.place(K.box("Sign", (0, 0, 0), (0.17, 0.12, 0.018), K.principled("#2f4a3a", 0.5), 0.01), sm)
    scr = K.principled("#b6fd98", 0.3, emit="#b6fd98", emit_str=1.4) if visited else K.principled("#3a5a48", 0.4, emit="#3a5a48", emit_str=0.4)
    K.place(K.box("Display", (0, 0, 0.02), (0.15, 0.1, 0.003), scr), sm)
    K.place(K.rod("SproutStem", Vector((0, -0.05, 0.026)), Vector((0, 0.03, 0.026)), 0.006, K.principled("#2a6a3a", 0.5)), sm)
    for s in (-1, 1):
        K.place(K.sphere(f"SproutLeaf{s}", (0.03 * s, 0.04, 0.027), (0.028, 0.016, 0.004), K.principled("#2a6a3a", 0.5)), sm)
    # Solar panel and sapling
    K.rod("PanelPost", (0.17, 0.1, 0.07), (0.17, 0.1, 0.3), 0.012, K.principled("#9aa0a6", 0.3, 0.8))
    K.box("Solar", (0.17, 0.08, 0.32), (0.11, 0.08, 0.008), K.principled("#2a4a8a", 0.25, 0.4), 0.004, rot=(math.radians(-30), 0, 0))
    K.cyl("Sapling", (0.12, -0.12, 0.13), 0.01, 0.12, K.principled("#5a3d28", 0.8))
    K.sphere("SaplingTop", (0.12, -0.12, 0.22), (0.05, 0.05, 0.045), K.principled(LEAF, 0.6))
    if visited:
        K.sphere("Flower", (0.15, -0.14, 0.26), 0.02, K.principled("#ff8ac8", 0.4, emit="#ff8ac8", emit_str=1.2), segs=10)


BUILDERS = {"sort": sort, "impact": impact, "action": action, "final": final,
            "forestLog": forestLog, "coralLog": coralLog, "futureLog": futureLog}

if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:]
    out_dir = argv[0]
    names = argv[1:] or list(BUILDERS)
    os.makedirs(os.path.join(out_dir, "source"), exist_ok=True)
    for name in names:
        f = FILES[name]
        K.build_sheet(BUILDERS[name], os.path.join(out_dir, f + ".png"),
                      os.path.join(out_dir, "source", f + ".blend"), world=WORLD)
