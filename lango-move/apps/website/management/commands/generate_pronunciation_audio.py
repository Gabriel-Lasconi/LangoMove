import asyncio
import os

import edge_tts
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.integrations.airtable.client import AirtableClient


class Command(BaseCommand):
    help = "Generate pronunciation audio for words and phrases using edge-tts and save as MP3"

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

        self.stdout.write("🎤 Generating pronunciation audio...")

        self.process_table(
            airtable=airtable,
            table_name=settings.AIRTABLE_TABLES["vocabulary"],
            text_field="word",
            folder="words",
            language_code_field="language-code",
        )

        self.process_table(
            airtable=airtable,
            table_name=settings.AIRTABLE_TABLES["phrases"],
            text_field="text",
            folder="phrases",
            language_code_field="language-code",
        )

        self.stdout.write(self.style.SUCCESS("✅ Done."))

    def process_table(self, airtable, table_name, text_field, folder, language_code_field):
        records = airtable.list_records(table_name)

        save_dir = os.path.join(settings.MEDIA_ROOT, "pronunciation", folder)
        os.makedirs(save_dir, exist_ok=True)

        for record in records:
            fields = record.get("fields", {})
            text = (fields.get(text_field) or "").strip()
            audio_status = fields.get("audio-status")

            raw_lang = fields.get(language_code_field)

            if isinstance(raw_lang, list) and raw_lang:
                raw_lang = raw_lang[0]

            language_code = self.LANG_MAP.get(
                (raw_lang or "en").strip().lower(),
                "en"
            )

            if not text or audio_status == "ready":
                continue

            filename = record["id"] + ".mp3"
            mp3_path = os.path.join(save_dir, filename)

            self.stdout.write(f"🔊 {text}")

            try:
                voice = self.pick_voice(language_code)

                if os.path.exists(mp3_path):
                    os.remove(mp3_path)

                asyncio.run(
                    self.generate_mp3(
                        text=text,
                        voice=voice,
                        output_path=mp3_path,
                    )
                )

                if not os.path.exists(mp3_path) or os.path.getsize(mp3_path) < 1000:
                    raise RuntimeError("MP3 file was not created correctly.")

                audio_url = f"http://127.0.0.1:8000{settings.MEDIA_URL}pronunciation/{folder}/{filename}"

                airtable.update_record(
                    table_name,
                    record["id"],
                    {
                        "audio-url": audio_url,
                        "audio-status": "ready",
                    },
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