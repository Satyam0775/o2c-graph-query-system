import cohere
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CohereClient:
    def __init__(self):
        self.client = cohere.Client(settings.COHERE_API_KEY)

    def complete(self, prompt: str):
        try:
            response = self.client.chat(
                model="command-r-plus-08-2024",  # ✅ FIXED
                message=prompt,
                temperature=0.3,
            )

            return response.text

        except Exception as e:
            logger.error(f"Cohere error: {e}")
            raise