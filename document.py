import json
import re
import string

import emoji
from icecream import ic


class Document:
    def __init__(self, json_data, count_emoji=False, first_table_only=False) -> None:
        self.json_data = json_data or {}

        if first_table_only:
            self.tables = self.find_tables()
            self.data = self.tables[0]["tableRows"][1]
            self.image_count = len(self.find_images())

        else:
            self.data = self.json_data.get("body", {}).get("content", None)
            self.image_count = len(self.json_data.get("inlineObjects", []))

        self.raw_content = self.extract_text_content_recursive(self.data)
        self.plain_text = self.raw_content.replace("\n", "")
        self.count_emoji = emoji.emoji_count(self.plain_text) if count_emoji else 0
        self.total_characters = (
            len(self.plain_text) + self.image_count + self.count_emoji
        )
        self.text_without_spaces = self.plain_text.replace(" ", "")
        self.characters_without_spaces = (
            len(self.text_without_spaces) + self.image_count + self.count_emoji
        )
        self.word_list = self.extract_words()
        self.word_count = len(self.word_list)
        self.urls = self.find_urls()

    def extract_text_content_recursive(self, element) -> str:
        content_list = []

        if (
            isinstance(element, dict)
            and "content" in element
            and isinstance(element["content"], str)
        ):
            content_list.append(element["content"])

        if isinstance(element, (dict, list)):
            for value in element.values() if isinstance(element, dict) else element:
                content_list.extend(self.extract_text_content_recursive(value))

        return "".join(content_list)

    def extract_words(self) -> list[str]:
        # Заменить повторяющиеся символы '\n' на одиночный символ '\n'
        words_with_spaces: str = re.sub(r"\n+", " ", self.raw_content)

        # Разделить текст на слова, заменяя определенные знаки пунктуации на пробелы
        words_list: list[str] = (
            words_with_spaces.strip()
            .replace(",", " ")
            .replace(".", " ")
            .replace(":", " ")
            .replace("#", " ")
            .replace(">", " ")
            .replace("<", " ")
            .replace("(", " ")
            .replace(")", " ")
            .replace("[", " ")
            .replace("]", " ")
            .replace("\\", " ")
            .replace("|", " ")
            .replace("/", " ")
            .replace("?", " ")
            .replace("\x0b", " ")
            .replace("—", " ")
            .replace("–", "")
            .replace("-", "")
            .replace("=", " ")
            .replace("”", " ")
            .replace("“", " ")
            .replace("!", " ")
            .replace("%", " ")
            .replace("	", " ")
            .split(" ")
        )

        # Фильтровать слова, оставляя только те, которые не состоят из знаков пунктуации
        return [
            word
            for word in words_list
            if any(char not in string.punctuation for char in word)
            and not word.isspace()
        ]

    def find_urls(self) -> list[str]:
        # Рекурсивный поиск всех URL в структуре данных
        urls: list[str] = []

        def extract_urls(element) -> None:
            if isinstance(element, dict):
                for key, value in element.items():
                    if key == "url" and isinstance(value, str):
                        urls.append(value)
                    else:
                        extract_urls(value)
            elif isinstance(element, list):
                for item in element:
                    extract_urls(item)

        extract_urls(self.data)
        return urls

    def save_json(self, file_path: str, json_data=None) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(json_data or self.json_data, f, ensure_ascii=False, indent=4)

    def find_tables(self) -> list[dict]:
        tables: list[dict] = []

        def extract_tables(element) -> None:
            if isinstance(element, dict):
                for key, value in element.items():
                    if key == "table" and isinstance(value, dict):
                        tables.append(value)
                    else:
                        extract_tables(value)
            elif isinstance(element, list):
                for item in element:
                    extract_tables(item)

        extract_tables(self.json_data)
        return tables

    def get_rows_content(self, table: dict) -> list[str]:
        rows = list(table["tableRows"])
        return [self.extract_text_content_recursive(row) for row in rows]

    def find_images(self) -> list[dict]:
        images: list[dict] = []

        def extract_images(element) -> None:
            if isinstance(element, dict):
                for key, value in element.items():
                    if key == "inlineObjectElement" and isinstance(value, dict):
                        images.append(value)
                    else:
                        extract_images(value)
            elif isinstance(element, list):
                for item in element:
                    extract_images(item)

        extract_images(self.data)
        return images

    def info(self) -> None:
        ic("Количество слов", self.word_count)
        ic("Количество знаков", self.total_characters)
        ic("Количество знаков без пробелов", self.characters_without_spaces)
        ic("Количество изображений", self.image_count)
        ic(len(self.urls), self.urls)
