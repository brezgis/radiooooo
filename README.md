# 📻 radiooooo

A terminal client for [radiooooo.com](https://radiooooo.com) — music from everywhere, everywhen.

Pick a country and a decade. Hear what people were listening to.

*Unofficial client — not affiliated with [radiooooo.com](https://radiooooo.com), just fond of it.*

## Quickstart

```bash
git clone https://github.com/brezgis/radiooooo.git
cd radiooooo
python3 radio.py italy 1970   # needs mpv or ffplay — see Install below
```

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

### macOS

```bash
brew install mpv
git clone https://github.com/brezgis/radiooooo.git
cd radiooooo

# Add alias for easy access (zsh is the macOS default shell)
echo "alias radio='python3 $PWD/radio.py'" >> ~/.zshrc
source ~/.zshrc
```

### Linux (Ubuntu/Debian)

```bash
sudo apt install mpv
git clone https://github.com/brezgis/radiooooo.git
cd radiooooo

echo "alias radio='python3 $PWD/radio.py'" >> ~/.bashrc
source ~/.bashrc
```

### Windows

1. **Install Python** (if you don't have it): download from [python.org](https://www.python.org/downloads/) — check "Add to PATH" during install

2. **Install mpv** (audio player) — pick one method:
   - **Direct download**: grab the `.7z` from [mpv.io/installation](https://mpv.io/installation/), extract it, and add the folder to your [system PATH](https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/)
   - **Scoop** (if you have it): `scoop install mpv`
   - **Chocolatey** (if you have it): `choco install mpv`

3. **Clone or download the repo**:
   ```
   git clone https://github.com/brezgis/radiooooo.git
   ```
   Or just [download the ZIP](https://github.com/brezgis/radiooooo/archive/refs/heads/main.zip) and extract it.

4. **Run it**:
   ```
   cd radiooooo
   python radio.py -1 italy 1970
   ```
   The `-1` flag plays one track and exits. Continuous mode's keyboard controls
   rely on Unix terminal input and may not work on Windows.

5. **(Optional) Create a shortcut** — add a `radio.bat` file somewhere in your PATH:
   ```bat
   @echo off
   python "C:\path\to\radiooooo\radio.py" %*
   ```
   Then you can just type `radio italy 1970` from anywhere.

## How it works

Uses the [radiooooo.com](https://radiooooo.com) public API to fetch random tracks filtered by country, decade, and mood. Streams audio via mpv. No account needed.

## Credits

- [radiooooo.com](https://radiooooo.com) — the wonderful music time machine
- API documentation from [radio5](https://github.com/ocvit/radio5) (Ruby adapter)

## License

[MIT](LICENSE)
