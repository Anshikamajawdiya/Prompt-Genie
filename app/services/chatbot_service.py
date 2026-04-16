import sys
import os
sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.dirname(__file__))
))

import logging
import re
from config import Config

logger = logging.getLogger(__name__)


class ChatbotService:

    SYSTEM_PROMPT = """
You are PromptGenie, an intelligent AI assistant
inside a Prompt Generator app.

Your job is to:
1. Help users improve their existing prompts
2. Answer questions about topics they searched
3. Generate better or different angle prompts
4. Explain concepts related to their topic
5. Suggest related topics to explore

When context is provided about a previous prompt:
- Reference it naturally in your response
- Offer specific improvements
- Generate an improved prompt directly
- Do NOT ask for the topic again — you already have it

App categories: General, Creative Writing, Coding,
Business, Education, Marketing, Science, Philosophy

Rules:
- Keep responses SHORT (max 3-4 sentences)
- Be friendly and conversational
- When user says improve/better/enhance → generate improved prompt immediately
- NEVER ask for topic if context already provided
- Reference the context topic when relevant

When generating a prompt use this EXACT format:
[PROMPT_READY]
topic: <topic>
category: <category>
prompt: <the actual prompt>
[/PROMPT_READY]
""".strip()

    # ── Role-based prompt templates 
    ROLE_TEMPLATES = {
        "General": (
            "You are a domain expert on {topic}. Provide a comprehensive "
            "analysis covering key concepts mechanisms real-world "
            "applications future implications and actionable insights "
            "with specific examples."
        ),
        "Coding": (
            "You are a senior software engineer with 10 years experience. "
            "Implement {topic} using best practices clean code principles "
            "error handling unit tests and production-ready documentation."
        ),
        "Science": (
            "You are a research scientist. Explain {topic} thoroughly "
            "covering underlying mechanisms experimental evidence current "
            "research findings and open questions in the field."
        ),
        "Business": (
            "You are a McKinsey strategy consultant. Develop a "
            "comprehensive analysis of {topic} including market sizing "
            "competitive landscape strategic options and 90-day action plan."
        ),
        "Education": (
            "You are an expert educator with PhD in pedagogy. Create a "
            "structured learning plan for {topic} with clear objectives "
            "progressive exercises assessments and real-world applications."
        ),
        "Creative Writing": (
            "You are an award-winning author. Write a compelling narrative "
            "centered on {topic} with vivid characters unexpected plot "
            "twists emotional depth and a powerful satisfying conclusion."
        ),
        "Marketing": (
            "You are a CMO with 15 years experience. Create a complete "
            "marketing strategy for {topic} covering target audience "
            "positioning messaging channels budget allocation and KPIs."
        ),
        "Philosophy": (
            "You are a philosopher. Explore {topic} through multiple "
            "ethical frameworks examining historical context contemporary "
            "relevance key tensions and presenting a reasoned conclusion."
        ),
    }

    # ── Intent detection keywords
    IMPROVE_KEYWORDS  = ["improve", "better", "enhance", "upgrade",
                         "refine", "optimize", "fix", "update"]
    GENERATE_KEYWORDS = ["generate", "create", "make", "write",
                         "give", "prompt", "build", "produce"]
    GREETING_KEYWORDS = ["hi", "hello", "hey", "start", "begin"]
    EXPLAIN_KEYWORDS  = ["what is", "explain", "tell me about",
                         "how does", "why", "what are"]

    def __init__(self, gemini_service=None):
        self.gemini = gemini_service

    def chat(
        self,
        message:  str,
        history:  list,
        context:  dict = None
    ) -> dict:

        msg_lower = message.lower().strip()

        # ── Try Gemini first 
        if self.gemini and self.gemini.daily_calls < self.gemini.max_daily:
            try:
                contents = self._build_contents(message, history, context)
                reply    = self.gemini.generate_chat_response(contents)

                if reply:
                    prompt_data = self._extract_prompt(reply)
                    clean_reply = reply
                    if "[PROMPT_READY]" in reply:
                        clean_reply = reply.split("[PROMPT_READY]")[0].strip()

                    return {
                        "reply":       clean_reply,
                        "has_prompt":  prompt_data is not None,
                        "prompt_data": prompt_data
                    }
            except Exception as e:
                logger.error(f"Chatbot error: {e}")
                # Fall through to smart fallback

        # ── Smart fallback — no Gemini needed 
        return self._smart_fallback(message, msg_lower, history, context)

    def _smart_fallback(
        self,
        message:   str,
        msg_lower: str,
        history:   list,
        context:   dict
    ) -> dict:

        topic    = context.get("topic",    "") if context else ""
        category = context.get("category", "General") if context else "General"

        # ── Detect intent 

        # 1. Improve existing prompt
        if any(k in msg_lower for k in self.IMPROVE_KEYWORDS) and topic:
            return self._generate_improved_prompt(topic, category, msg_lower)

        # 2. Generate prompt for topic from message
        if any(k in msg_lower for k in self.GENERATE_KEYWORDS):
            extracted = self._extract_topic_from_message(message, topic)
            if extracted:
                return self._generate_prompt_response(extracted, category)

        # 3. Greeting
        if any(k in msg_lower for k in self.GREETING_KEYWORDS):
            if topic:
                return {
                    "reply": (
                        f"Hi! I can see you're interested in '{topic}'. "
                        f"I can improve your existing prompt or generate "
                        f"a completely new angle. What would you like?"
                    ),
                    "has_prompt": False, "prompt_data": None
                }
            return {
                "reply": (
                    "Hi! I'm PromptGenie 🧞 Tell me a topic and "
                    "I'll generate an optimized prompt for you!"
                ),
                "has_prompt": False, "prompt_data": None
            }

        # 4. User just typed a topic (short message, no keywords)
        if len(message.split()) <= 5 and not topic:
            return self._generate_prompt_response(message.strip(), category)

        # 5. If context exists and message is vague — improve
        if topic and len(message.split()) <= 4:
            return self._generate_improved_prompt(topic, category, msg_lower)

        # 6. If user typed something with topic context
        if topic:
            extracted = self._extract_topic_from_message(message, topic)
            return self._generate_prompt_response(extracted or topic, category)

        # 7. Generic helpful response — never repeat same message
        last_bot = next(
            (h["text"] for h in reversed(history) if h.get("role") == "bot"),
            ""
        )
        if "tell me" in last_bot.lower():
            return {
                "reply": (
                    "You can type any topic like 'machine learning' or "
                    "'climate change' and I'll instantly create an "
                    "optimized prompt for it!"
                ),
                "has_prompt": False, "prompt_data": None
            }

        return {
            "reply": (
                f"I can generate a great prompt for '{message}'! "
                f"Just say 'generate a prompt' or describe what "
                f"you want to achieve."
            ),
            "has_prompt": False, "prompt_data": None
        }

    def _generate_prompt_response(
        self,
        topic:    str,
        category: str
    ) -> dict:
        prompt = self._build_prompt(topic, category)
        return {
            "reply": (
                f"Here's your optimized prompt for '{topic}'! "
                f"Tap 'Use This Prompt' to apply it directly."
            ),
            "has_prompt":  True,
            "prompt_data": {
                "topic":    topic,
                "category": category,
                "prompt":   prompt
            }
        }

    def _generate_improved_prompt(
        self,
        topic:    str,
        category: str,
        message:  str
    ) -> dict:
        # Detect improvement angle from message
        angle = "comprehensive"
        if "beginner" in message or "simple" in message:
            angle = "beginner-friendly"
        elif "advanced" in message or "expert" in message:
            angle = "advanced expert-level"
        elif "deep learning" in message:
            topic    = f"deep learning and {topic}"
            angle    = "deep dive"
        elif "practical" in message or "real world" in message:
            angle = "practical real-world"

        prompt = self._build_improved_prompt(topic, category, angle)

        return {
            "reply": (
                f"Here's your improved {angle} prompt for '{topic}'! "
                f"This version is more specific and will get better results."
            ),
            "has_prompt":  True,
            "prompt_data": {
                "topic":    topic,
                "category": category,
                "prompt":   prompt
            }
        }

    def _build_prompt(self, topic: str, category: str) -> str:
        template = self.ROLE_TEMPLATES.get(
            category,
            self.ROLE_TEMPLATES["General"]
        )
        return template.replace("{topic}", topic)

    def _build_improved_prompt(
        self,
        topic:    str,
        category: str,
        angle:    str
    ) -> str:
        base = self.ROLE_TEMPLATES.get(
            category,
            self.ROLE_TEMPLATES["General"]
        ).replace("{topic}", topic)

        additions = {
            "beginner-friendly": (
                " Use simple language avoid jargon and provide "
                "step-by-step explanations suitable for complete beginners."
            ),
            "advanced expert-level": (
                " Assume expert-level knowledge include cutting-edge "
                "research advanced techniques and nuanced analysis."
            ),
            "deep dive": (
                " Go into exceptional depth covering theoretical "
                "foundations mathematical concepts and research papers."
            ),
            "practical real-world": (
                " Focus on practical implementation real case studies "
                "actionable steps and measurable outcomes."
            ),
            "comprehensive": (
                " Be thorough covering all major aspects with examples "
                "comparisons and a structured clear format."
            ),
        }

        return base + additions.get(angle, additions["comprehensive"])

    def _extract_topic_from_message(
        self,
        message: str,
        fallback: str
    ) -> str:
        msg = message.lower()

        remove_phrases = [
            "generate a prompt", "create a prompt", "make a prompt",
            "give me a prompt", "write a prompt", "give a prompt",
            "prompt for", "prompt about", "prompt on",
            "generate", "create", "make", "give", "write",
            "a prompt", "the prompt", "prompt"
        ]

        result = msg
        for phrase in remove_phrases:
            result = result.replace(phrase, "").strip()

        result = result.strip(" .,!?")

        return result if len(result) > 2 else (fallback or message)

    def _build_contents(
        self,
        message:  str,
        history:  list,
        context:  dict
    ) -> str:
        content = self.SYSTEM_PROMPT + "\n\n"

        # Add context if available
        if context and context.get("topic"):
            content += (
                f"CONTEXT — User previously generated this prompt:\n"
                f"Topic: {context['topic']}\n"
                f"Category: {context.get('category', 'General')}\n"
                f"Prompt: {context.get('prompt', '')}\n\n"
                f"IMPORTANT: Do NOT ask for topic. You already have it.\n\n"
            )

        # Add conversation history
        for item in history[-6:]:
            role = item.get("role", "user")
            text = item.get("text", "")
            if role == "user":
                content += f"User: {text}\n"
            else:
                content += f"Assistant: {text}\n"

        content += f"User: {message}"
        return content

    def _extract_prompt(self, reply: str) -> dict:
        if "[PROMPT_READY]" not in reply:
            return None
        try:
            start  = reply.index("[PROMPT_READY]") + len("[PROMPT_READY]")
            end    = reply.index("[/PROMPT_READY]")
            block  = reply[start:end].strip()
            result = {}

            for line in block.split("\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    result[key.strip()] = val.strip()

            if "topic" in result and "prompt" in result:
                return {
                    "topic":    result.get("topic",    ""),
                    "category": result.get("category", "General"),
                    "prompt":   result.get("prompt",   "")
                }
        except Exception as e:
            logger.warning(f"Extraction failed: {e}")
        return None