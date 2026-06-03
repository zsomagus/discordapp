# modulok/draw_lord.py
import os
from modulok import draw

def generate_rashi_lord_chart(res: dict, bd: dict):
    """Átrendezi a bolygókat a Rashi Uraik (Ház urai) szerint és kirajzolja."""
    orig_planets = res["planet_data"]
    lord_planet_data = {}

    for p_name, p_info in orig_planets.items():
        rashi_lord_name = p_info.get("rashi_lord", "Unknown")
        
        # Megnézzük, hogy az adott bolygó ura melyik házban ül az eredeti képletben
        if rashi_lord_name in orig_planets:
            target_house_longitude = orig_planets[rashi_lord_name]["longitude"]
        else:
            target_house_longitude = p_info["longitude"] # Fallback

        lord_planet_data[p_name] = {
            "longitude": target_house_longitude
        }

    _, png_path = draw.rajzol_del_indiai_horoszkop_svg(
        varga_pos=res, bd=bd, planet_data=lord_planet_data,
        varga_name=f"{res['varga_code']} - Rashi Lord Map",
        tithi=None, horoszkop_nev=f"{res['varga_code']}_rashi_lord"
    )
    return png_path

def generate_nakshatra_lord_chart(res: dict, bd: dict):
    """Átrendezi a bolygókat a Nakshatra Uraik szerint és kirajzolja."""
    orig_planets = res["planet_data"]
    lord_planet_data = {}

    for p_name, p_info in orig_planets.items():
        naks_lord_name = p_info.get("nakshatra_lord", "Unknown")
        
        if naks_lord_name in orig_planets:
            target_house_longitude = orig_planets[naks_lord_name]["longitude"]
        else:
            target_house_longitude = p_info["longitude"] # Fallback

        lord_planet_data[p_name] = {
            "longitude": target_house_longitude
        }

    _, png_path = draw.rajzol_del_indiai_horoszkop_svg(
        varga_pos=res, bd=bd, planet_data=lord_planet_data,
        varga_name=f"{res['varga_code']} - Nakshatra Lord Map",
        tithi=None, horoszkop_nev=f"{res['varga_code']}_nakshatra_lord"
    )
    return png_path