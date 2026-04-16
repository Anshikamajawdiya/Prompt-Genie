import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import logging
import time
from google import genai
from google.genai import types
from config import Config

logger = logging.getLogger(__name__)


class GeminiService:

    def __init__(self):
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in .env file")

        self.client         = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model          = "gemini-2.0-flash"  
        self.last_call_time = 0
        self.min_interval   = 4
        self.daily_calls    = 0
        self.max_daily      = 50

    def generate_prompt(self, topic: str, category: str) -> str:

        if self.daily_calls >= self.max_daily:
            raise Exception("Daily Gemini quota reached — using ML model")

        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)

            self._wait_rate_limit()

        system_instruction = self._build_system_instruction(category)
        user_message       = self._build_user_message(topic, category)
        full_prompt        = f"{system_instruction}\n\n{user_message}"

        logger.info(f"Calling Gemini → topic='{topic}' "
                    f"category='{category}' "
                    f"calls today={self.daily_calls}")

        try:
            response = self.client.models.generate_content(
                model    = self.model,
                contents = full_prompt,
                config   = types.GenerateContentConfig(
                    max_output_tokens = Config.GEMINI_MAX_TOKENS,
                    temperature       = Config.GEMINI_TEMPERATURE,
                )
            )

            self.last_call_time  = time.time()
            self.daily_calls    += 1

            if not response or not response.text:
                raise ValueError("Empty response from Gemini")

            return response.text.strip()

        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                logger.warning("Gemini quota exceeded — ML model will handle")
                raise Exception("Quota exceeded")
            raise e
        
    def generate_chat_response(self, contents: str) -> str:
        if self.daily_calls >= self.max_daily:
            raise Exception("Daily quota reached")

        self._wait_rate_limit()

        try:
            response = self.client.models.generate_content(
                model    = self.model,
                contents = contents,
                config   = types.GenerateContentConfig(
                    max_output_tokens = 500,
                    temperature       = 0.7,
                )
            )

            self.last_call_time  = time.time()
            self.daily_calls    += 1

            if not response or not response.text:
                raise ValueError("Empty response")

            return response.text.strip()

        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                raise Exception("Quota exceeded")
            raise e
        

    def _wait_rate_limit(self):
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)

    def _build_system_instruction(self, category: str) -> str:
        instructions = {
            "General": (
                "You are an expert prompt engineer. Create clear "
                "detailed and effective prompts that get the best "
                "results from AI models."
            ),
            "Creative Writing": (
                "You are a creative writing specialist. Craft "
                "imaginative and inspiring prompts that spark "
                "creativity and storytelling."
            ),
            "Coding": (
                "You are a software engineering expert. Generate "
                "precise technical prompts that help developers "
                "solve coding problems effectively."
            ),
            "Business": (
                "You are a business strategy consultant. Create "
                "professional prompts focused on business analysis "
                "strategy and decision-making."
            ),
            "Education": (
                "You are an educational expert. Design prompts that "
                "facilitate learning explanation and knowledge "
                "transfer effectively."
            ),
            "Marketing": (
                "You are a marketing expert. Generate compelling "
                "prompts for campaigns copywriting and brand strategy."
            ),
            "Science": (
                "You are a scientific researcher. Create analytical "
                "prompts that encourage rigorous thinking and "
                "evidence-based reasoning."
            ),
            "Philosophy": (
                "You are a philosopher. Craft thought-provoking "
                "prompts that explore deep questions ethics and "
                "critical thinking."
            ),
        }
        return instructions.get(category, instructions["General"])

    def _build_user_message(self, topic: str, category: str) -> str:
        return f"""
Generate a detailed creative and highly effective AI prompt for:

Topic: {topic}
Category: {category}

Requirements:
- Ready to use directly with any AI model
- Be specific and provide clear context
- Include necessary constraints or guidelines
- Make it engaging and goal-oriented
- Output ONLY the prompt itself no explanations

Generated Prompt:
""".strip()
