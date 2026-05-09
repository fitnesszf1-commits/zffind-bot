import os
import discord
from discord import app_commands
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

GAMES_CHANNEL_ID = 1502022033851158638

ai = OpenAI(api_key=OPENAI_API_KEY)


class ZFindBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced")


client = ZFindBot()


def shorten_error(e):
    error_text = str(e)
    if len(error_text) > 1500:
        error_text = error_text[:1500] + "..."
    return error_text


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.tree.command(name="pitch", description="Find football pitch booking links")
async def pitch(
    interaction: discord.Interaction,
    area: str,
    date: str = "today",
    time: str = "8pm",
):
    await interaction.response.defer()

    powerleague_link = (
        f"https://www.powerleague.com/booking/find-location?"
        f"search_location={area}&territory_id=263&result_set=Pitch+search"
        f"&search_disclaimer=Select+your+pitch&action=searchSites"
    )

    message = f"""
⚽ **ZFind Pitch Search**

📍 Area: **{area}**
📅 Date: **{date}**
🕒 Time: **{time}**

🏟️ **Powerleague**
📡 Status: Booking page found
🕒 Times: Open live calendar
🔗 {powerleague_link}

⚠️ Live availability changes quickly. Check the booking page before travelling.
"""

    await interaction.followup.send(message[:1900])


@client.tree.command(name="goals", description="Find Goals football centres")
async def goals(interaction: discord.Interaction, area: str):
    await interaction.response.defer()

    link = f"https://www.goalsfootball.co.uk/centres?search={area}"

    message = f"""
⚽ **Goals Pitch Finder**

📍 Area: **{area}**

🔗 Search here:
{link}

⚠️ Live availability changes quickly. Check the Goals booking page directly.
"""

    await interaction.followup.send(message[:1900])


@client.tree.command(name="game", description="Post a football game needing players")
async def game(
    interaction: discord.Interaction,
    area: str,
    time: str,
    players_needed: int,
    cost: int,
    level: str,
    surface: str,
):
    await interaction.response.defer(ephemeral=True)

    embed = discord.Embed(
        title="⚽ GAME NEEDING PLAYERS",
        description=f"📍 **{area}**",
        color=0x00FF88,
    )

    embed.add_field(name="🕒 Time", value=time, inline=True)
    embed.add_field(name="👥 Players Needed", value=str(players_needed), inline=True)
    embed.add_field(name="💷 Cost", value=f"£{cost}", inline=True)
    embed.add_field(name="🔥 Level", value=level, inline=True)
    embed.add_field(name="🏟️ Surface", value=surface, inline=True)
    embed.set_footer(text=f"Posted by {interaction.user}")

    channel = client.get_channel(GAMES_CHANNEL_ID)

    if channel is None:
        await interaction.followup.send("❌ Could not find games channel.")
        return

    await channel.send(embed=embed)
    await interaction.followup.send("✅ Game posted in 🔥｜games-tonight")


@client.tree.command(
    name="freepitch",
    description="Find free football cages and open-access pitches",
)
async def freepitch(interaction: discord.Interaction, area: str):
    await interaction.response.defer()

    prompt = f"""
You are ZFind.

Search for free football cages, MUGAs, public astros,
park football pitches, and open-access football spots in:

{area}, London.

Include:
- location name
- surface type
- whether lights are likely available
- if it is usually busy
- nearest area/station if possible

Keep it short and Discord-friendly.

Format:

⚽ Free Football Spots

1️⃣ Spot Name
📍 Area
🏟️ Surface
💡 Lights: Yes/No/Unknown
👥 Usually Busy: Yes/No
"""

    try:
        response = ai.responses.create(
            model="gpt-4.1-mini",
            tools=[{"type": "web_search_preview"}],
            input=prompt,
        )

        answer = response.output_text

        if len(answer) > 1900:
            answer = answer[:1900]

        await interaction.followup.send(answer)

    except Exception as e:
        await interaction.followup.send(f"❌ Error:\n```{shorten_error(e)}```")


client.run(DISCORD_TOKEN)