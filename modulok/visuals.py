# modulok/visuals.py

def generate_visuals_from_summary(summary_text, planet, sign, house):
    """
    Egyszerű vizuális archetípus-generátor.
    Nem készít képet, csak szöveges promptokat ad vissza.
    Ezeket később AI képgenerátorhoz lehet használni.
    """

    prompts = []

    prompts.append(
        f"{planet} archetípusa: {sign} jegyben, {house}. ház energiájával, "
        f"misztikus, szimbolikus, fény-árnyék kontrasztokkal."
    )

    prompts.append(
        f"{planet} mint ősi istenalak, {sign} jegy színeivel és motívumaival, "
        f"asztrológiai ikonográfia, spirituális hangulat."
    )

    prompts.append(
        f"{planet} pszichológiai archetípusa: {sign} jegy, {house}. ház, "
        f"személyiségmélység, mitológiai szimbólumok."
    )

    return prompts
