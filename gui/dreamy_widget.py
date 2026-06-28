import discord
from discord import app_commands
from discord.ext import commands
from modulok.load_alomszotar import load_alomszotar
from modulok.music_prompt import build_music_prompt

class DreamyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.szotar = load_alomszotar()

    def levag_ragokat(self, szo: str) -> str:
        ragok = ["ban","ben","val","vel","hoz","hez","höz","nak","nek",
                 "ból","ből","ról","ről","tól","től","ra","re","ig","ért"]
        szo = szo.lower().strip()

        for rag in ragok:
            if szo.endswith(rag) and len(szo) > len(rag) + 2:
                szo = szo[:-len(rag)]
                break

        if len(szo) > 3:
            if szo.endswith("t") and szo[-2] in "aeoóéi":
                szo = szo[:-1]
            if szo.endswith("k") and szo[-2] in "aeoö":
                szo = szo[:-1]

        return szo

    @app_commands.command(name="alom", description="Álomértelmezés + AI zenei prompt generálás")
    @app_commands.describe(
        mit_almoltal="Írd le az álmodat",
        hangulat="Milyen érzés volt az álom?",
        kulcsszavak="Opcionális kulcsszavak"
    )
    async def alom(self, interaction: discord.Interaction,
                   mit_almoltal: str,
                   hangulat: str = "Nyugodt",
                   kulcsszavak: str = ""):

        await interaction.response.defer(ephemeral=True)

        text = mit_almoltal.strip()
        if not text:
            await interaction.followup.send("❌ Kérlek, írd le az álmodat!", ephemeral=True)
            return

        szavak = [s for s in text.split() if len(s) > 2]
        szavak_tovei = [self.levag_ragokat(s) for s in szavak]

        extra = [k.strip().lower() for k in kulcsszavak.split(",") if k.strip()]
        keresett = list(set(szavak_tovei + extra))

        talalatok = []
        szimbolumok = []

        if self.szotar:
            for szo in keresett:
                if len(szo) < 3:
                    continue
                for item in self.szotar.get("alomszotar", []):
                    kulcsszo = item.get("kulcsszo", "").lower().strip()
                    if szo == kulcsszo or kulcsszo in szo:
                        for j in item.get("jelentesek", []):
                            sor = f"• **{kulcsszo.capitalize()}**: {j}"
                            if sor not in talalatok:
                                talalatok.append(sor)
                        if kulcsszo not in szimbolumok:
                            szimbolumok.append(kulcsszo)

        if talalatok:
            ertelmezes = "\n".join(talalatok)
        else:
            ertelmezes = (
                "❌ Nincs találat az álomszótárban.\n"
                f"Próbált kulcsszavak: _{', '.join(keresett)}_"
            )

        prompt = build_music_prompt(text, hangulat, kulcsszavak, szimbolumok)

        valasz = (
            "✨ **Álomértelmezés** ✨\n\n"
            f"📝 **Álom:**\n_{text}_\n\n"
            f"🎭 **Hangulat:** `{hangulat}`\n"
            f"🏷️ **Szimbolumok:** {', '.join(szimbolumok) if szimbolumok else 'Nincs'}\n\n"
            f"🔮 **Jelentések:**\n{ertelmezes}\n\n"
            "🎵 **AI zenei prompt:**\n"
            f"```text\n{prompt}\n```"
        )

        await interaction.followup.send(valasz, ephemeral=True)

async def setup(bot):
    await bot.add_cog(DreamyCog(bot))
