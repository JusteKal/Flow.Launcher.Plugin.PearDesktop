# Pear Desktop for Flow Launcher

Control [Pear Desktop](https://github.com/pear-devs/pear-desktop) from [Flow Launcher](https://github.com/Flow-Launcher/Flow.Launcher).

<img width="1238" height="599" alt="output_20261009_203243_368146_55937d57" src="https://github.com/user-attachments/assets/4bb74d86-2b7e-4d75-a0d9-d4d3f3f0aee7" />


## Prerequisites
1. Pear Desktop: **Plugins > API Server** enabled (default port 26538).
2. Flow Launcher with Python configured (Settings > Python) — no libraries to install.

## Installation
Copy the `Flow.Launcher.Plugin.PearDesktop` folder into
`%APPDATA%%FLOWLAUNCHER%%PLUGINS%%` then restart Flow Launcher.

## First Use
Type `pear auth` → Enter, then click **Allow** in the Pear pop-up.
The token is stored in `%APPDATA%%FLOWLAUNCHER%%SETTINGS%%Plugins%%PearDesktop%%token.txt`.
(The token is stored in `%APPDATA%\FlowLauncher\Settings\Plugins\PearDesktop\token.txt`.)
> Tip: In Flow Launcher > Plugins > Pear Desktop, set a *Search delay* (≈ 400 ms) to avoid triggering a search on every key press.

| Command | Action |
|---|---|
| `pear` | Now Playing (with cover) + all commands |
| `pear play` / `pause` / `next` / `prev` | Play / Pause / Next / Previous |
| `pear like` / `dislike` | Like / Dislike |
| `pear shuffle` / `repeat` / `mute` / `full` | Shuffle / Repeat / Mute / Fullscreen |
| `pear vol 40` | Volume to 40%% |
| `pear seek 1:30` | Go to 1:30 |
| `pear +10` / `-10` | Forward / Backward 10 seconds |
| `pear search <texte>` (or `pear s <texte>`) | Search songs. Enter: play now; Shift+Enter: "Play later" / "Add to end of queue"

> Tip: In Flow Launcher > Plugins > Pear Desktop, set a *Search delay* (≈ 400 ms) to avoid triggering a search on every key press.
