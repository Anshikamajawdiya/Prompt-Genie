import random
import logging

logger = logging.getLogger(__name__)

class FallbackService:

    FALLBACK_BANK = {
        "General": [
            "Explain {topic} in simple terms, covering its key concepts, "
            "real-world applications, and common misconceptions. "
            "Provide examples to illustrate each point.",

            "Provide a comprehensive overview of {topic}. Include its history, "
            "current state, future trends, and how it impacts everyday life.",
        ],
        "Creative Writing": [
            "Write a compelling short story where {topic} is the central theme. "
            "Include vivid characters, unexpected plot twists, and a satisfying conclusion.",

            "Create an immersive world-building description for a story centered "
            "on {topic}. Describe the setting, atmosphere, and the central conflict.",
        ],
        "Coding": [
            "You are an expert developer. Help me implement {topic} with clean, "
            "well-documented code. Explain your approach, handle edge cases, "
            "and suggest best practices.",

            "Review and improve my implementation of {topic}. Identify potential "
            "bugs, performance issues, and suggest modern alternatives with examples.",
        ],
        "Business": [
            "Develop a comprehensive business strategy for {topic}. Include market "
            "analysis, competitive landscape, revenue model, and a 90-day action plan.",

            "Analyze the business implications of {topic}. Cover opportunities, "
            "risks, financial considerations, and strategic recommendations.",
        ],
        "Education": [
            "Create a structured lesson plan to teach {topic} to beginners. "
            "Include learning objectives, activities, examples, and assessment methods.",

            "Explain {topic} using the Feynman technique — break it down simply "
            "enough for a 12-year-old, then gradually increase complexity.",
        ],
        "Marketing": [
            "Create a full marketing campaign for {topic}. Include target audience, "
            "key messages, channels, content ideas, and success metrics.",

            "Write compelling copy for {topic} across three formats: "
            "a social media post, an email subject line, and a landing page headline.",
        ],
        "Science": [
            "Explain the science behind {topic} in detail. Cover the underlying "
            "mechanisms, key research findings, and current open questions in the field.",

            "Design a research study to investigate {topic}. Include hypothesis, "
            "methodology, variables, controls, and how you would analyze results.",
        ],
        "Philosophy": [
            "Explore the philosophical dimensions of {topic}. Examine it through "
            "multiple ethical frameworks, identify key tensions, and present "
            "a reasoned conclusion.",

            "What are the deepest questions raised by {topic}? Explore from the "
            "perspectives of major philosophical traditions and contemporary thought.",
        ],
    }

    def generate_prompt(self, topic: str, category: str) -> str:
        logger.warning(f"Fallback used → topic='{topic}' category='{category}'")
        bank     = self.FALLBACK_BANK.get(category, self.FALLBACK_BANK["General"])
        template = random.choice(bank)
        return template.replace("{topic}", topic)