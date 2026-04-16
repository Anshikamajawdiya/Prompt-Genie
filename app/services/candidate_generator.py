import random
from typing import List, Dict
from dataclasses import dataclass
from enum import Enum


class ToneStyle(Enum):
    """Different tone variations for prompts"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    SOCRATIC = "socratic"
    DETAILED = "detailed"
    CONCISE = "concise"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"


@dataclass
class PromptModifier:
    """Modifiers to customize prompt generation"""
    tone: ToneStyle = ToneStyle.PROFESSIONAL
    depth: str = "comprehensive"  # "brief", "moderate", "comprehensive", "expert-level"
    audience: str = "general"  # "general", "beginner", "intermediate", "expert"
    format: str = "narrative"  # "narrative", "structured", "bullet-points", "dialogue"
    include_examples: bool = True
    include_questions: bool = False
    include_limitations: bool = False


class CandidateGenerator:
    """
    Advanced prompt generator with dynamic variation and customization.
    Generates unique prompts every time while maintaining category relevance.
    """

    # Base templates with placeholders for dynamic variation
    BASE_TEMPLATES = {
        "General": {
            "roles": [
                "expert consultant", "subject matter specialist", "domain authority",
                "research director", "knowledge architect", "analytical thinker"
            ],
            "tasks": [
                "provide a comprehensive analysis covering key concepts, real-world applications, and future implications",
                "explore the fundamental principles, interconnections, and practical significance",
                "break down systematically with historical context, current landscape, and emerging trends",
                "deliver an in-depth examination including theory, practice, challenges, and opportunities",
                "synthesize knowledge across dimensions covering depth, breadth, and applicability",
            ],
            "additions": [
                "with specific, illustrative examples",
                "including case studies and real-world scenarios",
                "supported by evidence and expert insights",
                "addressing common misconceptions",
                "examining implications for stakeholders",
            ]
        },
        "Creative Writing": {
            "roles": [
                "award-winning novelist", "narrative architect", "storytelling master",
                "character development expert", "world-building specialist", "creative visionary"
            ],
            "tasks": [
                "craft a compelling narrative where {topic} becomes the heart of an unforgettable story",
                "weave an immersive tale exploring {topic} through multiple perspectives and emotional arcs",
                "create an engaging story that uses {topic} to explore deeper human truths",
                "construct a narrative where {topic} drives character development and plot evolution",
                "develop a richly detailed story where {topic} intersects with conflict and discovery",
            ],
            "additions": [
                "with vivid sensory details and authentic dialogue",
                "featuring complex characters with compelling motivations",
                "incorporating unexpected twists and emotional resonance",
                "with world-building that feels lived-in and authentic",
                "ending with a revelation that reframes the entire narrative",
            ]
        },
        "Coding": {
            "roles": [
                "principal software engineer", "architecture expert", "code quality advocate",
                "systems designer", "performance specialist", "technical lead"
            ],
            "tasks": [
                "implement {topic} following SOLID principles and industry best practices",
                "design a robust solution for {topic} with comprehensive error handling",
                "create production-grade code for {topic} emphasizing scalability and maintainability",
                "architect a clean, well-documented implementation of {topic}",
                "develop an optimized solution for {topic} with thorough test coverage",
            ],
            "additions": [
                "with clear, self-documenting code",
                "including unit tests and integration tests",
                "addressing edge cases and error scenarios",
                "optimized for performance and memory efficiency",
                "with comprehensive documentation and usage examples",
            ]
        },
        "Business": {
            "roles": [
                "strategic business consultant", "market analyst", "growth strategist",
                "executive advisor", "competitive intelligence specialist", "investment evaluator"
            ],
            "tasks": [
                "develop a comprehensive business strategy for {topic} with market positioning",
                "create a detailed action plan for {topic} including financial modeling",
                "analyze {topic} from business, market, and competitive perspectives",
                "formulate a growth strategy for {topic} addressing risks and opportunities",
                "build a strategic framework for {topic} with measurable outcomes",
            ],
            "additions": [
                "with SWOT analysis and market sizing",
                "including revenue projections and financial metrics",
                "addressing competitive landscape and differentiation",
                "with clear KPIs and execution milestones",
                "supported by market research and trend analysis",
            ]
        },
        "Education": {
            "roles": [
                "curriculum designer", "learning specialist", "educational innovator",
                "subject matter tutor", "instructional strategist", "pedagogical expert"
            ],
            "tasks": [
                "create an engaging learning experience around {topic} suited to diverse learners",
                "design a structured curriculum for teaching {topic} with clear progression",
                "develop a lesson framework for {topic} emphasizing active and experiential learning",
                "construct a learning pathway for {topic} with varied assessment methods",
                "build an educational program for {topic} that balances theory and practice",
            ],
            "additions": [
                "with clear learning objectives and outcomes",
                "including interactive activities and hands-on exercises",
                "with formative and summative assessments",
                "addressing multiple learning styles and abilities",
                "incorporating real-world applications and relevance",
            ]
        },
        "Marketing": {
            "roles": [
                "chief marketing officer", "brand strategist", "growth hacker",
                "campaign director", "audience psychologist", "communications expert"
            ],
            "tasks": [
                "create a multi-channel marketing strategy for {topic} driving awareness and conversion",
                "develop compelling messaging for {topic} that resonates with target audiences",
                "design a growth campaign for {topic} with clear customer acquisition funnel",
                "craft a brand narrative for {topic} across digital and traditional channels",
                "build a viral and referral strategy for {topic} maximizing reach and engagement",
            ],
            "additions": [
                "with detailed audience segmentation and personas",
                "including channel strategies and content calendars",
                "with conversion optimization and retention mechanics",
                "addressing brand positioning and unique value proposition",
                "with analytics framework and success metrics",
            ]
        },
        "Science": {
            "roles": [
                "research scientist", "data analyst", "science communicator",
                "experimental designer", "field expert", "evidence evaluator"
            ],
            "tasks": [
                "explain the mechanisms and evidence behind {topic} with scientific rigor",
                "analyze {topic} from current research perspective identifying cutting-edge insights",
                "break down the science of {topic} for varied audiences while maintaining accuracy",
                "synthesize {topic} across disciplines showing interconnections and implications",
                "design a research framework investigating {topic} with robust methodology",
            ],
            "additions": [
                "with current peer-reviewed research and citations",
                "addressing open questions and research frontiers",
                "explaining both consensus and contested areas",
                "with clear distinction between evidence and speculation",
                "including methodology and statistical considerations",
            ]
        },
        "Philosophy": {
            "roles": [
                "philosopher and critical thinker", "ethical analyst", "idea synthesizer",
                "logical reasoner", "historical contextualist", "systems thinker"
            ],
            "tasks": [
                "explore {topic} through multiple philosophical lenses revealing tensions and insights",
                "examine the deepest questions raised by {topic} with logical rigor",
                "analyze {topic} across historical and contemporary philosophical traditions",
                "construct a reasoned argument about {topic} acknowledging counterarguments",
                "investigate {topic} through ethics, epistemology, and metaphysics",
            ],
            "additions": [
                "with references to major philosophical traditions",
                "exploring ethical implications and paradoxes",
                "addressing fundamental assumptions and definitions",
                "considering multiple valid perspectives fairly",
                "with logical argumentation and evidence of deep thinking",
            ]
        },
    }

    # Tone-specific modifiers
    TONE_MODIFIERS = {
        ToneStyle.PROFESSIONAL: "in a professional and authoritative manner",
        ToneStyle.CASUAL: "in an approachable and conversational way",
        ToneStyle.SOCRATIC: "using the Socratic method to guide thinking",
        ToneStyle.DETAILED: "with comprehensive detail and nuance",
        ToneStyle.CONCISE: "with clarity and brevity",
        ToneStyle.CREATIVE: "with creative flair and imaginative approaches",
        ToneStyle.ANALYTICAL: "with rigorous analytical thinking",
    }

    # Audience-specific context
    AUDIENCE_CONTEXT = {
        "beginner": "suitable for someone new to the topic",
        "intermediate": "for someone with foundational knowledge",
        "expert": "at the level of deep technical expertise",
        "general": "accessible to a broad audience",
    }

    # Format-specific instructions
    FORMAT_INSTRUCTIONS = {
        "narrative": "presented as a flowing narrative",
        "structured": "organized with clear headings and sections",
        "bullet-points": "using concise bullet points and lists",
        "dialogue": "presented as a dialogue or conversation",
        "step-by-step": "broken into clear, sequential steps",
    }

    def __init__(self, seed: int = None):
        """Initialize generator with optional seed for reproducibility"""
        if seed is not None:
            random.seed(seed)

    def generate_candidates(
        self,
        topic: str,
        category: str,
        num_candidates: int = 5,
        modifier: PromptModifier = None,
        randomize: bool = True,
    ) -> List[str]:
        """
        Generate multiple unique prompt candidates.

        Args:
            topic: The topic to create prompts for
            category: The category (e.g., "General", "Coding", "Marketing")
            num_candidates: Number of unique prompts to generate
            modifier: PromptModifier object for customization (optional)
            randomize: Whether to randomize component selection

        Returns:
            List of unique, varied prompts
        """
        if modifier is None:
            modifier = PromptModifier()

        if category not in self.BASE_TEMPLATES:
            category = "General"

        candidates = []
        template_data = self.BASE_TEMPLATES[category]

        for _ in range(num_candidates):
            prompt = self._construct_dynamic_prompt(
                topic=topic,
                template_data=template_data,
                modifier=modifier,
                randomize=randomize,
            )
            if prompt not in candidates:  # Avoid duplicates
                candidates.append(prompt)

        return candidates

    def _construct_dynamic_prompt(
        self,
        topic: str,
        template_data: Dict,
        modifier: PromptModifier,
        randomize: bool,
    ) -> str:
        """Construct a single dynamic prompt from components"""

        # Select components
        role = random.choice(template_data["roles"]) if randomize else template_data["roles"][0]
        task = random.choice(template_data["tasks"]) if randomize else template_data["tasks"][0]
        addition = random.choice(template_data["additions"]) if randomize else template_data["additions"][0]

        # Build base prompt
        base = f"You are a {role}. {task.capitalize()}"

        # Add topic substitution
        base = base.replace("{topic}", f"'{topic}'")

        # Add tone modifier
        tone_phrase = self.TONE_MODIFIERS.get(modifier.tone, "")
        if tone_phrase:
            base += f" {tone_phrase}."
        else:
            base += "."

        # Add audience context if not general
        if modifier.audience != "general":
            audience_context = self.AUDIENCE_CONTEXT[modifier.audience]
            base += f" Keep in mind your audience is {audience_context}."

        # Add format instruction
        if modifier.format != "narrative":
            format_instruction = self.FORMAT_INSTRUCTIONS.get(modifier.format, "")
            base += f" Present your response {format_instruction}."

        # Add additional requirements
        extras = []
        if modifier.include_examples:
            extras.append("Include specific, illustrative examples")
        if modifier.include_questions:
            extras.append("Pose thought-provoking questions")
        if modifier.include_limitations:
            extras.append("Acknowledge limitations and uncertainties")

        if extras:
            base += f" {', and '.join(extras)}."

        # Add the main addition
        base += f" {addition.capitalize()}."

        return base

    def generate_single_prompt(
        self,
        topic: str,
        category: str,
        modifier: PromptModifier = None,
    ) -> str:
        """Generate a single dynamic prompt"""
        candidates = self.generate_candidates(
            topic=topic,
            category=category,
            num_candidates=1,
            modifier=modifier,
            randomize=True,
        )
        return candidates[0]

    def get_categories(self) -> List[str]:
        """Return available categories"""
        return list(self.BASE_TEMPLATES.keys())


# Example usage and demonstrations
if __name__ == "__main__":
    generator = CandidateGenerator()

    print("=" * 80)
    print("ENHANCED CANDIDATE GENERATOR DEMO")
    print("=" * 80)

    # Example 1: Basic usage - multiple varied prompts
    print("\n1. MULTIPLE VARIED PROMPTS FOR 'MACHINE LEARNING' (General Category)")
    print("-" * 80)
    topic = "Machine Learning"
    category = "General"

    prompts = generator.generate_candidates(
        topic=topic,
        category=category,
        num_candidates=3,
    )

    for i, prompt in enumerate(prompts, 1):
        print(f"\nPrompt {i}:")
        print(f"{prompt}\n")

    # Example 2: Customized prompts with modifier
    print("\n2. CUSTOMIZED PROMPTS FOR 'API DESIGN' (Coding Category)")
    print("-" * 80)
    custom_modifier = PromptModifier(
        tone=ToneStyle.DETAILED,
        audience="expert",
        format="structured",
        include_examples=True,
        include_questions=False,
    )

    prompts = generator.generate_candidates(
        topic="API Design",
        category="Coding",
        num_candidates=2,
        modifier=custom_modifier,
    )

    for i, prompt in enumerate(prompts, 1):
        print(f"\nPrompt {i}:")
        print(f"{prompt}\n")

    # Example 3: Creative writing with casual tone
    print("\n3. CREATIVE PROMPTS FOR 'TIME TRAVEL' (Creative Writing)")
    print("-" * 80)
    creative_modifier = PromptModifier(
        tone=ToneStyle.CREATIVE,
        audience="general",
        include_questions=True,
        include_examples=False,
    )

    prompts = generator.generate_candidates(
        topic="Time Travel",
        category="Creative Writing",
        num_candidates=2,
        modifier=creative_modifier,
    )

    for i, prompt in enumerate(prompts, 1):
        print(f"\nPrompt {i}:")
        print(f"{prompt}\n")

    # Example 4: Single prompt generation
    print("\n4. SINGLE DYNAMIC PROMPT FOR 'QUANTUM COMPUTING' (Science)")
    print("-" * 80)
    science_modifier = PromptModifier(
        tone=ToneStyle.ANALYTICAL,
        include_limitations=True,
    )

    prompt = generator.generate_single_prompt(
        topic="Quantum Computing",
        category="Science",
        modifier=science_modifier,
    )
    print(f"{prompt}\n")

    # Example 5: Available categories
    print("\n5. AVAILABLE CATEGORIES")
    print("-" * 80)
    categories = generator.get_categories()
    for cat in categories:
        print(f"  • {cat}")