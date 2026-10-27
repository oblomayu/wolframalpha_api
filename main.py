import logging
import os

from config import Config
from client import WolframAlphaClient, WolframAlphaError
from processor import extract_key_data, save_full_response, save_extracted_data, format_readable


# Настройка логирования: вывод в консоль и в файл
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


QUERIES = [
    # Обязательные
    ("01_math_integral",       "integrate x^2 sin^3 x dx"),
    ("02_population_russia",   "population of Russia 2024"),
    ("03_molar_mass_h2so4",    "molar mass of H2SO4"),
    ("04_kinetic_energy",      "kinetic energy of 5kg object at 10m/s"),
    ("05_distance_cities",     "distance between Moscow and Saint Petersburg"),
    ("06_currency_usd_rub",    "100 USD to RUB"),
    ("07_time_kazan",          "current time in Kazan"),
    ("08_distance_mars",       "distance to Mars"),
    ("09_bmi",                 "body mass index 180cm 75kg"),
    ("10_translate_hello",     "translate hello to Russian"),
    # custom
    ("11_ecuation",            "solve x^2 - 5x + 6 = 0"),
    ("12_physic_const",      "speed of light in km/h"),
    ("13_speed_of_light",      "speed of light"),
    ("14_diet",    "calories in 100 g of buckwheat"),
    ("15_math_analys",       "derivative of sin(x) * e^x"),
]


def main():
    try:
        config = Config("config.json")
    except (FileNotFoundError, ValueError) as exc:
        logger.error("Ошибка конфигурации: %s", exc)
        return

    client = WolframAlphaClient(config.app_id, timeout=config.timeout)
    os.makedirs(config.output_dir, exist_ok=True)

    report_lines = []
    successes, failures = 0, 0

    for name, query_text in QUERIES:
        logger.info("=" * 70)
        logger.info("Выполняется запрос [%s]: %s", name, query_text)
        try:
            response = client.query(query_text)
            data = extract_key_data(response)

            save_full_response(name, response, config.output_dir)
            save_extracted_data(name, data, config.output_dir)

            readable = format_readable(data)
            print(readable)
            report_lines.append(readable + "\n")

            successes += 1
        except WolframAlphaError as exc:
            logger.error("Ошибка запроса [%s]: %s", name, exc)
            report_lines.append(
                f"[{name}] ОШИБКА: {exc}\n"
            )
            failures += 1

    # Сохраняем общий отчёт
    report_path = os.path.join(config.output_dir, "report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    logger.info("=" * 70)
    logger.info(
        "Готово. Успешных запросов: %d, с ошибками: %d", successes, failures
    )
    logger.info("Отчёт сохранён: %s", report_path)


if __name__ == "__main__":
    main()
