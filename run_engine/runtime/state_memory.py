import json
import os

class StateMemory:

    def __init__(self, path="run_engine/runtime/memory.json"):

        self.path = path

        self.state = {
            "tick": 0,
            "bias_history": [],
            "action_history": [],
            "loss_streak_history": []
        }

        self._load()

    def _load(self):

        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                self.state = json.load(f)

    def _save(self):

        with open(self.path, "w") as f:
            json.dump(self.state, f)

    def update(self, tick, decision, loss_streak, bias):

        self.state["tick"] = tick
        self.state["bias_history"].append(bias)
        self.state["action_history"].append(decision.get("action"))
        self.state["loss_streak_history"].append(loss_streak)

        # keep memory bounded
        self.state["bias_history"] = self.state["bias_history"][-500:]
        self.state["action_history"] = self.state["action_history"][-500:]
        self.state["loss_streak_history"] = self.state["loss_streak_history"][-500:]

        self._save()

    def get(self):

        return self.state