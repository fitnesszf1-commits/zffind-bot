import os
import subprocess
import discord
from discord import app_commands
from openai import OpenAI

subprocess.run(["python", "-m", "playwright", "install", "chromium"], check=False)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

ai = OpenAI(api_key=OPENAI_API_KEY)


class ZFindBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()


client = ZFindBot()

GAMES_CHANNEL_ID = 1502022033851158638

def shorten_error(e):
    error_text = str(e)
    if len(error_text) > 1500:
        error_text = error_text[:1500] + "..."
    return error_text


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

async def check_powerleague(area: str, date: str, time: str):
    search_url = (
        "https://www.powerleague.com/booking/find-location"
        f"?search_location={area}"
        "&territory_id=263"
        "&result_set=Pitch+search"
        "&search_disclaimer=Select+your+pitch"
        "&action=searchSites"
    )

    results = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--single-process",
                    "--no-zygote",
                ],
            )

            page = await browser.new_page()
            await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(5000)

            page_text = await page.inner_text("body")
            await browser.close()

        text = page_text.lower()

        if area.lower() in text or "powerleague" in text:
            results.append({
                "provider": "Powerleague",
                "area": area,
                "status": "Booking page found",
                "times": "Live times need deeper calendar step",
                "link": search_url
            })

    except Exception as e:
        results.append({
            "provider": "Powerleague",
            "area": area,
            "status": f"Error: {shorten_error(e)}",
            "times": "Unavailable",
            "link": search_url
        })

    return results
    
@client.tree.command(name="pitch", description="Check live football pitch availability")
async def pitch(
    interaction: discord.Interaction,
    area: str,
    date: str = "today",
    time: str = "8pm",
):
    await interaction.response.defer()

    powerleague_results = await check_powerleague(area, date, time)

    message = f"""
⚽ **ZFind Live Pitch Search**

📍 Area: **{area}**
📅 Date: **{date}**
🕒 Time: **{time}**

"""

    for result in powerleague_results:
        message += f"""
🏟️ **{result['provider']}**
📡 Status: {result['status']}
🕒 Times: {result['times']}
🔗 {result['link']}

"""

    await interaction.followup.send(message[:1900])

    prompt = f"""
You are ZFind, a London football pitch finder inside Discord.

User request:
- Area: {area}, London
- Day: {day}
- Time: around {time}
- Pitch type: {pitch_type}

Search the web for real football pitches and booking pages.

Use sources like:
Playfinder, Powerleague, Goals, Better/GLL, PlayFootball, local council pages.

Rules:
- Do not invent confirmed availability.
- Include phone number if publicly available.
- Keep it short.
- Use Discord-friendly formatting.
- Maximum 5 results.

Format exactly like this:

⚽ **ZFind Results**
📍 Area: ...
🕒 Time: ...
🏟️ Type: ...

1️⃣ **Venue Name**
📍 Area
💷 Price
📞 Phone Number
✅ Status: ⚠️ Check live calendar
🔗 Booking: link

End with:
Slots change quickly — check the booking page before travelling.
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

        await interaction.followup.send(f"⚽ **ZFind AI Pitch Search**\n\n{answer}")

    except Exception as e:
        await interaction.followup.send(f"❌ Error:\n```{shorten_error(e)}```")



async def checkslot(interaction: discord.Interaction, url: str, time: str = "8pm"):
    await interaction.response.defer()

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
    headless=True,
    args=[
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--single-process",
        "--no-zygote",
    ],
)

            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(3000)

            page_text = await page.inner_text("body")
            await browser.close()

        time_lower = time.lower()
        page_lower = page_text.lower()

        booking_words = [
            "available",
            "book now",
            "select",
            "reserve",
            "slots",
            "availability",
            "choose a time",
            "add to basket",
        ]

        found_time = time_lower in page_lower
        found_booking_words = any(word in page_lower for word in booking_words)

        if found_time and found_booking_words:
            message = f"""
✅ **Possible slot found**

🕒 Time searched: **{time}**
🔗 Page: {url}

I found the time and booking/availability words on this page.
Open the page to confirm before booking.
"""
        elif found_booking_words:
            message = f"""
⚠️ **Booking page found**

🕒 Time searched: **{time}**
🔗 Page: {url}

I found booking/availability text, but could not confirm the exact time.
"""
        else:
            message = f"""
❌ **No clear slot found**

🕒 Time searched: **{time}**
🔗 Page: {url}

I could not detect availability from this page.
"""

        await interaction.followup.send(message)

    except Exception as e:
        await interaction.followup.send(f"❌ Error:\n```{shorten_error(e)}```")


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
        color=0x00FF88
    )

    embed.add_field(name="🕒 Time", value=time, inline=True)
    embed.add_field(name="👥 Players Needed", value=str(players_needed), inline=True)
    embed.add_field(name="💷 Cost", value=f"£{cost}", inline=True)
    embed.add_field(name="🔥 Level", value=level, inline=True)
    embed.add_field(name="🏟️ Surface", value=surface, inline=True)

    embed.set_footer(text=f"Posted by {interaction.user}")

    channel = client.get_channel(GAMES_CHANNEL_ID)

    print("CHANNEL:", channel)
    print("CHANNEL ID:", GAMES_CHANNEL_ID)

    if channel is None:
        await interaction.followup.send(
            "❌ Could not find games channel."
        )
        return

    await channel.send(embed=embed)

    await interaction.followup.send(
        "✅ Game posted in 🔥｜games-tonight"
    )
    message = f"""
⚽ **GAME POSTED**

📍 Area: **{area}**
🕒 Time: **{time}**
👥 Players Needed: **{players_needed}**
💷 Cost: **£{cost}**
🔥 Level: **{level}**
🏟️ Surface: **{surface}**

React with ⚽ if interested.
"""

    await interaction.response.send_message(message)


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



async def powerleague(interaction: discord.Interaction, venue: str = "shepherds bush"):
    await interaction.response.defer()

    search_url = "https://www.powerleague.com/booking/find-location?search_location=London%2C+United+Kingdom&search_lat=51.5074456&search_lng=-0.1277653&search_date=2026-05-08&search_range=&territory_id=263&result_set=Pitch+search&search_sport=&search_size=&search_surface=&search_booking_modifier=&search_disclaimer=Select+your+pitch&search_venue=&action=searchSites"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
    headless=True,
    args=[
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--single-process",
        "--no-zygote",
    ],
)

            page = await browser.new_page()
            await page.goto(search_url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(5000)

            page_text = await page.inner_text("body")
            await browser.close()

        if venue.lower() in page_text.lower():
            message = f"""
⚽ **Powerleague Check**

📍 Venue searched: **{venue}**
✅ Powerleague venue page loaded
⚠️ Next step: connect to its booking calendar

Use the Powerleague booking page to confirm live slots.
"""
        else:
            message = f"""
⚽ **Powerleague Check**

📍 Venue searched: **{venue}**
⚠️ I loaded Powerleague, but could not confirm this venue from the page text.
Try a different venue name.
"""

        await interaction.followup.send(message)

    except Exception as e:
        await interaction.followup.send(f"❌ Error:\n```{shorten_error(e)}```")


client.run(DISCORD_TOKEN)
