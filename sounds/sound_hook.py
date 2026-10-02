#!/usr/bin/env python3
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


SOUNDS = {
    "UserPromptSubmit": "Tink.aiff",
    "PreToolUse": "Pop.aiff",
    "Stop": "Glass.aiff",
}
SOUND_DIR = Path("/System/Library/Sounds")
STATE_DIR = Path(__file__).resolve().parent / ".state"


def session_dir(state_dir, session_id):
    digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()
    return Path(state_dir) / digest


def play_sound(path):
    if not path.is_file():
        return
    try:
        subprocess.Popen(
            ["/usr/bin/afplay", "-v", "0.20", str(path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        pass


def handle_event(event, state_dir=STATE_DIR, play=play_sound):
    if not isinstance(event, dict):
        return
    name = event.get("hook_event_name")
    session_id = event.get("session_id")
    turn_id = event.get("turn_id")
    if name not in SOUNDS or not isinstance(session_id, str) or not session_id:
        return
    if not isinstance(turn_id, str) or not turn_id:
        return

    directory = session_dir(state_dir, session_id)
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / ".lock").open("a") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        state_file = directory / "state.json"
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            state = {}
        if not isinstance(state, dict):
            state = {}

        if name == "UserPromptSubmit":
            if state.get("turn_id") == turn_id and state.get("seen_start"):
                return
            state = {
                "turn_id": turn_id,
                "seen_start": True,
                "seen_tool": False,
                "seen_stop": False,
            }
            sound = SOUNDS[name]
        elif state.get("turn_id") != turn_id or not state.get("seen_start"):
            return
        elif name == "PreToolUse":
            if state.get("seen_tool") or state.get("seen_stop"):
                return
            state["seen_tool"] = True
            sound = SOUNDS[name]
        else:
            if state.get("seen_stop"):
                return
            state["seen_stop"] = True
            sound = SOUNDS[name]

        temporary = directory / "state.tmp"
        temporary.write_text(json.dumps(state), encoding="utf-8")
        os.replace(temporary, state_file)
        play(SOUND_DIR / sound)


def handle_input(raw, state_dir=STATE_DIR, play=play_sound):
    try:
        handle_event(json.loads(raw), state_dir, play)
    except (OSError, ValueError, TypeError):
        pass
    return "{}"


def main():
    sys.stdout.write(handle_input(sys.stdin.read()) + "\n")


if __name__ == "__main__":
    main()
