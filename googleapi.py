import json
from typing import Union

from google.oauth2 import service_account
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from icecream import ic

# Levels of sharing permissions
PERMISSION_READ = "reader"
PERMISSION_WRITE = "writer"
PERMISSION_OWNER = "owner"

AUTH_TYPE_SERVICE_ACCOUNT = "service_account"


class GoogleAPI:
    def __init__(
        self,
        credentials_file=None,
        credentials_json=None,
        auto_ownership=False,
        default_owner_email="",
    ) -> None:
        self.CREDENTIALS = credentials_file
        self.CREDENTIALS_JSON = credentials_json
        self.service_email = None
        self.auth_type = None

        # if the authentication type is a service account, allow the user to specify if
        #   we should automatically make them the owner of every file we upload
        self.auto_owner = auto_ownership
        self.default_owner_email = default_owner_email

        self.drive_service = None
        self.doc_service = None
        self._drive_version = "v3"
        self._doc_version = "v1"

    def authorize(self, authentication_type: Union[str, None] = None) -> bool:
        if not authentication_type:
            authentication_type = AUTH_TYPE_SERVICE_ACCOUNT

        if not self.CREDENTIALS and not self.CREDENTIALS_JSON:
            raise FileNotFoundError(
                "No credentials file has been set.  See: \n\t"
                "https://developers.google.com/workspace/guides/create-credentials?hl=ru\n"
                "for instructions on how to obtain this file. "
            )

        credentials = self._get_credentials(authentication_type)

        self.auth_type = authentication_type

        self.drive_service = build(
            "drive", self._drive_version, credentials=credentials
        )

        self.doc_service = build("docs", self._doc_version, credentials=credentials)

        return True

    def _get_credentials(self, authentication_type: str) -> Credentials:
        if authentication_type == AUTH_TYPE_SERVICE_ACCOUNT:
            return self._get_service_account_credentials()
        else:
            raise AttributeError(
                f"Unsupported authentication type: `{authentication_type}`"
            )

    def _get_service_account_credentials(self) -> Credentials:
        # A complete list of scopes can be found at: https://developers.google.com/identity/protocols/googlescopes#drive
        SCOPES: list[str] = [
            "https://www.googleapis.com/auth/documents",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive.appdata",
            "https://www.googleapis.com/auth/drive.metadata",
        ]

        if self.CREDENTIALS:
            credentials: Credentials = (
                service_account.Credentials.from_service_account_file(
                    self.CREDENTIALS, scopes=SCOPES
                )
            )
            with open(self.CREDENTIALS) as f:
                cred_obj = json.load(f)
                self.service_email = cred_obj["client_email"]
        elif self.CREDENTIALS_JSON:
            credentials = service_account.Credentials.from_service_account_info(
                self.CREDENTIALS_JSON, scopes=SCOPES
            )
            self.service_email = self.CREDENTIALS_JSON["client_email"]
        else:
            raise FileNotFoundError("No service account credentials provided.")

        return credentials

    def extract_file_id_from_url(self, file_id: str) -> str:
        return file_id.split("/")[-2] if file_id.startswith("https://") else file_id

    def get_file_name(self, file_id: str):
        try:
            file_id = self.extract_file_id_from_url(file_id)
            if self.drive_service:
                return (
                    self.drive_service.files()
                    .get(fileId=file_id, fields="name")
                    .execute()["name"]
                )
        except HttpError as e:
            if e.resp.status == 404:
                print(f"Файл с ID {file_id} не найден.")
            else:
                print(f"Ошибка при получении имени файла: {e}")

        return None

    def get_files(self):
        if self.drive_service:
            return self.drive_service.files().list().execute()

        return None

    def delete_all_files(self) -> bool:
        if self.drive_service:
            if files := self.get_files():
                file_ids = [file["id"] for file in files.get("files", [])]
                for file_id in file_ids:
                    self.delete_file(file_id)
                return True

        return False

    def delete_file(self, file_id):
        file_id = self.extract_file_id_from_url(file_id)
        if self.drive_service:
            return self.drive_service.files().delete(fileId=file_id).execute()

        return None

    def get_document(self, file_id: str):
        try:
            file_id = self.extract_file_id_from_url(file_id)
            if self.doc_service:
                return self.doc_service.documents().get(documentId=file_id).execute()
        except HttpError as e:
            if e.resp.status == 403:
                print(
                    f"У вас нет прав для просмотра документа с ID {file_id}. Проверьте права доступа."
                )
            else:
                print(f"Ошибка при получении документа: {e}")

        return None


if __name__ == "__main__":
    credentials_file = "credentials.json"
    google_api = GoogleAPI(credentials_file)

    if google_api.authorize():
        ic("Авторизация прошла успешно.")

        my_doc_id = "1Yaajv5eZ07AotqMunkJMWU0SdiSa5ZhSi6-7bg6yS3w"
        ic(google_api.get_file_name(my_doc_id))

        # Получить список всех файлов
        # ic(google_api.get_files())

        # Удалить все файлы
        # ic(google_api.delete_all_files())
    else:
        ic("Ошибка авторизации.")
