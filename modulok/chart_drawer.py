import svgwrite
from modulok.tables import sign_positions, RASHI_LORDS, bolygo_nakshatra_map


def draw_four_charts(
        planets,
        asc_sign,
        varga_planets,
        varga_asc,
        tithi,
        filename="four_charts.svg",
        selected_varga="D1",
        person_name="",
        birth_date=""
        show_varshaphala=False,
        varshaphala_label=""
    ):

    cell_size = 120
    margin = 30
    chart_spacing_x = 40
    chart_spacing_y = 40

    chart_w = 4 * cell_size + 2 * margin
    chart_h = 4 * cell_size + 2 * margin

    total_w = 2 * chart_w + chart_spacing_x
    total_h = 2 * chart_h + chart_spacing_y + 120

    dwg = svgwrite.Drawing(filename, size=(total_w, total_h))
    dwg.add(dwg.rect((0, 0), ("100%", "100%"), fill="white"))

    # ---------------------------------------------------------
    # FELSŐ SZÖVEGEK – név + születési adatok
    # ---------------------------------------------------------
    dwg.add(dwg.text(
        f"név-adatok: {person_name}, {birth_date}",
        insert=(margin, 40),
        font_size="18px",
        fill="black"
    ))

    dwg.add(dwg.text(
        "sonicjyotish",
        insert=(total_w/2 - 60, 40),
        font_size="18px",
        fill="black"
    ))

    dwg.add(dwg.text(
        "jobb gomb rákatt valamelyik horoszkópra: menü: elemzés, zene, kotta-musicxml",
        insert=(margin, 70),
        font_size="14px",
        fill="black"
    ))

    # ---------------------------------------------------------
    # 4 HOROSZKÓP POZÍCIÓI
    # ---------------------------------------------------------
    positions = [
        (margin, 120),  # D1
        (chart_w + chart_spacing_x, 120),  # részhoroszkóp
        (margin, chart_h + chart_spacing_y + 120),  # jegy ura
        (chart_w + chart_spacing_x, chart_h + chart_spacing_y + 120)  # nakshatra ura
    ]

    titles = [
        "D1 – Rashi",
        "Részhoroszkóp",
        "Jegy ura",
        "Nakshatra ura"
    ]
    # KÖZÉPSŐ FELIRATOK – csak ha Varshaphala mód aktív
    if show_varshaphala:
        mid_y = 120 + chart_h + chart_spacing_y / 2

        # Bal oldal: Varshaphala
        dwg.add(dwg.text(
            varshaphala_label or "Varshaphala",
            insert=(margin + 2 * cell_size, mid_y),
            text_anchor="middle",
            font_size="18px",
            fill="darkgreen"
        ))

        # Jobb oldal: Részhoroszkóp (vagy a kiválasztott varga neve)
        dwg.add(dwg.text(
            f"{selected_varga} részhoroszkóp",
            insert=(chart_w + chart_spacing_x + 2 * cell_size, mid_y),
            text_anchor="middle",
            font_size="18px",
            fill="darkgreen"
        ))
    # ---------------------------------------------------------
    # 4 HOROSZKÓP RAJZOLÁSA
    # ---------------------------------------------------------
    for (x, y), title in zip(positions, titles):

        # Cím
        dwg.add(dwg.text(
            title,
            insert=(x + 2 * cell_size, y - 10),
            text_anchor="middle",
            font_size="16px",
            fill="black"
        ))

        # -----------------------------------------------------
        # RÁCS – belső keret van, középső kereszt nincs
        # -----------------------------------------------------
        for i in range(5):
            y_line = y + i * cell_size
            x_line = x + i * cell_size

            # vízszintes
            if i in [0, 4]:
                dwg.add(dwg.line((x, y_line), (x + 4 * cell_size, y_line), stroke="black"))
            else:
                dwg.add(dwg.line((x, y_line), (x + cell_size, y_line), stroke="black"))
                dwg.add(dwg.line((x + 3 * cell_size, y_line), (x + 4 * cell_size, y_line), stroke="black"))

            # függőleges
            if i in [0, 4]:
                dwg.add(dwg.line((x_line, y), (x_line, y + 4 * cell_size), stroke="black"))
            else:
                dwg.add(dwg.line((x_line, y), (x_line, y + cell_size), stroke="black"))
                dwg.add(dwg.line((x_line, y + 3 * cell_size), (x_line, y + 4 * cell_size), stroke="black"))

        # Belső keret
        dwg.add(dwg.rect(
            insert=(x + cell_size, y + cell_size),
            size=(2 * cell_size, 2 * cell_size),
            stroke="black",
            fill="none"
        ))
        yantra_path = get_tithi_yantra(tithi)
        dwg.add(dwg.image(href=yantra_path,
                  insert=(x + cell_size, y + cell_size),
                  size=(2 * cell_size, 2 * cell_size)))

        # -----------------------------------------------------
        # D1 – bolygók + Asc zöld átló
        # -----------------------------------------------------
        if title.startswith("D1"):
            offset = {}
            for name, data in planets.items():
                sign = data["sign"]
                cx, cy = sign_positions[sign]

                bx = x + cx * cell_size + cell_size/2
                by = y + cy * cell_size + cell_size/2

                idx = offset.get(sign, 0)
                offset[sign] = idx + 1

                # bolygó neve
                dwg.add(dwg.text(
                    name,
                    insert=(bx, by + idx*16 - 8),
                    text_anchor="middle",
                    font_size="13px",
                    fill="black"
                ))

                # ---------------------------
                # JEGY URA NYÍL (halvány)
                # ---------------------------
                sign_num = list(sign_positions.keys()).index(sign) + 1
                lord = RASHI_LORDS[sign_num][0]
                if lord in planets:
                    lord_sign = planets[lord]["sign"]
                    lx, ly = sign_positions[lord_sign]
                    dwg.add(dwg.line(
                        (bx, by),
                        (x + lx*cell_size + cell_size/2,
                         y + ly*cell_size + cell_size/2),
                        stroke="lightgray",
                        stroke_width=2
                    ))

                # ---------------------------
                # NAKSHATRA URA NYÍL (szaggatott)
                # ---------------------------
                if name in bolygo_nakshatra_map:
                    nak = bolygo_nakshatra_map[name][0]
                    ura = next((b for b, lst in bolygo_nakshatra_map.items() if nak in lst), None)
                    if ura and ura in planets:
                        ura_sign = planets[ura]["sign"]
                        ux, uy = sign_positions[ura_sign]
                        dwg.add(dwg.line(
                            (bx, by),
                            (x + ux*cell_size + cell_size/2,
                             y + uy*cell_size + cell_size/2),
                            stroke="lightgray",
                            stroke_width=2,
                            stroke_dasharray="4,2"
                        ))

            # Asc zöld átló
            asc_cx, asc_cy = sign_positions[asc_sign]
            dwg.add(dwg.line(
                (x + asc_cx * cell_size, y + asc_cy * cell_size),
                (x + asc_cx * cell_size + cell_size, y + asc_cy * cell_size + cell_size),
                stroke="green",
                stroke_width=4
            ))

        # -----------------------------------------------------
        # RÉSZHOROSZKÓP – varga bolygók + varga Asc
        # -----------------------------------------------------
        if title.startswith("Részhoroszkóp"):

            dwg.add(dwg.text(
                f"{selected_varga} részhoroszkóp",
                insert=(x + 2 * cell_size, y - 10),
                text_anchor="middle",
                font_size="16px",
                fill="black"
            ))

            offset = {}
            for name, data in varga_planets.items():
                sign = data["sign"]
                cx, cy = sign_positions[sign]

                bx = x + cx * cell_size + cell_size/2
                by = y + cy * cell_size + cell_size/2

                idx = offset.get(sign, 0)
                offset[sign] = idx + 1

                dwg.add(dwg.text(
                    name,
                    insert=(bx, by + idx*16 - 8),
                    text_anchor="middle",
                    font_size="13px",
                    fill="black"
                ))

            # varga Asc zöld átló
            asc_cx, asc_cy = sign_positions[varga_asc]
            dwg.add(dwg.line(
                (x + asc_cx * cell_size, y + asc_cy * cell_size),
                (x + asc_cx * cell_size + cell_size, y + asc_cy * cell_size + cell_size),
                stroke="green",
                stroke_width=4
            ))

        # -----------------------------------------------------
        # JEGY URA – bal alsó rács
        # -----------------------------------------------------
        if title.startswith("Jegy ura"):

            offset = {}
            for name, data in planets.items():
                sign = data["sign"]

                sign_num = list(sign_positions.keys()).index(sign) + 1
                lord = RASHI_LORDS[sign_num][0]

                cx, cy = sign_positions[sign]
                bx = x + cx * cell_size + cell_size/2
                by = y + cy * cell_size + cell_size/2

                idx = offset.get(sign, 0)
                offset[sign] = idx + 1

                dwg.add(dwg.text(
                    lord,
                    insert=(bx, by + idx*16 - 8),
                    text_anchor="middle",
                    font_size="13px",
                    fill="black"
                ))

            # Asc zöld átló
            asc_cx, asc_cy = sign_positions[asc_sign]
            dwg.add(dwg.line(
                (x + asc_cx * cell_size, y + asc_cy * cell_size),
                (x + asc_cx * cell_size + cell_size, y + asc_cy * cell_size + cell_size),
                stroke="green",
                stroke_width=4
            ))

        # -----------------------------------------------------
        # NAKSHATRA URA – jobb alsó rács
        # -----------------------------------------------------
        if title.startswith("Nakshatra ura"):

            offset = {}
            for name, data in planets.items():
                sign = data["sign"]
                cx, cy = sign_positions[sign]

                nak = bolygo_nakshatra_map[name][0]

                bx = x + cx * cell_size + cell_size/2
                by = y + cy * cell_size + cell_size/2

                idx = offset.get(sign, 0)
                offset[sign] = idx + 1

                dwg.add(dwg.text(
                    nak,
                    insert=(bx, by + idx*16 - 8),
                    text_anchor="middle",
                    font_size="13px",
                    fill="black"
                ))

            # Asc zöld átló
            asc_cx, asc_cy = sign_positions[asc_sign]
            dwg.add(dwg.line(
                (x + asc_cx * cell_size, y + asc_cy * cell_size),
                (x + asc_cx * cell_size + cell_size, y + asc_cy * cell_size + cell_size),
                stroke="green",
                stroke_width=4
            ))

    dwg.save()
    print(f"Kész: {filename}")
