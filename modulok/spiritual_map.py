# modulok/spiritual_map.py

import os
import svgwrite
from modulok.config import BASE_DIR

BASE_OUTPUT = os.path.expanduser("~/Letöltések/SonicJyotish")


PLANET_COLORS = {
    "Sun": "gold",
    "Moon": "silver",
    "Mars": "red",
    "Mercury": "gray",
    "Jupiter": "orange",
    "Venus": "green",
    "Saturn": "black",
    "Rahu": "#5A2A82",
    "Ketu": "#5A2A82",
}


def _safe_person_folder(meta):
    name = f"{meta.get('keresztnev','')}_{meta.get('vezeteknev','')}".strip()
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in name)
    folder = os.path.join(BASE_OUTPUT, safe or "ismeretlen")
    os.makedirs(folder, exist_ok=True)
    return folder


def generate_spiritual_map(chart, meta, filename="spiritual_map.svg"):
    planets = chart.get("planets", {})
    width, height = 1400, 900

    folder = _safe_person_folder(meta)
    out_path = os.path.join(folder, filename)

    dwg = svgwrite.Drawing(out_path, size=(width, height))

    # Háttér
    bg_path = BASE_DIR / "static" / "background.jpg"
    if bg_path.exists():
        dwg.add(dwg.image(href=str(bg_path), insert=(0, 0), size=(width, height)))

    center = (width / 2, height / 2)

    # Nyíl marker
    marker = dwg.marker(insert=(10, 5), size=(10, 10), orient="auto", id="arrow")
    marker.add(dwg.path(d="M 0 0 L 10 5 L 0 10 z", fill="#FFFFFF"))
    dwg.defs.add(marker)

    def arrow(start, end, color="#FFFFFF", width=2):
        dwg.add(dwg.line(
            start=start,
            end=end,
            stroke=color,
            stroke_width=width,
            marker_end=marker.get_funciri()
        ))

    def node(x, y, title, subtitle="", color="#2E4E1F"):
        dwg.add(dwg.circle(center=(x, y), r=70,
                           fill="rgba(0,0,0,0.55)",
                           stroke=color,
                           stroke_width=3))
        dwg.add(dwg.text(
            title,
            insert=(x, y - 5),
            text_anchor="middle",
            fill="white",
            font_size="18px"
        ))
        if subtitle:
            dwg.add(dwg.text(
                subtitle,
                insert=(x, y + 18),
                text_anchor="middle",
                fill="#DDFFDD",
                font_size="13px"
            ))

    # Középső csomópont – Te / Lélek
    node(center[0], center[1],
         f"{meta.get('keresztnev','')} {meta.get('vezeteknev','')}",
         "Lélek / Én",
         color="#FFFFFF")

    # Fő csomópontok
    sun_pos   = (center[0], center[1] - 220)
    moon_pos  = (center[0] - 320, center[1])
    sat_pos   = (center[0] + 320, center[1])
    mars_pos  = (center[0], center[1] + 220)
    d9_pos    = (center[0] - 320, center[1] - 220)
    d10_pos   = (center[0] + 320, center[1] - 220)
    life_pos  = (center[0] + 320, center[1] + 220)

    # Nap – cél
    sun = planets.get("Sun", {})
    sun_sign = sun.get("sign", "ismeretlen")
    node(sun_pos[0], sun_pos[1], "Nap – Cél", sun_sign, color=PLANET_COLORS["Sun"])
    arrow(center, sun_pos, color=PLANET_COLORS["Sun"], width=3)

    # Hold – lélek
    moon = planets.get("Moon", {})
    moon_sign = moon.get("sign", "ismeretlen")
    node(moon_pos[0], moon_pos[1], "Hold – Lélek", moon_sign, color=PLANET_COLORS["Moon"])
    arrow(center, moon_pos, color=PLANET_COLORS["Moon"], width=3)

    # Szaturnusz – lecke
    sat = planets.get("Saturn", {})
    sat_sign = sat.get("sign", "ismeretlen")
    node(sat_pos[0], sat_pos[1], "Szaturnusz – Lecke", sat_sign, color=PLANET_COLORS["Saturn"])
    arrow(center, sat_pos, color=PLANET_COLORS["Saturn"], width=3)

    # Mars – fejlődés
    mars = planets.get("Mars", {})
    mars_sign = mars.get("sign", "ismeretlen")
    node(mars_pos[0], mars_pos[1], "Mars – Fejlődés", mars_sign, color=PLANET_COLORS["Mars"])
    arrow(center, mars_pos, color=PLANET_COLORS["Mars"], width=3)

    # D9 / D10
    node(d9_pos[0], d9_pos[1], "D9 – Bhakti mód", "Lélek útja", color="#FFCC66")
    node(d10_pos[0], d10_pos[1], "D10 – Karma mód", "Hivatás útja", color="#FF9966")

    # Életmód ág
    node(life_pos[0], life_pos[1], "Életmód", "Test – Lélek – Szellem", color="#66CC99")
    arrow(center, life_pos, color="#66CC99", width=2)

    # Nap ↔ Hold, Nap ↔ Szaturnusz
    arrow(sun_pos, moon_pos, color=PLANET_COLORS["Moon"], width=2)
    arrow(sun_pos, sat_pos, color=PLANET_COLORS["Saturn"], width=2)

    dwg.save()
    return out_path
