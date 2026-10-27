"""Stage 5 (연소 생성물 분석실) station sprites — spectral glass lab look.

Usage:
  blender -b --factory-startup --python stage5_props.py -- <props_dir> [water gas archive prism report log restore]
Writes <props_dir>/<file>.png (two 192px cells: before | done or inspected) and <props_dir>/source/<file>.blend.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Matrix, Vector
import prop_kit as K

WORLD = "#bcc6e6"  # cool lavender fill to match the spectral lab
FILES = {
    "water": "s5-cobalt-paper",
    "gas": "s5-limewater",
    "archive": "s5-safety-record",
    "prism": "s5-prism-scope",
    "report": "s5-analysis-report",
    "log": "s5-incident-log",
    "restore": "s5-restore-core",
}

CHROME, SLATE, DARK, LAB = "#aebccb", "#3d5f80", "#1f2c3d", "#9fb0c4"


def tilt_frame(center, angle_deg):
    return Matrix.Translation(Vector(center)) @ Matrix.Rotation(math.radians(angle_deg), 4, "X")


def chrome():
    return K.principled(CHROME, 0.3, 0.85)


def lamp_mat(on, off_color="#ff6a5a", on_color="#7cf0c8"):
    c = on_color if on else off_color
    return K.principled(c, 0.3, emit=c, emit_str=3 if on else 2.4)


def bench(top=LAB, body=SLATE, top_z=0.3, half=(0.48, 0.25)):
    K.box("BenchBody", (0, 0, top_z / 2 - 0.01), (half[0] - 0.03, half[1] - 0.03, top_z / 2 - 0.01), K.principled(body, 0.5, 0.3), 0.012)
    K.box("BenchTop", (0, 0, top_z), (half[0], half[1], 0.025), K.principled(top, 0.45), 0.012)
    K.box("BenchTrim", (0, -half[1] - 0.003, top_z - 0.005), (half[0], 0.006, 0.02), chrome())
    K.box("BenchPlinth", (0, 0, 0.02), (half[0] - 0.02, half[1] - 0.02, 0.02), K.principled(DARK, 0.7))
    return top_z + 0.025


def candle(x, y, base, lit, name="C"):
    K.cyl(f"Dish{name}", (x, y, base + 0.008), 0.07, 0.016, chrome())
    K.cyl(f"Candle{name}", (x, y, base + 0.016 + 0.065), 0.042, 0.13, K.principled("#fbf3e2", 0.45), 0.008, verts=24)
    top = base + 0.016 + 0.13
    K.cyl(f"Wick{name}", (x, y, top + 0.012), 0.006, 0.024, K.principled("#1d1712", 0.9), verts=8)
    if lit:
        K.flame(f"Flame{name}", (x, y, top + 0.02), 1.15)
    return top


# ---------------------------------------------------------------- 염화 코발트 종이 실험대
def water(after):
    base = bench()
    G = K.glass()
    cx = -0.13
    candle(cx, 0.0, base, lit=not after)
    K.open_jar("Jar", (cx, 0.0, base), 0.17, 0.38, G)
    if after:  # water droplets condensed on the inside of the jar
        drop = K.principled("#d6f0ff", 0.05, emit="#bfe6ff", emit_str=0.5)
        for i in range(14):
            a = math.radians(-160 + i * 10 + (i % 3) * 4)
            z = base + 0.14 + (i * 37 % 19) / 19 * 0.2
            K.sphere(f"Drop{i}", (cx + 0.15 * math.cos(a), 0.15 * math.sin(a), z), (0.011, 0.011, 0.014), drop, segs=10)
    # Cobalt chloride paper held with tweezers against the jar: blue -> pink when it meets water
    paper = K.principled("#ec6f9b" if after else "#3d7fd8", 0.6)
    K.box("Paper", (0.1, -0.09, base + 0.2), (0.032, 0.005, 0.09), paper, rot=(0, math.radians(-25), 0))
    tw = chrome()
    K.rod("TweezerA", (0.34, -0.1, base + 0.36), (0.13, -0.095, base + 0.27), 0.009, tw)
    K.rod("TweezerB", (0.34, -0.1, base + 0.36), (0.14, -0.085, base + 0.25), 0.009, tw)
    # Petri dish with spare blue strips
    dish = K.cyl("Petri", (0.32, 0.1, base + 0.012), 0.1, 0.024, G)
    K.remove_cap(dish, top=True)
    for i in range(3):
        K.box(f"Spare{i}", (0.29 + i * 0.03, 0.1, base + 0.006), (0.01, 0.05, 0.002), K.principled("#3d7fd8", 0.6),
              rot=(0, 0, math.radians(-15 + i * 12)))


# ---------------------------------------------------------------- 석회수 반응 실험대
def gas(after):
    base = bench(top="#a99fc6", body="#5a4a78")
    G = K.glass()
    candle(-0.3, 0.02, base, lit=not after)
    if after:  # smoke wisps from the extinguished candle
        smoke = K.principled("#cfd3dc", 0.8, emit="#cfd3dc", emit_str=0.15)
        for i, (dx, dz, r) in enumerate(((0.0, 0.22, 0.02), (0.02, 0.27, 0.025), (-0.01, 0.33, 0.03))):
            K.sphere(f"Smoke{i}", (-0.3 + dx, 0.02, base + dz), r, smoke, segs=12)
    # Gas jar with limewater: clear before, milky after carbon dioxide
    jx = 0.04
    jar = K.cyl("GasJar", (jx, 0.0, base + 0.17), 0.14, 0.34, G)
    K.remove_cap(jar, top=True)
    K.cyl("GlassLid", (jx, 0.0, base + 0.345), 0.155, 0.012, G)
    lime = K.principled("#f4f3ee", 0.6, emit="#ffffff", emit_str=0.35) if after else \
        K.principled("#5f9fc8", 0.05)
    K.cyl("Limewater", (jx, 0.0, base + 0.05), 0.13, 0.09, lime)
    if after:
        for i in range(5):
            a = i * 1.3
            K.sphere(f"Cloud{i}", (jx + 0.07 * math.cos(a), -0.02 + 0.05 * math.sin(a), base + 0.11), 0.03,
                     K.principled("#ffffff", 0.7, emit="#ffffff", emit_str=0.3), segs=12)
    # Reagent bottle
    K.cyl("Bottle", (0.32, 0.06, base + 0.1), 0.065, 0.2, G, 0.02)
    K.cyl("BottleLiquid", (0.32, 0.06, base + 0.07), 0.056, 0.13, K.principled("#cfeeff", 0.08, emit="#bfe6ff", emit_str=0.2))
    K.cyl("BottleCap", (0.32, 0.06, base + 0.225), 0.035, 0.04, K.principled("#5a4a78", 0.5))
    K.box("BottleLabel", (0.32, -0.006, base + 0.1), (0.045, 0.003, 0.035), K.principled("#ffffff", 0.6))


# ---------------------------------------------------------------- 실험 안전 기록
def archive(inspected):
    K.cyl("Base", (0, 0.02, 0.03), 0.26, 0.06, K.principled(SLATE, 0.5, 0.4), 0.012, verts=40)
    K.torus("BaseRing", (0, 0.02, 0.06), 0.26, 0.01, chrome())
    K.rod("Post", (0, 0.06, 0.06), (0, 0.06, 0.38), 0.025, chrome())
    tm = tilt_frame((0, 0.03, 0.47), 62)
    K.place(K.box("Tablet", (0, 0, 0), (0.25, 0.18, 0.018), K.principled(DARK, 0.4, 0.3), 0.012), tm)
    if inspected:
        scr, ink = K.principled("#5fe0c8", 0.3, emit="#5fe0c8", emit_str=1.4), K.principled("#12463c", 0.5)
    else:
        scr, ink = K.principled("#2a4566", 0.3, emit="#2a4566", emit_str=0.8), K.principled("#ffc060", 0.4, emit="#ffb040", emit_str=2.0)
    K.place(K.box("Screen", (0, 0, 0.02), (0.22, 0.155, 0.003), scr), tm)
    K.place(K.cyl("Warn", (-0.1, 0.02, 0.026), 0.07, 0.004, ink, verts=3), tm)
    for i in range(3):
        K.place(K.box(f"Row{i}", (0.07, 0.07 - i * 0.05, 0.026), (0.09 - i * 0.015, 0.009, 0.002), ink), tm)
    # Safety goggles on the base
    gm = K.principled("#9ad4ff", 0.1, emit="#9ad4ff", emit_str=0.3)
    for s in (-1, 1):
        K.torus(f"Lens{s}", (0.06 * s, -0.16, 0.085), 0.045, 0.012, gm, rot=(math.radians(70), 0, 0))
    K.box("Strap", (0, -0.13, 0.08), (0.14, 0.008, 0.012), K.principled("#5a4a78", 0.6))


# ---------------------------------------------------------------- 색 변화 관찰경
def prism(inspected):
    K.cyl("Base", (0, 0.02, 0.03), 0.24, 0.06, K.principled(SLATE, 0.5, 0.4), 0.012, verts=40)
    K.rod("Column", (0, 0.04, 0.06), (0, 0.04, 0.3), 0.03, chrome())
    K.box("Mount", (0, 0.03, 0.32), (0.3, 0.07, 0.02), chrome(), 0.008)
    # Lens tube on the left aiming at the prism
    K.cyl("Tube", (-0.17, 0.03, 0.39), 0.045, 0.22, K.principled("#3a3a5a", 0.4, 0.4), rot=(0, math.radians(90), 0))
    K.cyl("Lens", (-0.055, 0.03, 0.39), 0.04, 0.01, K.principled("#bfe6ff", 0.05, emit="#bfe6ff", emit_str=1.5 if inspected else 0.2),
          rot=(0, math.radians(90), 0))
    K.rod("TubeLeg", (-0.17, 0.03, 0.34), (-0.17, 0.03, 0.36), 0.02, chrome())
    # Triangular glass prism, standing upright on the mount
    K.cyl("Prism", (0.07, 0.03, 0.41), 0.09, 0.16, K.glass("#d9ccff"), verts=3, rot=(0, 0, math.radians(90)))
    inner = K.principled("#b7a4ff", 0.2, emit="#c8b6ff", emit_str=1.4 if inspected else 0.25)
    K.cyl("PrismCore", (0.07, 0.03, 0.41), 0.05, 0.12, inner, verts=3, rot=(0, 0, math.radians(90)))
    if inspected:  # white light in, spectrum out
        K.rod("Beam", (-0.05, 0.03, 0.39), (0.03, 0.03, 0.4), 0.008, K.glow("#ffffff", 3))
        for i, c in enumerate(("#ff4a4a", "#ff9a3a", "#ffe04a", "#5ae07a", "#4aa8ff", "#9a6aff")):
            a = math.radians(-22 + i * 9)
            K.rod(f"Ray{i}", (0.12, 0.03, 0.41), (0.12 + 0.34 * math.cos(a), 0.03 - 0.04 * i / 5, 0.41 + 0.34 * math.sin(a)), 0.014, K.glow(c, 2.2))
        K.point_light((0.1, -0.1, 0.45), 1.5, (0.85, 0.8, 1.0), 0.05)


# ---------------------------------------------------------------- 연소 생성물 분석 보고서
def report(done):
    K.box("Desk", (0, 0.03, 0.17), (0.46, 0.22, 0.17), K.principled("#2f4f66", 0.5, 0.3), 0.012)
    K.box("DeskTop", (0, 0.03, 0.35), (0.48, 0.24, 0.018), K.principled(LAB, 0.45), 0.01)
    K.box("Plinth", (0, 0.03, 0.02), (0.47, 0.23, 0.02), K.principled(DARK, 0.7))
    top = 0.368
    G = K.glass()
    strength = 2.2 if done else 0.25
    # Left pod: water (H2O) drop. Right pod: carbon dioxide (CO2) cloud.
    for s, name in ((-1, "Water"), (1, "CO2")):
        x = 0.33 * s
        K.cyl(f"PodBase{name}", (x, -0.02, top + 0.03), 0.09, 0.06, chrome())
        dome = K.sphere(f"Dome{name}", (x, -0.02, top + 0.06), 0.085, G)
        if name == "Water":
            K.sphere("Drop", (x, -0.02, top + 0.11), (0.035, 0.035, 0.05), K.principled("#4aa8ff", 0.2, emit="#4aa8ff", emit_str=strength))
            K.cyl("DropTip", (x, -0.02, top + 0.165), 0.02, 0.05, K.principled("#4aa8ff", 0.2, emit="#4aa8ff", emit_str=strength), r2=0.0)
        else:
            for i, (dx, dz, r) in enumerate(((-0.025, 0.1, 0.03), (0.025, 0.1, 0.03), (0.0, 0.13, 0.034))):
                K.sphere(f"Cloud{i}", (x + dx, -0.02, top + dz), r, K.principled("#dfe4ee", 0.5, emit="#ffffff", emit_str=strength * 0.6), segs=12)
        cable = K.principled("#5fe0c8", 0.3, emit="#5fe0c8", emit_str=2.5) if done else K.principled("#40506a", 0.6)
        K.tube(f"Cable{name}", [(x, 0.03, top + 0.03), (x * 0.7, 0.12, top + 0.02), (0.12 * s, 0.14, top + 0.08)], 0.012, cable)
    # Centre monitor with the report
    K.box("Stand", (0, 0.15, top + 0.06), (0.04, 0.03, 0.06), K.principled(DARK, 0.6))
    mm = tilt_frame((0, 0.15, top + 0.22), -12)
    K.place(K.box("Monitor", (0, 0, 0), (0.2, 0.04, 0.15), K.principled("#24323f", 0.5), 0.012), mm)
    scr = K.principled("#8ef0e0", 0.3, emit="#8ef0e0", emit_str=1.3) if done else K.principled("#22384a", 0.3, emit="#22384a", emit_str=0.6)
    K.place(K.box("Screen", (0, -0.042, 0), (0.175, 0.003, 0.125), scr), mm)
    K.place(K.box("Doc", (-0.05, -0.046, 0), (0.07, 0.003, 0.095), K.principled("#ffffff" if done else "#55708a", 0.5)), mm)
    for i in range(4):
        K.place(K.box(f"DocLine{i}", (-0.05, -0.049, 0.055 - i * 0.035), (0.05, 0.002, 0.007), K.principled("#2a5a6a", 0.5)), mm)
    if done:
        mark = K.principled("#1e5a3c", 0.5)
        K.place(K.box("Check1", (0.07, -0.049, -0.015), (0.025, 0.002, 0.01), mark, rot=(0, math.radians(45), 0)), mm)
        K.place(K.box("Check2", (0.115, -0.049, 0.01), (0.05, 0.002, 0.01), mark, rot=(0, math.radians(-50), 0)), mm)


# ---------------------------------------------------------------- 연구소 사고 기록
def log(inspected):
    body = K.principled("#3b3555", 0.5, 0.4)
    K.box("Cabinet", (0, 0.04, 0.27), (0.38, 0.2, 0.27), body, 0.015)
    K.box("Plinth", (0, 0.04, 0.02), (0.39, 0.21, 0.02), K.principled(DARK, 0.7))
    K.box("Top", (0, 0.04, 0.55), (0.39, 0.21, 0.015), K.principled("#5a5478", 0.4, 0.5), 0.006)
    # Reel-to-reel recorder on the front
    fm = tilt_frame((0, -0.165, 0.33), 90)
    K.place(K.box("Deck", (0, 0, 0), (0.33, 0.17, 0.008), K.principled("#24203a", 0.5)), fm)
    reel = K.principled("#d6c3ff", 0.35, 0.3, emit="#b7a4ff", emit_str=1.8 if inspected else 0.0)
    for s in (-1, 1):
        K.place(K.cyl(f"Reel{s}", (0.16 * s, 0.03, 0.02), 0.1, 0.018, reel), fm)
        K.place(K.cyl(f"Tape{s}", (0.16 * s, 0.03, 0.03), 0.065, 0.006, K.principled("#3a2a22", 0.6)), fm)
        K.place(K.cyl(f"Hub{s}", (0.16 * s, 0.03, 0.036), 0.022, 0.01, chrome()), fm)
    K.place(K.box("TapeLink", (0, -0.035, 0.032), (0.16, 0.004, 0.003), K.principled("#3a2a22", 0.6)), fm)
    K.place(K.box("Head", (0, -0.06, 0.03), (0.04, 0.02, 0.012), chrome()), fm)
    # Small status screen on top
    sm = tilt_frame((0.0, 0.08, 0.64), -15)
    K.place(K.box("ScreenBox", (0, 0, 0), (0.2, 0.035, 0.08), K.principled("#24203a", 0.5), 0.01), sm)
    scr = K.principled("#d6c3ff", 0.3, emit="#c8b6ff", emit_str=1.5) if inspected else K.principled("#2a2440", 0.4)
    K.place(K.box("Screen", (0, -0.037, 0), (0.18, 0.003, 0.065), scr), sm)
    if inspected:
        for i in range(7):
            h = (0.012, 0.035, 0.02, 0.05, 0.015, 0.04, 0.02)[i]
            K.place(K.box(f"Wave{i}", (-0.12 + i * 0.04, -0.041, 0), (0.008, 0.002, h), K.principled("#3a2a6a", 0.5)), sm)
    K.sphere("RecLamp", (0.3, -0.16, 0.5), (0.025, 0.015, 0.025), lamp_mat(inspected, "#ff4a4a", "#c8b6ff"))


# ---------------------------------------------------------------- 중앙 연구소 복구 패널
def restore(done):
    K.cyl("Platform", (0, 0.02, 0.04), 0.44, 0.08, K.principled("#2b3a52", 0.5, 0.4), 0.012, verts=6)
    K.cyl("Tier", (0, 0.02, 0.11), 0.3, 0.06, K.principled(SLATE, 0.45, 0.5), 0.01, verts=6)
    K.torus("TierRing", (0, 0.02, 0.14), 0.3, 0.012, chrome())
    G = K.glass("#dffcf4")
    K.cyl("Capsule", (0, 0.02, 0.36), 0.15, 0.42, G)
    K.torus("RingBottom", (0, 0.02, 0.16), 0.155, 0.02, chrome())
    K.torus("RingTop", (0, 0.02, 0.57), 0.155, 0.02, chrome())
    K.cyl("Cap", (0, 0.02, 0.6), 0.12, 0.05, chrome())
    K.cyl("Spire", (0, 0.02, 0.66), 0.02, 0.08, chrome())
    core = K.principled("#7fffd9", 0.2, emit="#7fffd9", emit_str=3.5) if done else K.principled("#7a5aa0", 0.3, emit="#7a5aa0", emit_str=0.5)
    K.sphere("Core", (0, 0.02, 0.36), (0.075, 0.075, 0.13), core, segs=6)
    if done:
        halo = K.glow("#b0fae1", 2.2)
        K.torus("Halo1", (0, 0.02, 0.3), 0.11, 0.008, halo)
        K.torus("Halo2", (0, 0.02, 0.42), 0.11, 0.008, halo, rot=(math.radians(18), 0, 0))
        K.point_light((0, -0.15, 0.4), 3.0, (0.6, 1.0, 0.9), 0.05)
    for s in (-1, 1):
        K.box(f"SideConsole{s}", (0.34 * s, -0.12, 0.17), (0.07, 0.06, 0.06), K.principled("#2f4f66", 0.5, 0.3), 0.01)
        K.sphere(f"SideLamp{s}", (0.34 * s, -0.18, 0.2), (0.022, 0.012, 0.022), lamp_mat(done))


BUILDERS = {"water": water, "gas": gas, "archive": archive, "prism": prism,
            "report": report, "log": log, "restore": restore}

if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:]
    out_dir = argv[0]
    names = argv[1:] or list(BUILDERS)
    os.makedirs(os.path.join(out_dir, "source"), exist_ok=True)
    for name in names:
        f = FILES[name]
        K.build_sheet(BUILDERS[name], os.path.join(out_dir, f + ".png"),
                      os.path.join(out_dir, "source", f + ".blend"), world=WORLD)
