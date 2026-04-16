import csv
import random
import os

TOPICS = {
    "General": [
        "productivity", "mental health", "future of work",
        "sustainable living", "personal finance", "leadership",
        "communication skills", "time management", "creativity", "resilience",
        "emotional intelligence", "habit formation", "decision making",
        "conflict resolution", "public speaking"
    ],
    "Creative Writing": [
        "time travel", "dystopian society", "artificial intelligence",
        "lost civilization", "parallel universe", "underwater world",
        "space exploration", "virtual reality", "identity crisis", "redemption",
        "post apocalyptic world", "magic system", "unreliable narrator",
        "found family", "mystery thriller"
    ],
    "Coding": [
        "machine learning", "REST API", "binary search tree",
        "design patterns", "microservices", "blockchain",
        "neural networks", "sorting algorithms", "docker", "kubernetes",
        "graph algorithms", "recursion", "database indexing",
        "system design", "concurrency"
    ],
    "Business": [
        "marketing strategy", "product launch", "startup funding",
        "customer retention", "brand identity", "supply chain",
        "digital transformation", "team management", "pricing strategy",
        "market analysis", "business model canvas", "venture capital",
        "competitive analysis", "revenue model", "strategic planning"
    ],
    "Education": [
        "critical thinking", "online learning", "project based learning",
        "student motivation", "curriculum design", "assessment methods",
        "learning disabilities", "STEM education", "classroom management",
        "gamification", "personalized learning", "flipped classroom",
        "peer teaching", "formative assessment", "blended learning"
    ],
    "Marketing": [
        "social media campaign", "email marketing", "influencer strategy",
        "brand storytelling", "viral content", "SEO strategy",
        "content marketing", "product positioning", "customer journey",
        "growth hacking", "affiliate marketing", "video marketing",
        "community building", "referral program", "conversion optimization"
    ],
    "Science": [
        "black holes", "quantum mechanics", "DNA replication",
        "photosynthesis", "relativity theory", "nuclear fusion",
        "climate change", "evolution", "dark matter", "CRISPR",
        "stem cells", "vaccine development", "nanotechnology",
        "plate tectonics", "particle physics"
    ],
    "Philosophy": [
        "free will", "consciousness", "ethics of AI",
        "meaning of life", "moral relativism", "existentialism",
        "justice and equality", "mind body problem",
        "truth and knowledge", "digital identity",
        "social contract", "utilitarianism", "stoicism",
        "epistemology", "political philosophy"
    ]
}

HIGH_QUALITY_TEMPLATES = [
    "You are an expert in {topic}. Provide a comprehensive analysis covering key concepts mechanisms real-world applications and future implications with specific examples.",
    "Act as a specialist in {topic}. Break down this subject systematically explaining core components their relationships and practical applications in {category} context.",
    "As a domain expert, explain {topic} thoroughly including historical background current state of knowledge common misconceptions and practical significance.",
    "You are a senior professional in {category}. Analyze {topic} providing actionable insights research-backed recommendations and step-by-step implementation guidance.",
    "Act as a thought leader on {topic}. Explore multiple perspectives identify key challenges propose innovative solutions and outline measurable outcomes.",
    "You are a world-renowned expert in {topic}. Provide an authoritative deep-dive covering theoretical foundations empirical evidence practical applications and future directions.",
    "As a leading researcher in {category}, analyze {topic} with academic rigor covering methodology findings implications and areas requiring further investigation.",
    "Act as a seasoned practitioner with 20 years experience in {topic}. Share expert insights common pitfalls best practices and real-world case studies.",
]

MEDIUM_QUALITY_TEMPLATES = [
    "Explain {topic} in detail with examples and practical applications.",
    "Provide an overview of {topic} covering the main concepts and how they apply to {category}.",
    "Describe {topic} including its key features benefits and limitations.",
    "What are the most important aspects of {topic} in the context of {category}?",
    "Give a structured explanation of {topic} with clear sections and examples.",
    "Walk me through {topic} step by step covering the basics and intermediate concepts.",
    "Explain {topic} for someone with basic knowledge of {category} using clear language.",
]

LOW_QUALITY_TEMPLATES = [
    "Tell me about {topic}",
    "Explain {topic}",
    "What is {topic}?",
    "Write about {topic}",
    "Describe {topic} briefly",
    "Give me info on {topic}",
    "{topic} explanation",
    "help with {topic}",
]

def generate_score(template_type: str) -> float:
    if template_type == "high":
        return round(random.uniform(0.82, 0.98), 2)
    elif template_type == "medium":
        return round(random.uniform(0.50, 0.80), 2)
    else:
        return round(random.uniform(0.15, 0.45), 2)

def generate_dataset(output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    rows = []

    for category, topics in TOPICS.items():
        for topic in topics:
            for template in HIGH_QUALITY_TEMPLATES:
                prompt = template.replace("{topic}", topic).replace("{category}", category)
                rows.append([topic, category, prompt, generate_score("high")])

            for template in MEDIUM_QUALITY_TEMPLATES:
                prompt = template.replace("{topic}", topic).replace("{category}", category)
                rows.append([topic, category, prompt, generate_score("medium")])

            for template in LOW_QUALITY_TEMPLATES:
                prompt = template.replace("{topic}", topic).replace("{category}", category)
                rows.append([topic, category, prompt, generate_score("low")])

    random.shuffle(rows)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["topic", "category", "prompt", "quality_score"])
        writer.writerows(rows)

    print(f"Dataset generated: {len(rows)} samples → {output_path}")

if __name__ == "__main__":
    generate_dataset("dataset/prompts.csv")