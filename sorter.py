import json
import requests

from config import get_gemini_api_key


class GeminiSortingError(Exception):
    pass


def filter_tracks_with_ai(
    tracks: list,
    user_prompt: str
) -> list:

    api_key = get_gemini_api_key()

    if not api_key:
        raise GeminiSortingError(
            "Gemini API key is not configured."
        )

    ai_prompt = f"""
Ти професійний музичний редактор.

Твоє завдання — ВІДФІЛЬТРУВАТИ треки з наданого списку відповідно до запиту користувача.

Запит користувача:
"{user_prompt}"

ВАЖЛИВІ ПРАВИЛА:

1. Перевір КОЖЕН трек зі списку.
2. Не рекомендуй треки і не створюй власний список рекомендацій.
3. Потрібно знайти ВСІ треки, які відповідають запиту.
4. Будь достатньо широким у виборі. Якщо є обґрунтована ймовірність, що трек відповідає критерію — включай його.
5. НІКОЛИ не обмежуй результат кількома треками.
6. НІКОЛИ не вигадуй треки, яких немає у вхідному списку.
7. Не змінюй title та video_id.
8. Не додавай один і той самий video_id більше одного разу.
9. Зберігай порядок треків таким самим, як у вхідному списку.

ПРІОРИТЕТ ІНФОРМАЦІЇ:

- Назва треку (title) — ОСНОВНЕ джерело інформації.
- Виконавець, якщо він присутній у title — ОСНОВНЕ джерело інформації.
- Description — ДОДАТКОВЕ джерело інформації, а НЕ головне.

Не відхиляй трек тільки через те, що його description порожній,
неповний або не містить інформації про жанр.

Description використовуй для уточнення, коли інформації в title недостатньо.
Якщо title явно відповідає запиту, включай трек навіть якщо description цьому не допомагає.
Якщо title явно НЕ відповідає запиту, не включай трек тільки через те,
що в description випадково зустрічається потрібне слово.

Наприклад:
- title містить відомого реп-виконавця → це сильний аргумент для включення.
- description містить слово "rap", але сам трек за title очевидно не є репом → не включай тільки через description.

Поверни ТІЛЬКИ валідний JSON-масив без markdown та пояснень:

[
    {{
        "title": "Назва треку",
        "video_id": "оригінальний_id_треку"
    }}
]

Ось список треків:

{json.dumps(tracks, ensure_ascii=False)}
"""

    try:
        print(
            f"Аналізуємо {len(tracks)} треків через Gemini..."
        )

        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            "models/gemini-3.5-flash-lite:generateContent"
        )

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": ai_prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 8192,
                "responseMimeType": "application/json"
            }
        }

        response = requests.post(
            url,
            headers=headers,
            params={
                "key": api_key
            },
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        raw_text = (
            data["candidates"][0]["content"]["parts"][0]["text"]
            .strip()
        )

        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]

        if raw_text.startswith("```"):
            raw_text = raw_text[3:]

        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]

        selected_tracks = json.loads(
            raw_text.strip()
        )

        print(
            f"Успішно відібрано треків: "
            f"{len(selected_tracks)} / {len(tracks)}"
        )

        return selected_tracks

    except requests.RequestException as error:
        print(
            f"Gemini API request failed: {error}"
        )

        raise GeminiSortingError(
            "Gemini API request failed. "
            "Please check your API key and internet connection."
        ) from error

    except (
        KeyError,
        IndexError,
        TypeError,
        json.JSONDecodeError
    ) as error:
        print(
            f"Invalid Gemini response: {error}"
        )

        raise GeminiSortingError(
            "Gemini returned an invalid response."
        ) from error

    except GeminiSortingError:
        raise

    except Exception as error:
        print(
            f"Gemini sorting failed: {error}"
        )

        raise GeminiSortingError(
            "AI sorting failed. Please try again."
        ) from error