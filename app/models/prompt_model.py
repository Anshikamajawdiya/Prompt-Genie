from dataclasses import dataclass
from typing import Optional

@dataclass
class PromptRequest:
    topic: str
    category: str

    def validate(self) -> Optional[str]:
        if not self.topic or not self.topic.strip():
            return "Topic is required"
        if not self.category or not self.category.strip():
            return "Category is required"
        if len(self.topic.strip()) > 200:
            return "Topic must be under 200 characters"
        return None

@dataclass
class PromptResponse:
    prompt: str
    source: str
    success: bool
    message: str = ""

    def to_dict(self) -> dict:
        return {
            "prompt":  self.prompt,
            "source":  self.source,
            "success": self.success,
            "message": self.message
        }