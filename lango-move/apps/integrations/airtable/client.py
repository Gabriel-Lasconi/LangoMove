import base64
import mimetypes
from pathlib import Path

import requests
from django.conf import settings


class AirtableClient:
    BASE_URL = "https://api.airtable.com/v0"
    CONTENT_BASE_URL = "https://content.airtable.com/v0"

    def __init__(self) -> None:
        self.base_id = settings.AIRTABLE_BASE_ID
        self.token = settings.AIRTABLE_API_TOKEN

        if not self.base_id or not self.token:
            raise ValueError("Airtable credentials are missing in settings/environment variables.")

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def list_records(self, table_name: str, view: str | None = None) -> list[dict]:
        url = f"{self.BASE_URL}/{self.base_id}/{table_name}"
        params = {}
        if view:
            params["view"] = view

        all_records: list[dict] = []
        offset = None

        while True:
            current_params = params.copy()
            if offset:
                current_params["offset"] = offset

            response = requests.get(
                url,
                headers=self.headers,
                params=current_params,
                timeout=90,
            )
            response.raise_for_status()
            data = response.json()

            all_records.extend(data.get("records", []))
            offset = data.get("offset")

            if not offset:
                break

        return all_records

    def update_record(self, table_name: str, record_id: str, fields: dict) -> dict:
        url = f"{self.BASE_URL}/{self.base_id}/{table_name}/{record_id}"
        payload = {"fields": fields}

        response = requests.patch(
            url,
            headers=self.headers,
            json=payload,
            timeout=90,
        )

        if not response.ok:
            print("Airtable update failed")
            print("Payload:", payload)
            print("Status:", response.status_code)
            print("Response:", response.text)

        response.raise_for_status()
        return response.json()

    def upload_attachment(
        self,
        table_name: str,
        record_id: str,
        field_name: str,
        file_path: str,
    ) -> dict:
        """
        Upload file bytes directly to an Airtable attachment field.
        Returns the JSON response from Airtable's upload-attachment endpoint.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Attachment file not found: {file_path}")

        mime_type, _ = mimetypes.guess_type(str(path))
        mime_type = mime_type or "application/octet-stream"

        file_bytes = path.read_bytes()
        encoded = base64.b64encode(file_bytes).decode("utf-8")

        url = (
            f"{self.CONTENT_BASE_URL}/{self.base_id}/"
            f"{record_id}/{field_name}/uploadAttachment"
        )

        payload = {
            "filename": path.name,
            "contentType": mime_type,
            "file": encoded,
        }

        response = requests.post(
            url,
            headers=self.headers,
            json=payload,
            timeout=90,
        )

        if not response.ok:
            print("Airtable attachment upload failed")
            print("URL:", url)
            print("Payload filename:", payload["filename"])
            print("Status:", response.status_code)
            print("Response:", response.text)

        response.raise_for_status()
        return response.json()