import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class RedTeamAssistant:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def generate_recon_plan(self, target_domain):
        # Everything below this line is pushed in by exactly 8 spaces
        system_prompt = (
            "You are a Senior Lead Pentester. Generate a reconnaissance plan. "
            "Output MUST be a valid JSON object with 'target' and 'phases' keys. "
            "Inside 'tasks', include: 'task_name', 'objective', 'risk_level', and 'tool_suggested'. "
            "Do not use markdown code blocks."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create a recon plan for: {target_domain}"}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            with open("working_recon_output.json", "w") as f:
                f.write(content)
                
            print("✅ Brain: Data successfully saved!")
            return content
            
        except Exception as e:
            print(f"❌ API Error: {e}")
            return "{}"

