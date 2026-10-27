"""Stage 3 (산소 공급실) station sprites.

Usage:
  blender -b --factory-startup --python stage3_props.py -- <props_dir> [generator valve console helper archive]
Writes <props_dir>/<file>.png (two 192px cells: before | done) and <props_dir>/source/<file>.blend.
The candle bench has its own script (candle_compare.py).
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Matrix, Vector
import prop_kit as K

FILES = {
    "generator": "oxygen-generator",
    "valve": "air-valve",
    "console": "oxygen-console",
    "helper": "guide-robot",
    "archive": "research-archive",
}


def tilt_frame(center, angle_deg):
    """Frame rotated about X: local +Z becomes the panel's surface normal."""
    return Matrix.Translation(Vector(center)) @ Matrix.Rotation(math.radians(angle_deg), 4, "X")


# ---------------------------------------------------------------- 산소 생성 장치
def generator(done):
    steel = K.principled("#b4ccce", 0.4, 0.3)
    body = K.principled("#2b6a74", 0.55, 0.3)
    dark = K.principled("#1e3a42", 0.7)
    rubber = K.principled("#5a3b33", 0.7)
    hose = K.principled("#d9a066", 0.5)
    water = K.principled("#2f8fb8", 0.15, emit="#2f8fb8", emit_str=0.08)
    h2o2 = K.principled("#8fd6f0", 0.1, emit="#8fd6f0", emit_str=0.15)
    powder = K.principled("#2a2420", 0.9)
    bubble = K.principled("#e8fffb", 0.1, emit="#bff8f0", emit_str=1.2)
    G = K.glass()

    TOP = 0.3
    K.box("Body", (0, 0, TOP / 2 - 0.01), (0.47, 0.24, TOP / 2 - 0.01), body, 0.012)
    K.box("Top", (0, 0, TOP), (0.52, 0.28, 0.022), steel, 0.01)
    K.box("Plinth", (0, 0, 0.02), (0.48, 0.25, 0.02), dark)
    for i in range(4):
        K.box(f"Vent{i}", (-0.33 + i * 0.07, -0.243, 0.16), (0.022, 0.004, 0.07), dark)
    lamp = K.principled("#5bf0c9", 0.3, emit="#5bf0c9", emit_str=3) if done else K.principled("#ffb04a", 0.3, emit="#ff9a3a", emit_str=2.5)
    K.box("LampRing", (0.3, -0.244, 0.17), (0.055, 0.004, 0.055), dark, 0.006)
    K.sphere("Lamp", (0.3, -0.25, 0.17), (0.035, 0.02, 0.035), lamp)
    base = TOP + 0.022

    # Conical flask with manganese dioxide + dropping funnel of hydrogen peroxide
    fx = -0.24
    K.cyl("FlaskBody", (fx, 0, base + 0.09), 0.13, 0.18, G, r2=0.045)
    K.cyl("FlaskNeck", (fx, 0, base + 0.22), 0.045, 0.08, G)
    K.cyl("Powder", (fx, 0, base + 0.01), 0.11, 0.015, powder)
    K.cyl("Liquid", (fx, 0, base + 0.04), 0.115, 0.06, h2o2, r2=0.085)
    K.cyl("Stopper", (fx, 0, base + 0.27), 0.05, 0.04, rubber)
    K.cyl("StandRod", (fx - 0.17, 0.1, base + 0.2), 0.012, 0.4, steel)
    K.box("StandFoot", (fx - 0.17, 0.1, base + 0.01), (0.06, 0.05, 0.01), dark)
    K.box("Clamp", (fx - 0.085, 0.05, base + 0.37), (0.085, 0.012, 0.012), steel)
    K.sphere("FunnelBulb", (fx, 0, base + 0.39), (0.06, 0.06, 0.075), G)
    K.sphere("FunnelLiquid", (fx, 0, base + 0.37), (0.048, 0.048, 0.045), h2o2)
    K.cyl("FunnelStem", (fx, 0, base + 0.3), 0.012, 0.1, G)
    K.box("Stopcock", (fx, 0, base + 0.315), (0.03, 0.008, 0.008), K.principled("#e0584f", 0.5))

    # Water tub with an upside-down collecting jar
    tx = 0.22
    tub = K.cyl("Tub", (tx, 0, base + 0.06), 0.18, 0.12, G)
    K.remove_cap(tub, top=True)
    K.cyl("TubWater", (tx, 0, base + 0.04), 0.17, 0.075, water)
    jx = tx + 0.04
    K.open_jar("CollectJar", (jx, 0.02, base), 0.075, 0.32, G, round_top=0.03)
    level = 0.1 if done else 0.29
    K.cyl("JarWater", (jx, 0.02, base + level / 2), 0.067, level, water)
    K.tube("Hose", [(fx + 0.03, 0, base + 0.29), (fx + 0.16, 0, base + 0.36), (tx - 0.1, -0.01, base + 0.24),
                    (tx - 0.06, 0.0, base + 0.05), (jx - 0.01, 0.02, base + 0.03)], 0.018, hose)
    if done:
        for i, (x, z, r) in enumerate(((0.02, 0.06, 0.012), (-0.04, 0.05, 0.01), (0.05, 0.035, 0.009), (-0.06, 0.03, 0.008))):
            K.sphere(f"FlaskBubble{i}", (fx + x, -0.06, base + z), r, bubble, segs=10)
        for i, (x, z, r) in enumerate(((0.0, 0.07, 0.016), (-0.02, 0.13, 0.013), (0.015, 0.18, 0.011), (-0.01, 0.23, 0.01))):
            K.sphere(f"JarBubble{i}", (jx + x, -0.03, base + z), r, bubble, segs=10)


# ---------------------------------------------------------------- 공기 흐름 밸브
def valve(done):
    steel = K.principled("#a9bcc8", 0.3, 0.8)
    dark = K.principled("#26384a", 0.6, 0.3)
    paint = K.principled("#3f6f9e", 0.45, 0.3)
    wheel = K.principled("#4fd8b8", 0.4, 0.2) if done else K.principled("#e0584f", 0.4, 0.2)
    face = K.principled("#f4f7f2", 0.5)
    lamp = K.principled("#5bf0c9", 0.3, emit="#5bf0c9", emit_str=3) if done else K.principled("#ff6a5a", 0.3, emit="#ff5a4a", emit_str=2.5)

    K.box("Plate", (0, 0.02, 0.025), (0.5, 0.27, 0.025), dark, 0.01)
    for x in (-0.44, 0.44):
        for y in (-0.2, 0.24):
            K.cyl(f"Bolt{x}{y}", (x, y, 0.055), 0.018, 0.012, steel, verts=12)
    PZ, PY = 0.2, 0.1
    K.cyl("Pipe", (0, PY, PZ), 0.08, 1.04, paint, rot=(0, math.radians(90), 0))
    for x in (-0.3, 0.3):
        K.cyl(f"Flange{x}", (x, PY, PZ), 0.105, 0.04, steel, rot=(0, math.radians(90), 0))
        K.box(f"Support{x}", (x * 1.27, PY, 0.09), (0.04, 0.06, 0.07), dark)
    K.box("ValveBody", (0, 0.04, 0.27), (0.11, 0.1, 0.09), paint, 0.035)
    K.cyl("Riser", (0, 0.04, 0.39), 0.045, 0.08, steel)
    K.cyl("Stem", (0, 0.04, 0.46), 0.015, 0.08, steel)
    WZ = 0.5
    K.torus("Wheel", (0, 0.04, WZ), 0.15, 0.022, wheel)
    for i in range(3):
        K.box(f"Spoke{i}", (0, 0.04, WZ), (0.15, 0.012, 0.01), wheel, rot=(0, 0, math.radians(60 * i)))
    K.cyl("Hub", (0, 0.04, WZ + 0.005), 0.035, 0.03, steel)
    K.sphere("Lamp", (0, -0.065, 0.29), (0.03, 0.018, 0.03), lamp)

    # Pressure gauge, tilted to face the camera; needle low before, high after
    K.cyl("GaugeStalk", (0.3, 0.0, 0.3), 0.015, 0.14, steel)
    gm = tilt_frame((0.3, -0.02, 0.4), 50)
    K.place(K.cyl("GaugeBody", (0, 0, 0), 0.085, 0.03, steel), gm)
    K.place(K.cyl("GaugeFace", (0, 0, 0.016), 0.072, 0.004, face), gm)
    K.place(K.box("GaugeGreen", (0.04, 0.035, 0.019), (0.02, 0.01, 0.002), K.principled("#4fd8a0", 0.5), rot=(0, 0, math.radians(-40))), gm)
    K.place(K.box("GaugeRed", (-0.045, 0.03, 0.019), (0.02, 0.01, 0.002), K.principled("#e0584f", 0.5), rot=(0, 0, math.radians(40))), gm)
    ang = math.radians(-35 if done else 125)
    needle = K.box("Needle", (0, 0, 0), (0.005, 0.03, 0.003), K.principled("#1d2730", 0.5))
    needle.location = (0, 0.028, 0.024)
    K.place(needle, gm @ Matrix.Rotation(ang, 4, "Z"))

    if done:  # airflow arrows along the pipe
        flow = K.glow("#9de8ff", 2.2)
        for i, x in enumerate((-0.42, -0.2, 0.2, 0.42)):
            for s in (1, -1):
                K.box(f"Arrow{i}{s}", (x, PY - 0.035 * s, PZ + 0.085), (0.04, 0.008, 0.006), flow,
                      rot=(0, 0, math.radians(35 * s)))


# ---------------------------------------------------------------- 최종 산소 제어기
def console(done):
    body = K.principled("#3a5a4c", 0.55, 0.25)
    dark = K.principled("#1d2e2a", 0.7)
    trim = K.principled("#a9c7b0", 0.35, 0.6)
    K.box("Desk", (0, 0.02, 0.16), (0.48, 0.24, 0.16), body, 0.012)
    K.box("Plinth", (0, 0.02, 0.02), (0.49, 0.25, 0.02), dark)
    K.box("Trim", (0, -0.225, 0.3), (0.49, 0.008, 0.012), trim)

    # Sloped control panel
    pm = tilt_frame((0, -0.08, 0.34), 22)
    K.place(K.box("Panel", (0, 0, 0), (0.46, 0.14, 0.025), K.principled("#2c443b", 0.5), 0.01), pm)
    for i, (x, c) in enumerate(((-0.34, "#e0584f"), (-0.24, "#ffcf5a"), (-0.14, "#5aa8ff"))):
        K.place(K.cyl(f"Button{i}", (x, -0.03, 0.035), 0.03, 0.02, K.principled(c, 0.35)), pm)
    for i in range(3):
        on = K.principled("#5bf0c9", 0.3, emit="#5bf0c9", emit_str=3) if done else \
            K.principled("#ffb04a" if i else "#ff6a5a", 0.3, emit="#ff7a4a", emit_str=2.2)
        K.place(K.sphere(f"Lamp{i}", (0.0 + i * 0.08, 0.06, 0.03), (0.025, 0.025, 0.018), on), pm)
    K.place(K.box("Slider", (0.03, -0.05, 0.03), (0.09, 0.012, 0.005), dark), pm)
    lever_angle = -35 if done else 30  # pushed forward when the system is on
    lm = pm @ Matrix.Translation((0.32, 0.0, 0.03)) @ Matrix.Rotation(math.radians(lever_angle), 4, "X")
    K.place(K.box("LeverSlot", (0, 0, -0.005), (0.025, 0.07, 0.006), dark), pm @ Matrix.Translation((0.32, 0.0, 0.03)))
    K.place(K.cyl("LeverRod", (0, 0, 0.06), 0.011, 0.12, trim), lm)
    K.place(K.sphere("LeverKnob", (0, 0, 0.13), 0.03, K.principled("#5bf0c9" if done else "#e0584f", 0.35)), lm)

    # Monitor
    K.box("MonitorStand", (0, 0.17, 0.4), (0.05, 0.03, 0.08), dark)
    mm = tilt_frame((0, 0.18, 0.56), -14)
    K.place(K.box("Monitor", (0, 0, 0), (0.4, 0.045, 0.19), K.principled("#24352f", 0.5), 0.015), mm)
    if done:
        screen = K.principled("#5fe89a", 0.4, emit="#5fe89a", emit_str=1.5)
        mark = K.principled("#1e5a3c", 0.5)
        K.place(K.box("Screen", (0, -0.047, 0), (0.36, 0.003, 0.16), screen), mm)
        K.place(K.box("Check1", (-0.065, -0.052, -0.025), (0.05, 0.003, 0.018), mark, rot=(0, math.radians(45), 0)), mm)
        K.place(K.box("Check2", (0.035, -0.052, 0.015), (0.1, 0.003, 0.018), mark, rot=(0, math.radians(-49), 0)), mm)
    else:
        screen = K.principled("#21424a", 0.4, emit="#21424a", emit_str=0.6)
        mark = K.principled("#6fe0e6", 0.4, emit="#6fe0e6", emit_str=1.6)
        K.place(K.box("Screen", (0, -0.047, 0), (0.36, 0.003, 0.16), screen), mm)
        K.place(K.box("Diamond", (0, -0.052, 0), (0.06, 0.003, 0.06), mark, rot=(0, math.radians(45), 0)), mm)
        for i in range(3):
            K.place(K.box(f"Line{i}", (-0.2, -0.052, 0.09 - i * 0.05), (0.08 - i * 0.015, 0.003, 0.008), mark), mm)


# ---------------------------------------------------------------- 탐사 안내 로봇
def helper(done):
    white = K.principled("#eef5f3", 0.35)
    teal = K.principled("#3fbfc0", 0.4, 0.3)
    navy = K.principled("#173247", 0.2)
    eye = K.principled("#9dffc8" if done else "#7ff6ff", 0.3, emit="#9dffc8" if done else "#7ff6ff", emit_str=3)
    tip = K.principled("#5be0c9" if done else "#ffd18b", 0.3, emit="#5be0c9" if done else "#ffc060", emit_str=3.5)

    K.cyl("Pad", (0, 0, 0.02), 0.19, 0.04, K.principled("#2a3d4a", 0.6, 0.3), 0.01)
    K.torus("PadRing", (0, 0, 0.045), 0.15, 0.012, K.glow("#7ff6ff", 2))
    K.sphere("Thruster", (0, 0, 0.12), (0.06, 0.06, 0.03), K.glow("#7ff6ff", 2.5))
    K.sphere("Body", (0, 0, 0.27), (0.16, 0.14, 0.15), white)
    K.sphere("Belly", (0, -0.11, 0.26), (0.085, 0.04, 0.065), teal)
    for s in (-1, 1):
        K.sphere(f"Arm{s}", (0.18 * s, -0.02, 0.27), (0.045, 0.045, 0.07), teal)
        K.cyl(f"Ear{s}", (0.19 * s, 0, 0.49), 0.05, 0.04, teal, rot=(0, math.radians(90), 0))
    K.sphere("Head", (0, 0, 0.49), (0.19, 0.17, 0.15), white)
    K.sphere("Visor", (0, -0.07, 0.49), (0.15, 0.11, 0.1), navy)
    for s in (-1, 1):
        if done:  # happy, squinting eyes
            K.sphere(f"Eye{s}", (0.055 * s, -0.172, 0.5), (0.032, 0.012, 0.014), eye, segs=12)
        else:
            K.sphere(f"Eye{s}", (0.055 * s, -0.172, 0.5), (0.026, 0.012, 0.036), eye, segs=12)
    K.cyl("Antenna", (0, 0, 0.67), 0.008, 0.08, K.principled("#9fb3c0", 0.3, 0.8))
    K.sphere("AntennaTip", (0, 0, 0.72), 0.03, tip, segs=16)
    K.scale_all(1.35)


# ---------------------------------------------------------------- 연구 자료 보관함
def archive(done):
    body = K.principled("#6c6c9e", 0.5, 0.35)
    face = K.principled("#8a8ac0", 0.45, 0.3)
    dark = K.principled("#2b2b45", 0.7)
    label = K.principled("#eef0ff", 0.5)
    brass = K.principled("#d0b070", 0.35, 0.8)
    paper = K.principled("#f6f3ea", 0.6)

    K.box("Cabinet", (0, 0.04, 0.3), (0.42, 0.22, 0.3), body, 0.012)
    K.box("TopCap", (0, 0.04, 0.615), (0.44, 0.24, 0.015), dark, 0.006)
    K.box("Plinth", (0, 0.04, 0.02), (0.43, 0.23, 0.02), dark)
    FRONT = 0.04 - 0.22
    for col, x in enumerate((-0.2, 0.2)):
        for row, z in enumerate((0.13, 0.31, 0.49)):
            pulled = done and col == 1 and row == 2
            dy = -0.16 if pulled else 0.0
            K.box(f"Drawer{col}{row}", (x, FRONT - 0.012 + dy, z), (0.18, 0.012, 0.078), face, 0.006)
            K.box(f"Label{col}{row}", (x, FRONT - 0.026 + dy, z + 0.035), (0.07, 0.003, 0.018), label)
            K.box(f"Handle{col}{row}", (x, FRONT - 0.03 + dy, z - 0.025), (0.06, 0.008, 0.01), brass)
            if pulled:
                K.box("Tray", (x, FRONT + 0.06 + dy, z - 0.01), (0.17, 0.08, 0.06), dark)
                for i in range(4):
                    K.box(f"Paper{i}", (x - 0.1 + i * 0.065, FRONT + 0.05 + dy, z + 0.07),
                          (0.004, 0.06, 0.05 + 0.01 * (i % 2)), paper, rot=(0, math.radians(-8 + i * 5), 0))
                K.box("GlowFile", (x + 0.02, FRONT + 0.02 + dy, z + 0.1), (0.07, 0.004, 0.05),
                      K.principled("#c0c1ff", 0.4, emit="#c0c1ff", emit_str=2.2), rot=(math.radians(-15), 0, 0))
    # Books and a rolled chart on top
    top = 0.63
    for i, (w, h, c) in enumerate(((0.035, 0.15, "#e0584f"), (0.03, 0.13, "#ffcf5a"), (0.04, 0.16, "#5aa8ff"),
                                    (0.03, 0.12, "#5be0c9"), (0.035, 0.14, "#c0c1ff"))):
        K.box(f"Book{i}", (-0.33 + i * 0.075, 0.08, top + h / 2), (w, 0.09, h / 2), K.principled(c, 0.6), 0.004)
    K.box("LeanBook", (0.07, 0.08, top + 0.06), (0.03, 0.09, 0.07), K.principled("#f29a6b", 0.6), 0.004,
          rot=(0, math.radians(30), 0))
    K.cyl("Scroll", (0.27, 0.02, top + 0.035), 0.035, 0.24, paper, rot=(0, math.radians(90), math.radians(15)))


BUILDERS = {"generator": generator, "valve": valve, "console": console, "helper": helper, "archive": archive}

if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:]
    out_dir = argv[0]
    names = argv[1:] or list(BUILDERS)
    os.makedirs(os.path.join(out_dir, "source"), exist_ok=True)
    for name in names:
        f = FILES[name]
        K.build_sheet(BUILDERS[name], os.path.join(out_dir, f + ".png"), os.path.join(out_dir, "source", f + ".blend"))
