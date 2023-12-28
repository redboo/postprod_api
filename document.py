import re
import string

import emoji


class Document:
    def __init__(self, json_data, count_emoji=False):
        self.json_data = json_data or {}
        self.raw_content = self.extract_text_content_recursive(
            self.json_data.get("body", {}).get("content", None)
        )
        self.plain_text = self.raw_content.replace("\n", "")
        self.count_emoji = emoji.emoji_count(self.plain_text) if count_emoji else 0
        self.image_count = len(self.json_data.get("inlineObjects", []))
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

    def extract_text_content_recursive(self, element):
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

        return "".join(content_list) if content_list else ""

    def extract_words(self):
        # Заменить повторяющиеся символы '\n' на одиночный символ '\n'
        words_with_spaces = re.sub(r"\n+", " ", self.raw_content)

        # Разделить текст на слова, заменяя определенные знаки пунктуации на пробелы
        words_list = (
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
        ]

    def find_urls(self):
        # Рекурсивный поиск всех URL в структуре данных
        urls = []

        def extract_urls(element):
            if isinstance(element, dict):
                for key, value in element.items():
                    if key == "url" and isinstance(value, str):
                        urls.append(value)
                    else:
                        extract_urls(value)
            elif isinstance(element, list):
                for item in element:
                    extract_urls(item)

        extract_urls(self.json_data)
        return urls
