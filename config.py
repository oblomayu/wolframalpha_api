import json
import os


class Config:
    """Хранит настройки приложения: API-ключ, таймаут, папку для результатов."""

    def __init__(self, path: str = "config.json"):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Файл конфигурации не найден: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Проверяем, что ключ задан
        self.app_id = data.get("app_id")
        if not self.app_id or self.app_id == "YOUR-APP-ID-HERE":
            raise ValueError("В config.json не указан корректный app_id")

        self.timeout = data.get("timeout", 15)
        self.output_dir = data.get("output_dir", "results")
