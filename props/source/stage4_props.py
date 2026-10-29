"""Stage 4 (발화점 실험실) station sprites — brass / sandstone forge look.

Usage:
  blender -b --factory-startup --python stage4_props.py -- <props_dir> [match thermo triangle final sign lift cooler notes]
Writes <props_dir>/<file>.png (two 192px cells: before | done or inspected) and <props_dir>/source/<file>.blend.
liftA and liftB share the "lift" sprite.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Matrix, Vector
import prop_kit as K

WORLD = "#d9bfa4"  # warm fill light to match the forge floors
FILES = {
    "match": "s4-match-bench",
    "thermo": "s4-ignition-dial",
    "triangle": "s4-fire-triangle",
    "final": "s4-emergency-stop",
    "sign": "s4-safety-sign",
    "lift": "s4-brass-lift",
    "cooler": "s4-cooler",
    "notes": "s4-research-notes",
}

# Forge palette
BRASS, BRONZE, COPPER = "#d2a15a", "#8a5a36", "#c77a4c"
IRON, DARKWOOD, WOOD, SAND = "#4a3f3c", "#5b3a2a", "#a87a52", "#c29a6e"


def tilt_frame(center, angle_deg):
    """Frame rotated about X: local +Z becomes the surface normal (90 = upright, facing the camera)."""
    return Matrix.Translation(Vector(center)) @ Matrix.Rotation(math.radians(angle_deg), 4, "X")


def lamp_mat(on, off_color="#ffb04a"):
    if on:
        return K.principled("#7cf0a0", 0.3, emit="#7cf0a0", emit_str=3)
    return K.principled(off_color, 0.3, emit=off_color, emit_str=2.5)


def bench(top_z=0.3, half=(0.48, 0.25), top="#b58a63"):
    """Sandstone-topped wooden forge bench shared by several props."""
    K.box("BenchBody", (0, 0, top_z / 2 - 0.01), (half[0] - 0.03, half[1] - 0.03, top_z / 2 - 0.01), K.principled(DARKWOOD, 0.7), 0.012)
    K.box("BenchTop", (0, 0, top_z), (half[0], half[1], 0.025), K.principled(top, 0.6), 0.012)
    K.box("BenchTrim", (0, -half[1] - 0.003, top_z - 0.005), (half[0], 0.006, 0.02), K.principled(BRASS, 0.35, 0.8))
    K.box("BenchPlinth", (0, 0, 0.02), (half[0] - 0.02, half[1] - 0.02, 0.02), K.principled(IRON, 0.7))
    return top_z + 0.025


# ---------------------------------------------------------------- 성냥 비교 실험대
def match(done):
    base = bench()
    iron = K.principled("#5a5050", 0.45, 0.7)
    plate = K.principled("#8a7e76", 0.4, 0.6)
    G = K.glass("#f3e3c8")
    # Alcohol lamp
    K.cyl("LampBody", (0, 0.02, base + 0.05), 0.08, 0.1, G, 0.02)
    K.cyl("LampFuel", (0, 0.02, base + 0.03), 0.07, 0.05, K.principled("#b8d9e8", 0.1, emit="#b8d9e8", emit_str=0.2))
    K.cyl("LampNeck", (0, 0.02, base + 0.11), 0.03, 0.03, K.principled(BRASS, 0.35, 0.8))
    K.cyl("Wick", (0, 0.02, base + 0.135), 0.008, 0.025, K.principled("#2a2018", 0.9), verts=8)
    if done:
        K.flame("LampFlame", (0, 0.02, base + 0.14), 1.3, outer="#ff9a3a")
    # Tripod and iron plate
    PZ = base + 0.27
    K.torus("TripodRing", (0, 0.02, PZ - 0.012), 0.15, 0.01, iron)
    for i in range(3):
        a = math.radians(90 + 120 * i)
        K.rod(f"Leg{i}", (0.15 * math.cos(a), 0.02 + 0.15 * math.sin(a), PZ - 0.012),
              (0.2 * math.cos(a), 0.02 + 0.2 * math.sin(a), base), 0.01, iron)
    K.box("Plate", (0, 0.02, PZ), (0.22, 0.18, 0.008), plate, 0.004)
    # Match head (left) and wood piece (right), same distance from the centre
    K.sphere("MatchHead", (-0.1, 0.0, PZ + 0.025), (0.04, 0.04, 0.026), K.principled("#d8352a", 0.6))
    K.box("WoodPiece", (0.1, 0.0, PZ + 0.022), (0.06, 0.018, 0.014), K.principled("#f0d098", 0.7))
    if done:  # the head reaches its (lower) ignition point first
        K.flame("HeadFlame", (-0.1, 0.0, PZ + 0.045), 1.6)
        K.point_light((0, -0.05, PZ - 0.06), 1.5, (1, 0.6, 0.3))
    # Matchbox on the bench
    K.box("Matchbox", (0.36, -0.08, base + 0.025), (0.07, 0.045, 0.025), K.principled("#e0583c", 0.6), 0.004)
    K.box("MatchboxLabel", (0.36, -0.08, base + 0.051), (0.05, 0.03, 0.002), K.principled("#ffd36a", 0.6))
    K.box("Strike", (0.36, -0.126, base + 0.025), (0.06, 0.002, 0.018), K.principled("#4a2a22", 0.9))


# ---------------------------------------------------------------- 발화점 온도 조절기
def thermo(done):
    brass = K.principled(BRASS, 0.35, 0.8)
    K.box("Cabinet", (-0.05, 0.03, 0.22), (0.3, 0.2, 0.22), K.principled(BRONZE, 0.5, 0.4), 0.02)
    K.box("Plinth", (-0.05, 0.03, 0.02), (0.32, 0.22, 0.02), K.principled(IRON, 0.7))
    K.box("TopTrim", (-0.05, 0.03, 0.445), (0.31, 0.21, 0.012), brass)
    # Big dial tilted toward the camera: blue (low) / orange (head ignites) / red (both ignite)
    dm = tilt_frame((-0.05, -0.02, 0.52), 62)
    K.place(K.cyl("DialBody", (0, 0, 0), 0.2, 0.05, brass), dm)
    K.place(K.cyl("DialFace", (0, 0, 0.026), 0.17, 0.004, K.principled("#f3e6c8", 0.5)), dm)
    for i, (deg, c) in enumerate(((150, "#5aa8ff"), (90, "#ff9a3a"), (30, "#e0483c"))):
        a = math.radians(deg)
        K.place(K.box(f"Zone{i}", (0.125 * math.cos(a), 0.125 * math.sin(a), 0.03), (0.035, 0.014, 0.003),
                      K.principled(c, 0.5), rot=(0, 0, a + math.pi / 2)), dm)
    ang = math.radians(90 if done else 150)
    needle = K.box("Needle", (0, 0, 0), (0.008, 0.06, 0.004), K.principled("#2a1d18", 0.5))
    needle.location = (0, 0.055, 0.034)
    K.place(needle, dm @ Matrix.Rotation(ang - math.pi / 2, 4, "Z"))
    K.place(K.cyl("DialHub", (0, 0, 0.036), 0.025, 0.012, brass), dm)
    # Thermometer column
    G = K.glass("#fff2dc")
    K.cyl("ThermoTube", (0.33, 0.0, 0.33), 0.032, 0.5, G)
    K.sphere("ThermoBulb", (0.33, 0.0, 0.1), 0.045, K.principled("#e0483c", 0.3, emit="#e0483c", emit_str=0.6))
    level = 0.26 if done else 0.08
    K.cyl("ThermoLiquid", (0.33, 0.0, 0.1 + level / 2), 0.018, level, K.principled("#e0483c", 0.3, emit="#e0483c", emit_str=0.6))
    K.box("ThermoBack", (0.33, 0.04, 0.33), (0.05, 0.01, 0.26), K.principled(DARKWOOD, 0.6), 0.008)
    # Knob and lamp on the cabinet front
    K.cyl("Knob", (-0.2, -0.18, 0.2), 0.05, 0.04, brass, rot=(math.radians(90), 0, 0))
    K.box("KnobMark", (-0.2, -0.205, 0.225), (0.006, 0.004, 0.02), K.principled("#2a1d18", 0.5))
    K.box("LampRing", (0.12, -0.172, 0.2), (0.045, 0.004, 0.045), K.principled(IRON, 0.7), 0.006)
    K.sphere("Lamp", (0.12, -0.178, 0.2), (0.03, 0.018, 0.03), lamp_mat(done))


# ---------------------------------------------------------------- 연소 조건 제어판
def triangle(done):
    brass = K.principled(BRASS, 0.35, 0.8)
    K.cyl("Pedestal", (0, 0.02, 0.07), 0.4, 0.14, K.principled("#a07a5a", 0.7), 0.02, verts=6)
    K.cyl("PedestalTop", (0, 0.02, 0.15), 0.36, 0.025, K.principled(IRON, 0.6, 0.4), verts=6)
    K.torus("PedestalRing", (0, 0.02, 0.14), 0.4, 0.012, brass)
    K.rod("Post", (0, 0.06, 0.16), (0, 0.06, 0.26), 0.03, brass)
    # Upright triangle facing the camera: heat (top), fuel (left), oxygen (right)
    tm = tilt_frame((0, 0.06, 0.48), 72)
    R = 0.24
    pts = [Vector((R * math.cos(math.radians(a)), R * math.sin(math.radians(a)), 0)) for a in (90, 210, 330)]
    edge = K.principled("#ffd36a", 0.3, emit="#ffc040", emit_str=2.5) if done else K.principled(BRONZE, 0.5, 0.5)
    for i in range(3):
        a, b = pts[i], pts[(i + 1) % 3]
        K.place(K.rod(f"Edge{i}", a, b, 0.018, edge), tm)
    nodes = (("#e0483c", "Heat"), ("#a8693a", "Fuel"), ("#5aa8ff", "Oxygen"))
    for p, (c, n) in zip(pts, nodes):
        m = K.principled(c, 0.35, emit=c, emit_str=2.2 if done else 0.25)
        K.place(K.sphere(f"Node{n}", tuple(p), 0.055, m), tm)
        K.place(K.torus(f"NodeRing{n}", tuple(p), 0.06, 0.01, brass), tm)
    # Centre burner: lit only when all three conditions are met
    K.place(K.cyl("Burner", (0, -0.03, 0), 0.04, 0.03, K.principled(IRON, 0.5, 0.6), rot=(math.radians(-72), 0, 0)), tm)
    if done:
        c = tm @ Vector((0, -0.04, 0.02))
        K.flame("CoreFlame", (c.x, c.y, c.z), 1.6)


# ---------------------------------------------------------------- 최종 비상 정지기 (과열로)
def final(done):
    brass = K.principled(BRASS, 0.35, 0.8)
    iron = K.principled(IRON, 0.6, 0.5)
    FX = -0.12
    K.box("Furnace", (FX, 0.06, 0.27), (0.3, 0.19, 0.27), K.principled("#6a3f33", 0.75), 0.02)
    for z in (0.12, 0.42):
        K.box(f"Band{z}", (FX, 0.06, z), (0.305, 0.195, 0.018), brass)
    K.box("FurnaceTop", (FX, 0.06, 0.55), (0.32, 0.21, 0.02), iron, 0.008)
    K.cyl("Chimney", (FX + 0.12, 0.12, 0.66), 0.06, 0.2, iron)
    K.torus("ChimneyRim", (FX + 0.12, 0.12, 0.76), 0.062, 0.012, brass)
    # Furnace window: roaring fire before, cold after the emergency stop
    K.box("WindowFrame", (FX, -0.135, 0.27), (0.16, 0.012, 0.11), brass, 0.01)
    if done:
        K.box("Window", (FX, -0.142, 0.27), (0.13, 0.006, 0.085), K.principled("#2a3440", 0.4))
    else:
        K.box("Window", (FX, -0.142, 0.27), (0.13, 0.006, 0.085), K.glow("#ff7a2a", 2.4))
        K.box("WindowHot", (FX, -0.147, 0.24), (0.1, 0.004, 0.04), K.glow("#ffd27a", 3.2))
        K.point_light((FX, -0.3, 0.3), 3.0, (1, 0.55, 0.25), 0.05)
    for i in range(3):
        K.box(f"Grill{i}", (FX - 0.07 + i * 0.07, -0.152, 0.27), (0.008, 0.004, 0.085), iron)
    K.sphere("Beacon", (FX - 0.2, 0.0, 0.59), (0.04, 0.04, 0.035), lamp_mat(done, "#ff4a3a"))
    # Emergency stop pedestal
    SX, SY = 0.3, -0.08
    K.cyl("StopPost", (SX, SY, 0.15), 0.085, 0.3, K.principled("#f2c14e", 0.5), 0.01)
    for i in range(3):
        K.cyl(f"Stripe{i}", (SX, SY, 0.06 + i * 0.09), 0.087, 0.03, K.principled("#2a2420", 0.6))
    K.cyl("StopCollar", (SX, SY, 0.31), 0.1, 0.03, iron)
    press = 0.025 if done else 0.0
    K.cyl("StopStem", (SX, SY, 0.34 - press / 2), 0.04, 0.04, K.principled("#7a1c18", 0.5))
    K.sphere("StopButton", (SX, SY, 0.37 - press), (0.09, 0.09, 0.045), K.principled("#e0302a", 0.35))


# ---------------------------------------------------------------- 안전 안내판
def sign(inspected):
    brass = K.principled(BRASS, 0.35, 0.8)
    for x in (-0.22, 0.22):
        K.box(f"Foot{x}", (x, 0.04, 0.02), (0.05, 0.14, 0.02), K.principled(IRON, 0.7), 0.008)
        K.rod(f"PostRod{x}", (x, 0.04, 0.03), (x, 0.06, 0.62), 0.022, brass)
    sm = tilt_frame((0, 0.03, 0.42), 76)
    K.place(K.box("BoardFrame", (0, 0, 0), (0.28, 0.2, 0.025), K.principled(DARKWOOD, 0.6), 0.012), sm)
    K.place(K.box("BoardFace", (0, 0, 0.022), (0.25, 0.175, 0.006), K.principled("#efdcb4", 0.6)), sm)
    K.place(K.cyl("Warning", (0, 0.0, 0.03), 0.14, 0.008, K.principled("#f2b232", 0.5), verts=3), sm)
    K.place(K.cyl("WarningInner", (0, 0.0, 0.036), 0.105, 0.004, K.principled("#ffd36a", 0.5), verts=3), sm)
    K.place(K.box("Bang", (0, 0.015, 0.042), (0.012, 0.035, 0.004), K.principled("#2a1d18", 0.5)), sm)
    K.place(K.cyl("Dot", (0, -0.04, 0.042), 0.013, 0.008, K.principled("#2a1d18", 0.5)), sm)
    K.box("TopBar", (0, 0.07, 0.62), (0.26, 0.025, 0.02), brass, 0.008)
    K.sphere("Lamp", (0, 0.07, 0.67), (0.045, 0.045, 0.04), lamp_mat(inspected))


# ---------------------------------------------------------------- 열차단 이동 발판 (A/B)
def lift(inspected):
    brass = K.principled(BRASS, 0.35, 0.8)
    K.cyl("Base", (0, 0, 0.035), 0.44, 0.07, brass, 0.015, verts=48)
    K.cyl("Inner", (0, 0, 0.065), 0.35, 0.02, K.principled("#3a3352", 0.5, 0.3), verts=48)
    rune = K.principled("#c8b6ff", 0.3, emit="#b7a4ff", emit_str=3.2 if inspected else 0.6)
    K.torus("RuneRing", (0, 0, 0.08), 0.27, 0.014, rune)
    K.torus("RuneRing2", (0, 0, 0.08), 0.16, 0.01, rune)
    for i in range(8):
        a = math.radians(i * 45)
        K.box(f"Rune{i}", (0.215 * math.cos(a), 0.215 * math.sin(a), 0.078), (0.025, 0.008, 0.004), rune, rot=(0, 0, a))
    for i in range(4):
        a = math.radians(45 + i * 90)
        K.cyl(f"Pillar{i}", (0.4 * math.cos(a), 0.4 * math.sin(a), 0.1), 0.035, 0.14, K.principled(BRONZE, 0.5, 0.5))
        K.sphere(f"PillarCap{i}", (0.4 * math.cos(a), 0.4 * math.sin(a), 0.18), 0.04, rune)
    crystal = K.principled("#d9ccff", 0.15, emit="#b7a4ff", emit_str=3.5 if inspected else 0.8)
    K.sphere("Crystal", (0, 0, 0.3), (0.07, 0.07, 0.12), crystal, segs=4)
    if inspected:  # active portal: floating rings
        beam = K.glow("#c8b6ff", 2.2)
        for z, r in ((0.18, 0.13), (0.3, 0.1), (0.42, 0.07)):
            K.torus(f"Halo{z}", (0, 0, z), r, 0.008, beam)
        K.point_light((0, -0.1, 0.3), 2.5, (0.75, 0.65, 1.0), 0.05)


# ---------------------------------------------------------------- 냉각 보급 장치
def cooler(inspected):
    steel = K.principled("#8fb4bf", 0.35, 0.7)
    body = K.principled("#426b76", 0.5, 0.4)
    K.box("Cabinet", (-0.08, 0.03, 0.24), (0.3, 0.2, 0.24), body, 0.02)
    K.box("Plinth", (-0.08, 0.03, 0.02), (0.32, 0.22, 0.02), K.principled(IRON, 0.7))
    K.box("Lid", (-0.08, 0.03, 0.49), (0.31, 0.21, 0.02), K.principled("#7fa6b2", 0.4, 0.5), 0.012)
    flake = K.principled("#e8f8ff", 0.4, emit="#bff0ff", emit_str=1.5 if inspected else 0.3)
    for i in range(3):
        K.box(f"Flake{i}", (-0.08, 0.03, 0.512), (0.11, 0.012, 0.004), flake, rot=(0, 0, math.radians(60 * i)))
    # Fan grill on the front
    fm = tilt_frame((-0.12, -0.172, 0.26), 90)
    K.place(K.cyl("FanBack", (0, 0, 0), 0.15, 0.01, K.principled("#1e3540", 0.6)), fm)
    K.place(K.torus("FanRim", (0, 0, 0.01), 0.15, 0.016, steel), fm)
    for i in range(4):
        K.place(K.box(f"Blade{i}", (0, 0, 0.012), (0.13, 0.025, 0.004), steel, rot=(0, 0, math.radians(45 * i + 20))), fm)
    K.place(K.cyl("FanHub", (0, 0, 0.02), 0.03, 0.02, K.principled(BRASS, 0.35, 0.8)), fm)
    # Coolant tank
    G = K.glass("#e8fbff")
    K.cyl("Tank", (0.33, 0.0, 0.27), 0.09, 0.42, G, 0.02)
    K.cyl("Coolant", (0.33, 0.0, 0.2), 0.078, 0.26, K.principled("#5ad0ff", 0.15, emit="#5ad0ff", emit_str=1.6 if inspected else 0.4))
    K.cyl("TankCap", (0.33, 0.0, 0.5), 0.095, 0.04, K.principled(BRASS, 0.35, 0.8))
    K.cyl("TankBase", (0.33, 0.0, 0.04), 0.1, 0.06, K.principled(IRON, 0.6, 0.4))
    K.tube("Pipe", [(0.33, 0.0, 0.42), (0.26, -0.02, 0.5), (0.16, 0.0, 0.42), (0.2, -0.05, 0.36)], 0.016, K.principled(COPPER, 0.35, 0.8))
    for i in range(3):
        K.sphere(f"Light{i}", (0.06 + i * 0.07, -0.175, 0.42), (0.022, 0.014, 0.022),
                 K.principled("#7fe6ff", 0.3, emit="#7fe6ff", emit_str=3) if inspected else K.principled("#355a66", 0.4))
    if inspected:  # cold mist
        mist = K.principled("#f2fcff", 0.5, emit="#d8f6ff", emit_str=0.6)
        for i, (x, z, r) in enumerate(((-0.25, 0.53, 0.05), (-0.12, 0.55, 0.06), (0.02, 0.53, 0.045), (0.12, 0.52, 0.035))):
            K.sphere(f"Mist{i}", (x, 0.0, z), r, mist, segs=12)


# ---------------------------------------------------------------- 발화점 연구 노트
def notes(inspected):
    wood = K.principled(DARKWOOD, 0.65)
    K.box("Desk", (0, 0.04, 0.2), (0.4, 0.21, 0.2), wood, 0.015)
    K.box("DeskTop", (0, 0.04, 0.41), (0.43, 0.24, 0.018), K.principled(WOOD, 0.6), 0.01)
    K.box("Plinth", (0, 0.04, 0.02), (0.41, 0.22, 0.02), K.principled(IRON, 0.7))
    K.box("Drawer", (0, -0.172, 0.28), (0.25, 0.006, 0.07), K.principled(WOOD, 0.6), 0.006)
    K.box("DrawerPull", (0, -0.18, 0.28), (0.05, 0.008, 0.01), K.principled(BRASS, 0.35, 0.8))
    # Open notebook on a slanted reading board
    bm_ = tilt_frame((-0.05, 0.02, 0.47), 28)
    K.place(K.box("Board", (0, 0, 0), (0.25, 0.17, 0.012), K.principled(BRONZE, 0.5, 0.4), 0.006), bm_)
    page = K.principled("#f3e2bd", 0.6, emit="#ffe6a8", emit_str=0.9 if inspected else 0.0)
    for s in (-1, 1):
        K.place(K.box(f"Page{s}", (0.105 * s, 0, 0.022), (0.1, 0.14, 0.008), page, rot=(0, math.radians(-6 * s), 0)), bm_)
        for i in range(4):
            K.place(K.box(f"Line{s}{i}", (0.105 * s, 0.08 - i * 0.045, 0.033), (0.07, 0.006, 0.002), K.principled("#6a4a36", 0.6)), bm_)
    K.place(K.box("Spine", (0, 0, 0.018), (0.008, 0.145, 0.01), K.principled("#7a2a22", 0.6)), bm_)
    if inspected:
        K.place(K.box("Ribbon", (0.02, -0.17, 0.03), (0.012, 0.05, 0.002), K.principled("#e0483c", 0.5)), bm_)
        K.point_light((-0.05, -0.2, 0.62), 1.2, (1, 0.85, 0.6), 0.05)
    # Scroll, ink bottle and quill
    K.cyl("Scroll", (0.31, 0.1, 0.46), 0.035, 0.2, K.principled("#efdcb4", 0.6), rot=(math.radians(90), 0, math.radians(20)))
    K.cyl("Ink", (0.3, -0.12, 0.46), 0.04, 0.07, K.principled("#1e2430", 0.2))
    K.cyl("InkCap", (0.3, -0.12, 0.505), 0.02, 0.02, K.principled(BRASS, 0.35, 0.8))
    K.rod("Quill", (0.3, -0.12, 0.49), (0.38, -0.05, 0.66), 0.006, K.principled("#f6f3ea", 0.6))
    K.sphere("Feather", (0.355, -0.07, 0.6), (0.025, 0.012, 0.07), K.principled("#f6f3ea", 0.6))


# ================================================================ Fire-out puzzle
# Fires block the maze until the right condition of combustion is removed.
# Frame 0 = burning, frame 1 = extinguished (the tile becomes walkable).
def scorch(r=0.3):
    K.cyl("Scorch", (0, 0, 0.004), r, 0.008, K.principled("#2a1d1a", 0.95), verts=24)


def fire_cluster(points):
    """Several stacked flames read as one fire at sprite size."""
    for i, (x, y, z, s) in enumerate(points):
        K.flame(f"Fire{i}", (x, y, z), s, outer="#ff7a1f" if i % 2 else "#ff9a3a")


def smoke(points):
    m = K.principled("#b9b2aa", 0.8, emit="#b9b2aa", emit_str=0.15)
    for i, (x, y, z, r) in enumerate(points):
        K.sphere(f"Smoke{i}", (x, y, z), r, m, segs=12)


def fire_lamp(out):
    """Knocked-over alcohol lamp: put out by covering it (cut off oxygen)."""
    scorch(0.34)
    G = K.glass("#f3e3c8")
    brass = K.principled(BRASS, 0.35, 0.8)
    if out:
        K.cyl("Lamp", (-0.05, 0.04, 0.06), 0.09, 0.12, G, 0.02)
        K.cyl("Fuel", (-0.05, 0.04, 0.035), 0.08, 0.05, K.principled("#b8d9e8", 0.1))
        K.cyl("Neck", (-0.05, 0.04, 0.13), 0.035, 0.03, brass)
        K.cyl("Cap", (-0.05, 0.04, 0.175), 0.05, 0.07, brass, 0.01)  # the lid smothers the flame
        K.sphere("FireBlanket", (0.14, -0.06, 0.03), (0.17, 0.12, 0.04), K.principled("#c9b48a", 0.9))
        smoke([(0.12, -0.06, 0.14, 0.04), (0.15, -0.05, 0.22, 0.05)])
    else:
        lamp = K.cyl("Lamp", (0, 0, 0), 0.09, 0.12, G, 0.02, rot=(0, math.radians(90), math.radians(20)))
        lamp.location = (-0.17, 0.08, 0.09)
        K.cyl("Neck", (-0.07, 0.04, 0.09), 0.035, 0.05, brass, rot=(0, math.radians(90), math.radians(20)))
        K.sphere("Spill", (0.08, -0.04, 0.008), (0.26, 0.17, 0.01), K.principled("#6f9fc8", 0.05, emit="#5f8fd8", emit_str=0.25))
        fire_cluster([(0.03, -0.02, 0.0, 3.6), (0.16, -0.06, 0.0, 3.0), (-0.07, -0.08, 0.0, 2.6), (0.1, 0.07, 0.0, 2.8), (0.23, 0.02, 0.0, 2.2)])


def fire_gas(out):
    """Leaking gas pipe: put out by closing the valve (remove the fuel)."""
    scorch(0.26)
    pipe = K.principled("#e8c040", 0.4, 0.4)
    K.box("Floorplate", (0, 0.12, 0.02), (0.22, 0.1, 0.02), K.principled(IRON, 0.6, 0.5), 0.008)
    K.cyl("PipeRun", (0, 0.16, 0.08), 0.045, 0.44, pipe, rot=(0, math.radians(90), 0))
    K.cyl("Riser", (0.02, 0.1, 0.16), 0.045, 0.16, pipe)
    K.cyl("Flange", (0.02, 0.1, 0.25), 0.065, 0.025, K.principled(IRON, 0.5, 0.6))
    K.cyl("BrokenTip", (0.02, 0.1, 0.28), 0.04, 0.04, K.principled("#8a7a5a", 0.6, 0.4), r2=0.03)
    for x in (-0.18, 0.18):
        K.box(f"Bracket{x}", (x, 0.16, 0.05), (0.02, 0.05, 0.05), K.principled(IRON, 0.6))
    K.box("Warn", (-0.13, 0.205, 0.14), (0.05, 0.004, 0.04), K.principled("#f2c14e", 0.5))
    if out:
        smoke([(0.03, 0.1, 0.36, 0.035)])
    else:  # tall jet flame with a blue core
        K.sphere("JetCore", (0.02, 0.1, 0.38), (0.03, 0.03, 0.1), K.glow("#7fb8ff", 3.0), segs=14)
        fire_cluster([(0.02, 0.1, 0.28, 4.2), (0.06, 0.08, 0.3, 3.0), (-0.03, 0.12, 0.29, 2.8)])


def fire_wood(out):
    """Burning woodpile: put out with water (cool it below the ignition point)."""
    scorch(0.36)
    log = K.principled("#2a1d18", 0.9) if out else K.principled("#7a4a2a", 0.85)
    ember = K.principled("#3a2420", 0.9) if out else K.principled("#c8501f", 0.5, emit="#ff5a1a", emit_str=1.5)
    for i, a in enumerate((0, 60, 120)):
        K.cyl(f"Log{i}", (0, 0, 0.05 + i * 0.03), 0.045, 0.5, log, 0.01, rot=(0, math.radians(90), math.radians(a)))
    K.cyl("Embers", (0, 0, 0.03), 0.16, 0.03, ember)
    for i, (x, y) in enumerate(((-0.24, 0.12), (0.26, 0.1), (0.2, -0.15))):
        K.sphere(f"Stone{i}", (x, y, 0.03), (0.06, 0.05, 0.04), K.principled("#6a6058", 0.8))
    if out:
        K.sphere("Puddle", (0.02, -0.04, 0.006), (0.3, 0.2, 0.008), K.principled("#5aa8d8", 0.05, emit="#5aa8d8", emit_str=0.3))
        steam = K.principled("#f2f6f8", 0.7, emit="#e8f0f4", emit_str=0.4)
        for i, (x, z, r) in enumerate(((-0.05, 0.2, 0.05), (0.06, 0.28, 0.06), (-0.02, 0.38, 0.05))):
            K.sphere(f"Steam{i}", (x, 0.0, z), r, steam, segs=12)
    else:
        fire_cluster([(0.0, 0.0, 0.1, 3.6), (0.1, -0.04, 0.08, 2.6), (-0.11, 0.03, 0.08, 2.6), (0.03, 0.08, 0.09, 2.2), (-0.04, -0.08, 0.07, 2.0)])


def gas_valve(closed):
    """Gas shut-off valve on a wall pipe. Lever along the pipe = open, across the pipe = closed."""
    pipe = K.principled("#e8c040", 0.4, 0.4)
    K.box("Wall", (0, 0.2, 0.32), (0.3, 0.04, 0.3), K.principled("#986b52", 0.8), 0.01)
    K.cyl("PipeIn", (-0.15, 0.12, 0.32), 0.04, 0.3, pipe, rot=(0, math.radians(90), 0))
    K.cyl("PipeOut", (0.15, 0.12, 0.32), 0.04, 0.3, pipe, rot=(0, math.radians(90), 0))
    K.box("Body", (0, 0.1, 0.32), (0.07, 0.06, 0.07), K.principled("#c08a3a", 0.4, 0.6), 0.02)
    K.cyl("Stem", (0, 0.05, 0.32), 0.015, 0.06, K.principled(IRON, 0.4, 0.7), rot=(math.radians(90), 0, 0))
    lever = K.principled("#e0302a", 0.4) if closed else K.principled("#3aa860", 0.4)
    rot = (math.radians(90), 0, 0) if closed else (0, math.radians(90), 0)
    K.box("Lever", (0, 0.0, 0.32), (0.14, 0.02, 0.02), lever, 0.008, rot=(0, 0, 0) if not closed else (0, math.radians(90), 0))
    K.box("Tag", (0.18, 0.06, 0.48), (0.06, 0.006, 0.035), K.principled("#e0302a" if closed else "#f2c14e", 0.5))
    K.box("Base", (0, 0.12, 0.02), (0.3, 0.12, 0.02), K.principled(IRON, 0.6, 0.5), 0.008)
    K.sphere("Lamp", (-0.2, 0.15, 0.55), 0.03, lamp_mat(closed, "#ff6a3a"))


def water_tank(taken):
    """Firefighting water tank with a bucket under the tap."""
    tank = K.principled("#3a6fa8", 0.4, 0.4)
    K.cyl("Tank", (-0.08, 0.06, 0.28), 0.2, 0.5, tank, 0.03)
    K.cyl("TankTop", (-0.08, 0.06, 0.54), 0.21, 0.03, K.principled("#c4d0dc", 0.3, 0.8))
    K.torus("Band1", (-0.08, 0.06, 0.15), 0.205, 0.012, K.principled("#c4d0dc", 0.3, 0.8))
    K.torus("Band2", (-0.08, 0.06, 0.4), 0.205, 0.012, K.principled("#c4d0dc", 0.3, 0.8))
    K.box("Label", (-0.08, -0.14, 0.3), (0.1, 0.006, 0.06), K.principled("#e0302a", 0.5))
    K.box("LabelMark", (-0.08, -0.148, 0.3), (0.06, 0.003, 0.012), K.principled("#ffffff", 0.5))
    K.rod("Tap", (0.1, 0.0, 0.18), (0.22, -0.02, 0.18), 0.02, K.principled("#c4d0dc", 0.3, 0.8))
    K.cyl("Spout", (0.22, -0.02, 0.15), 0.018, 0.06, K.principled("#c4d0dc", 0.3, 0.8))
    if taken:  # bucket carried away; tap still dripping
        K.sphere("Drip", (0.22, -0.02, 0.06), (0.012, 0.012, 0.018), K.principled("#7fc8f0", 0.05, emit="#7fc8f0", emit_str=0.8))
        K.cyl("Ring", (0.24, -0.05, 0.004), 0.08, 0.006, K.principled("#5aa8d8", 0.1))
    else:
        K.cyl("Bucket", (0.24, -0.05, 0.06), 0.085, 0.12, K.principled("#e0583c", 0.5), r2=0.07)
        K.cyl("BucketWater", (0.24, -0.05, 0.115), 0.075, 0.01, K.principled("#5aa8d8", 0.05, emit="#5aa8d8", emit_str=0.6))
        K.torus("Handle", (0.24, -0.05, 0.13), 0.08, 0.006, K.principled("#c4d0dc", 0.3, 0.8), rot=(math.radians(90), 0, 0))


FILES.update({"fire_lamp": "s4-fire-lamp", "fire_gas": "s4-fire-gas", "fire_wood": "s4-fire-wood",
              "gas_valve": "s4-gas-valve", "water_tank": "s4-water-tank"})

BUILDERS = {"match": match, "thermo": thermo, "triangle": triangle, "final": final,
            "sign": sign, "lift": lift, "cooler": cooler, "notes": notes,
            "fire_lamp": fire_lamp, "fire_gas": fire_gas, "fire_wood": fire_wood,
            "gas_valve": gas_valve, "water_tank": water_tank}

if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:]
    out_dir = argv[0]
    names = argv[1:] or list(BUILDERS)
    os.makedirs(os.path.join(out_dir, "source"), exist_ok=True)
    for name in names:
        f = FILES[name]
        K.build_sheet(BUILDERS[name], os.path.join(out_dir, f + ".png"),
                      os.path.join(out_dir, "source", f + ".blend"), world=WORLD)
