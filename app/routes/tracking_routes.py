import sys
import os
sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.dirname(__file__))
))

from flask import Blueprint, request, jsonify
import logging
import re

logger      = logging.getLogger(__name__)
tracking_bp = Blueprint("tracking", __name__)

# ── Topic similarity groups ───────────────────────────────────────────────
TOPIC_GROUPS = {
    "rest api":        ["rest", "api", "endpoint", "http", "get", "post",
                        "put", "delete", "restful", "web service",
                        "rest api integration", "rest api methods",
                        "rest api design", "api development"],
    "machine learning":["ml", "machine learning", "deep learning",
                        "neural", "model", "training", "ai model",
                        "supervised", "unsupervised"],
    "python":          ["python", "django", "flask", "fastapi",
                        "pip", "numpy", "pandas", "pytorch"],
    "android":         ["android", "kotlin", "jetpack", "compose",
                        "mobile app", "android development"],
    "politics":        ["politics", "political", "government",
                        "democracy", "election", "voting", "policy"],
    "climate":         ["climate", "global warming", "carbon",
                        "renewable", "environment", "green energy"],
    "business":        ["business", "startup", "entrepreneurship",
                        "revenue", "marketing", "sales", "strategy"],
    "ai":              ["ai", "artificial intelligence", "chatgpt",
                        "gemini", "llm", "gpt", "generative ai",
                        "prompt engineering"],
    "data science":    ["data science", "data analysis", "statistics",
                        "visualization", "pandas", "numpy", "dataset"],
    "web development": ["web", "html", "css", "javascript", "react",
                        "vue", "angular", "frontend", "backend"],
    "blockchain":      ["blockchain", "crypto", "bitcoin", "ethereum",
                        "nft", "web3", "defi"],
    "health":          ["health", "fitness", "nutrition", "workout",
                        "diet", "mental health", "wellness", "yoga"],
    "finance":         ["finance", "investment", "stocks", "trading",
                        "cryptocurrency", "budget", "saving", "money"],
}

# ── Recommendations for each group ────────────────────────────────────────
GROUP_RECOMMENDATIONS = {
    "rest api":         ["REST API Best Practices",
                         "API Authentication Methods",
                         "REST vs GraphQL Comparison",
                         "API Rate Limiting Strategies",
                         "REST API Security Guide"],
    "machine learning": ["Deep Learning Fundamentals",
                         "ML Model Deployment",
                         "Neural Network Architecture",
                         "Feature Engineering Techniques",
                         "ML Evaluation Metrics"],
    "python":           ["Python Design Patterns",
                         "Python Performance Optimization",
                         "Python Testing Best Practices",
                         "Async Python Programming",
                         "Python Microservices"],
    "android":          ["Jetpack Compose Basics",
                         "Android MVVM Architecture",
                         "Kotlin Coroutines Guide",
                         "Android Performance Tips",
                         "Material Design 3"],
    "politics":         ["Political Systems Compared",
                         "Democracy vs Autocracy",
                         "Electoral Reform Strategies",
                         "Political Philosophy Overview",
                         "Civic Engagement Guide"],
    "climate":          ["Renewable Energy Solutions",
                         "Carbon Footprint Reduction",
                         "Climate Policy Analysis",
                         "Sustainable Technology",
                         "Green Energy Future"],
    "business":         ["Business Model Innovation",
                         "Startup Growth Strategies",
                         "Market Research Methods",
                         "Customer Acquisition Tactics",
                         "Product Market Fit"],
    "ai":               ["Prompt Engineering Mastery",
                         "Large Language Models Explained",
                         "AI Ethics and Society",
                         "Generative AI Applications",
                         "AI in Healthcare"],
    "data science":     ["Data Visualization Techniques",
                         "Statistical Analysis Methods",
                         "Big Data Processing",
                         "Predictive Analytics",
                         "Data Engineering Basics"],
    "web development":  ["Modern JavaScript Frameworks",
                         "Full Stack Development",
                         "Web Performance Optimization",
                         "Progressive Web Apps",
                         "Web Security Best Practices"],
    "blockchain":       ["DeFi Explained Simply",
                         "Smart Contract Development",
                         "Blockchain Use Cases",
                         "Crypto Trading Strategies",
                         "Web3 Development Guide"],
    "health":           ["Evidence-Based Nutrition",
                         "Mental Health Techniques",
                         "Exercise Science Basics",
                         "Sleep Optimization Guide",
                         "Stress Management Methods"],
    "finance":          ["Investment Portfolio Strategy",
                         "Personal Finance Mastery",
                         "Stock Market Analysis",
                         "Passive Income Strategies",
                         "Financial Freedom Plan"],
}


def normalize_topic(topic: str) -> str:
    topic = topic.lower().strip()
    topic = re.sub(r'[^a-z0-9\s]', '', topic)
    return topic


def find_topic_group(topic: str) -> str:
    normalized = normalize_topic(topic)

    # Check each group
    for group_name, keywords in TOPIC_GROUPS.items():
        for keyword in keywords:
            if (keyword in normalized or
                normalized in keyword or
                any(word in normalized
                    for word in keyword.split()
                    if len(word) > 3)):
                return group_name

    return "unknown"


def get_recommendations_for_group(
    group:       str,
    topic:       str,
    count:       int
) -> dict:
    recs = GROUP_RECOMMENDATIONS.get(group, [])

    if not recs:
        # Generate topic-based recommendations
        clean = topic.strip().title()
        recs  = [
            f"{clean} Fundamentals",
            f"{clean} Advanced Concepts",
            f"{clean} Best Practices",
            f"Future of {clean}",
        ]

    return {
        "group":           group,
        "recommendations": recs[:3],
        "reason":          build_reason(topic, count),
        "should_notify":   count >= 2
    }


def build_reason(topic: str, count: int) -> str:
    if count >= 5:
        return f"You frequently explore {topic}"
    elif count >= 3:
        return f"You searched {topic} {count} times"
    else:
        return f"Based on your interest in {topic}"


# ── Track topic endpoint ──────────────────────────────────────────────────

@tracking_bp.route("/track-topic", methods=["POST"])
def track_topic():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False}), 400

    topic    = data.get("topic",    "").strip()
    category = data.get("category", "General").strip()
    count    = data.get("count",    1)

    if not topic:
        return jsonify({"success": False}), 422

    group = find_topic_group(topic)
    recs  = GROUP_RECOMMENDATIONS.get(group, [])

    if not recs:
        clean = topic.strip().title()
        recs  = [
            f"{clean} Fundamentals",
            f"{clean} Advanced Concepts",
            f"{clean} Best Practices"
        ]

    reason = (
        f"You frequently explore {topic}" if count >= 5 else
        f"You searched {topic} {count} times" if count >= 3 else
        f"Based on your interest in {topic}"
    )

    # ← Only notify if count >= 2
    should_notify = count >= 2

    logger.info(
        f"Track → topic='{topic}' group='{group}' "
        f"count={count} notify={should_notify}"
    )

    return jsonify({
        "success":         True,
        "topic":           topic,
        "group":           group,           # ← add group to response
        "count":           count,
        "should_notify":   should_notify,
        "recommendations": recs[:3],
        "reason":          reason
    }), 200
    


# ── Get group for topic 
@tracking_bp.route("/topic-group", methods=["POST"])
def topic_group():
    data  = request.get_json(silent=True)
    topic = data.get("topic", "").strip()
    group = find_topic_group(topic)

    return jsonify({
        "topic": topic,
        "group": group
    }), 200