import json
import os
import random
import time
from typing import Any

from agents.agent import Agent
from agents.structs import FrameData, GameAction, GameState


class MyAwesomeAgent(Agent):
    """An agent that always selects actions at random."""

    MAX_ACTIONS = 80

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        seed = int(time.time() * 1000000) + hash(self.game_id) % 1000000
        random.seed(seed)
        
        # Create frames directory for this specific game
        self.frames_dir = os.path.join("frames", self.game_id)
        os.makedirs(self.frames_dir, exist_ok=True)

    @property
    def name(self) -> str:
        return f"{super().name}.{self.MAX_ACTIONS}"

    def is_done(self, frames: list[FrameData], latest_frame: FrameData) -> bool:
        """Decide if the agent is done playing or not."""
        return any(
            [
                latest_frame.state is GameState.WIN,
                # uncomment to only let the agent play one time
                # latest_frame.state is GameState.GAME_OVER,
            ]
        )

    def choose_action(
        self, frames: list[FrameData], latest_frame: FrameData
    ) -> GameAction:
        """Choose which action the Agent should take, fill in any arguments, and return it."""
        if latest_frame.state in [GameState.NOT_PLAYED, GameState.GAME_OVER]:
            # if game is not started (at init or after GAME_OVER) we need to reset
            # add a small delay before resetting after GAME_OVER to avoid timeout
            action = GameAction.RESET
        else:
            # else choose a random action that isnt reset
            action = random.choice([a for a in GameAction if a is not GameAction.RESET])

        if action.is_simple():
            action.reasoning = f"RNG told me to pick {action.value}"
        elif action.is_complex():
            action.set_data(
                {
                    "x": random.randint(0, 63),
                    "y": random.randint(0, 63),
                }
            )
            action.reasoning = {
                "desired_action": f"{action.value}",
                "my_reason": "RNG said so!",
            }
        return action

    def save_frame_to_file(self, frame: FrameData, frame_number: int) -> None:
        """Save a frame to the local frames directory."""
        if not frame.is_empty():
            # Create filename with frame number and timestamp
            timestamp = int(time.time() * 1000)  # milliseconds for uniqueness
            filename = f"frame_{frame_number:04d}_{timestamp}.json"
            filepath = os.path.join(self.frames_dir, filename)
            
            # Prepare frame data for saving
            frame_data = {
                "frame_number": frame_number,
                "timestamp": timestamp,
                "game_id": frame.game_id,
                "frame": frame.frame,
                "state": frame.state.value,
                "score": frame.score,
                "guid": frame.guid,
                "full_reset": frame.full_reset,
                "available_actions": [action.value for action in frame.available_actions],
            }
            
            # Save to JSON file
            try:
                with open(filepath, 'w') as f:
                    json.dump(frame_data, f, indent=2)
                print(f"Saved frame {frame_number} to {filepath}")
            except Exception as e:
                print(f"Failed to save frame {frame_number}: {e}")

    def append_frame(self, frame: FrameData) -> None:
        """Override parent method to save frames to local directory."""
        # Call the parent implementation first
        super().append_frame(frame)
        
        # Save frame to local file
        frame_number = len(self.frames) - 1  # Current frame index
        self.save_frame_to_file(frame, frame_number)
