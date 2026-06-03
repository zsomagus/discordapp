# modulok/terkep.py

import os
from pathlib import Path
import svgwrite

from modulok.config import BASE_DIR

OUTPUT_DIR = os.path.expanduser("~/Letöltések/SonicJyotish")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_karmic_map_svg(chart, meta, filename="karmikus_terkep.svg"):
    """
    Karmikus–spirituális életfeladat térkép.
    chart: astro_core.generate_chart() dict
    meta:  név, dátum stb. (ugyanaz, mint elemzésnél)
    """

    planets = chart.get("planets", {})
    asc = chart.get("ascendant", {})
    tithi = chart.get("tithi")

    width, height = 1200, 800
    dwg = svgwrite.Drawing(
        filename=os.path.join(OUTPUT_DIR, filename),
        size=(width, height)
    )

    # Háttérkép
    bg_path = BASE_DIR / "static" / "background.jpg"
    if bg_path.exists():
        dwg.add(dwg.image(
            href=str(bg_path),
            insert=(0, 0),
            size=(width, height)
        ))

    # Középső "Te" csomópont
    center = (width / 2, height / 2)
    dwg.add(dwg.circle(center=center, r=70, fill="rgba(0,0,0,0.6)"))
    dwg.add(dwg.text(
        f"{meta.get('keresztnev','')} {meta.get('vezeteknev','')}",
        insert=(center[0], center[1] - 5),
        text_anchor="middle",
        fill="white",
        font_size="18px"
    ))
    dwg.add(dwg.text(
        "Lélek / Én",
        insert=(center[0], center[1] + 18),
        text_anchor="middle",
        fill="white",
        font_size="14px"
    ))

    # Segédfüggvény csomópont rajzolására
    def node(x, y, title, subtitle, color="#2E4E1F"):
        dwg.add(dwg.circle(center=(x, y), r=60, fill="rgba(0,0,0,0.55)", stroke=color, stroke_width=3))
        dwg.add(dwg.text(
            title,
            insert=(x, y - 5),
            text_anchor="middle",
            fill="white",
            font_size="15px"
        ))
        dwg.add(dwg.text(
            subtitle,
            insert=(x, y + 15),
            text_anchor="middle",
            fill="#DDFFDD",
            font_size="12px"
        ))

    def arrow(from_xy, to_xy, color="#88FF88"):
        dwg.add(dwg.line(
            start=from_xy,
            end=to_xy,
            stroke=color,
            stroke_width=2,
            marker_end=dwg.marker(id="arrow")
        ))

    # Marker a nyilakhoz
    marker = dwg.marker(insert=(10, 5), size=(10, 10), orient="auto", id="arrow")
    marker.add(dwg.path(d="M 0 0 L 10 5 L 0 10 z", fill="#88FF88"))
    dwg.defs.add(marker)

    # Pozíciók
    dharma_pos = (center[0] - 300, center[1] - 150)
    karma_pos = (center[0] + 300, center[1] - 150)
    axis_pos  = (center[0] - 300, center[1] + 150)
    heart_pos = (center[0] + 300, center[1] + 150)

    # Nap – Dharma / Életcél
    sun = planets.get("Sun", {})
    sun_sign = sun.get("sign", "ismeretlen")
    node(dharma_pos[0], dharma_pos[1], "Dharma / Cél", f"Nap: {sun_sign}")

    # Szaturnusz – Karma / Lecke
    sat = planets.get("Saturn", {})
    sat_sign = sat.get("sign", "ismeretlen")
    node(karma_pos[0], karma_pos[1], "Karma / Lecke", f"Szaturnusz: {sat_sign}")

    # Rahu–Ketu tengely
    rahu = planets.get("Rahu", {})
    ketu = planets.get("Ketu", {})
    rahu_sign = rahu.get("sign", "?")
    ketu_sign = ketu.get("sign", "?")
    node(axis_pos[0], axis_pos[1], "Rahu–Ketu tengely", f"{rahu_sign} ↔ {ketu_sign}")

    # Hold / Szív / Kapcsolódás
    moon = planets.get("Moon", {})
    moon_sign = moon.get("sign", "ismeretlen")
    node(heart_pos[0], heart_pos[1], "Szív / Kapcsolódás", f"Hold: {moon_sign}")

    # Nyilak a középpontból
    arrow(center, dharma_pos)
    arrow(center, karma_pos)
    arrow(center, axis_pos)
    arrow(center, heart_pos)

    # Tithi felirat
    if tithi is not None:
        dwg.add(dwg.text(
            f"Tithi: {tithi}",
            insert=(width / 2, 60),
            text_anchor="middle",
            fill="#FFFFFF",
            font_size="14px"
        ))

    dwg.save()
    return os.path.join(OUTPUT_DIR, filename)
