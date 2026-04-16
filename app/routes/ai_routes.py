import sys
import os
sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.dirname(__file__))
))

from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)
ai_bp  = Blueprint("ai", __name__)

ANGLE_EMOJIS = {
    "Scientific Analysis":   "🔬",
    "Research Design":       "📊",
    "Future Implications":   "🚀",
    "Common Misconceptions": "❌",
    "Implementation":        "💻",
    "Best Practices":        "✅",
    "Performance":           "⚡",
    "Security":              "🔒",
    "Strategy":              "♟️",
    "Market Analysis":       "📈",
    "Risk Assessment":       "⚠️",
    "Case Study":            "📚",
    "Beginner Guide":        "🎯",
    "Deep Dive":             "🔍",
    "Practical Skills":      "🛠️",
    "Assessment":            "📝",
    "Short Story":           "📖",
    "World Building":        "🌍",
    "Character Study":       "👤",
    "Plot Twist":            "🌀",
    "Campaign":              "📣",
    "Content Strategy":      "✍️",
    "Target Audience":       "🎯",
    "Viral Strategy":        "🔥",
    "Ethical Analysis":      "⚖️",
    "Historical View":       "🏛️",
    "Modern Perspective":    "💡",
    "Thought Experiment":    "🧠",
    "Overview":              "📋",
    "Pros and Cons":         "⚖️",
    "Future Trends":         "🔮",
    "Practical Tips":        "💡",
    "Business Impact":       "💼",
    "Solutions Focus":       "🌱",
    "Educational":           "🎓",
    "Policy Analysis":       "📜",
}

STATIC_SUGGESTIONS = {
    "Science": [
        {"angle": "Scientific Analysis",    "emoji": "🔬"},
        {"angle": "Research Design",        "emoji": "📊"},
        {"angle": "Future Implications",    "emoji": "🚀"},
        {"angle": "Common Misconceptions",  "emoji": "❌"},
    ],
    "Coding": [
        {"angle": "Implementation",  "emoji": "💻"},
        {"angle": "Best Practices",  "emoji": "✅"},
        {"angle": "Performance",     "emoji": "⚡"},
        {"angle": "Security",        "emoji": "🔒"},
    ],
    "Business": [
        {"angle": "Strategy",        "emoji": "♟️"},
        {"angle": "Market Analysis", "emoji": "📈"},
        {"angle": "Risk Assessment", "emoji": "⚠️"},
        {"angle": "Case Study",      "emoji": "📚"},
    ],
    "Education": [
        {"angle": "Beginner Guide",   "emoji": "🎯"},
        {"angle": "Deep Dive",        "emoji": "🔍"},
        {"angle": "Practical Skills", "emoji": "🛠️"},
        {"angle": "Assessment",       "emoji": "📝"},
    ],
    "Creative Writing": [
        {"angle": "Short Story",     "emoji": "📖"},
        {"angle": "World Building",  "emoji": "🌍"},
        {"angle": "Character Study", "emoji": "👤"},
        {"angle": "Plot Twist",      "emoji": "🌀"},
    ],
    "Marketing": [
        {"angle": "Campaign",          "emoji": "📣"},
        {"angle": "Content Strategy",  "emoji": "✍️"},
        {"angle": "Target Audience",   "emoji": "🎯"},
        {"angle": "Viral Strategy",    "emoji": "🔥"},
    ],
    "Philosophy": [
        {"angle": "Ethical Analysis",    "emoji": "⚖️"},
        {"angle": "Historical View",     "emoji": "🏛️"},
        {"angle": "Modern Perspective",  "emoji": "💡"},
        {"angle": "Thought Experiment",  "emoji": "🧠"},
    ],
    "General": [
        {"angle": "Overview",      "emoji": "📋"},
        {"angle": "Pros and Cons", "emoji": "⚖️"},
        {"angle": "Future Trends", "emoji": "🔮"},
        {"angle": "Practical Tips","emoji": "💡"},
    ]
}


def build_suggestions(topic: str, category: str) -> list:
    base = STATIC_SUGGESTIONS.get(
        category,
        STATIC_SUGGESTIONS["General"]
    )
    return [
        {
            "angle":       item["angle"],
            "emoji":       item["emoji"],
            "topic":       f"{item['angle']} of {topic}",
            "category":    category,
            "description": f"Explore {topic} from a "
                           f"{item['angle'].lower()} perspective"
        }
        for item in base
    ]


@ai_bp.route("/suggest-topics", methods=["POST"])
def suggest_topics():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid JSON"
        }), 400

    topic    = data.get("topic",    "").strip()
    category = data.get("category", "General").strip()

    if not topic:
        return jsonify({
            "success": False,
            "message": "Topic is required"
        }), 422

    logger.info(
        f"Suggestions for topic='{topic}' category='{category}'"
    )

    # ── Static suggestions only — no Gemini quota used ────────────────
    suggestions = build_suggestions(topic, category)

    return jsonify({
        "success":     True,
        "topic":       topic,
        "category":    category,
        "source":      "static",
        "suggestions": suggestions
    }), 200