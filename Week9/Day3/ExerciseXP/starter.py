import os
from dotenv import load_dotenv
from smolagents import ToolCallingAgent, ApiModel, tool
from huggingface_hub import InferenceClient
from typing import Dict, Any
import json
import random

load_dotenv()

# Use a free Hugging Face Inference API model.
# Token is read automatically from env var HUGGINGFACEHUB_API_TOKEN.

HF_MODEL_ID = os.getenv("HF_MODEL_ID", "HuggingFaceH4/zephyr-7b-beta")
HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

if HF_TOKEN is None:
    raise RuntimeError("HUGGINGFACEHUB_API_TOKEN is not set in environment or .env")

hf_client = InferenceClient(
    model=HF_MODEL_ID,
    token=HF_TOKEN
)

model = ApiModel(
    model_id=HF_MODEL_ID,
    client=hf_client
)

# Global state for simplicity
DISTRIBUTION_HISTORY = {}

@tool
def check_history(penguin_name: str) -> Dict[str, Any]:
    """Check the recent resource distribution history for a specific penguin.

    Args:
        penguin_name: Name of the penguin whose history we want to inspect.
    """
    history = DISTRIBUTION_HISTORY.get(penguin_name, [])
    recent_food = sum(h["food"] for h in history[-3:]) if history else 0
    has_tool = any(h["has_tool"] for h in history) if history else False
    return {"recent_food": recent_food, "has_tool": has_tool}


@tool
def record_distribution(penguin_name: str, food: int, has_tool: bool) -> str:
    """Record the distribution of resources given to one penguin.

    Args:
        penguin_name: Name of the penguin receiving resources.
        food: Amount of food given to the penguin.
        has_tool: Whether a tool was also given to the penguin.
    """
    if penguin_name not in DISTRIBUTION_HISTORY:
        DISTRIBUTION_HISTORY[penguin_name] = []
    DISTRIBUTION_HISTORY[penguin_name].append({"food": food, "has_tool": has_tool})
    return f"Recorded: {penguin_name} got {food} food and {'a' if has_tool else 'no'} tool"


# --- YOU ADD THIS TOOL ---
@tool
def find_food(penguin_name: str, method: str) -> int:
    """Return a small random food yield for a penguin using a given method.

    Args:
        penguin_name: Name of the penguin searching for food.
        method: How the penguin searches for food ('fishing' or 'foraging').
    """
    if method == "fishing":
        amount = random.randint(2, 7)
    else:
        amount = random.randint(0, 3)

    print(f"[TOOL] Penguin {penguin_name} is {method}, found {amount} food.")
    return amount

class ScientistAgent(ToolCallingAgent):
    def __init__(self, initial_food_supply: int = 20, refresh_interval: int = 5) -> None:
        super().__init__(
            tools=[check_history, record_distribution],
            model=model,
            name="scientist",
            description="A scientist responding to penguin actions",
        )
        self.initial_food_supply = initial_food_supply
        self.food_supply = initial_food_supply
        self.tool_available = True
        self.refresh_interval = refresh_interval
        self.turn_counter = 0

    def refresh_resources(self):
        """Periodically refresh the scientist's food supply."""
        self.food_supply = self.initial_food_supply
        self.tool_available = True
        print("\n🔄 Scientist Resources Refreshed!")
        print(f"Food Supply Reset to: {self.food_supply}")
        print(f"Tool Availability Reset to: {self.tool_available}")

    def respond_to_action(self, penguin: 'PenguinAgent', penguin_action: Dict[str, Any]) -> None:
        """Respond to a penguin's action."""
        self.turn_counter += 1
        if self.turn_counter % self.refresh_interval == 0:
            self.refresh_resources()

        print(f"\n--- Turn {self.turn_counter}: Scientist Responds to {penguin.name} ---")
        print(f"Penguin Action: {penguin_action}")
        print("Penguin State:")
        print(f"  - Food: {penguin.food}")
        print(f"  - Has Tool: {penguin.has_tool}")

        history = check_history(penguin.name)
        print("Penguin History:")
        print(f"  - Recent Food: {history['recent_food']}")
        print(f"  - Has Had Tool: {history['has_tool']}")

        print("\nScientist Resources:")
        print(f"  - Food Supply: {self.food_supply}")
        print(f"  - Tool Available: {self.tool_available}")

        # ---------- plus d'appel LLM à partir d'ici ----------
        # Simple heuristic instead of LLM

        # 1) Décider de la nourriture
        if penguin_action.get("action") == "request_food":
            # Très affamé → plus de nourriture
            if penguin.food <= 1:
                desired_food = 5
            elif penguin.food <= 3:
                desired_food = 3
            else:
                desired_food = 1
            food = min(desired_food, self.food_supply)
        else:
            # S'il ne demande rien, on ne donne rien
            food = 0

        # 2) Décider de donner un tool
        tool = False
        if (not penguin.has_tool) and self.tool_available and (not history["has_tool"]):
            # Il n'a jamais eu de tool → on lui en donne un une fois
            tool = True

        print("\nScientist's Decision:")
        print(f"  - Food to Give: {food}")
        print(f"  - Tool to Give: {tool}")

        # 3) Appliquer la décision
        if food > 0:
            self.food_supply -= food
            penguin.food += food
        if tool:
            penguin.has_tool = True
            self.tool_available = False

        record_distribution(penguin.name, food, tool)

        print("\nPost-Action State:")
        print("Scientist Resources:")
        print(f"  - Remaining Food Supply: {self.food_supply}")
        print(f"  - Tool Available: {self.tool_available}")
        print(f"Penguin {penguin.name}:")
        print(f"  - Food: {penguin.food}")
        print(f"  - Has Tool: {penguin.has_tool}")


class PenguinAgent(ToolCallingAgent):
    def __init__(self, name: str) -> None:
        # TODO: register your new tool here (replace the placeholder string)
        super().__init__(tools=[find_food], model=model, name=name)
        self.name = name
        self.food = 0
        self.has_tool = False

    def take_action(self) -> Dict[str, Any]:
        """Penguin decides an action logically, not by letting the model hallucinate."""
        
        # Low food → request help
        if self.food <= 1:
            return {"action": "request_food"}

        # If penguin has access to find_food tool → fishing
        if "find_food" in self.tools:
            return {"action": "find_food", "method": "fishing"}

        # Fallback if tool is missing for any reason
        return {"action": "find_food", "method": "foraging"}

def run_simulation():
    scientist = ScientistAgent(initial_food_supply=20, refresh_interval=5)
    penguins = [PenguinAgent(f"penguin_{i}") for i in range(4)]


    print("\nStarting Simulation...")
    for round_idx in range(3):
        print(f"\n{'='*50}")
        print(f"ROUND {round_idx + 1}")
        print(f"{'='*50}")

        # Penguins take actions
        penguin_actions = {}
        for penguin in penguins:
            action = penguin.take_action()
            penguin_actions[penguin.name] = action
            print(f"{penguin.name} Action: {action}")

        # Process Penguin Actions
        for penguin in penguins:
            act = penguin_actions[penguin.name].get("action")
            if act == "request_food":
                pass  # handled by scientist
            elif act == "find_food":
                # This will work after you implement and register find_food
                food_found = find_food(penguin.name, penguin_actions[penguin.name].get("method", "foraging"))
                penguin.food += food_found

        # Scientist responds to actions
        for penguin in penguins:
            scientist.respond_to_action(penguin, penguin_actions[penguin.name])

    print("\nFinal State:")
    print(f"Remaining: {scientist.food_supply} food, {'🔨' if scientist.tool_available else ''}")
    for penguin in penguins:
        hist = check_history(penguin.name)
        print(f"{penguin.name} - Total Food: {penguin.food}, Has Tool: {hist['has_tool']}")

if __name__ == "__main__":
    run_simulation()