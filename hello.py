import os
import math
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

import discord
from discord import app_commands
from openai import OpenAI


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

GAMES_CHANNEL_ID = 1502022033851158638

ai = OpenAI(api_key=OPENAI_API_KEY)


VENUES = [
    # POWERLEAGUE
    {
        "name": "Powerleague Shepherd's Bush",
        "provider": "Powerleague",
        "area": "White City / Shepherd's Bush",
        "postcode": "W12",
        "lat": 51.5067,
        "lng": -0.2248,
        "formats": "5-a-side",
        "powerleague_id": "ab9b7a16-b3fc-2b90-8214-69ba3020d23c",
    },
    {
        "name": "Powerleague Shoreditch",
        "provider": "Powerleague",
        "area": "Shoreditch",
        "postcode": "E1",
        "lat": 51.5235,
        "lng": -0.0755,
        "formats": "5-a-side / 7-a-side",
        "powerleague_id": "a20a54a1-3bdd-57b8-e211-6f44da11e82f",
    },
    {
        "name": "Powerleague Southwark",
        "provider": "Powerleague",
        "area": "Southwark",
        "postcode": "SE1",
        "lat": 51.5035,
        "lng": -0.0804,
        "formats": "5-a-side",
        "powerleague_id": "4f9d2f19-3d3c-11ef-943e-6045bd0f4951",
    },
    {
        "name": "Powerleague Battersea",
        "provider": "Powerleague",
        "area": "Battersea",
        "postcode": "SW11",
        "lat": 51.4776,
        "lng": -0.1481,
        "formats": "5-a-side / 7-a-side",
        "powerleague_id": "dcce87d1-c60a-d5a5-3814-3fa0b007c0b1",
    },
    {
        "name": "Powerleague Vauxhall",
        "provider": "Powerleague",
        "area": "Vauxhall",
        "postcode": "SW8",
        "lat": 51.4862,
        "lng": -0.1229,
        "formats": "5-a-side / 7-a-side",
        "powerleague_id": "e5bf4727-e258-bf85-ef13-714728d4ba74",
    },
    {
        "name": "Powerleague Fairlop",
        "provider": "Powerleague",
        "area": "Fairlop",
        "postcode": "IG6",
        "lat": 51.5956,
        "lng": 0.0912,
        "formats": "5-a-side / 6-a-side / 7-a-side",
        "powerleague_id": "cb58ea55-6dec-d1bd-e211-ee5818802d19",
    },
    {
        "name": "Powerleague Barnet",
        "provider": "Powerleague",
        "area": "Barnet",
        "postcode": "EN5",
        "lat": 51.6529,
        "lng": -0.1997,
        "formats": "5-a-side / 7-a-side",
        "powerleague_id": "f43ae0e2-58fb-11b8-e211-712e3ec94836",
    },
    {
        "name": "Powerleague Romford",
        "provider": "Powerleague",
        "area": "Romford",
        "postcode": "RM1",
        "lat": 51.5758,
        "lng": 0.1801,
        "formats": "5-a-side / 7-a-side",
        "powerleague_id": "a21f6d63-4043-a38a-8214-65baa0218977",
    },
    {
        "name": "Powerleague Croydon",
        "provider": "Powerleague",
        "area": "Croydon",
        "postcode": "CR0",
        "lat": 51.3762,
        "lng": -0.0982,
        "formats": "5-a-side / 7-a-side",
        "powerleague_id": "9a1b8d33-91e7-d88e-e211-0f5fe2796d5c",
    },

    # GOALS
    {
        "name": "Goals Wembley",
        "provider": "Goals",
        "area": "Wembley",
        "postcode": "HA9",
        "lat": 51.5588,
        "lng": -0.2796,
        "formats": "5-a-side",
        "booking_url": "https://www.goalsfootball.co.uk/our-clubs/london/wembley",
    },
    {
        "name": "Goals Southall",
        "provider": "Goals",
        "area": "Southall",
        "postcode": "UB1",
        "lat": 51.5111,
        "lng": -0.3759,
        "formats": "5-a-side",
        "booking_url": "https://www.goalsfootball.co.uk/our-clubs/london/southall",
    },
    {
        "name": "Goals Eltham",
        "provider": "Goals",
        "area": "Eltham",
        "postcode": "SE9",
        "lat": 51.4513,
        "lng": 0.0542,
        "formats": "5-a-side",
        "booking_url": "https://www.goalsfootball.co.uk/our-clubs/london/eltham",
    },
    {
        "name": "Goals Beckenham",
        "provider": "Goals",
        "area": "Beckenham",
        "postcode": "BR3",
        "lat": 51.4088,
        "lng": -0.0253,
        "formats": "5-a-side",
        "booking_url": "https://www.goalsfootball.co.uk/our-clubs/london/beckenham",
    },
    {
        "name": "Goals Chingford",
        "provider": "Goals",
        "area": "Chingford",
        "postcode": "E4",
        "lat": 51.6303,
        "lng": 0.0007,
        "formats": "5-a-side",
        "booking_url": "https://www.goalsfootball.co.uk/our-clubs/london/chingford",
    },
    {
        "name": "Goals Wimbledon",
        "provider": "Goals",
        "area": "Wimbledon",
        "postcode": "SW19",
        "lat": 51.4214,
        "lng": -0.2064,
        "formats": "5-a-side",
        "booking_url": "https://www.goalsfootball.co.uk/our-clubs/south-east/wimbledon",
    },

    # BETTER / GLL
    {
        "name": "Better Market Road Football Pitches",
        "provider": "Better",
        "area": "Islington / Caledonian Road",
        "postcode": "N7",
        "lat": 51.5476,
        "lng": -0.1162,
        "formats": "5-a-side / 7-a-side / 11-a-side",
        "booking_url": "https://www.better.org.uk/leisure-centre/london/islington/marketroad/football",
    },
    {
        "name": "Better Hackney Football Pitches",
        "provider": "Better",
        "area": "Hackney",
        "postcode": "E8",
        "lat": 51.5450,
        "lng": -0.0553,
        "formats": "5-a-side / 7-a-side / 11-a-side",
        "booking_url": "https://www.better.org.uk/leisure-centre/london/hackney/football",
    },
    {
        "name": "Better Greenwich Football Pitches",
        "provider": "Better",
        "area": "Greenwich",
        "postcode": "SE10",
        "lat": 51.4826,
        "lng": -0.0077,
        "formats": "5-a-side / 7-a-side / 11-a-side",
        "booking_url": "https://www.better.org.uk/leisure-centre/london/greenwich/football",
    },
]


AREA_LOCATIONS = {
    "w12": {"name": "W12", "lat": 51.5067, "lng": -0.2248},
    "ladbroke grove": {"name": "Ladbroke Grove", "lat": 51.5172, "lng": -0.2107},
    "white city": {"name": "White City", "lat": 51.5123, "lng": -0.2247},
    "shepherds bush": {"name": "Shepherd's Bush", "lat": 51.5067, "lng": -0.2248},
    "shepherd's bush": {"name": "Shepherd's Bush", "lat": 51.5067, "lng": -0.2248},
    "hammersmith": {"name": "Hammersmith", "lat": 51.4927, "lng": -0.2339},
    "shoreditch": {"name": "Shoreditch", "lat": 51.5235, "lng": -0.0755},
    "hackney": {"name": "Hackney", "lat": 51.5450, "lng": -0.0553},
    "islington": {"name": "Islington", "lat": 51.5465, "lng": -0.1058},
    "southwark": {"name": "Southwark", "lat": 51.5035, "lng": -0.0804},
    "battersea": {"name": "Battersea", "lat": 51.4776, "lng": -0.1481},
    "vauxhall": {"name": "Vauxhall", "lat": 51.4862, "lng": -0.1229},
    "croydon": {"name": "Croydon", "lat": 51.3762, "lng": -0.0982},
    "barnet": {"name": "Barnet", "lat": 51.6529, "lng": -0.1997},
    "romford": {"name": "Romford", "lat": 51.5758, "lng": 0.1801},
    "fairlop": {"name": "Fairlop", "lat": 51.5956, "lng": 0.0912},
    "harrow": {"name": "Harrow", "lat": 51.5790, "lng": -0.3370},
    "wembley": {"name": "Wembley", "lat": 51.5588, "lng": -0.2796},
    "greenwich": {"name": "Greenwich", "lat": 51.4826, "lng": -0.0077},
    "wimbledon": {"name": "Wimbledon", "lat": 51.4214, "lng": -0.2064},
    "brixton": {"name": "Brixton", "lat": 51.4613, "lng": -0.1156},
    "camden": {"name": "Camden", "lat": 51.5390, "lng": -0.1426},
    "stratford": {"name": "Stratford", "lat": 51.5416, "lng": -0.0034},
    "ealing": {"name": "Ealing", "lat": 51.5130, "lng": -0.3089},
}


class ZFindBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced")


client = ZFindBot()


def normalise(text):
    return text.lower().strip().replace("’", "'")


def shorten_error(e):
    error_text = str(e)
    if len(error_text) > 1500:
        error_text = error_text[:1500] + "..."
    return error_text


def parse_date(date_text):
    value = normalise(date_text)

    if value == "today":
        return datetime.now().strftime("%Y-%m-%d")

    if value == "tomorrow":
        return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    return date_text


def distance_km(lat1, lng1, lat2, lng2):
    radius = 6371
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])

    dlat = lat2 - lat1
    dlng = lng2 - lng1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


def postcode_lookup(area):
    cleaned = area.strip().replace(" ", "")
    encoded = urllib.parse.quote(cleaned)

    try:
        url = f"https://api.postcodes.io/postcodes/{encoded}"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())

        if data.get("status") == 200:
            result = data["result"]
            return {
                "name": result.get("postcode", area),
                "lat": result["latitude"],
                "lng": result["longitude"],
                "source": "postcode",
            }

    except Exception:
        return None

    return None


def local_area_lookup(area):
    key = normalise(area)

    if key in AREA_LOCATIONS:
        found = AREA_LOCATIONS[key]
        return {
            "name": found["name"],
            "lat": found["lat"],
            "lng": found["lng"],
            "source": "saved area",
        }

    # Fuzzy spelling match
    best_key = None
    best_score = 0

    for saved_key in AREA_LOCATIONS.keys():
        score = simple_similarity(key, saved_key)
        if score > best_score:
            best_score = score
            best_key = saved_key

    if best_key and best_score >= 0.72:
        found = AREA_LOCATIONS[best_key]
        return {
            "name": found["name"],
            "lat": found["lat"],
            "lng": found["lng"],
            "source": "fuzzy match",
        }

    return None


def simple_similarity(a, b):
    a_words = set(a.replace("-", " ").split())
    b_words = set(b.replace("-", " ").split())

    if not a_words or not b_words:
        return 0

    overlap = len(a_words.intersection(b_words))
    return overlap / max(len(a_words), len(b_words))


def ai_area_lookup(area):
    try:
        prompt = f"""
You are helping a London football booking Discord bot.

User entered this location:
"{area}"

Work out the most likely London UK area or postcode location.

Return ONLY valid JSON in this exact format:
{{
  "recognised": true,
  "name": "Clean area name",
  "lat": 51.0000,
  "lng": -0.0000
}}

Rules:
- Only return locations in or around London, UK.
- If the input is misspelt, infer the likely London area.
- If the input is too unclear, return:
{{
  "recognised": false,
  "name": null,
  "lat": null,
  "lng": null
}}
"""

        response = ai.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )

        text = response.output_text.strip()
        data = json.loads(text)

        if data.get("recognised") and data.get("lat") and data.get("lng"):
            return {
                "name": data["name"],
                "lat": float(data["lat"]),
                "lng": float(data["lng"]),
                "source": "AI guess",
            }

    except Exception:
        return None

    return None


def resolve_location(area):
    return (
        postcode_lookup(area)
        or local_area_lookup(area)
        or ai_area_lookup(area)
    )


def make_booking_url(venue, date):
    if venue["provider"] == "Powerleague":
        return (
            "https://www.powerleague.com/booking/select-time"
            "?search_booking_type_name=5-a-side%20Football"
            f"&search_location_id={venue['powerleague_id']}"
            f"&search_date={date}"
            "&search_booking_modifier="
        )

    return venue["booking_url"]


def find_nearest_pitches(location, date, provider="any"):
    results = []

    for venue in VENUES:
        if provider.lower() != "any" and venue["provider"].lower() != provider.lower():
            continue

        km = distance_km(
            location["lat"],
            location["lng"],
            venue["lat"],
            venue["lng"],
        )

        venue_copy = dict(venue)
        venue_copy["booking_url"] = make_booking_url(venue, date)

        results.append((km, venue_copy))

    results.sort(key=lambda x: x[0])
    return results[:5]


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
@client.event
async def on_raw_reaction_add(payload):
    if payload.user_id == client.user.id:
        return

    if str(payload.emoji) != "⚽":
        return

    guild = client.get_guild(payload.guild_id)

    if guild is None:
        return

    channel = guild.get_channel(payload.channel_id)

    if channel is None:
        return

    try:
        message = await channel.fetch_message(payload.message_id)

        if not message.embeds:
            return

        embed = message.embeds[0]

        if "GAME NEEDING PLAYERS" not in embed.title:
            return

        organiser_name = embed.footer.text.replace("Hosted by ", "")

        user = guild.get_member(payload.user_id)

        await channel.send(
            f"⚽ {user.mention} wants to join this game."
        )

    except Exception as e:
        print(e)

@client.tree.command(name="pitch", description="Find local football pitches near any London area/postcode")
async def pitch(
    interaction: discord.Interaction,
    area: str,
    date: str = "today",
    time: str = "8pm",
    provider: str = "any",
):
    await interaction.response.defer()

    clean_date = parse_date(date)
    location = resolve_location(area)

    if not location:
        embed = discord.Embed(
            title="⚽ ZFind Local Pitch Search",
            description=f"I couldn't understand **{area}** yet.",
            color=0xFFAA00,
        )

        embed.add_field(
            name="Try examples",
            value="w12, ladbroke grove, brixton, hackney, croydon, wembley, east london",
            inline=False,
        )

        await interaction.followup.send(embed=embed)
        return

    results = find_nearest_pitches(location, clean_date, provider)

    hour = time.lower()

    if "6" in hour or "7" in hour or "8" in hour:
        busy_hint = "🔥 Peak football hours — pitches may book out quickly."
    elif "9" in hour or "10" in hour:
        busy_hint = "✅ Later evening slots are usually easier to find."
    else:
        busy_hint = "⚽ Availability varies depending on the venue and day."

    embed = discord.Embed(
        title="⚽ Nearby Football Pitches",
        description=(
            f"Closest pitches to **{location['name']}**\n"
            f"🧠 Matched using: **{location['source']}**"
        ),
        color=0x00FF88,
    )

    for km, venue in results:
        embed.add_field(
            name=f"{venue['provider']} — {venue['name']}",
            value=(
                f"📍 **Area:** {venue['area']}\n"
                f"📮 **Postcode:** {venue['postcode']}\n"
                f"🏟️ **Formats:** {venue['formats']}\n"
                f"📏 **Distance:** {km:.1f} km\n"
                f"🕒 **Requested:** {time}\n"
                f"🔗 [Open Booking Page]({venue['booking_url']})"
            ),
            inline=False,
        )

    embed.add_field(
        name="📈 Booking Insight",
        value=busy_hint,
        inline=False,
    )

    embed.set_footer(text="Booking availability updates live on provider pages.")

    await interaction.followup.send(embed=embed)
    
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

    embed.add_field(
        name="✅ How To Join",
        value="React with ⚽ below and the organiser will contact you.",
        inline=False,
    )

    embed.set_footer(text=f"Hosted by {interaction.user}")

    channel = client.get_channel(GAMES_CHANNEL_ID)

    if channel is None:
        await interaction.followup.send("❌ Games channel not found.")
        return

    game_message = await channel.send(embed=embed)

    await game_message.add_reaction("⚽")
    await game_message.add_reaction("🔥")

    await interaction.followup.send("✅ Game posted.")


@client.tree.command(name="venues", description="Show saved football venues")
async def venues(interaction: discord.Interaction):
    venue_list = "\n".join(
        [f"• {venue['provider']} — {venue['name']}" for venue in VENUES]
    )

    embed = discord.Embed(
        title="⚽ ZFind Saved Venues",
        description=venue_list[:4000],
        color=0x00FF88,
    )

    await interaction.response.send_message(embed=embed)


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

@client.tree.command(name="games", description="Show recent football games")
async def games(interaction: discord.Interaction):
    await interaction.response.defer()

    channel = client.get_channel(GAMES_CHANNEL_ID)

    if channel is None:
        await interaction.followup.send("❌ Games channel not found.")
        return

    messages = []

    async for msg in channel.history(limit=10):
        if msg.embeds:
            embed = msg.embeds[0]

            if "GAME NEEDING PLAYERS" in embed.title:
                messages.append(embed)

    if not messages:
        await interaction.followup.send("❌ No active games found.")
        return

    await interaction.followup.send(
        f"⚽ Found {len(messages)} recent games."
    )

    for embed in messages:
        await interaction.channel.send(embed=embed)
client.run(DISCORD_TOKEN)
