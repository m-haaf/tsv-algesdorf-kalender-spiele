import requests
from ics import Calendar, Event
from datetime import datetime, timedelta
import pytz
import urllib.parse

TEAM_NAME = "TSV Algesdorf II"
TEAM_ID = "011MID2C7G000000VTVG0001VTR8C1K7"
SAISON = "2526"

API_URL = f"https://www.fussball.de/api/team/matches/{TEAM_ID}?season={SAISON}"

cal = Calendar()
tz = pytz.timezone("Europe/Berlin")
headers = {"User-Agent": "Mozilla/5.0"}

try:
    response = requests.get(API_URL, headers=headers, timeout=15)
    response.raise_for_status()
    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        print("⚠️ JSON konnte nicht geparst werden")
        data = {"matches": []}
except Exception as e:
    print("⚠️ Fehler beim Abrufen der API:", e)
    data = {"matches": []}

for match in data.get("matches", []):
    try:
        match_id = match.get("matchId")
        date_str = match.get("matchDate")
        status = match.get("matchStatus")
        if not date_str:
            continue

        start_dt = datetime.fromisoformat(date_str.replace("Z", "+00:00")).astimezone(tz)
        end_dt = start_dt + timedelta(minutes=90)

        home = match.get("homeTeamName")
        away = match.get("awayTeamName")
        location = match.get("venueName", "Unbekannt")
        address = match.get("venueAddress", "")
        competition = match.get("competitionName", "")
        home_goals = match.get("homeGoals")
        away_goals = match.get("awayGoals")

        heimstatus = "🏠 Heim" if home == TEAM_NAME else "🚌 Auswärts"

        if status == "FINISHED" and home_goals is not None:
            result_text = f"{home_goals}:{away_goals}"
            status_icon = "✅"
        elif status == "CANCELLED":
            result_text = "Abgesagt"
            status_icon = "❌"
        elif status == "POSTPONED":
            result_text = "Verlegt"
            status_icon = "🔁"
        else:
            result_text = "Geplant"
            status_icon = "📅"

        maps_query = urllib.parse.quote_plus(f"{location}, {address}")
        google_maps_url = f"https://www.google.com/maps/search/?api=1&query={maps_query}"
        match_link = f"https://www.fussball.de/spiel/{match_id}"

        event = Event()
        event.uid = match_id
        event.name = f"{status_icon} {home} – {away} ({heimstatus})"
        event.begin = start_dt
        event.end = end_dt
        event.location = google_maps_url
        event.description = (
            f"Wettbewerb: {competition}\n"
            f"Status: {result_text}\n\n"
            f"Spielort:\n{location}\n{address}\n\n"
            f"⚽ Spiel auf Fußball.de:\n{match_link}\n\n"
            f"🗺 Google Maps:\n{google_maps_url}"
        )

        cal.events.add(event)
    except Exception as e:
        print("⚠️ Fehler bei Spiel:", e)

# Statt "kalender.ics" im Root:
with open("docs/kalender.ics", "w") as f:
    f.writelines(cal)

print("✅ kalender.ics wurde erstellt")
