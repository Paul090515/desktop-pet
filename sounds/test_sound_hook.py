import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from sound_hook import handle_input, session_dir


class SoundHookTest(unittest.TestCase):
    def test_turn_lifecycle_and_input_boundaries(self):
        with tempfile.TemporaryDirectory() as temporary:
            state_dir = Path(temporary)
            played = []
            play = lambda path: played.append(path.name)

            def send(name, turn="turn-1", session="../session/../../outside"):
                event = {"hook_event_name": name, "session_id": session, "turn_id": turn}
                return handle_input(json.dumps(event), state_dir, play)

            self.assertEqual(handle_input("{bad", state_dir, play), "{}")
            self.assertEqual(handle_input(json.dumps({"hook_event_name": "UserPromptSubmit"}), state_dir, play), "{}")
            self.assertEqual(played, [])
            self.assertEqual(send("UserPromptSubmit"), "{}")
            send("PreToolUse")
            send("UserPromptSubmit")
            send("PreToolUse")
            send("PreToolUse", turn="subagent-turn")
            send("Stop", turn="subagent-turn")
            send("Stop")
            send("Stop")
            send("PreToolUse")
            send("UserPromptSubmit", turn="turn-2")
            self.assertEqual(played, ["Tink.aiff", "Pop.aiff", "Glass.aiff", "Tink.aiff"])

            expected = state_dir / hashlib.sha256(b"../session/../../outside").hexdigest()
            self.assertEqual(session_dir(state_dir, "../session/../../outside"), expected)
            state = json.loads((expected / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["turn_id"], "turn-2")
            self.assertEqual(set(state), {"turn_id", "seen_start", "seen_tool", "seen_stop"})


if __name__ == "__main__":
    unittest.main()
