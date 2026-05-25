# Countdown Timer

A lightweight desktop countdown timer built with Python and Tkinter, featuring a borderless, always-on-top dark theme interface.

## Features

- **Two counting modes:**
  - **Duration** - Count down from a custom time (default: 25 minutes)
  - **Deadline** - Count down to a specific date and time in the future
- **Floating window** - Borderless design, drag to reposition, always stays on top
- **Quick adjustments** - `-1m` / `+1m` buttons for fast time tweaking
- **Start/Pause** - Toggle the countdown at any time
- **Reset** - Instantly reset to the default 25-minute duration
- **Deadline display** - Shows remaining time in `Y y Mo mo D d HH:MM:SS` format for long deadlines, or `H:MM:SS` / `MM:SS` for shorter durations
- **Red flash** on completion
- **Right-click** anywhere or click the `x` button to close

## Requirements

- Python 3.x (standard library only, no extra dependencies)

## Usage

```bash
python countdown_timer.py
```

### Controls

| Button | Action |
|--------|--------|
| `Start` / `Pause` | Start or pause the countdown |
| `-1m` | Subtract 1 minute (Duration mode only, when paused) |
| `+1m` | Add 1 minute (Duration mode only, when paused) |
| `Reset` | Reset to default 25-minute Duration mode |
| `Set` | Open settings to configure a custom Duration or Deadline |
| `x` | Close the timer |

### Set Dialog

1. Click `Set` to open the settings window.
2. Choose **Duration** or **Deadline** mode.
3. Enter the desired hours/minutes/seconds, or a future date and time.
4. Click `Apply` to start.
