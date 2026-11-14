# Pole / NeoMir Python Plugin Documentation

Template and architectural guide for developing **Python** plugins (utilizing GTK4 and Libadwaita user interfaces) for the Pole / NeoMir educational IDE.

---

## 1. Plugin Directory Structure

Each plugin is organized as a standalone directory containing a `plugin.json` manifest and an executable entry point:

```text
example-plugin/
├── meson.build               # Standalone Meson build configuration
├── README.md                 # Plugin technical documentation
└── example/
    ├── plugin.json           # Plugin metadata manifest
    └── example_plugin.py     # Executable script (GTK4/Adwaita + IPC socket client)
```

### Manifest: `plugin.json`
```json
{
  "id": "example",
  "name": "Python Example Plugin",
  "version": "1.0.0",
  "author": "NeoMir Team",
  "description": "Standard boilerplate for creating Python plugins with Adwaita UI and IPC bridge.",
  "enabled": false,
  "entry": "example_plugin.py"
}
```

---

## 2. IPC Protocol Specification

Plugins communicate with the host Pole application over a local Unix Domain Socket:
* **Environment Variable:** `NEOMIR_SOCKET` or `POLE_SOCKET` (injected by Pole upon process launch).
* **Fallback Socket Path:** `$XDG_RUNTIME_DIR/neomir.sock` (or `/tmp/neomir.sock`).
* **Frame Delimiter:** Newline-terminated JSON strings (`\n`).

### API Command Reference

| Command | Description | Payload Example |
|---------|-------------|-----------------|
| `up` / `down` / `left` / `right` | Move Robot actor by one cell | `{"cmd": "up"}` |
| `paint` | Mark / paint current cell | `{"cmd": "paint"}` |
| `reset` | Reset Robot actor to initial spawn position | `{"cmd": "reset"}` |
| `step_back` | Revert actor movement by one step | `{"cmd": "step_back"}` |
| `get_state` | Query coordinates, sensors, wall boundaries | `{"cmd": "get_state"}` |
| `turtle_forward` | Move Turtle forward | `{"cmd": "turtle_forward", "dist": 50}` |
| `turtle_left` / `turtle_right` | Turn Turtle heading angle | `{"cmd": "turtle_left", "angle": 90}` |
| `console_print` | Stream log message to Pole console | `{"cmd": "console_print", "text": "Log\n"}` |
| `console_clear` | Clear Pole console output | `{"cmd": "console_clear"}` |

### Sample Response (`get_state`):
```json
{
  "status": "ok",
  "x": 2,
  "y": 1,
  "is_painted": false,
  "crashed": false,
  "wall_up": true,
  "wall_down": false,
  "wall_left": false,
  "wall_right": false
}
```

---

## 3. Building & Installation via Meson

The plugin can be built and packaged using Meson and Ninja without external build dependencies.

### Generate `.plug` Package Bundle:
```bash
meson setup _build
ninja -C _build
```
This produces `_build/example.plug`.

### Direct System Installation (Without Archive):
```bash
ninja -C _build install
```
Directly installs plugin assets to `$datadir/neomir/plugins/example/`.

### Installation in Pole GUI:
Open **Settings → Extensions Tab → Click "Install from File..." (Select .plug...)** and pick `example.plug` (or the folder directly).
