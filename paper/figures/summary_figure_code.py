import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, Rectangle, Circle
import numpy as np
from pathlib import Path

output_dir = Path(__file__).resolve().parent
out_pdf = output_dir / "summary_figure.pdf"

plt.rcParams.update({
    # Fontconfig maps this metrically compatible Times face on the build host.
    "font.family": "Nimbus Roman",
    "font.size": 7.5,
    "mathtext.fontset": "stix",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "axes.unicode_minus": False,
})

fig = plt.figure(figsize=(8.0, 4.5), facecolor="white")
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

blue = "#315b8a"
orange = "#d06b1f"
red = "#bd3f3a"
green = "#3f7f52"
purple = "#6d4a8e"
gray = "#5b5b5b"
dark = "#222222"
lightgray = "#d8d8d8"
red_light = "#f8ecea"
green_light = "#edf5ef"
purple_light = "#f2edf6"

xA0, xA1 = 0.018, 0.323
xB0, xB1 = 0.335, 0.675
xC0, xC1 = 0.687, 0.982

for x in [0.329, 0.681]:
    ax.plot([x, x], [0.045, 0.970], color="#c5c5c5", lw=0.65, ls=(0, (2, 3)))

def box(x, y, w, h, text="", edge=dark, face="white", fs=6.7, lw=0.8, color=dark, weight="normal"):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.004,rounding_size=0.010",
                       ec=edge, fc=face, lw=lw)
    ax.add_patch(p)
    if text:
        ax.text(x+w/2, y+h/2, text, ha="center", va="center", fontsize=fs, color=color, weight=weight)
    return p

def arr(a, b, color=dark, lw=0.9, ms=7, rad=0):
    p = FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=ms, lw=lw, color=color,
                        connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0)
    ax.add_patch(p)
    return p

def hydro_icon(cx, cy, w, h, vertices):
    """Draw one of the n=5 hydrotope cross-sections used in Fig. 5."""
    dx, dy = 0.16 * w, 0.14 * h
    x0, y0 = cx - w / 2, cy - h / 2
    ax.add_patch(Rectangle((x0 + dx, y0 + dy), w, h, fill=False,
                           ec="#b8c0c6", lw=0.45))
    ax.add_patch(Rectangle((x0, y0), w, h, fill=False,
                           ec="#b8c0c6", lw=0.45))
    for px, py in [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)]:
        ax.plot([px, px + dx], [py, py + dy], color="#b8c0c6", lw=0.45)
    points = [(x0 + vx * w, y0 + vy * h) for vx, vy in vertices]
    ax.add_patch(Polygon(points, closed=True, ec=blue, fc="#c7ddf4",
                         alpha=0.82, lw=0.85))

# ---------------- A ----------------
ax.text((xA0+xA1)/2, 0.965, "(a)  Scientific problem", fontsize=10.2,
        weight="bold", ha="center", va="top")

# Follow the discovery sequence used in Fig. 5: a formula is tested in another
# chamber, fails there, and is recognized as one member of a chamber family.
box(xA0+0.064, 0.805, 0.177, 0.080,
    "BG recursion: exact values\nat chosen frequencies", edge=dark, fs=7.1)
arr(((xA0+xA1)/2, 0.802), ((xA0+xA1)/2, 0.752), lw=0.95, ms=6)
box(xA0+0.064, 0.665, 0.177, 0.080,
    "A simple formula works\nin one frequency chamber", edge=blue,
    face="#f4f8fb", fs=7.1, color=blue, weight="bold")
ax.text(xA0+0.245, 0.635, "test another chamber", fontsize=5.7,
        color=gray, ha="right", va="center")
arr(((xA0+xA1)/2, 0.662), ((xA0+xA1)/2, 0.612), color=red,
    lw=0.95, ms=6)
box(xA0+0.064, 0.525, 0.177, 0.080,
    "A counterexample shows\nthat other chambers differ", edge=red,
    face=red_light, fs=7.1, color=red, weight="bold")

ax.text((xA0+xA1)/2, 0.472,
        "Changing the frequencies changes the chamber",
        ha="center", fontsize=6.7, color=dark)
icon_y = 0.390
icon_xs = np.linspace(xA0+0.050, xA1-0.050, 4)
icon_shapes = [
    [(0.08, 0.08), (0.90, 0.08), (0.36, 0.82)],
    [(0.05, 0.08), (0.92, 0.08), (0.72, 0.78), (0.25, 0.88)],
    [(0.05, 0.30), (0.30, 0.92), (0.72, 0.78), (0.94, 0.28), (0.55, 0.04)],
    [(0.10, 0.08), (0.18, 0.80), (0.72, 0.92), (0.92, 0.20)],
]
for icon_x, vertices in zip(icon_xs, icon_shapes):
    hydro_icon(icon_x, icon_y, 0.048, 0.070, vertices)
ax.text((xA0+xA1)/2, 0.316,
        "Different chambers have different formulas",
        ha="center", fontsize=6.7, color=blue, weight="bold")

box(xA0+0.020, 0.135, 0.265, 0.105,
    "Task: find one exact formula\nvalid in every chamber and for every $n$.",
    edge=green, face=green_light, fs=7.1, color=green, weight="bold")

# ---------------- B ----------------
ax.text((xB0+xB1)/2, 0.965, "(b)  Where most runs stop", fontsize=10.2,
        weight="bold", ha="center", va="top")

ax.text((xB0+xB1)/2, 0.865,
        "Finding a formula for at least one chamber is common.",
        ha="center", fontsize=7.8, color=dark)
box(xB0+0.060, 0.715, 0.220, 0.105,
    "15 / 18 runs\nfind a correct chamber formula",
    edge=blue, face="#f4f8fb", fs=7.7, color=blue, weight="bold")
arr(((xB0+xB1)/2, 0.710), ((xB0+xB1)/2, 0.660),
    color=red, lw=1.0, ms=7)

box(xB0+0.025, 0.395, 0.290, 0.255,
    edge=red, face=red_light, lw=1.1)
ax.text((xB0+xB1)/2, 0.615, "TWO STEPS REMAIN",
        ha="center", va="center", fontsize=7.7, color=red, weight="bold")
box(xB0+0.043, 0.465, 0.118, 0.105,
    "1. Combine\nall chamber formulas\ninto one expression",
    edge=red, face="white", fs=6.7, color=dark)
ax.text((xB0+xB1)/2, 0.518, "+", ha="center", va="center",
        fontsize=10.5, color=red, weight="bold")
box(xB0+0.179, 0.465, 0.118, 0.105,
    "2. Test\nin new chambers\nnot used before",
    edge=red, face="white", fs=6.7, color=dark)
ax.text((xB0+xB1)/2, 0.427,
        "11 of these 15 runs stop before completing both steps",
        ha="center", fontsize=6.7, color=red, weight="bold")

arr(((xB0+xB1)/2, 0.390), ((xB0+xB1)/2, 0.340),
    color=green, lw=1.0, ms=7)
box(xB0+0.060, 0.195, 0.220, 0.140,
    "Only 4 / 18 runs\nfind one formula for\nevery chamber and\ncheck it in new chambers",
    edge=green, face=green_light, fs=7.0, color=green, weight="bold")

# ---------------- C ----------------
ax.text((xC0+xC1)/2, 0.965, "(c)  PI + students: process and results",
        fontsize=9.8, weight="bold", ha="center", va="top")

# Student cards include compact visual cues for exploration and synthesis.
box(xC0+0.010,0.735,0.103,0.155,edge=blue,fs=6.2)
ax.text(xC0+0.0615,0.862,"Student 1",ha="center",fontsize=7.4,weight="bold")
ax.text(xC0+0.0615,0.833,"test many chambers",ha="center",fontsize=6.2)
sx, sy = xC0+0.030, 0.755
ax.plot([sx,sx],[sy,sy+0.060],color=dark,lw=0.7)
ax.plot([sx,sx+0.063],[sy,sy],color=dark,lw=0.7)
# Rays extend past the sampled points to suggest continued chamber searches.
for dx,dy in [(0.023,0.066),(0.051,0.053),(0.047,0.028),(0.062,0.017)]:
    ax.plot([sx,sx+dx],[sy,sy+dy],color=gray,lw=0.6,ls=(0,(3,2)))
for dx,dy,col in [
    (0.018,0.052,"#d34bb4"),
    (0.036,0.037,"#3b9bd5"),
    (0.030,0.018,"#55a85d"),
    (0.052,0.014,"#e98924"),
]:
    ax.add_patch(Circle((sx+dx,sy+dy),0.0035,ec=dark,fc=col,lw=0.4,zorder=3))

box(xC0+0.182,0.735,0.103,0.155,edge=blue,fs=6.2)
ax.text(xC0+0.2335,0.862,"Student 2",ha="center",fontsize=7.4,weight="bold")
ax.text(xC0+0.2335,0.833,"derive the formula",ha="center",fontsize=6.2)
tx = np.linspace(xC0+0.198,xC0+0.268,80)
ty = 0.790 + 0.008*np.sin(np.linspace(0,4*np.pi,80))*(0.75+0.25*np.cos(np.linspace(0,2*np.pi,80)))
ax.plot(tx,ty,color="#6b42c7",lw=0.8)
ax.text(xC0+0.2335,0.755,r"$\sum_S(-1)^{|S|}[\,\cdot\,]_+^{n-3}$",ha="center",fontsize=6.8)

box(xC0+0.065,0.585,0.165,0.095,edge=purple,face="white",fs=6.2)
ax.text(xC0+0.1475,0.645,"shared research\nrecord",ha="center",va="center",
        fontsize=7.3,color=purple,weight="bold")
ax.text(xC0+0.1475,0.600,"formulas  •  tests  •  failures",ha="center",fontsize=6.3,color=purple)

# Symmetric, edge-aware connectors: tails and arrowheads remain clear of the
# rounded borders instead of visually merging with them.
arr((xC0+0.075,0.731),(xC0+0.105,0.684),lw=1.0,ms=7)
arr((xC0+0.220,0.731),(xC0+0.190,0.684),lw=1.0,ms=7)

box(xC0+0.090,0.455,0.115,0.072,edge=green,face="white")
ax.text(xC0+0.1475,0.505,"PI",ha="center",va="center",fontsize=7.8,weight="bold")
ax.text(xC0+0.1475,0.478,"checks the formula\nin new chambers",ha="center",va="center",
        fontsize=6.5,linespacing=1.08)
arr((xC0+0.1475,0.581),(xC0+0.1475,0.531),lw=1.0,ms=7)

# Red feedback loop: failed counterexamples return to both students.
ax.plot([xC0+0.084,xC0+0.030,xC0+0.030],[0.490,0.490,0.720],color=red,lw=0.9)
arr((xC0+0.030,0.720),(xC0+0.030,0.733),color=red,lw=0.9,ms=6)
ax.plot([xC0+0.211,xC0+0.267,xC0+0.267],[0.490,0.490,0.720],color=red,lw=0.9)
arr((xC0+0.267,0.720),(xC0+0.267,0.733),color=red,lw=0.9,ms=6)
ax.text(xC0+0.055,0.545,"failed\ntest",fontsize=5.4,color=red,
        ha="center",va="center",linespacing=1.05)

arr((xC0+0.1475,0.455),(xC0+0.1475,0.390),color=green,ms=6)
ax.text(xC0+0.157,0.414,"pass (complete formula)",fontsize=5.8,color=dark,va="center")
ax.plot([xC0+0.055,xC0+0.240],[0.382,0.382],color=green,lw=0.9)
arr((xC0+0.055,0.382),(xC0+0.055,0.355),color=green,ms=6)
arr((xC0+0.240,0.382),(xC0+0.240,0.355),color=green,ms=6)

box(xC0+0.001,0.135,0.138,0.210,edge=green,face="white")
ax.text(xC0+0.070,0.313,"Hydrotope rediscovery",ha="center",fontsize=6.8,color=green,weight="bold")
ax.text(xC0+0.070,0.288,"for every $n$",ha="center",fontsize=6.6,color=green,weight="bold")
ax.text(xC0+0.070,0.252,"no-hint single agents",ha="center",fontsize=6.4)
ax.text(xC0+0.070,0.225,"0 / 6",ha="center",fontsize=8.2)
ax.plot([xC0+0.010,xC0+0.129],[0.215,0.215],color=green,lw=0.55,ls=(0,(2,2)))
ax.text(xC0+0.070,0.180,"PI + two students",ha="center",fontsize=6.2)
ax.text(xC0+0.070,0.148,"2 / 2",ha="center",fontsize=8.2,color=green)

box(xC0+0.148,0.135,0.138,0.210,edge=green,face="white")
ax.text(xC0+0.217,0.313,"New three-minus",ha="center",fontsize=6.8,color=green,weight="bold")
ax.text(xC0+0.217,0.288,"result",ha="center",fontsize=6.8,color=green,weight="bold")
ax.text(xC0+0.217,0.245,r"$A_6=i\,2^5g^{-3}\dfrac{N_6}{e_3^-+e_3^+}$",ha="center",fontsize=7.1)
ax.text(xC0+0.163,0.195,"•  140/140 exact tests",fontsize=6.5)
ax.text(xC0+0.163,0.155,"•  58 chambers",fontsize=6.5)

fig.savefig(out_pdf, bbox_inches="tight", pad_inches=0.03)
plt.close(fig)

print(f"Saved {out_pdf}")
