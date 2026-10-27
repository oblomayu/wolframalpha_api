import logging 
import requests

logger = logging.getLogger(__name__)


class WolframAlphaError(Exception):
    """Базовое исключение для ошибок Wolfram Alpha API."""


class WolframAlphaClient:
    """Клиент для выполнения запросов к Wolfram Alpha API v2."""

    def __init__(self, app_id: str, timeout: int = 15):
        self.base_url = "https://api.wolframalpha.com/v2/query"
        self.app_id = app_id
        self.timeout = timeout

    def query(self, input_text: str) -> dict:
        """
        Выполняет запрос к API и возвращает JSON-ответ в виде словаря.
        Бросает WolframAlphaError при сетевых сбоях или ошибках API.
        """
        params = {
            "input": input_text,
            "format": "plaintext",
            "output": "json",
            "appid": self.app_id,
        }

        logger.info("Запрос: %s", input_text)

        try:
            response = requests.get(
                self.base_url, params=params, timeout=self.timeout
            )
            response.raise_for_status()  # выбросит HTTPError на 4xx/5xx
        except requests.exceptions.Timeout as exc:
            raise WolframAlphaError(
                f"Таймаут при запросе '{input_text}'"
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise WolframAlphaError(
                f"Сетевая ошибка при запросе '{input_text}': {exc}"
            ) from exc

        # Проверяем, что API вернул валидный JSON
        try:
            data = response.json()
        except ValueError as exc:
            raise WolframAlphaError(
                f"Некорректный JSON в ответе на '{input_text}'"
            ) from exc

        # Если API вернул ошибку — сообщаем о ней
        if not data.get("queryresult", {}).get("success", False):
            error_info = data.get("queryresult", {}).get(
                "error", "неизвестная ошибка"
            )
            raise WolframAlphaError(
                f"API не смог обработать запрос '{input_text}': {error_info}"
            )

        return data
