import swisseph as swe
from modulok.settings import SWEPH_PATH, check_sweph_files

def test_swe():
    print("Beállított path:", SWEPH_PATH)
    swe.set_ephe_path(SWEPH_PATH)
    check_sweph_files()

    jd = swe.julday(2000, 1, 1, 12.0)
    res = swe.calc_ut(jd, swe.SUN)

    if len(res) == 2:
        print("❌  Hiba: a Swiss Ephemeris nem tudta kiszámítani a Nap pozícióját.")
        print("Visszatérési érték:", res)
    else:
        lon, lat, dist, speed = res
        print("✅  Swiss Ephemeris működik.")
        print(f"Nap hosszúság: {lon:.6f}°")

if __name__ == "__main__":
    test_swe()
