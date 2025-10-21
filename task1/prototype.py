import textwrap

#const for comment width
max_width = 60

def match_comments_to_events(events, comments):
    """
    Returns a dictionary mapping each event_id to its associated comment (if any),
    including comment id, text, and author. If no comment exists, the value is None.
    """
    # Build a lookup table for comments by ID
    comment_by_id = {c["id"]: c for c in comments}

    matches = {}
    for ev in events:
        comment_id = ev.get("comment_id")
        if comment_id and comment_id in comment_by_id:
            c = comment_by_id[comment_id]
            matches[ev["event_id"]] = {
                "id": c["id"],
                "text": c["text"],
            }
        else:
            matches[ev["event_id"]] = None

    return matches

def generate_article(match, events, matches):
    home = match["home_team"]
    away = match["away_team"]
    stadium = match.get("stadium", "neznámé")
    date = match["date"]
    attendance = match.get("attendance", None)
    total_score = f"{match['score_home']}:{match['score_away']}"
    length = match.get("length_minutes", 90)
    extra = f", zápas trval {length} minut" if length and length!=90 else ""
    att_text = f", za přítomnosti cca {attendance} diváků" if attendance else ""
    intro = (f"Na stadionu {stadium} se dne {date} odehrál zápas mezi {home} (domácími) a {away} (hosté). "
             f"Utkání skončilo výsledkem {total_score}{extra}{att_text}.")
    narrative_lines = []
    events_sorted = sorted(events, key=lambda e: e["minute"])
    for ev in events_sorted:
        m = ev["minute"]
        typ = ev["type"]
        if typ == "goal":
            line = f"Ve {m}. minutě skóroval {ev['player']} za {ev['team']}."
        elif typ == "penalty":
            line = f"Ve {m}. minutě byla nařízena penalta ({ev.get('detail','')})."
        elif typ in ("yellow_card","red_card"):
            card = "žlutou kartu" if typ=="yellow_card" else "červenou kartu"
            line = f"Ve {m}. minutě obdržel {ev['player']} ze týmu {ev['team']} {card}."
        elif typ == "substitution":
            line = f"Ve {m}. minutě proběhlo střídání: {ev['out']} vystřídal {ev['in']}."
        else:
            line = f"{m}. minuta: {typ} - {ev.get('detail','')}"
        ev_matches = matches.get(ev["event_id"])
        if ev_matches:
            wrapped_comment = textwrap.fill(ev_matches['text'], width=max_width)
            line += f" — „{wrapped_comment}“"
        narrative_lines.append(line)
    narrative = "\n".join(narrative_lines)
    stats = match.get("stats", {})
    stats_lines = []
    if stats:
        if "possession_home" in stats:
            stats_lines.append(f"{home} mělo {stats['possession_home']}% držení míče.")
        if "shots_home" in stats and "shots_away" in stats:
            stats_lines.append(f"{home}: {stats['shots_home']} střel ({stats.get('shots_on_target_home',0)} na bránu), "
                               f"{away}: {stats['shots_away']} střel ({stats.get('shots_on_target_away',0)} na bránu).")
        if "saves_home" in stats or "saves_away" in stats:
            stats_lines.append(f"Brankáři si připsali zákroky — {home}: {stats.get('saves_home',0)}, {away}: {stats.get('saves_away',0)}.")
    stats_par = " ".join(stats_lines)
    full = f"{intro}\n\n{narrative}\n\n{stats_par}\n"
    return full

# Example data prototype
match = {
    "home_team": "Sparta Praha",
    "away_team": "Zbrojovka Brno",
    "stadium": "Sparta",
    "date": "02.04.2023 16:00",
    "attendance": "17 288",
    "score_home": 3,
    "score_away": 1,
    "length_minutes": 94,
    "stats": {
        "possession_home": 65,
        "shots_home": 14,
        "shots_on_target_home": 7,
        "shots_away": 8,
        "shots_on_target_away": 2,
        "saves_home": 1,
        "saves_away": 4
    }
}

events = [
    {"event_id": "e1","comment_id" : "c1", "type": "goal", "minute": 17, "player": "Šimon Falta", "team": "Zbrojovka Brno"},
    {"event_id": "e2","comment_id" : "c2", "type": "goal", "minute": 20, "player": "Ladislav Krejčí", "team": "Sparta Praha"},
    {"event_id": "e3","comment_id" : "c3", "type": "goal", "minute": 24, "player": "Jan Kuchta", "team": "Sparta Praha"},
    {"event_id": "e4","comment_id" : None, "type": "yellow_card", "minute": 65, "player": "Kaan Kairinen", "team": "Sparta Praha"},
    {"event_id": "e5","comment_id" : "c4", "type": "goal", "minute": 49, "player": "Tomáš Wiesner", "team": "Sparta Praha"},
    {"event_id": "e6","comment_id" : None, "type": "substitution", "minute": 70, "out": "Jan Mejdr", "in": "Tomáš Wiesner"}
]


comments = [
    {"id":"c1", "text":"Je to gól! Šimon Falta vyslal přesný centr do pokutového území, kde se nejlépe zorientoval Jakub Řezníček (Zbrojovka Brno) a doklepl míč do pravé části branky. Skóre je 0:1."},
    {"id":"c2", "text":"Ladislav Krejčí (Sparta Praha) ukázal svůj cit pro gól, když si pro sebe vybojoval místo po rohovém kopu a z bezprostřední blízkosti míč hlavou neomylně uklidil do levého dolního rohu branky. Upravil tak skóre zápasu na 1:1."},
    {"id":"c3", "text":"Kvalitní centr právě zužitkoval Jan Kuchta (Sparta Praha). Přesnou a razantní střelou po zemi k levé tyči překonal brankáře soupeře."},
    {"id":"c4", "text":"Gól! Tomáš Wiesner (Sparta Praha) se ve vápně dostal k přihrávce vzduchem, kterou vyslal Tomáš Čvančara, a zužitkoval ji nejlépe jak mohl. Pohotově vystřelil do pravého spodního rohu a upravuje skóre na 3:1."},
]
matches = match_comments_to_events(events, comments)
article = generate_article(match, events, matches)

print(article)
