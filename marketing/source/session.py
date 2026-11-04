"""Drives the dev server (over RCON) and the dev client (on an X display) for the listing screenshots.

  from session import Session
  s = Session()
  s.cmd('time set noon'); s.hud(False); s.shot('out.png')

Commands go to the server console, keys and mouse go to the game window with xdotool, and captures are the X
display's pixels (ImageMagick `import`). Start the server and client first with marketing/source/devrun.sh.
"""
from __future__ import annotations

import math
import os
import socket
import struct
import subprocess
import time
from pathlib import Path

PLAYER = 'Sugarplum'


class Rcon:
    def __init__(self, host='127.0.0.1', port=25575, password='bunny', timeout=60.0):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.next_id = 1
        if self._request(3, password)[0] == -1:
            raise PermissionError('RCON authentication failed')

    def _packet(self, kind, body):
        rid = self.next_id
        self.next_id += 1
        data = struct.pack('<ii', rid, kind) + body.encode('utf-8') + b'\x00\x00'
        self.sock.sendall(struct.pack('<i', len(data)) + data)
        return rid

    def _read(self):
        def recv(n):
            buf = b''
            while len(buf) < n:
                chunk = self.sock.recv(n - len(buf))
                if not chunk:
                    raise ConnectionError('RCON connection closed')
                buf += chunk
            return buf
        length = struct.unpack('<i', recv(4))[0]
        payload = recv(length)
        rid, kind = struct.unpack('<ii', payload[:8])
        return rid, kind, payload[8:-2].decode('utf-8', 'replace')

    def _request(self, kind, body):
        self._packet(kind, body)
        rid, _, text = self._read()
        return rid, text

    def command(self, cmd):
        """Runs a command; long replies come split over several packets, so a marker packet ends the read."""
        rid = self._packet(2, cmd)
        got, _, text = self._read()
        parts = [text] if got == rid else []
        marker = self._packet(0, '')
        while True:
            got, _, text = self._read()
            if got == marker:
                return ''.join(parts)
            if got == rid:
                parts.append(text)


def wait_for(port=25575, password='bunny', seconds=600):
    deadline = time.time() + seconds
    while time.time() < deadline:
        try:
            return Rcon(port=port, password=password)
        except OSError:
            time.sleep(2)
    raise TimeoutError('RCON did not come up')


class Session:
    def __init__(self, display=':1', port=25575):
        self.env = dict(os.environ, DISPLAY=display)
        self.rcon = wait_for(port)
        # F1 toggles the HUD, so remember its state between scripts.
        self.hud_file = Path(os.environ.get('SHOT_LOGS', '/tmp/bunnyland-shots')) / 'hud-hidden'
        self.hud_hidden = self.hud_file.exists()

    # Server side
    def cmd(self, *commands):
        out = ''
        for c in commands:
            out = self.rcon.command(c)
        return out

    def tp(self, x, y, z, yaw=0.0, pitch=0.0, facing=None, eye=1.62):
        """Puts the camera (the player's eyes) eye blocks above x y z, looking along yaw/pitch or at facing."""
        if facing:
            dx, dy, dz = facing[0] - x, facing[1] - (y + eye), facing[2] - z
            yaw = math.degrees(math.atan2(-dx, dz))
            pitch = -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
        return self.cmd(f'tp {PLAYER} {x:.2f} {y:.2f} {z:.2f} {yaw:.2f} {pitch:.2f}')

    # Client side
    def xdo(self, *args):
        subprocess.run(['xdotool', *args], env=self.env, check=False)

    def window(self):
        out = subprocess.run(['xdotool', 'search', '--name', 'Minecraft'], env=self.env, capture_output=True, text=True).stdout.split()
        return out[-1] if out else None

    def focus(self):
        w = self.window()
        if w:
            # Xvfb has no window manager, so focus the window directly.
            self.xdo('windowfocus', '--sync', w)
        return w

    def key(self, *keys, delay=0.15):
        self.focus()
        for k in keys:
            self.xdo('key', '--delay', '60', k)
            time.sleep(delay)

    def type(self, text):
        self.focus()
        self.xdo('type', '--delay', '40', text)

    def hold(self, button, seconds, sneak=False):
        self.focus()
        if sneak:
            self.xdo('keydown', 'shift')
            time.sleep(0.3)
        self.xdo('mousedown', str(button))
        time.sleep(seconds)
        self.xdo('mouseup', str(button))
        if sneak:
            self.xdo('keyup', 'shift')

    def click(self, button=1, x=None, y=None):
        self.focus()
        if x is not None:
            self.xdo('mousemove', str(x), str(y))
            time.sleep(0.1)
        self.xdo('click', str(button))

    def move(self, x, y):
        self.focus()
        self.xdo('mousemove', str(x), str(y))

    def hud(self, visible):
        if visible == self.hud_hidden:
            self.key('F1')
            self.hud_hidden = not visible
            if self.hud_hidden:
                self.hud_file.touch()
            else:
                self.hud_file.unlink(missing_ok=True)

    def shot(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['import', '-window', 'root', str(path)], env=self.env, check=True)
        return path

    @staticmethod
    def wait(seconds):
        time.sleep(seconds)
