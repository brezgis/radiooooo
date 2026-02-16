# 📻 radiooooo

A terminal client for [radiooooo.com](https://radiooooo.com) — music from everywhere, everywhen.

Pick a country and a decade. Hear what people were listening to.

## Usage

```bash
radio italy 1970           # Italian music from the 70s
radio japan 80s            # Japanese music from the 80s
radio brazil               # Random decade, Brazilian music
radio 1950                 # Random country, 1950s music
radio --mood slow france   # Slow French music
radio --mood weird 60s     # Weird 60s music from anywhere
radio                      # Surprise me!
```

### Controls

In continuous mode:
- `Enter` or `n` — next track
- `q` — quit

### Options

```
-m, --mood {slow,fast,weird}   Filter by mood (can repeat)
-l, --list [DECADE]            List countries (optionally for a decade)
-1, --one                      Play one track and exit
```

## Install

### Requirements

- Python 3.7+
- An audio player: [mpv](https://mpv.io/) (recommended) or ffplay

```bash
# macOS
brew install mpv

# Ubuntu/Debian
sudo apt install mpv
```

### Setup

```bash
git clone https://github.com/brezgis/radiooooo.git
cd radiooooo

# Option 1: symlink to your PATH
ln -sf "$(pwd)/radio.py" /usr/local/bin/radio

# Option 2: alias in your shell config
echo 'alias radio="python3 ~/path/to/radiooooo/radio.py"' >> ~/.bashrc
```

## How it works

Uses the [radiooooo.com](https://radiooooo.com) public API to fetch random tracks filtered by country, decade, and mood. Streams audio via mpv. No account needed.

## Credits

- [radiooooo.com](https://radiooooo.com) — the wonderful music time machine
- API documentation from [radio5](https://github.com/ocvit/radio5) (Ruby adapter)
