import os

SWEPH_PATH = r"C:\Users\MZs\Documents\A pykódok\asztro elemzés\sonicjh\static\ephe"

REQUIRED_FILES = [
    "seas_18.se1", "sepl_18.se1", "semo_18.se1"
]

def check_sweph_files():
    """Ellenőrzi, hogy a Swiss Ephemeris fájlok megvannak‑e."""
    missing = []
    for fname in REQUIRED_FILES:
        full_path = os.path.join(SWEPH_PATH, fname)
        if not os.path.exists(full_path):
            missing.append(fname)

    if missing:
        print("⚠️  Hiányzó efemerisz fájlok:", ", ".join(missing))
        print("Töltsd le innen: https://www.astro.com/swisseph/sweph_e.htm")
        return False
    else:
        print("✅  Minden szükséges efemerisz fájl megtalálható.")
        return True
