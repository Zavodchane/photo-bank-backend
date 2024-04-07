import re
from io import BytesIO

import httpx
import requests
from PIL import Image as pImage
from exif import Image
from datetime import datetime
from dateutil.parser import parse
from colorthief import ColorThief
import hashlib


async def get_map_urls(place_name):
    """
    получает на вход название фотографии например “МГУ” после чего возвращает 3 ссылки на яндекс карты
     если статус код != 200 вернется пустой список
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": place_name,
        "format": "json",
        "accept-language": "ru",
        "countrycodes": "ru",
        "limit": 3,
    }
    urls_list = []

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code != 200:
            return urls_list
        data = response.json()
        for item in data:
            latitude = float(item["lat"])
            longitude = float(item["lon"])
            urls_list.append(
                f"https://yandex.ru/maps/?pt={longitude},{latitude}&z=18&l=map"
            )
    return urls_list


def get_metadata(file_bytes: bytes):
    """
    получает на вход файл, вернет словаь метаданных
    если файл не найден вернется пустой словарь
    если отсутствуют метаданные вернется пустой словарь
    ключи словаря:
    Make;
    Model;
    Lens make;
    Lens model;
    Lens specification;
    OS version;
    Date/time taken;
    Latitude;
    gps_latitude_ref;
    Longitude;
    gps_longitude;
    """

    metadata_dict = {}
    try:
        with BytesIO(file_bytes) as image_buffer:
            my_image = Image(image_buffer)
            if my_image.has_exif:
                metadata_dict["Make"] = my_image.get("make", "Unknown")
                metadata_dict["Model"] = my_image.get("model", "Unknown")

                metadata_dict["Lens make"] = my_image.get("lens_make", "Unknown")
                metadata_dict["Lens model"] = my_image.get("lens_model", "Unknown")
                metadata_dict["Lens specification"] = my_image.get(
                    "lens_specification", "Unknown"
                )
                metadata_dict["OS version"] = my_image.get("software", "Unknown")
                metadata_dict["Date/time taken"] = my_image.get("datetime_original")

                metadata_dict["Latitude"] = my_image.get("gps_latitude", "Unknown")
                metadata_dict["gps_latitude_ref"] = my_image.get(
                    "gps_latitude_ref", "Unknown"
                )

                metadata_dict["Longitude"] = my_image.get("gps_longitude", "Unknown")
                metadata_dict["gps_longitude"] = my_image.get(
                    "gps_longitude_ref", "Unknown"
                )
    except Exception:
        return metadata_dict
    return metadata_dict


def get_coords(data: dict) -> dict:
    if "Latitude" in data and "Longitude" in data:
        if data["Latitude"] != "Unknown" and data["Longitude"] != "Unknown":
            return {"Latitude": data["Latitude"], "Longitude": data["Longitude"]}
    if "gps_latitude_ref" in data and "gps_longitude" in data:
        if data["gps_latitude_ref"] != "Unknown" and data["gps_longitude"] != "Unknown":
            return {
                "Latitude": data["gps_latitude_ref"],
                "Longitude": data["gps_longitude"],
            }
    return {"Latitude": -1.0, "Longitude": -1.0}


def get_format(filename: str) -> int:
    if "." in filename:
        format = filename.rsplit(".", 1)[-1].lower()
        match format:
            case "jpg":
                return 0
            case "jpeg":
                return 0
            case "png":
                return 1
            case _:
                return 99


def get_timeobj(data: dict) -> datetime:
    """
    получает на вход словать с метаданыыми который можно получить в функции get_metadata()
    возвращает объект datetime
    если нужные тег отсутсвует или ошибка при парсинге вернет текущее время
    """
    time = data.get("Date/time taken")
    if time is None:
        return datetime.now()
    try:
        return parse(time)
    except Exception:
        return datetime.now()


def get_time_day(data: datetime) -> int:
    """
    получает datetime который можно получить в get_timeobj()
    возвращает int
    0-утро;
    1-день;
    2-вечер;
    3-ночь;
    """
    hour = data.hour
    if 0 <= hour < 6:
        return 3
    elif 6 <= hour < 12:
        return 0
    elif 12 <= hour < 18:
        return 1
    elif 18 <= hour < 24:
        return 2


def get_season(data: datetime) -> int:
    """
    получает datetime который можно получить в get_timeobj()
    возвращает int
    0 - лето
    1- осень
    2- зима
    3 весна
    """

    month = data.month
    match month:
        case 1:
            return 2
        case 2:
            return 2
        case 3:
            return 3
        case 4:
            return 3
        case 5:
            return 3
        case 6:
            return 0
        case 7:
            return 0
        case 8:
            return 0
        case 9:
            return 1
        case 10:
            return 1
        case 11:
            return 1
        case 12:
            return 2


def get_file_size_name_orientation(file_content: bytes) -> tuple[str, int, int]:
    """
    :param file_content: содержимое файла в виде байтов
    :return:
    первое значение: 1920x1080
    второе значение:
    0-очень большое;
    1-большое;
    2-среднее;
    3-маленькое;
    третье значение:
    0-горизонтальная
    1-вертикальная
    2-квадратная
    """
    with pImage.open(BytesIO(file_content)) as img:
        width, height = img.size

        # Определение размера изображения
    if width * height > 1920 * 1080:
        size_category = 0  # Очень большое
    elif width * height > 1280 * 720:
        size_category = 1  # Большое
    elif width * height > 640 * 480:
        size_category = 2  # Среднее
    else:
        size_category = 3  # Маленькое

        # Определение ориентации изображения
    if width > height:
        orientation = 0  # Горизонтальная
    elif width < height:
        orientation = 1  # Вертикальная
    else:
        orientation = 2  # Квадратная

        # Формирование строки с размером изображения
    size_name = f"{width}x{height}"

    return size_name, size_category, orientation


def get_hash(file_bytes: bytes) -> str:
    """
    Вычисляет MD5 хеш переданных байт.
    Аргументы:
    file_bytes (bytes): Байты файла, для которых нужно вычислить MD5 хеш.
    Возвращает:
    str: Строковое представление MD5 хеша файла.
    """
    # Создаем объект для вычисления MD5 хеша
    hasher = hashlib.md5()

    # Обновляем хеш байтами файла
    hasher.update(file_bytes)

    # Получаем значение MD5 хеша в виде строкового представления
    md5_hash = hasher.hexdigest()

    # Возвращаем значение MD5 хеша
    return md5_hash


def rgb_to_color_name(rgb) -> int:
    """
    вспомогательная функция для определения кода цвета по rgb
    :param rgb:
    :return:
    """
    red, green, blue = rgb
    if red > green and red > blue:
        return 2
    elif green > red and green > blue:
        return 3
    elif blue > red and blue > green:
        return 4
    elif red < 50 and green < 50 and blue < 50:
        return 0
    else:
        return 1


def get_color(filepath: bytes) -> int:
    """
    :param filepath: путь к файлу
    :return: возвращает код цвета
    0-black;
    1-white;
    2-red;
    3-green;
    4-blue;
    """
    color_thief = ColorThief(BytesIO(filepath))
    dominant_color = color_thief.get_color(quality=100)
    return rgb_to_color_name(dominant_color)


def transliterate(text):
    """
    используется при создании слага
    :param text: текс на русском
    :return: текс на английском
    """
    translit_dict = {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ё": "yo",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "h",
        "ц": "c",
        "ч": "ch",
        "ш": "sh",
        "щ": "sch",
        "ъ": "",
        "ы": "y",
        "ь": "",
        "э": "e",
        "ю": "yu",
        "я": "ya",
    }

    transliterated_text = ""
    for char in text:
        if char in translit_dict:
            transliterated_text += translit_dict[char]
        elif char.isalnum() or char == "-":
            transliterated_text += char
    return transliterated_text


def generate_slug(name: str, unique_str: str) -> str:
    """
    возвращает slug транслитерирует русский текст отбрасывает спец символы
    в качестве уникальной строки можно передавать id переведенный в str
    :param name: имя фотографии
    :param unique_str: строка для добавления
    :return: готовый слаг
    """
    slug = name.lower().replace(" ", "-")
    slug = re.sub(r"\-+", "-", slug)
    transliterated_slug = transliterate(slug)
    return f"{transliterated_slug}-{unique_str}"
