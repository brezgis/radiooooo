#!/usr/bin/env python3
"""
radiooooo — a terminal client for radiooooo.com
Pick a country and decade. Hear music from there and then.
"""

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import textwrap
import urllib.request
import urllib.error

API_BASE = "https://radiooooo.com"
ASSET_BASE = "https://asset.radiooooo.com"
DECADES = list(range(1900, 2030, 10))
MOODS = ["SLOW", "FAST", "WEIRD"]

# ANSI colors (Catppuccin Mocha-inspired)
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    ITALIC  = "\033[3m"
    MAUVE   = "\033[38;2;203;166;247m"
    PINK    = "\033[38;2;245;194;231m"
    PEACH   = "\033[38;2;250;179;135m"
    GREEN   = "\033[38;2;166;227;161m"
    BLUE    = "\033[38;2;137;180;250m"
    YELLOW  = "\033[38;2;249;226;175m"
    RED     = "\033[38;2;243;139;168m"
    TEXT    = "\033[38;2;205;214;244m"
    SUBTEXT = "\033[38;2;166;173;200m"
    SURFACE = "\033[38;2;69;71;90m"

# Country name → ISO code mapping (cached)
_countries_cache = None

def get_countries():
    global _countries_cache
    if _countries_cache is not None:
        return _countries_cache

    try:
        req = urllib.request.Request(f"{API_BASE}/language/countries/en.json")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"{C.RED}Error fetching countries: {e}{C.RESET}")
        sys.exit(1)

    # Build lookup: lowercase name → iso code, plus iso → iso
    mapping = {}
    names = {}
    for item in data:
        iso, name = item[0], item[1]
        mapping[name.lower()] = iso
        mapping[iso.lower()] = iso
        names[iso] = name

    _countries_cache = (mapping, names)
    return _countries_cache


def resolve_country(query):
    """Resolve a country name or ISO code to an ISO code."""
    mapping, names = get_countries()

    q = query.lower().strip()

    # Exact match on ISO or name
    if q in mapping:
        return mapping[q]

    # Partial match on country names
    matches = [(iso, name) for name, iso in mapping.items()
               if q in name and len(name) > 3]  # skip iso codes in partial match

    # Deduplicate
    seen = set()
    unique = []
    for iso, name in matches:
        if iso not in seen:
            seen.add(iso)
            unique.append((iso, name))

    if len(unique) == 1:
        return unique[0][0]
    elif len(unique) > 1:
        print(f"{C.YELLOW}Multiple matches for '{query}':{C.RESET}")
        for iso, _ in unique[:10]:
            print(f"  {C.BLUE}{iso}{C.RESET} — {names.get(iso, '?')}")
        sys.exit(1)

    print(f"{C.RED}Unknown country: '{query}'{C.RESET}")
    print(f"{C.SUBTEXT}Try a country name (italy, japan) or ISO code (ITA, JPN){C.RESET}")
    sys.exit(1)


def resolve_decade(dec_str):
    """Resolve a decade string like '1970', '70s', '70'."""
    s = dec_str.lower().strip().rstrip('s')
    try:
        n = int(s)
    except ValueError:
        print(f"{C.RED}Invalid decade: '{dec_str}'{C.RESET}")
        print(f"{C.SUBTEXT}Try: 1970, 70s, 70, 2000{C.RESET}")
        sys.exit(1)

    if n < 100:
        # Two-digit: 70 → 1970, 00 → 2000
        if n >= 0 and n <= 20:
            n = 2000 + n
        else:
            n = 1900 + n

    # Round down to decade
    n = (n // 10) * 10

    if n not in DECADES:
        print(f"{C.RED}Decade {n} out of range (1900-2020){C.RESET}")
        sys.exit(1)

    return n


def get_track(country=None, decades=None, moods=None):
    """Fetch a random track from the API."""
    body = {
        "mode": "explore",
        "isocodes": [country] if country else [],
        "decades": decades or [],
        "moods": moods or MOODS
    }

    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{API_BASE}/play", data=data)
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 400:
            err = json.loads(e.read())
            if "No track" in err.get("error", ""):
                return None
        raise


def play_track(track):
    """Play a track using mpv or ffplay."""
    url = track.get("links", {}).get("mpeg")
    if not url:
        print(f"{C.RED}No audio URL found{C.RESET}")
        return None

    # Try mpv first, then ffplay
    player = shutil.which("mpv") or shutil.which("ffplay")
    if not player:
        print(f"{C.RED}No audio player found. Install mpv:{C.RESET}")
        print(f"  {C.SUBTEXT}brew install mpv  {C.DIM}(macOS){C.RESET}")
        print(f"  {C.SUBTEXT}sudo apt install mpv  {C.DIM}(Ubuntu){C.RESET}")
        return None

    if "mpv" in player:
        cmd = [player, "--no-video", "--really-quiet", url]
    else:
        cmd = [player, "-nodisp", "-autoexit", "-loglevel", "quiet", url]

    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def display_track(track, country_names=None):
    """Display track info beautifully."""
    artist = track.get("artist", "Unknown")
    title = track.get("title", "Unknown")
    album = track.get("album")
    year = track.get("year", "?")
    decade = track.get("decade", "?")
    country_code = track.get("country", "?")
    mood = track.get("mood", "?").lower()
    label = track.get("label")
    songwriter = track.get("songwriter")
    length = track.get("length", 0)

    country_name = country_code
    if country_names:
        country_name = country_names.get(country_code, country_code)

    mood_color = {
        "slow": C.BLUE,
        "fast": C.PEACH,
        "weird": C.MAUVE
    }.get(mood, C.TEXT)

    mins = length // 60
    secs = length % 60

    print()
    print(f"  {C.SURFACE}{'─' * 50}{C.RESET}")
    print(f"  {C.BOLD}{C.PINK}♫ {artist}{C.RESET}")
    print(f"  {C.BOLD}{C.TEXT}{title}{C.RESET}")
    if album:
        print(f"  {C.SUBTEXT}{album}{C.RESET}")
    print()
    print(f"  {C.GREEN}{country_name}{C.RESET}  ·  {C.YELLOW}{year}{C.RESET}  ·  {mood_color}{mood}{C.RESET}  ·  {C.SUBTEXT}{mins}:{secs:02d}{C.RESET}")
    if label or songwriter:
        parts = []
        if label:
            parts.append(label)
        if songwriter:
            parts.append(f"written by {songwriter}")
        print(f"  {C.DIM}{' · '.join(parts)}{C.RESET}")
    print(f"  {C.SURFACE}{'─' * 50}{C.RESET}")
    print()


def interactive_mode(country=None, decades=None, moods=None):
    """Continuous playback mode."""
    _, country_names = get_countries()

    print(f"\n  {C.BOLD}{C.MAUVE}📻  radiooooo{C.RESET}")
    print(f"  {C.SUBTEXT}Music from everywhere, everywhen{C.RESET}")

    filters = []
    if country:
        filters.append(country_names.get(country, country))
    if decades:
        filters.append(", ".join(f"{d}s" for d in decades))
    if moods and set(moods) != set(MOODS):
        filters.append(", ".join(m.lower() for m in moods))

    if filters:
        print(f"  {C.DIM}Filters: {' · '.join(filters)}{C.RESET}")

    print(f"\n  {C.SUBTEXT}[n] next  [q] quit{C.RESET}\n")

    process = None

    def cleanup(*_):
        if process and process.poll() is None:
            process.terminate()
        print(f"\n  {C.DIM}goodbye 📻{C.RESET}\n")
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)

    while True:
        track = get_track(country, decades, moods)
        if not track:
            print(f"  {C.RED}No tracks found for this selection. Try different filters.{C.RESET}")
            break

        display_track(track, country_names)

        # Kill previous track
        if process and process.poll() is None:
            process.terminate()

        process = play_track(track)
        if not process:
            break

        # Wait for input or track to end
        while True:
            try:
                if process.poll() is not None:
                    # Track ended naturally
                    break

                # Non-blocking input check
                import select
                if select.select([sys.stdin], [], [], 0.5)[0]:
                    key = sys.stdin.readline().strip().lower()
                    if key in ('q', 'quit', 'exit'):
                        cleanup()
                    elif key in ('n', 'next', ''):
                        break
            except (EOFError, KeyboardInterrupt):
                cleanup()

        if process and process.poll() is None:
            process.terminate()


def list_countries(decade=None):
    """List available countries, optionally for a specific decade."""
    _, names = get_countries()
    
    if decade:
        # Fetch countries that have tracks for this decade
        try:
            req = urllib.request.Request(
                f"{API_BASE}/country/mood?decade={decade}")
            req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            
            print(f"\n  {C.BOLD}Countries with tracks in the {decade}s:{C.RESET}\n")
            all_countries = set()
            for mood, countries in data.items():
                all_countries.update(countries)
            
            for iso in sorted(all_countries):
                name = names.get(iso, iso)
                print(f"  {C.BLUE}{iso}{C.RESET}  {name}")
            print(f"\n  {C.DIM}{len(all_countries)} countries{C.RESET}\n")
        except Exception as e:
            print(f"{C.RED}Error: {e}{C.RESET}")
    else:
        print(f"\n  {C.BOLD}All countries:{C.RESET}\n")
        for iso, name in sorted(names.items(), key=lambda x: x[1]):
            print(f"  {C.BLUE}{iso}{C.RESET}  {name}")
        print(f"\n  {C.DIM}{len(names)} countries{C.RESET}\n")


def main():
    parser = argparse.ArgumentParser(
        prog="radio",
        description="🎵 Terminal client for radiooooo.com — music from everywhere, everywhen",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            examples:
              radio italy 1970           Italian music from the 70s
              radio japan 80s            Japanese music from the 80s
              radio brazil               Random decade, Brazilian music
              radio 1950                 Random country, 1950s music
              radio --mood slow france   Slow French music
              radio --mood weird 60s     Weird music from the 60s
              radio                      Surprise me!
              radio --list               List all countries
              radio --list 1970          Countries with 70s music
        """)
    )

    parser.add_argument("filters", nargs="*",
                       help="Country name/code and/or decade (e.g., 'italy 1970')")
    parser.add_argument("-m", "--mood", action="append", choices=["slow", "fast", "weird"],
                       help="Filter by mood (can repeat: -m slow -m weird)")
    parser.add_argument("-l", "--list", nargs="?", const="all", metavar="DECADE",
                       help="List countries (optionally for a decade)")
    parser.add_argument("-1", "--one", action="store_true",
                       help="Play one track and exit")

    args = parser.parse_args()

    # Handle --list
    if args.list is not None:
        decade = None
        if args.list != "all":
            decade = resolve_decade(args.list)
        list_countries(decade)
        return

    # Parse positional filters into country and decades
    country = None
    decades = []

    for f in (args.filters or []):
        # Try as decade first
        s = f.lower().strip().rstrip('s')
        try:
            n = int(s)
            decades.append(resolve_decade(f))
            continue
        except (ValueError, SystemExit):
            pass

        # Must be a country
        if country is not None:
            print(f"{C.RED}Multiple countries specified. Use one at a time.{C.RESET}")
            sys.exit(1)
        country = resolve_country(f)

    moods = [m.upper() for m in args.mood] if args.mood else None

    if args.one:
        _, country_names = get_countries()
        track = get_track(country, decades, moods)
        if track:
            display_track(track, country_names)
            proc = play_track(track)
            if proc:
                try:
                    proc.wait()
                except KeyboardInterrupt:
                    proc.terminate()
        else:
            print(f"  {C.RED}No tracks found for this selection.{C.RESET}")
    else:
        interactive_mode(country, decades, moods)


if __name__ == "__main__":
    main()
