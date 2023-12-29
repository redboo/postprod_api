from icecream import ic

from document import Document
from googleapi import GoogleAPI

# 1. Чтение гуглодока (первый ендпоинт) без АПИ. Тестировать будем чисто на сервере во время звонка с тобой. Будем закидывать идентификаторы гуглодока и сверять количество всяких значений. Наверное, только джейсон текста не сможем потестить с точки зрения применимости при вставке

credentials_file = "credentials.json"
google_api = GoogleAPI(credentials_file)

if google_api.authorize():
    # Тестовый документ
    doc_id = "https://docs.google.com/document/d/12YJt38e0mTMMos-6nmIW4amFR9mfx9pqDaNooX7MhX0/edit"

    ic(google_api.get_file_name(doc_id))
    if doc_json := google_api.get_document(doc_id):
        doc = Document(doc_json, count_emoji=True, first_table_only=True)

        # - Контент текущей версии без форматирования
        # ic(document.plain_text)
        doc.info()

else:
    ic("Ошибка авторизации.")


# 2. Запись в гуглодок (второй ендпоинт) без АПИ. Также на звонке симулируем вызов чтения, возьмем оттуда джейсом, сделаем запись в гуглодок новый или существующий этого джейсона

# 3. Два метода АПИ. Тут я уже смогу асинхронно тестировать, дергая ручки

# from datetime import datetime

# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# from icecream import ic

# # Путь к файлу с учетными данными
# credentials_file = "credentials.json"

# # Создаем объект учетных данных
# credentials = service_account.Credentials.from_service_account_file(
#     credentials_file,
#     scopes=[
#         "https://www.googleapis.com/auth/documents",
#         "https://www.googleapis.com/auth/drive",
#     ],
# )

# # Создаем объекты API для работы с Google Docs и Google Drive
# docs_service = build("docs", "v1", credentials=credentials)
# drive_service = build("drive", "v3", credentials=credentials)

# # Форматируем текущую дату и время в нужный формат
# formatted_datetime = datetime.now().strftime("%Y.%m.%d %H:%M:%S")

# # Создаем новый документ с именем в формате YYYY.MM.DD HH:mm:ss
# document = docs_service.documents().create(body={"title": formatted_datetime}).execute()
# document_id = document["documentId"]

# # Добавляем текст в документ
# requests = [
#     {
#         "insertText": {
#             "location": {
#                 "index": 1,
#             },
#             "text": "Привет, мир!",
#         },
#     },
# ]

# docs_service.documents().batchUpdate(
#     documentId=document_id, body={"requests": requests}
# ).execute()

# # Добавляем разрешения для доступа всем по ссылке
# drive_service.permissions().create(
#     fileId=document_id,
#     body={
#         "role": "reader",
#         "type": "anyone",
#     },
#     fields="id",
# ).execute()

# print(
#     f"Документ создан и доступен по ссылке: https://docs.google.com/document/d/{document_id}/edit"
# )
