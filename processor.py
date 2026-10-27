import json
import logging
import os

logger = logging.getLogger(__name__)


def extract_key_data(response: dict) -> dict:
    """
    Извлекает ключевые данные из JSON-ответа Wolfram Alpha.
    Возвращает словарь: текст запроса, итоговый ответ, все pods.
    """
    qr = response.get("queryresult", {})
    pods = qr.get("pods", [])

    # Ищем pod с "primary" = True — это главный результат
    primary_text = None
    for pod in pods:
        if pod.get("primary"):
            subpods = pod.get("subpods", [])
            if subpods:
                primary_text = subpods[0].get("plaintext")
            break

    # Если главного pod нет — берём первый непустой subpod
    if primary_text is None:
        for pod in pods:
            for subpod in pod.get("subpods", []):
                if subpod.get("plaintext"):
                    primary_text = subpod["plaintext"]
                    break
            if primary_text:
                break

    return {
        "input": qr.get("input", ""),
        "primary_result": primary_text or "Результат не найден",
        "pods": [
            {
                "title": pod.get("title"),
                "plaintext": [
                    sp.get("plaintext", "")
                    for sp in pod.get("subpods", [])
                ],
            }
            for pod in pods
        ],
    }


def save_full_response(name: str, response: dict, output_dir: str) -> str:
    """Сохраняет полный JSON-ответ в файл results/<name>_full.json."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{name}_full.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(response, f, ensure_ascii=False, indent=2)
    logger.info("Полный ответ сохранён: %s", path)
    return path


def save_extracted_data(name: str, data: dict, output_dir: str) -> str:
    """Сохраняет извлечённые данные в файл results/<name>_extracted.json."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{name}_extracted.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info("Извлечённые данные сохранены: %s", path)
    return path


def format_readable(data: dict) -> str:
    """Формирует удобочитаемый текст для вывода в консоль и в отчёт."""
    lines = [
        f"Запрос: {data['input']}",
        f"Ответ:  {data['primary_result']}",
        "-" * 60,
    ]
    for pod in data["pods"]:
        texts = [t for t in pod["plaintext"] if t]
        if texts:
            lines.append(f"  [{pod['title']}]")
            for t in texts:
                lines.append(f"    {t}")
    return "\n".join(lines)
