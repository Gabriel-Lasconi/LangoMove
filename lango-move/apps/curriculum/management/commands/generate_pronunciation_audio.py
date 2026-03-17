import asyncio
import os
import tempfile

import edge_tts
from django.core.files import File
from django.core.management.base import BaseCommand

from apps.curriculum.models import PhraseTranslation, VocabularyTranslation


class Command(BaseCommand):
    help = "Generate pronunciation audio for vocabulary and phrases using edge-tts and save into Django media storage"

    LANG_VOICE_MAP = {
        "en": "en-US-AriaNeural",
        "fr": "fr-FR-DeniseNeural",
        "de": "de-DE-KatjaNeural",
        "es": "es-ES-ElviraNeural",
        "it": "it-IT-ElsaNeural",
        "pt": "pt-PT-RaquelNeural",
        "nl": "nl-NL-ColetteNeural",
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Regenerate audio even if a file already exists",
        )
        parser.add_argument(
            "--type",
            choices=["all", "vocabulary", "phrases"],
            default="all",
            help="Choose what to generate",
        )

    def handle(self, *args, **options):
        force = options["force"]
        item_type = options["type"]

        self.stdout.write(self.style.NOTICE("Generating pronunciation audio..."))

        if item_type in ["all", "vocabulary"]:
            self.process_vocabulary(force=force)

        if item_type in ["all", "phrases"]:
            self.process_phrases(force=force)

        self.stdout.write(self.style.SUCCESS("Done."))

    def process_vocabulary(self, force=False):
        queryset = VocabularyTranslation.objects.select_related("language").all()

        created_count = 0
        skipped_count = 0
        failed_count = 0

        for item in queryset:
            text = (item.word or "").strip()
            language_code = (item.language.code or "").strip().lower()

            if not text:
                skipped_count += 1
                continue

            if item.audio_file and not force:
                skipped_count += 1
                continue

            try:
                self.generate_and_attach_audio(
                    instance=item,
                    text=text,
                    language_code=language_code,
                    filename_stem=f"vocab_{item.id}_{self.slugify_filename(text)}",
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Vocabulary audio created: {text} [{language_code}]"))
            except Exception as exc:
                failed_count += 1
                self.stderr.write(f"Failed vocabulary '{text}' [{language_code}]: {exc}")

        self.stdout.write(
            self.style.NOTICE(
                f"Vocabulary finished. Created: {created_count}, Skipped: {skipped_count}, Failed: {failed_count}"
            )
        )

    def process_phrases(self, force=False):
        queryset = PhraseTranslation.objects.select_related("language").all()

        created_count = 0
        skipped_count = 0
        failed_count = 0

        for item in queryset:
            text = (item.text or "").strip()
            language_code = (item.language.code or "").strip().lower()

            if not text:
                skipped_count += 1
                continue

            if item.audio_file and not force:
                skipped_count += 1
                continue

            try:
                self.generate_and_attach_audio(
                    instance=item,
                    text=text,
                    language_code=language_code,
                    filename_stem=f"phrase_{item.id}_{self.slugify_filename(text)}",
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Phrase audio created: {text[:60]} [{language_code}]"))
            except Exception as exc:
                failed_count += 1
                self.stderr.write(f"Failed phrase '{text[:60]}' [{language_code}]: {exc}")

        self.stdout.write(
            self.style.NOTICE(
                f"Phrases finished. Created: {created_count}, Skipped: {skipped_count}, Failed: {failed_count}"
            )
        )

    def generate_and_attach_audio(self, instance, text, language_code, filename_stem):
        voice = self.pick_voice(language_code)

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                temp_path = tmp.name

            asyncio.run(self.generate_mp3(text=text, voice=voice, output_path=temp_path))

            if not os.path.exists(temp_path) or os.path.getsize(temp_path) < 1000:
                raise RuntimeError("Generated MP3 is missing or too small.")

            final_name = f"{filename_stem}.mp3"

            if instance.audio_file:
                instance.audio_file.delete(save=False)

            with open(temp_path, "rb") as audio_handle:
                instance.audio_file.save(final_name, File(audio_handle), save=False)

            instance.save(update_fields=["audio_file", "updated_at"])

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    async def generate_mp3(self, text: str, voice: str, output_path: str):
        communicate = edge_tts.Communicate(text=text, voice=voice)
        await communicate.save(output_path)

    def pick_voice(self, language_code: str) -> str:
        return self.LANG_VOICE_MAP.get(language_code, "en-US-AriaNeural")

    def slugify_filename(self, value: str) -> str:
        cleaned = "".join(char.lower() if char.isalnum() else "_" for char in value.strip())
        cleaned = "_".join(part for part in cleaned.split("_") if part)
        return cleaned[:60] or "audio"