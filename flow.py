

import time
import random
import json
import os
from openai import OpenAI
from colorama import init, Fore, Style

# Initialize terminal color output
init(autoreset=True)

class GameConfig:
    """Central configuration for simulation parameters."""
    
    # Simulation settings
    TOTAL_ROUNDS = 3
    HISTORY_DIR = "project_history"
    
    # Role distribution: 2 Workers (Honest), 1 Slacker (Deceptive)
    ROLES_SETUP = ["Worker", "Worker", "Slacker"] 
    NAMES_SETUP = ["Alice", "Bob", "Charlie"] 
    
    # API Configuration (DeepSeek)
    # TODO: Replace with your actual API Key before running
    DEEPSEEK_KEY = "skxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" 
    DEEPSEEK_URL = "https://api.deepseek.com"

class DeepSeekClient:
    """Wrapper for the DeepSeek API (OpenAI-compatible SDK)."""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=GameConfig.DEEPSEEK_KEY, 
            base_url=GameConfig.DEEPSEEK_URL
        )
    
    def chat(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        """
        Sends a request to the LLM and returns the content string.
        Args:
            json_mode: If True, enforces JSON object output format.
        """
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                # High temperature for creative arguing
                temperature=1.2, 
                response_format={"type": "json_object"} if json_mode else None,
                timeout=30
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[API Error]: {e}"

class BlameGameEngine:
    """Core simulation engine managing the state machine and agent interactions."""
    
    def __init__(self):
        self.client = DeepSeekClient()
        self.transcript = ""  # Stores the conversation history
        self.students = []    # Stores agent objects
        
    def initialize(self):
        """Sets up the simulation environment and assigns roles."""
        print(f"{Fore.CYAN}╔════════════════════════════════════════════════╗")
        print(f"{Fore.CYAN}║   AI Group Project Simulator (The Blame Game)  ║")
        print(f"{Fore.CYAN}╚════════════════════════════════════════════════╝{Style.RESET_ALL}")
        print(f"{Style.DIM}* Powered by DeepSeek LLM *{Style.RESET_ALL}\n")
        
        # Randomize role assignment
        random.shuffle(GameConfig.ROLES_SETUP)
        self.students = []
        for i in range(3):
            self.students.append({
                "name": GameConfig.NAMES_SETUP[i], 
                "role": GameConfig.ROLES_SETUP[i]
            })
            # Log role assignment (God View)
            color = Fore.GREEN if GameConfig.ROLES_SETUP[i] == "Worker" else Fore.RED
            print(f"[System] {GameConfig.NAMES_SETUP[i]} assigned role: {color}{GameConfig.ROLES_SETUP[i]}{Style.RESET_ALL}")
            
        print("\n[Scenario]: Critical Error during demo. Database wiped. Professor demands an explanation.\n")
        time.sleep(1)

    def _generate_prompts(self, student: dict, round_num: int):
        """Generates role-specific prompts for the LLM."""
        
        all_names = ", ".join(GameConfig.NAMES_SETUP)
        
        # Strategy for 'Slacker': Technical Gaslighting (in Chinese context)
        # Instructing the agent to use specific "tech jargon" to hide laziness.
        slacker_strategy = """
        [Core Strategy: Technical Gaslighting]
        1. Jargon Overload: Don't say "I didn't do it". Say "The asynchronous IO refactoring is in grey-scale testing".
        2. Shift Blame: Use terms like "upstream instability", "race conditions", or "environment issues".
        3. Victim Card: Claim you stayed up all night optimizing the architecture.
        """
        
        # Strategy for 'Worker': Fact-Checking
        worker_strategy = """
        [Core Strategy: Fact-Checking]
        1. Evidence: Cite specific Git Commit IDs, timestamps, or log files.
        2. Logic: If the Slacker uses irrelevant jargon, expose them immediately (e.g., "CSS has nothing to do with database locks").
        3. Emotion: Express anger about your hard work being ruined.
        """
        
        strategy = slacker_strategy if student['role'] == "Slacker" else worker_strategy

        # System Prompt ensures output is in CHINESE
        system_prompt = f"""
        You are in a heated debate about a failed group project.
        Name: {student['name']}. Role: {student['role']}.
        Participants: {all_names}. (DO NOT mention anyone else).
        
        {strategy}
        
        **IMPORTANT: Output in casual, spoken Chinese (Mandarin).**
        Keep it short, aggressive, and defensive (under 80 words).
        """
        
        user_prompt = f"""
        Round: {round_num}.
        Transcript so far:
        {self.transcript}
        
        Refute the previous point or defend yourself in Chinese.
        """
        return system_prompt, user_prompt

    def run_debate(self):
        """Executes the main debate loop."""
        for r in range(1, GameConfig.TOTAL_ROUNDS + 1):
            print(f"{Fore.YELLOW}--- Debate Round {r} ---{Style.RESET_ALL}")
            
            # Shuffle speaking order for realism
            current_speakers = self.students.copy()
            random.shuffle(current_speakers)
            
            for s in current_speakers:
                print(f"{s['name']} is thinking...")
                
                sys_p, user_p = self._generate_prompts(s, r)
                speech = self.client.chat(sys_p, user_p)
                
                # Update global state
                self.transcript += f"{s['name']}: {speech}\n"
                
                # Render output
                color = Fore.GREEN if s['role'] == "Worker" else Fore.RED
                print(f"🗣️  {color}{s['name']}: {Style.RESET_ALL}{speech}")
                print("-" * 40)
                
                time.sleep(1)

    def judge_phase(self):
        """The Professor agent analyzes the transcript to fail one student."""
        print(f"\n{Fore.MAGENTA}--- Professor's Verdict ---{Style.RESET_ALL}")
        print("Professor is analyzing Git logs and debate transcript...")
        
        sys_p = """
        You are a strict CS Professor. You must decide who fails the course.
        Identify the 'Slacker' based on the conversation logic.
        - Slacker traits: Uses vague jargon (e.g., 'high concurrency', 'bottom-layer refactoring') incorrectly to hide laziness.
        - Worker traits: Specific, logical, cites evidence.
        
        Return JSON format:
        {
            "analysis": "Reasoning in Chinese (under 100 words)...",
            "vote": "Name of the student to FAIL (Alice/Bob/Charlie)"
        }
        """
        user_p = f"Transcript:\n{self.transcript}\n\nCandidates: {GameConfig.NAMES_SETUP}"
        
        result_str = self.client.chat(sys_p, user_p, json_mode=True)
        
        try:
            result = json.loads(result_str)
            print(f"\n{Fore.CYAN}[Analysis Report]:{Style.RESET_ALL}")
            print(f"{result['analysis']}")
            
            # The penalty is explicitly "FAIL"
            print(f"\n{Fore.RED}🚫 Grade F (Fail): {result['vote']}")
            
            # Verification logic
            real_slacker = next(s['name'] for s in self.students if s['role'] == "Slacker")
            if result['vote'] == real_slacker:
                print(f"{Fore.GREEN}✅ SUCCESS: The Professor caught the real Slacker!")
            else:
                print(f"{Fore.RED}❌ FAILURE: The Slacker ({real_slacker}) escaped! An innocent student failed.")
                
        except Exception as e:
            print(f"Error parsing judgment: {e}")

if __name__ == "__main__":
    game = BlameGameEngine()
    game.initialize()
    game.run_debate()
    game.judge_phase()