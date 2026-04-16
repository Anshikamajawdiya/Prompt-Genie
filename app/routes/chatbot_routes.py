import sys
import os
sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.dirname(__file__))
))

from flask import Blueprint, request, jsonify
import logging
from app.services.chatbot_service import ChatbotService
from app.services.gemini_service  import GeminiService

logger     = logging.getLogger(__name__)
chatbot_bp = Blueprint("chatbot", __name__)

try:
    gemini_svc = GeminiService()
    chatbot    = ChatbotService(gemini_svc)
    logger.info("✅ ChatbotService ready")
except Exception as e:
    chatbot = ChatbotService(None)    # ← fallback mode no Gemini
    logger.warning(f"ChatbotService in fallback mode: {e}")


@chatbot_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "Invalid JSON"}), 400

    message = data.get("message", "").strip()
    history = data.get("history", [])
    context = data.get("context", None)    # ← receive context

    if not message:
        return jsonify({"success": False, "message": "Message required"}), 422

    logger.info(
        f"Chat → message='{message}' "
        f"context_topic='{context.get('topic') if context else None}'"
    )

    result = chatbot.chat(message, history, context)

    return jsonify({
        "success":     True,
        "reply":       result["reply"],
        "has_prompt":  result["has_prompt"],
        "prompt_data": result["prompt_data"]
    }), 200