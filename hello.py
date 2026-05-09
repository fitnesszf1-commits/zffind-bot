import os
import discord
from discord import app_commands
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

GAMES_CHANNEL_ID = 1502022033851158638
POWERLEAGUE_VENUES = {
    "shoreditch": {
        "name": "Powerleague Shoreditch",
        "id": "a20a54a1-3bdd-57b8-e211-6f44da11e82f",
        "formats": ["5-a-side Football", "7-a-side Football"],
    },
    "southwark": {
        "name": "Powerleague Southwark",
        "id": "4f9d2f19-3d3c-11ef-943e-6045bd0f4951",
        "formats": ["5-a-side Football"],
    },
    "shepherds bush": {
        "name": "Powerleague Shepherd's Bush",
        "id": "ab9b7a16-b3fc-2b90-8214-69ba3020d23c",
        "formats": ["5-a-side Football"],
    },
    "harrow": {
        "name": "Powerleague Harrow",
        "id": "ac1c8e58-0f26-c6b9-6214-1e8fc029ef3a",
        "formats": ["5-a-side Football"],
    },
    "battersea": {
        "name": "Powerleague Battersea",
        "id": "dcce87d1-c60a-d5a5-3814-3fa0b007c0b1",
        "formats": ["5-a-side Football", "7-a-side Football"],
    },
    "vauxhall": {
        "name": "Powerleague Vauxhall",
        "id": "e5bf4727-e258-bf85-ef13-714728d4ba74",
        "formats": ["5-a-side Football", "7-a-side Football"],
    },
    "fairlop": {
        "name": "Powerleague Fairlop",
        "id": "cb58ea55-6dec-d1bd-e211-ee5818802d19",
        "formats": ["5-a-side Football", "6-a-side Football", "7-a-side Football"],
    },
    "barnet": {
        "name": "Powerleague Barnet",
        "id": "f43ae0e2-58fb-11b8-e211-712e3ec94836",
        "formats": ["5-a-side Football", "7-a-side Football"],
    },
    "romford": {
        "name": "Powerleague Romford",
        "id": "a21f6d63-4043-a38a-8214-65baa0218977",
        "formats": ["5-a-side Football", "7-a-side Football"],
    },
    "croydon": {
        "name": "Powerleague Croydon",
        "id": "9a1b8d33-91e7-d88e-e211-0f5fe2796d5c",
        "formats": ["5-a-side Football", "7-a-side Football"],
    },
}

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


@client.tree.command(name="pitch", description="Find Powerleague football booking links")
async def pitch(
    interaction: discord.Interaction,
    area: str,
    date: str = "2026-05-09",
    time: str = "8pm",
    pitch_type: str = "5-a-side Football",
):
    await interaction.response.defer()

    area_key = area.lower().strip().replace("’", "'")
    venue = POWERLEAGUE_VENUES.get(area_key)

    if venue is None:
        available_venues = ", ".join(POWERLEAGUE_VENUES.keys())

        london_search_link = (
            "https://www.powerleague.com/booking/find-location"
            "?search_location=London%2C+ENG%2C+United+Kingdom"
            "&search_lat=51.5074456"
            "&search_lng=-0.1277653"
            f"&search_date={date}"
            "&search_range="
            "&territory_id=263"
            "&result_set=Pitch+search"
            "&search_sport="
            "&search_size="
            "&search_surface="
            "&search_booking_modifier="
            "&search_disclaimer=Select+your+pitch"
            "&search_venue="
            "&action=searchSites"
        )

        message = f"""
⚽ **ZFind Powerleague Search**

❌ I don't have a direct calendar for **{area}** yet.

✅ Saved venues:
{available_venues}

🔗 London search:
{london_search_link}
"""
        await interaction.followup.send(message[:1900])
        return

    if pitch_type not in venue["formats"]:
        formats = "\n".join([f"• {f}" for f in venue["formats"]])

        message = f"""
⚽ **ZFind Powerleague Search**

📍 Venue: **{venue['name']}**

❌ **{pitch_type}** is not saved for this venue yet.

Available formats:
{formats}
"""
        await interaction.followup.send(message[:1900])
        return

    encoded_pitch_type = pitch_type.replace(" ", "%20")

    booking_url = (
        "https://www.powerleague.com/booking/select-time"
        f"?search_booking_type_name={encoded_pitch_type}"
        f"&search_location_id={venue['id']}"
        f"&search_date={date}"
        "&search_booking_modifier="
    )

    message = f"""
⚽ **ZFind Live Booking**

📍 Venue: **{venue['name']}**
📅 Date: **{date}**
🕒 Requested Time: **{time}**
🏟️ Format: **{pitch_type}**

✅ Live booking calendar found

🔗 {booking_url}

⚠️ Availability changes quickly. Open the booking page to confirm the exact slot.
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