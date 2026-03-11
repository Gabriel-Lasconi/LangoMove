import asyncio
import os
import tempfile

import edge_tts
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.integrations.airtable.client import AirtableClient


class Command(BaseCommand):
    help = "Generate pronunciation audio for words and phrases using edge-tts and upload to Airtable attachment field"

    LANG_MAP = {
        "english": "en",
        "en": "en",
        "french": "fr",
        "français": "fr",
        "francais": "fr",
        "fr": "fr",
        "german": "de",
        "deutsch": "de",
        "de": "de",
        "spanish": "es",
        "español": "es",
        "espanol": "es",
        "es": "es",
        "italian": "it",
        "italien": "it",
        "it": "it",
        "portuguese": "pt",
        "portugais": "pt",
        "pt": "pt",
        "dutch": "nl",
        "néerlandais": "nl",
        "neerlandais": "nl",
        "nl": "nl",
    }

    def handle(self, *args, **options):
        airtable = AirtableClient()

        self.stdout.write("🎤 Generating pronunciation audio and uploading to Airtable...")

        self.process_table(
            airtable=airtable,
            table_name=settings.AIRTABLE_TABLES["vocabulary"],
            text_field="word",
            language_code_field="language-code",
            attachment_field="audio-file",
        )

        self.process_table(
            airtable=airtable,
            table_name=settings.AIRTABLE_TABLES["phrases"],
            text_field="text",
            language_code_field="language-code",
            attachment_field="audio-file",
        )

        self.stdout.write(self.style.SUCCESS("✅ Done."))

    def process_table(self, airtable, table_name, text_field, language_code_field, attachment_field):
        records = airtable.list_records(table_name)

        for record in records:
            fields = record.get("fields", {})
            text = (fields.get(text_field) or "").strip()
            audio_status = fields.get("audio-status")
            existing_attachment = fields.get(attachment_field)

            raw_lang = fields.get(language_code_field)
            if isinstance(raw_lang, list) and raw_lang:
                raw_lang = raw_lang[0]

            language_code = self.LANG_MAP.get(
                (raw_lang or "en").strip().lower(),
                "en"
            )

            # Skip already ready records that already have an attachment
            if not text:
                continue
            if audio_status == "ready" and existing_attachment:
                continue

            self.stdout.write(f"🔊 {text}")

            temp_file = None

            try:
                voice = self.pick_voice(language_code)

                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                    temp_file = tmp.name

                asyncio.run(
                    self.generate_mp3(
                        text=text,
                        voice=voice,
                        output_path=temp_file,
                    )
                )

                if not os.path.exists(temp_file) or os.path.getsize(temp_file) < 1000:
                    raise RuntimeError("MP3 file was not created correctly.")

                upload_response = airtable.upload_attachment(
                    table_name=table_name,
                    record_id=record["id"],
                    field_name=attachment_field,
                    file_path=temp_file,
                )

                # The upload endpoint stores the file directly in the cell.
                # Then we only need to update the status.
                airtable.update_record(
                    table_name,
                    record["id"],
                    {
                        "audio-status": "ready",
                    },
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Uploaded audio for '{text}'"
                    )
                )

            except Exception as exc:
                self.stderr.write(f"❌ Failed for '{text}': {exc}")

                try:
                    airtable.update_record(
                        table_name,
                        record["id"],
                        {
                            "audio-status": "failed",
                        },
                    )
                except Exception as update_exc:
                    self.stderr.write(
                        f"⚠️ Could not update Airtable status for '{text}': {update_exc}"
                    )

            finally:
                if temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)

    async def generate_mp3(self, text: str, voice: str, output_path: str):
        communicate = edge_tts.Communicate(text=text, voice=voice)
        await communicate.save(output_path)

    def pick_voice(self, language_code: str) -> str:
        voice_map = {
            "en": "en-US-AriaNeural",
            "fr": "fr-FR-DeniseNeural",
            "de": "de-DE-KatjaNeural",
            "es": "es-ES-ElviraNeural",
            "it": "it-IT-ElsaNeural",
            "pt": "pt-PT-RaquelNeural",
            "nl": "nl-NL-ColetteNeural",
        }
        return voice_map.get(language_code, "en-US-AriaNeural")