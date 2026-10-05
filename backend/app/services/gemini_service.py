import time

from google import genai
from google.genai import errors

from app.core.config import settings


class GeminiService:

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    def generate_text(
        self,
        prompt: str,
    ) -> str:

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return response.text

    def generate_json(
        self,
        prompt: str,
        max_retries: int = 3,
    ) -> str:

        for attempt in range(max_retries):

            try:

                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json"
                    },
                )

                return response.text

            except errors.ServerError as exc:

                if attempt == max_retries - 1:
                    raise exc

                wait_time = 2 ** attempt

                time.sleep(wait_time)

        raise RuntimeError(
            "Gemini request failed."
        )