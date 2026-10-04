#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import json
import socket
from typing import Optional, Dict, Any

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Adw, GLib, Gio


class NeoMirIpcClient:
    # Class for network interaction with the NeoMir core via IPC socket.
    
    def __init__(self):
        # NeoMir passes the socket path via the NEOMIR_SOCKET environment variable
        self.sock_path = os.environ.get("NEOMIR_SOCKET")
        if not self.sock_path:
            xdg = os.environ.get("XDG_RUNTIME_DIR", "/tmp")
            self.sock_path = os.path.join(xdg, "neomir.sock")

    def is_connected(self) -> bool:
        # Check if the socket is available.
        return bool(self.sock_path and os.path.exists(self.sock_path))

    def send_command(self, payload: Any) -> Optional[Dict[str, Any]]:
        # Send a command in JSON format and receive a response from the NeoMir core.
        if not self.is_connected():
            return None

        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect(self.sock_path)

            if isinstance(payload, str):
                data = json.dumps({"cmd": payload})
            else:
                data = json.dumps(payload)

            s.sendall((data + "\n").encode("utf-8"))
            resp_bytes = s.recv(4096)
            s.close()

            if resp_bytes:
                line = resp_bytes.decode("utf-8").strip()
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    return {"raw_response": line}
        except Exception as e:
            print(f"[ExamplePlugin] Socket communication error: {e}", file=sys.stderr)

        return None

    # Helper methods for the NeoMir API
    def move_up(self):
        return self.send_command("up")

    def move_down(self):
        return self.send_command("down")

    def move_left(self):
        return self.send_command("left")

    def move_right(self):
        return self.send_command("right")

    def paint(self):
        return self.send_command("paint")

    def reset(self):
        return self.send_command("reset")

    def step_back(self):
        return self.send_command("step_back")

    def get_state(self):
        return self.send_command("get_state")

    def print_to_console(self, text: str):
        return self.send_command({"cmd": "console_print", "text": text})

    def exec_in_console(self, code: str):
        return self.send_command({"cmd": "exec_console", "text": code})


class ExamplePluginWindow(Adw.ApplicationWindow):
    # Main window of the example plugin.
    
    def __init__(self, app):
        super().__init__(application=app, title="NeoMir Example Plugin")
        self.set_default_size(520, 560)

        self.ipc = NeoMirIpcClient()

        # Root container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_content(main_box)

        # Window header bar
        header = Adw.HeaderBar()
        self.title_widget = Adw.WindowTitle(
            title="Example Plugin",
            subtitle="Connecting to NeoMir IPC..."
        )
        header.set_title_widget(self.title_widget)

        btn_refresh = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
        btn_refresh.set_tooltip_text("Update Robot state")
        btn_refresh.connect("clicked", lambda _: self.update_state_from_neomir())
        header.pack_end(btn_refresh)

        main_box.append(header)

        # Scrollable page with controls
        pref_page = Adw.PreferencesPage()
        main_box.append(pref_page)

        # Group 1: Connection status and Robot coordinates
        group_status = Adw.PreferencesGroup()
        group_status.set_title("Robot Actor State")
        group_status.set_description("Data is retrieved directly from the main NeoMir window via socket.")
        pref_page.add(group_status)

        self.row_coords = Adw.ActionRow()
        self.row_coords.set_title("Robot Position (X, Y)")
        self.row_coords.set_subtitle("Unknown")
        self.row_coords.set_icon_name("find-location-symbolic")
        group_status.add(self.row_coords)

        self.row_cell = Adw.ActionRow()
        self.row_cell.set_title("Current Cell")
        self.row_cell.set_subtitle("Unknown")
        self.row_cell.set_icon_name("format-text-color-symbolic")
        group_status.add(self.row_cell)

        # Group 2: Remote Robot Movement Control
        group_ctrl = Adw.PreferencesGroup()
        group_ctrl.set_title("Remote Robot Control")
        group_ctrl.set_description("Buttons send JSON commands to the NeoMir environment.")
        pref_page.add(group_ctrl)

        row_dpad = Adw.ActionRow()
        row_dpad.set_title("Movement buttons")

        dpad_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        dpad_box.set_valign(Gtk.Align.CENTER)

        btn_up = Gtk.Button.new_from_icon_name("go-up-symbolic")
        btn_up.set_tooltip_text("Up")
        btn_up.connect("clicked", lambda _: self.action_move("up"))
        dpad_box.append(btn_up)

        btn_down = Gtk.Button.new_from_icon_name("go-down-symbolic")
        btn_down.set_tooltip_text("Down")
        btn_down.connect("clicked", lambda _: self.action_move("down"))
        dpad_box.append(btn_down)

        btn_left = Gtk.Button.new_from_icon_name("go-previous-symbolic")
        btn_left.set_tooltip_text("Left")
        btn_left.connect("clicked", lambda _: self.action_move("left"))
        dpad_box.append(btn_left)

        btn_right = Gtk.Button.new_from_icon_name("go-next-symbolic")
        btn_right.set_tooltip_text("Right")
        btn_right.connect("clicked", lambda _: self.action_move("right"))
        dpad_box.append(btn_right)

        btn_paint = Gtk.Button.new_from_icon_name("color-select-symbolic")
        btn_paint.set_tooltip_text("Paint Cell")
        btn_paint.connect("clicked", lambda _: self.action_paint())
        dpad_box.append(btn_paint)

        row_dpad.add_suffix(dpad_box)
        group_ctrl.add(row_dpad)

        # Group 3: Environment Console Interaction
        group_console = Adw.PreferencesGroup()
        group_console.set_title("NeoMir Console")
        group_console.set_description("Send messages and execute code in the application console.")
        pref_page.add(group_console)

        row_msg = Adw.EntryRow()
        row_msg.set_title("Text to output in the console:")
        row_msg.set_text("Hello from the example plugin!")
        self.entry_msg = row_msg

        btn_send_msg = Gtk.Button.new_with_label("Print")
        btn_send_msg.add_css_class("suggested-action")
        btn_send_msg.set_valign(Gtk.Align.CENTER)
        btn_send_msg.connect("clicked", lambda _: self.send_console_message())
        row_msg.add_suffix(btn_send_msg)
        group_console.add(row_msg)

        # Periodically poll the environment state every second
        GLib.timeout_add_seconds(1, self.on_timer_tick)
        self.update_state_from_neomir()

    def on_timer_tick(self) -> bool:
        self.update_state_from_neomir()
        return True

    def update_state_from_neomir(self):
        if not self.ipc.is_connected():
            self.title_widget.set_subtitle("Socket not found (start NeoMir)")
            self.row_coords.set_subtitle("Socket not connected")
            self.row_cell.set_subtitle("—")
            return

        resp = self.ipc.get_state()
        if not resp:
            self.title_widget.set_subtitle("No response from socket")
            return

        x = resp.get("x", "?")
        y = resp.get("y", "?")
        painted = resp.get("is_painted", False)
        crashed = resp.get("crashed", False)

        status_text = f"X: {x} | Y: {y}"
        if crashed:
            status_text += " (Robot crashed!)"

        self.title_widget.set_subtitle(f"Connected to NeoMir | {status_text}")
        self.row_coords.set_subtitle(f"Column {x}, Row {y}")

        cell_str = "Painted" if painted else "Clean"
        self.row_cell.set_subtitle(cell_str)

    def action_move(self, direction: str):
        if direction == "up":
            self.ipc.move_up()
        elif direction == "down":
            self.ipc.move_down()
        elif direction == "left":
            self.ipc.move_left()
        elif direction == "right":
            self.ipc.move_right()
        self.update_state_from_neomir()

    def action_paint(self):
        self.ipc.paint()
        self.update_state_from_neomir()

    def send_console_message(self):
        text = self.entry_msg.get_text().strip()
        if text:
            self.ipc.print_to_console(f"[ExamplePlugin] {text}\n")


class ExamplePluginApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="io.github.neomir.plugin.example",
            flags=Gio.ApplicationFlags.NON_UNIQUE
        )

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = ExamplePluginWindow(self)
        win.present()


def main():
    app = ExamplePluginApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
