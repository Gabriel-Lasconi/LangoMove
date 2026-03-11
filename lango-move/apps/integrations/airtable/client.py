import requests
from django.conf import settings


class AirtableClient:
    BASE_URL = "https://api.airtable.com/v0"

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
            if offset:
                params["offset"] = offset

            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            all_records.extend(data.get("records", []))
            offset = data.get("offset")

            if not offset:
                break

        return all_records