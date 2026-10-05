from app.services.gemini_service import GeminiService


def test_gemini_connection():

    service = GeminiService()

    response = service.generate_text(
        "Reply with exactly: Gemini connection successful"
    )

    assert response is not None
    assert len(response.strip()) > 0

    print("\nGemini response:")
    print(response)