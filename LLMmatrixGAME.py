import random
from openai import OpenAI

class LLMAgent:
    def __init__(self, name, model="hermes3"):
        self.name = name
        self.model = model
        self.client = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')
        self.state = "Proposing"

    def generate_response(self, prompt, system_message):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    def propose_action(self, context):
        prompt = f"Given the context: {context}, propose an action and provide 3 justification statements."
        return self.generate_response(prompt, f"You are {self.name}. Your state is {self.state}.")

    def respond_to_action(self, action, justifications):
        prompt = f"Respond to this action: {action}\nJustifications:\n{justifications}\nProvide 3 counter-arguments."
        return self.generate_response(prompt, f"You are {self.name}. Your state is {self.state}.")

    def rebut_arguments(self, counter_arguments):
        prompt = f"Rebut these counter-arguments:\n{counter_arguments}\nProvide 2 rebuttals."
        return self.generate_response(prompt, f"You are {self.name}. Your state is {self.state}.")

class NeutralAdjudicator:
    def __init__(self, model="llama2"):
        self.model = model
        self.client = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')
        self.state = "Evaluating"

    def evaluate(self, action, justifications, counter_arguments, rebuttals):
        prompt = f"""Evaluate this scenario:
        Action: {action}
        Justifications: {justifications}
        Counter-arguments: {counter_arguments}
        Rebuttals: {rebuttals}
        
        Assign weights to arguments, calculate a total modifier, and determine if the action succeeds or fails. Provide a brief explanation."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a neutral adjudicator. Your state is Evaluating."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

class GameManager:
    def __init__(self, scenario, agent_a, agent_b, adjudicator):
        self.scenario = scenario
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.adjudicator = adjudicator
        self.state = {"round": 0, "score_a": 0, "score_b": 0, "history": []}

    def run_round(self):
        self.state["round"] += 1
        print(f"\n--- Round {self.state['round']} ---")

        # Proposal Phase
        action = self.agent_a.propose_action(self.scenario)
        print(f"{self.agent_a.name} proposes: {action}")

        # Response Phase
        counter_arguments = self.agent_b.respond_to_action(action, "")
        print(f"{self.agent_b.name} counters: {counter_arguments}")

        # Rebuttal Phase
        rebuttals = self.agent_a.rebut_arguments(counter_arguments)
        print(f"{self.agent_a.name} rebuts: {rebuttals}")

        # Adjudication Phase
        result = self.adjudicator.evaluate(action, "", counter_arguments, rebuttals)
        print(f"Adjudicator: {result}")

        # Update state and switch roles
        self.update_state(result)
        self.agent_a, self.agent_b = self.agent_b, self.agent_a

    def update_state(self, result):
        # Simple scoring: +1 for success, -1 for failure
        if "succeeds" in result.lower():
            self.state["score_a"] += 1
        elif "fails" in result.lower():
            self.state["score_b"] += 1

        self.state["history"].append({
            "round": self.state["round"],
            "result": result
        })

    def run_game(self, num_rounds):
        for _ in range(num_rounds):
            self.run_round()

        print("\n--- Game Over ---")
        print(f"Final Score: {self.agent_a.name}: {self.state['score_a']}, {self.agent_b.name}: {self.state['score_b']}")

# Example usage
if __name__ == "__main__":
    scenario = "Debate on the impact of artificial intelligence on job markets."
    agent_a = LLMAgent("Optimist")
    agent_b = LLMAgent("Skeptic")
    adjudicator = NeutralAdjudicator()

    game = GameManager(scenario, agent_a, agent_b, adjudicator)
    game.run_game(3)  # Run for 3 rounds
