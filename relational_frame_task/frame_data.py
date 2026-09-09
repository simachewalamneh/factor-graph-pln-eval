from dataclasses import dataclass
from typing import Optional
@dataclass(frozen=True)
class Frame:
    frame_id: str
    parent_id: Optional[str]  # "NONE" in the deck -- a root frame
    status: str                # active | completed | pending
    priority: str               # high | medium | low
    deliverable: str
    results: str
# Context-Frames data set I  
DATA_SET_I = [
    Frame("F1", None, "active", "high",
          "What is the time?", "The current time is 10:42 AM."),
    Frame("F2", "F1", "completed", "medium",
          "What is the time in Asia?", "Asia spans multiple time zones."),
    Frame("F3", None, "active", "high",
          "Teach me Python.", "Started with variables, data types, and basic syntax."),
    Frame("F4", "F3", "pending", "medium",
          "Teach me Python loops.", "Not started."),
    Frame("F5", "F3", "completed", "low",
          "Give me an example of a Python for loop.", "for i in range(5): print(i)"),
    Frame("F6", None, "completed", "medium",
          "Explain photosynthesis.", "Plants convert light energy into chemical energy."),
    Frame("F7", "F6", "active", "high",
          "Explain photosynthesis to a 10-year-old.", "Plants use sunlight to make their own food."),
    Frame("F8", None, "pending", "low",
          "Plan a trip to Japan.", "No itinerary generated yet."),
    Frame("F9", "F8", "active", "high",
          "Find places to visit in Tokyo.", "Tokyo Tower, Shibuya, Asakusa, and Meiji Shrine."),
    Frame("F10", "F8", "pending", "medium",
          "Create a three-day Tokyo itinerary.", "Waiting for destination preferences."),
]
# Context-Frames data set II
DATA_SET_II = [
    Frame("F11", None, "completed", "high",
          "Calculate 25 multiplied by 16.", "400"),
    Frame("F12", None, "active", "medium",
          "Help me learn machine learning.", "Outlined supervised, unsupervised, and reinforcement learning."),
    Frame("F13", "F12", "completed", "high",
          "Explain supervised learning.", "Supervised learning trains models using labeled examples."),
    Frame("F14", "F12", "active", "medium",
          "Explain neural networks.", "Introduced neurons, layers, weights, and activation functions."),
    Frame("F15", "F14", "pending", "low",
          "Give me a simple neural network example.", "No example generated yet."),
    Frame("F16", None, "completed", "low",
          "Write a short poem about rain.", "Rain taps softly against the sleeping street."),
    Frame("F17", None, "active", "high",
          "Help me build a website.", "Defined an initial HTML, CSS, and JavaScript structure."),
    Frame("F18", "F17", "completed", "medium",
          "Create the website navigation bar.", "Created a navigation bar with Home, About, and Contact links."),
    Frame("F19", "F17", "active", "high",
          "Add a login page to the website.", "Created username and password input fields."),
    Frame("F20", "F19", "pending", "high",
          "Add password validation to the login page.", "Password validation has not been implemented yet."),
]
ALL_FRAMES = DATA_SET_I + DATA_SET_II
FRAMES_BY_ID = {f.frame_id: f for f in ALL_FRAMES}

def parent_child_pairs():
    return [(f.parent_id, f.frame_id) for f in ALL_FRAMES if f.parent_id is not None]
   
