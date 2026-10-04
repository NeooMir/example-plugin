# NeoMir Plugin Architecture

## 1. Structure
Each plugin is a dedicated directory containing a `plugin.json` manifest and an executable entry point.

## 2. IPC (Inter-Process Communication)
* **Transport:** Unix Domain Socket via `$NEOMIR_SOCKET` (fallback: `$XDG_RUNTIME_DIR/neomir.sock`).
* **Protocol:** Newline-terminated JSON messages (`\n`).
* **API Commands:**
  * **Robot:** `up`, `down`, `left`, `right`, `paint`, `step_back`, `reset`.
  * **State:** `get_state` (returns coordinates, sensors, collisions).
  * **Console:** `console_print`, `console_clear`, `exec_console`, `set_console_input`, `get_console_input`.

## 3. Language-Agnostic
Write plugins in Python or any other language capable of socket communication. Just connect to the Unix socket, send a serialized JSON request, and read the synchronous response from the NeoMir core. Zero framework lock-in.

## 4. Build & Distribution
* **System-wide (Meson):** Integrated into the core `meson.build`, installs directly to `$datadir/neomir/plugins/`.
* **User Packages (.plug):** A standard `tar.gz` archive containing the plugin source. Installable directly via the NeoMir GUI (Settings → Extensions).
