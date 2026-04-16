# from flask import Blueprint, request, jsonify
# import logging

# from app.models.prompt_model   import PromptRequest, PromptResponse
# from app.services.gemini_service   import GeminiService
# from app.services.fallback_service import FallbackService
# from config import Config

# logger    = logging.getLogger(__name__)
# prompt_bp = Blueprint("prompt", __name__)

# # Initialise once at module level
# try:
#     gemini_service = GeminiService()
#     logger.info("GeminiService ready")
# except Exception as e:
#     gemini_service = None
#     logger.error(f"GeminiService failed to init: {e}")

# fallback_service = FallbackService()


# @prompt_bp.route("/generate", methods=["POST"])
# def generate():
#     # Parse request
#     data = request.get_json(silent=True)
#     if not data:
#         return jsonify({"success": False, "message": "Invalid JSON body"}), 400

#     prompt_req = PromptRequest(
#         topic    = data.get("topic", "").strip(),
#         category = data.get("category", "General").strip()
#     )

#     error = prompt_req.validate()
#     if error:
#         return jsonify({"success": False, "message": error}), 422

#     # Try Gemini
#     if gemini_service:
#         try:
#             text     = gemini_service.generate_prompt(prompt_req.topic, prompt_req.category)
#             response = PromptResponse(prompt=text, source="gemini", success=True,
#                                       message="Generated successfully")
#             logger.info("Served via Gemini")
#             return jsonify(response.to_dict()), 200
#         except Exception as e:
#             logger.warning(f"Gemini failed: {e} — switching to fallback")

#     #  Fallback
#     if Config.FALLBACK_ENABLED:
#         try:
#             text     = fallback_service.generate_prompt(prompt_req.topic, prompt_req.category)
#             response = PromptResponse(prompt=text, source="fallback", success=True,
#                                       message="Generated via fallback")
#             logger.info("Served via fallback")
#             return jsonify(response.to_dict()), 200
#         except Exception as e:
#             logger.error(f"Fallback also failed: {e}")

#     # Both failed
#     return jsonify({
#         "success": False,
#         "message": "All generation services failed. Please try again.",
#         "prompt":  "",
#         "source":  "none"
#     }), 503


# @prompt_bp.route("/health", methods=["GET"])
# def health():
#     return jsonify({
#         "status":           "ok",
#         "gemini_available": gemini_service is not None,
#         "fallback_enabled": Config.FALLBACK_ENABLED
#     }), 200


# @prompt_bp.route("/categories", methods=["GET"])
# def categories():
#     return jsonify({
#         "categories": list(FallbackService.FALLBACK_BANK.keys())
#     }), 200

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from flask import Blueprint, request, jsonify
import logging

from app.models.prompt_model            import PromptRequest, PromptResponse
from app.services.candidate_generator   import CandidateGenerator
from app.services.prompt_scorer         import PromptScorer
from app.services.gemini_service        import GeminiService
from app.services.fallback_service      import FallbackService
from config import Config

logger    = logging.getLogger(__name__)
prompt_bp = Blueprint("prompt", __name__)

# ── Initialise all services once 
candidate_generator = CandidateGenerator()
fallback_service    = FallbackService()

try:
    prompt_scorer = PromptScorer()
    logger.info("✅ PromptScorer loaded successfully")
except Exception as e:
    prompt_scorer = None
    logger.error(f"❌ PromptScorer failed: {e}")

try:
    gemini_service = GeminiService()
    logger.info("✅ GeminiService ready")
except Exception as e:
    gemini_service = None
    logger.error(f"❌ GeminiService failed: {e}")


@prompt_bp.route("/generate", methods=["POST"])
def generate():

    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid JSON body"
        }), 400

    prompt_req = PromptRequest(
        topic    = data.get("topic",    "").strip(),
        category = data.get("category", "General").strip()
    )

    error = prompt_req.validate()
    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 422

    candidates = candidate_generator.generate_candidates(
        prompt_req.topic,
        prompt_req.category
    )
    logger.info(f"Generated {len(candidates)} candidates for "
                f"topic='{prompt_req.topic}' "
                f"category='{prompt_req.category}'")

    best_prompt = candidates[0]
    best_score  = 0.0
    source      = "ml_model"

    if prompt_scorer:
        try:
            scored = [
                (c, prompt_scorer.score(
                    c,
                    prompt_req.topic,
                    prompt_req.category
                ))
                for c in candidates
            ]
            scored.sort(key=lambda x: x[1], reverse=True)
            best_prompt, best_score = scored[0]

            logger.info(f"Best ML score: {best_score:.3f}")
            logger.info(f"All scores: "
                        f"{[round(s, 3) for _, s in scored]}")

        except Exception as e:
            logger.warning(f"ML scoring failed: {e}")
            best_prompt = candidates[0]
            source      = "fallback"

    if gemini_service and best_score < 0.50:
        try:
            enhanced = gemini_service.generate_prompt(
                prompt_req.topic,
                prompt_req.category
            )

            if prompt_scorer:
                enhanced_score = prompt_scorer.score(
                    enhanced,
                    prompt_req.topic,
                    prompt_req.category
                )
            else:
                enhanced_score = 0.9

            if enhanced_score > best_score:
                best_prompt = enhanced
                best_score  = enhanced_score
                source      = "gemini"
                logger.info(f"Gemini improved score: "
                            f"{enhanced_score:.3f}")
            else:
                logger.info(f"ML model kept — score "
                            f"{best_score:.3f} > "
                            f"Gemini {enhanced_score:.3f}")

        except Exception as e:
            logger.warning(f"Gemini enhancement failed: {e}")

    if not best_prompt or len(best_prompt) < 10:
        try:
            best_prompt = fallback_service.generate_prompt(
                prompt_req.topic,
                prompt_req.category
            )
            source = "fallback"
            logger.info("Using fallback service")
        except Exception as e:
            logger.error(f"Fallback also failed: {e}")
            return jsonify({
                "success": False,
                "message": "All services failed. Please try again.",
                "prompt":  "",
                "source":  "none"
            }), 503

    response = PromptResponse(
        prompt  = best_prompt,
        source  = source,
        success = True,
        message = f"Generated with confidence {best_score:.0%}"
    )

    logger.info(f"Response sent — source={source} "
                f"score={best_score:.3f}")

    return jsonify(response.to_dict()), 200


@prompt_bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status":           "ok",
        "ml_model_loaded":  prompt_scorer  is not None,
        "gemini_available": gemini_service is not None,
        "fallback_enabled": Config.FALLBACK_ENABLED
    }), 200


@prompt_bp.route("/categories", methods=["GET"])
def categories():
    return jsonify({
        "categories": list(
            FallbackService.FALLBACK_BANK.keys()
        )
    }), 200