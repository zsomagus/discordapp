import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import pendulum

from modulok.elemzes import generate_full_analysis
from modulok.astro_core import generate_chart
from modulok.chart_drawer import draw_four_charts
from modulok.varshaphala_tools import compute_varshaphala_chart
from modulok.elemzes import (
    generate_markdown_summary_from_chart,
    save_analysis_pdf,
    generate_varshaphala_forecast_block,
)
from modulok.spiritual_map import generate_spiritual_map
from modulok.sonic_world import generate_full_audio  # feltételezzük: (wav_path, mxl_path)


DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Letöltések", "SonicJyotish")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


class SonicJyotishGUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        # --- CANVAS ---
        self.canvas = tk.Canvas(self, width=900, height=900, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        # --- MENTETT SZEMÉLYEK COMBOBOX ---
        tk.Label(self, text="Mentett személy:").grid(row=9, column=0, sticky="e", padx=10, pady=2)
        self.saved_var = tk.StringVar()
        self.saved_combo = ttk.Combobox(self, textvariable=self.saved_var, width=30, state="readonly")
        self.saved_combo.grid(row=9, column=1, columnspan=2, sticky="w")

        self.load_saved_persons()
        self.saved_combo.bind("<<ComboboxSelected>>", self.load_person_data)

        # --- SZEMÉLY MENTÉSE GOMB ---
        self.btn_save_person = tk.Button(self, text="Személy mentése", command=self.save_person_to_json)
        self.btn_save_person.grid(row=9, column=3, sticky="w", padx=10)

        # --- VARGA COMBOBOX ---
        self.varga_var = tk.StringVar(value="D1")
        self.varga_combo = ttk.Combobox(
            self,
            textvariable=self.varga_var,
            values=["D1","D2","D3","D4","D7","D9","D10","D12","D16","D20","D24","D27","D30","D40","D45","D60"],
            state="readonly",
            width=10
        )
        self.varga_combo.grid(row=1, column=0, sticky="w", padx=10)
        self.varga_combo.bind("<<ComboboxSelected>>", self.refresh_chart)

        # --- ELEMZÉS GOMB ---
        self.btn_analyze = tk.Button(self, text="Elemzés", command=self.run_analysis)
        self.btn_analyze.grid(row=1, column=1, sticky="e", padx=10)

        # --- ÉLETKOR MEZŐ (Varshaphala) ---
        tk.Label(self, text="Életkor (Varshaphala):").grid(row=1, column=2, sticky="e", padx=10)
        self.age_var = tk.StringVar()
        tk.Entry(self, textvariable=self.age_var, width=10).grid(row=1, column=3, sticky="w", padx=5)

        # --- VARSHAPHALA GOMB ---
        self.btn_varsha = tk.Button(self, text="Varshaphala", command=self.run_varshaphala)
        self.btn_varsha.grid(row=2, column=0, sticky="w", padx=10, pady=5)

        # --- MENTÉS MINDENT GOMB ---
        self.btn_save_all = tk.Button(self, text="Mentés mindent", command=self.run_save_all)
        self.btn_save_all.grid(row=2, column=1, columnspan=3, pady=5, sticky="w")

        # --- ADATBEVITELI MEZŐK ---

        # Név
        tk.Label(self, text="Név:").grid(row=3, column=0, sticky="e", padx=10, pady=2)
        self.name_var = tk.StringVar()
        tk.Entry(self, textvariable=self.name_var, width=30).grid(row=3, column=1, columnspan=3, sticky="w", pady=2)

        # Születési dátum (YYYY-MM-DD)
        tk.Label(self, text="Születési dátum (ÉÉÉÉ-HH-NN):").grid(row=4, column=0, sticky="e", padx=10, pady=2)
        self.date_var = tk.StringVar()
        tk.Entry(self, textvariable=self.date_var, width=15).grid(row=4, column=1, sticky="w", pady=2)

        # Születési idő (HH:MM)
        tk.Label(self, text="Születési idő (ÓÓ:PP):").grid(row=4, column=2, sticky="e", padx=10, pady=2)
        self.time_var = tk.StringVar()
        tk.Entry(self, textvariable=self.time_var, width=10).grid(row=4, column=3, sticky="w", pady=2)

        # Szélesség
        tk.Label(self, text="Szélesség:").grid(row=5, column=0, sticky="e", padx=10, pady=2)
        self.lat_var = tk.StringVar()
        self.lat_var_entry = tk.Entry(self, textvariable=self.lat_var, width=15)
        self.lat_var_entry.grid(row=5, column=1, sticky="w", pady=2)

        # Hosszúság
        tk.Label(self, text="Hosszúság:").grid(row=5, column=2, sticky="e", padx=10, pady=2)
        self.lng_var = tk.StringVar()
        self.lng_var_entry = tk.Entry(self, textvariable=self.lng_var, width=15)
        self.lng_var_entry.grid(row=5, column=3, sticky="w", pady=2)

        # --- HELY / VÁROS MEZŐ ---
        tk.Label(self, text="Hely / Város:").grid(row=6, column=0, sticky="e", padx=10, pady=2)
        self.city_var = tk.StringVar()
        self.city_entry = tk.Entry(self, textvariable=self.city_var, width=20)
        self.city_entry.grid(row=6, column=1, sticky="w", pady=2)

        # --- KITÖLTÉS GOMB ---
        self.btn_fill = tk.Button(self, text="Kitöltés", command=self.fill_from_city)
        self.btn_fill.grid(row=6, column=2, sticky="w", padx=10)

        # --- IDŐZÓNA MEZŐ ---
        tk.Label(self, text="Időzóna:").grid(row=7, column=0, sticky="e", padx=10, pady=2)
        self.tz_var = tk.StringVar()
        self.tz_entry = tk.Entry(self, textvariable=self.tz_var, width=25)
        self.tz_entry.grid(row=7, column=1, sticky="w", pady=2)

        # --- DST (nyári idő) ---
        tk.Label(self, text="Nyári időszámítás (DST):").grid(row=7, column=2, sticky="e", padx=10, pady=2)
        self.dst_var = tk.StringVar()
        self.dst_label = tk.Label(self, textvariable=self.dst_var)
        self.dst_label.grid(row=7, column=3, sticky="w", pady=2)

        self._img = None

        # Belső alapértékek (ha start_gui tölti)
        self.person_name = ""
        self.vezeteknev = ""
        self.keresztnev = ""
        self.date_str = ""
        self.time_str = ""
        self.timezone_str = "Europe/Budapest"
        self.latitude_str = ""
        self.longitude_str = ""
        self.year = 0
        self.month = 0
        self.day = 0
        self.hour = 0
        self.minute = 0
        self.lat = 0.0
        self.lng = 0.0

    # --- MENTETT SZEMÉLYEK BETÖLTÉSE ---
    def load_saved_persons(self):
        import json
        path = os.path.join("static", "mentett_adatok.json")
        if not os.path.exists(path):
            self.saved_data = {}
            return

        with open(path, "r", encoding="utf-8") as f:
            self.saved_data = json.load(f)

        self.saved_combo["values"] = list(self.saved_data.keys())

    # --- MENTETT SZEMÉLY BETÖLTÉSE ---
    def load_person_data(self, event=None):
        name = self.saved_var.get()
        person = self.saved_data.get(name)
        if not person:
            return

        self.name_var.set(name)
        self.date_var.set(person["date"])
        self.time_var.set(person["time"])
        self.lat_var.set(person["lat"])
        self.lng_var.set(person["lng"])
        self.tz_var.set(person["timezone"])
        self.dst_var.set("Igen" if person.get("dst") else "Nem")

        self.timezone_str = self.tz_var.get().strip() or "Europe/Budapest"

        self._update_internal_from_entries()
        self.refresh_chart()

    # --- SZEMÉLY MENTÉSE JSON-BA ---
    def save_person_to_json(self):
        import json

        name = self.name_var.get().strip()
        if not name:
            print("Név nincs megadva.")
            return

        person = {
            "date": self.date_var.get().strip(),
            "time": self.time_var.get().strip(),
            "lat": self.lat_var.get().strip(),
            "lng": self.lng_var.get().strip(),
            "timezone": self.tz_var.get().strip(),
            "dst": True if self.dst_var.get() == "Igen" else False
        }

        path = os.path.join("static", "mentett_adatok.json")

        if not os.path.exists(path):
            data = {}
        else:
            with open(path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except:
                    data = {}

        data[name] = person

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print("Személy elmentve:", name)

        self.saved_data = data
        self.saved_combo["values"] = list(data.keys())

    # --- KÉP BETÖLTÉSE ---
    def load_chart_image(self, path):
        img = Image.open(path)
        self._img = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(10, 10, anchor="nw", image=self._img)

    # --- ADATOK FRISSÍTÉSE A MEZŐKBŐL ---
    def _update_internal_from_entries(self):
        self.person_name = self.name_var.get().strip() or self.person_name

        if self.date_var.get().strip():
            self.date_str = self.date_var.get().strip()
        if self.time_var.get().strip():
            self.time_str = self.time_var.get().strip()

        if self.lat_var.get().strip():
            self.latitude_str = self.lat_var.get().strip()
        if self.lng_var.get().strip():
            self.longitude_str = self.lng_var.get().strip()
        if self.tz_var.get().strip():
            self.timezone_str = self.tz_var.get().strip()

        if self.date_str and self.time_str:
            y, m, d = map(int, self.date_str.split("-"))
            hh, mm = map(int, self.time_str.split(":"))
            self.year = y
            self.month = m
            self.day = d
            self.hour = hh
            self.minute = mm

        if self.latitude_str:
            self.lat = float(self.latitude_str)
        if self.longitude_str:
            self.lng = float(self.longitude_str)

    # --- RÉSZHOROSZKÓP VÁLTÁS ---
    def refresh_chart(self, event=None):
        self._update_internal_from_entries()
        varga = self.varga_var.get()

        chart = generate_chart(
            self.person_name,
            self.year, self.month, self.day,
            self.hour, self.minute,
            self.lat, self.lng
        )

        out_path = os.path.join(DOWNLOAD_DIR, "four_charts.png")

        draw_four_charts(
            chart["planets"],
            chart["ascendant"]["sign"],
            {},
            chart["ascendant"]["sign"],
            filename=out_path,
            selected_varga=varga,
            person_name=self.person_name,
            birth_date=f"{self.year}-{self.month}-{self.day}"
        )

        self.load_chart_image(out_path)

    # --- ELEMZÉS GOMB ---
    def run_analysis(self):
        self._update_internal_from_entries()

        chart_data, pdf_path = generate_full_analysis(
            self.date_str,
            self.time_str,
            self.timezone_str,
            self.latitude_str,
            self.longitude_str,
            self.vezeteknev,
            self.keresztnev,
            self.varga_var.get(),
            is_prashna=False
        )
        print("Elemzés kész:", pdf_path)

    # --- VARSHAPHALA GOMB ---
    def run_varshaphala(self):
        self._update_internal_from_entries()

        age = int(self.age_var.get() or 0)

        birth_dt = pendulum.datetime(
            self.year, self.month, self.day,
            self.hour, self.minute,
            tz=self.timezone_str or "Europe/Budapest"
        )

        result = compute_varshaphala_chart(
            birth_dt=birth_dt,
            age=age,
            lat=self.lat,
            lon=self.lng
        )

        chart = result["chart"]

        meta = {
            "date_str": str(result["datetime"].date()),
            "time_str": str(result["datetime"].time())[:5],
            "vezeteknev": self.vezeteknev,
            "keresztnev": self.keresztnev,
            "horoszkop_nev": f"Varshaphala_{age}",
        }

        md = generate_markdown_summary_from_chart(chart, meta)
        md += generate_varshaphala_forecast_block(result, age)
        pdf_path = save_analysis_pdf(md, meta)
        print("Varshaphala PDF:", pdf_path)

        svg_path = os.path.join(DOWNLOAD_DIR, "four_charts.png")

        draw_four_charts(
            chart["planets"],
            chart["ascendant"]["sign"],
            {},
            chart["ascendant"]["sign"],
            filename=svg_path,
            selected_varga=self.varga_var.get(),
            person_name=self.person_name,
            birth_date=f"{self.year}-{self.month}-{self.day}",
            show_varshaphala=True,
            varshaphala_label=f"Varshaphala – {age}. év"
        )

        self.load_chart_image(svg_path)

    # --- MENTÉS MINDENT GOMB ---
    def run_save_all(self):
        self._update_internal_from_entries()

        # 1) Teljes elemzés (PDF + WAV + horoszkóp kép)
        result = generate_full_analysis(
            self.date_str,
            self.time_str,
            self.timezone_str,
            self.latitude_str,
            self.longitude_str,
            self.vezeteknev,
            self.keresztnev,
            self.varga_var.get(),
            is_prashna=False
        )
        chart = result["chart"]
        meta = {
            "date_str": self.date_str,
            "time_str": self.time_str,
            "vezeteknev": self.vezeteknev,
            "keresztnev": self.keresztnev,
            "horoszkop_nev": self.varga_var.get(),
        }

        print("PDF:", result["pdf_path"])
        print("WAV (felolvasás):", result["audio_path"])
        print("Horoszkóp kép:", result["image_path"])

        # 2) SVG chart (four_charts)
        svg_path = os.path.join(DOWNLOAD_DIR, "four_charts.png")
        draw_four_charts(
            chart["planets"],
            chart["ascendant"]["sign"],
            {},
            chart["ascendant"]["sign"],
            filename=svg_path,
            selected_varga=self.varga_var.get(),
            person_name=self.person_name,
            birth_date=self.date_str
        )
        print("SVG chart (PNG):", svg_path)

        # 3) Spirituális térkép
        spiritual_path = generate_spiritual_map(chart, meta)
        print("Spiritual_map:", spiritual_path)

        # 4) Zene + MusicXML – feltételezzük: generate_full_audio(chart, meta) -> (wav_path, mxl_path)
        try:
            wav_music, mxl_music = generate_full_audio(chart, meta)
            print("Zene WAV:", wav_music)
            print("MusicXML:", mxl_music)
        except Exception as e:
            print("Hiba a zene generálásánál:", e)

    # --- VÁROS → KOORDINÁTA + IDŐZÓNA + DST ---
    def fill_from_city(self):
        import modulok.config as cfg

        city = self.city_var.get().strip()
        if not city:
            print("Nincs város megadva.")
            return

        ok = cfg.fill_coordinate_entries(
            city,
            lat_entry=self.lat_var_entry,
            lon_entry=self.lng_var_entry
        )

        if not ok:
            print("Nem található koordináta ehhez a városhoz:", city)
            return

        try:
            lat = float(self.lat_var_entry.get())
            lon = float(self.lng_var_entry.get())
            tz = cfg.get_timezone_from_coordinates(lat, lon)
            if tz:
                self.tz_var.set(tz)
                self.timezone_str = tz
            else:
                self.tz_var.set("Europe/Budapest")
                self.timezone_str = "Europe/Budapest"
        except:
            self.tz_var.set("Europe/Budapest")
            self.timezone_str = "Europe/Budapest"

        try:
            dt = pendulum.now(self.timezone_str)
            dst_active = cfg.is_dst_active(dt, self.timezone_str)
            self.dst_var.set("Igen" if dst_active else "Nem")
        except:
            self.dst_var.set("Ismeretlen")

        print("Kitöltve:", city)


def start_gui(person_name, birth_data):
    root = tk.Tk()
    root.title("SonicJyotish")

    gui = SonicJyotishGUI(root)

    gui.person_name = person_name
    gui.vezeteknev = birth_data["vezeteknev"]
    gui.keresztnev = birth_data["keresztnev"]
    gui.date_str = birth_data["date_str"]
    gui.time_str = birth_data["time_str"]
    gui.timezone_str = birth_data["timezone_str"]
    gui.latitude_str = birth_data["latitude"]
    gui.longitude_str = birth_data["longitude"]

    y, m, d = map(int, gui.date_str.split("-"))
    hh, mm = map(int, gui.time_str.split(":"))

    gui.year = y
    gui.month = m
    gui.day = d
    gui.hour = hh
    gui.minute = mm
    gui.lat = float(gui.latitude_str)
    gui.lng = float(gui.longitude_str)

    gui.name_var.set(f"{gui.keresztnev} {gui.vezeteknev}")
    gui.date_var.set(gui.date_str)
    gui.time_var.set(gui.time_str)
    gui.lat_var.set(gui.latitude_str)
    gui.lng_var.set(gui.longitude_str)
    gui.tz_var.set(gui.timezone_str)

    gui.pack(fill="both", expand=True)

    gui.refresh_chart()

    root.mainloop()
