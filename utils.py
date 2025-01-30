import openpyxl
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def create_driver():
    options = Options()
    options.add_argument(
        f"user-data-dir=Market_Parser")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36")
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--v=99")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options, service=Service(
            ChromeDriverManager().install()))
    return driver

def clean_price_data(file_path):
    """
    Читает данные из Excel-файла, удаляет лишние строки и оставляет только данные по технике с ценами,
    формируя словарь типа {"model": model, "price": price_model, "customer": customer}.

    Args:
        file_path (str): Путь к Excel-файлу.

    Returns:
        list or None: Список словарей или None, если произошла ошибка.
    """
    try:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        cleaned_data = []
        current_provider = None
        
        for row in sheet.iter_rows(values_only=True):
             if row is None or len(row) < 2: # проверка на пустую строку
                continue
             line, provider = row

             if provider: # проверка на наличие поставщика
                current_provider = provider

             if line is None:
               continue
             line = str(line).strip()  # Убираем пробелы в начале и конце строки

             if not line:  # пропускаем пустые строки
                continue
  
             if re.match(r"^\s*(\(.*\)\s*|\d+\s*/\s*\d+|[♦️🔸⚜️🌐🔥📱🪩⚫️🫧\u2066\u200d\uf000-\uf8ff\u2000-\u206F]+\s*.*[♦️🔸⚜️🌐🔥📱🪩⚫️🫧\u2066\u200d\uf000-\uf8ff\u2000-\u206F]+|[-━─≪≫]+|\(От\s+\d+шт\s*\)|\d+\s*-|[\w\s]+(S\/M|M\/L|X\/L)[\s\d-]*|[\w\s]+(SB|SL|AL|TL|BL|OB)[\s\d-]*)\s*$",line):
                continue
             elif re.match(r"^[\w\s]+,\s*\[\d{2}\.\d{2}\.\d{4}", line):
                 continue #пропускаем строки типа ‼️HI‼️, [09.12.2024
             elif re.match(r"^‼️.+‼️$", line):
               continue # Пропускаем строки содержащие  ‼️
             elif re.match(r"^[\w\s\d]+[-_\s:,.+]+$",line):
                 continue #пропускаем строки типа  "Продаем миксом от 10шт"  или "MiHonor Оптом Apple Samsung Xiaom,"
             elif re.match(r"^[\w\s]+\s*-\s*\d+\s*[\w/]*$", line):
                 continue # пропускаем строки типа SE2 40 - 20000
             elif re.match(r"(.+)\s+(\d+)([\w/]+)?", line):
                name, price, region = re.match(r"(.+)\s+(\d+)([\w/]+)?", line).groups()
                if int(price) > 100:
                    cleaned_data.append({
                    "model": name.strip(),
                    "price": int(price),
                    "customer": current_provider
                        })
        return cleaned_data
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден: {file_path}")
        return None
    except Exception as e:
        print(f"Произошла ошибка при чтении файла: {e}")
        return None