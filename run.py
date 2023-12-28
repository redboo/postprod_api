from icecream import ic

from document import Document
from googleapi import GoogleAPI

# 1. Чтение гуглодока (первый ендпоинт) без АПИ. Тестировать будем чисто на сервере во время звонка с тобой. Будем закидывать идентификаторы гуглодока и сверять количество всяких значений. Наверное, только джейсон текста не сможем потестить с точки зрения применимости при вставке

# по gdoc id получить документ
credentials_file = "credentials.json"
google_api = GoogleAPI(credentials_file)

if google_api.authorize():
    # ПостПрод
    doc_id = "1Yaajv5eZ07AotqMunkJMWU0SdiSa5ZhSi6-7bg6yS3w"
    # Миллиарды потеряют работу
    # doc_id = "12CoQ21TNv0HQPvmmy_u5a_wyipYlOIiGh7xeK-T4S0g"
    # Безопасность сообщества
    # doc_id = "1ksd50jFVQx4MbnSQmmhA3cIZGWJXb9xwYyG36B63PKA"
    # Постпрод оригинал
    doc_id = "1zuJPsUHxhe1Hg5cNt91_8jOvSxqTVl_PYvLXjtBscUc"
    # Боевые документы
    doc_id = "1mrlGxyomUtbGTeKi92aStt2UvF37rUmej2JU_WC3yA8"
    doc_id = "18DQTp5usgBDmu5MuyHoZt4f5eOXY4YRH3C4Ymm661vA"
    doc_id = "1_fopifkbEk5NCkXnTOQqP9L4pQU1EU_TIdgyvJJwV54"
    ic(google_api.get_file_name(doc_id))

    # На выход
    # - Успех или не успех
    # - Контент текущей версии форматированный
    doc_json = google_api.get_document(doc_id)

    doc = Document(doc_json, count_emoji=True)

    # - Контент текущей версии без форматирования
    # ic(document.text)
    # - Количество символов с пробелами
    ic("Количество символов с пробелами", doc.total_characters)
    # - Количество символов без пробелов
    ic("Количество символов без пробелов", doc.characters_without_spaces)
    # - Количество слов
    # ic(doc.words)
    ic("Количество слов", doc.word_count)
    # - Количество изображений
    ic("Количество изображений", doc.image_count)
    # - Список всех ссылок
    ic(len(doc.urls), doc.urls)
else:
    ic("Ошибка авторизации.")


# 2. Запись в гуглодок (второй ендпоинт) без АПИ. Также на звонке симулируем вызов чтения, возьмем оттуда джейсом, сделаем запись в гуглодок новый или существующий этого джейсона

# 3. Два метода АПИ. Тут я уже смогу асинхронно тестировать, дергая ручки
