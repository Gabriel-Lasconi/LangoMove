from django.conf import settings
from .client import AirtableClient


class AirtableContentService:
    def __init__(self) -> None:
        self.client = AirtableClient()

    def _records_to_dict(self, records: list[dict], key_field: str = "name") -> dict:
        result = {}
        for record in records:
            result[record["id"]] = {
                "id": record["id"],
                **record.get("fields", {}),
            }
        return result

    def get_vocabulary_map(self) -> dict:
        records = self.client.list_records(settings.AIRTABLE_TABLES["vocabulary"])
        return self._records_to_dict(records)

    def get_phrases_map(self) -> dict:
        records = self.client.list_records(settings.AIRTABLE_TABLES["phrases"])
        return self._records_to_dict(records)

    def get_languages_map(self) -> dict:
        records = self.client.list_records(settings.AIRTABLE_TABLES["languages"])
        return self._records_to_dict(records)

    def get_age_groups_map(self) -> dict:
        records = self.client.list_records(settings.AIRTABLE_TABLES["age_groups"])
        return self._records_to_dict(records)

    def get_topics_map(self) -> dict:
        records = self.client.list_records(settings.AIRTABLE_TABLES["topics"])
        return self._records_to_dict(records)

    def get_games_map(self) -> dict:
        records = self.client.list_records(settings.AIRTABLE_TABLES["games"])
        return self._records_to_dict(records)

    def get_game_by_slug(self, slug: str) -> dict | None:
        records = self.client.list_records(settings.AIRTABLE_TABLES["games"])

        for record in records:
            fields = record.get("fields", {})
            if fields.get("slug") == slug and fields.get("status") == "published":
                return {
                    "airtable_id": record["id"],
                    "name": fields.get("name", ""),
                    "name_fr": fields.get("name-fr", ""),
                    "slug": fields.get("slug", ""),
                    "main_image": fields.get("main-image", []),
                    "duration_minutes": fields.get("duration-minutes", 0),
                    "description": fields.get("description", ""),
                    "description_fr": fields.get("description-fr", ""),
                    "variants": fields.get("variants", ""),
                    "materials_needed": fields.get("materials-needed", ""),
                    "activity_type": fields.get("activity-type", ""),
                    "notes_for_facilitator": fields.get("notes-for-facilitator", ""),
                    "status": fields.get("status", ""),
                }
        return None

    def get_vocabulary_for_game(self, game_airtable_id: str) -> list[dict]:
        vocabulary_map = self.get_vocabulary_map()
        languages_map = self.get_languages_map()
        records = self.client.list_records(settings.AIRTABLE_TABLES["game_vocabulary"])

        result = []
        for record in records:
            fields = record.get("fields", {})
            game_ids = fields.get("game", [])
            if not game_ids or game_ids[0] != game_airtable_id:
                continue

            vocabulary_ids = fields.get("vocabulary", [])
            vocabulary = vocabulary_map.get(vocabulary_ids[0], {}) if vocabulary_ids else {}

            language_ids = vocabulary.get("language-code", [])
            language = languages_map.get(language_ids[0], {}) if language_ids else {}

            result.append({
                "word": vocabulary.get("word", ""),
                "word_fr": vocabulary.get("word-fr", ""),
                "category": vocabulary.get("category", ""),
                "part_of_speech": vocabulary.get("part-of-speech", ""),
                "phonetic": vocabulary.get("phonetic", ""),
                "audio_file": vocabulary.get("audio-file", []),
                "audio_status": vocabulary.get("audio-status", ""),
                "language_code": language.get("code", ""),
                "language_name": language.get("name", ""),
                "flashcard_pdf": vocabulary.get("flashcard-pdf", []),
                "importance": fields.get("importance", ""),
                "display_order": fields.get("display-order", 9999),
                "notes": fields.get("notes", ""),
            })

        return sorted(result, key=lambda x: x["display_order"])

    def get_phrases_for_game(self, game_airtable_id: str) -> list[dict]:
        phrases_map = self.get_phrases_map()
        languages_map = self.get_languages_map()
        records = self.client.list_records(settings.AIRTABLE_TABLES["game_phrases"])

        result = []
        for record in records:
            fields = record.get("fields", {})
            game_ids = fields.get("game", [])
            if not game_ids or game_ids[0] != game_airtable_id:
                continue

            phrase_ids = fields.get("phrase", [])
            phrase = phrases_map.get(phrase_ids[0], {}) if phrase_ids else {}

            language_ids = phrase.get("language-code", [])
            language = languages_map.get(language_ids[0], {}) if language_ids else {}

            result.append({
                "text": phrase.get("text", ""),
                "text_fr": phrase.get("text-fr", ""),
                "phrase_type": phrase.get("phrase-type", ""),
                "phonetic": phrase.get("phonetic", ""),
                "audio_file": phrase.get("audio-file", []),
                "audio_status": phrase.get("audio-status", ""),
                "language_code": language.get("code", ""),
                "language_name": language.get("name", ""),
                "importance": fields.get("importance", ""),
                "display_order": fields.get("display-order", 9999),
                "notes": fields.get("notes", ""),
            })

        return sorted(result, key=lambda x: x["display_order"])

    def get_game_detail_payload(self, slug: str) -> dict | None:
        game = self.get_game_by_slug(slug)
        if not game:
            return None

        vocabulary = self.get_vocabulary_for_game(game["airtable_id"])
        phrases = self.get_phrases_for_game(game["airtable_id"])

        return {
            "game": game,
            "vocabulary": vocabulary,
            "phrases": phrases,
        }

    def get_all_vocabulary(self) -> list[dict]:
        records = self.client.list_records(settings.AIRTABLE_TABLES["vocabulary"])
        languages_map = self.get_languages_map()
        result = []

        for record in records:
            fields = record.get("fields", {})

            language_ids = fields.get("language-code", [])
            language = languages_map.get(language_ids[0], {}) if language_ids else {}

            result.append({
                "airtable_id": record["id"],
                "word": fields.get("word", ""),
                "word_fr": fields.get("word-fr", ""),
                "category": fields.get("category", ""),
                "part_of_speech": fields.get("part-of-speech", ""),
                "phonetic": fields.get("phonetic", ""),
                "audio_file": fields.get("audio-file", []),
                "audio_status": fields.get("audio-status", ""),
                "language_code": language.get("code", ""),
                "language_name": language.get("name", ""),
                "flashcard_pdf": fields.get("flashcard-pdf", []),
            })

        return result

    def get_all_phrases(self) -> list[dict]:
        records = self.client.list_records(settings.AIRTABLE_TABLES["phrases"])
        languages_map = self.get_languages_map()
        result = []

        for record in records:
            fields = record.get("fields", {})

            language_ids = fields.get("language-code", [])
            language = languages_map.get(language_ids[0], {}) if language_ids else {}

            result.append({
                "airtable_id": record["id"],
                "text": fields.get("text", ""),
                "text_fr": fields.get("text-fr", ""),
                "phrase_type": fields.get("phrase-type", ""),
                "phonetic": fields.get("phonetic", ""),
                "audio_file": fields.get("audio-file", []),
                "audio_status": fields.get("audio-status", ""),
                "language_code": language.get("code", ""),
                "language_name": language.get("name", ""),
            })

        return result

    def get_published_courses(self) -> list[dict]:
        language_map = self.get_languages_map()
        age_group_map = self.get_age_groups_map()

        records = self.client.list_records(settings.AIRTABLE_TABLES["courses"])
        courses = []

        for record in records:
            fields = record.get("fields", {})
            if fields.get("status") != "published":
                continue

            language_ids = fields.get("language", [])
            age_group_ids = fields.get("age-group", [])

            language = language_map.get(language_ids[0], {}) if language_ids else {}
            age_group = age_group_map.get(age_group_ids[0], {}) if age_group_ids else {}

            courses.append({
                "airtable_id": record["id"],
                "title": fields.get("title", ""),
                "slug": fields.get("slug", ""),
                "description": fields.get("description", ""),
                "sessions_count": fields.get("sessions-count", 0),
                "minutes_per_session": fields.get("minutes-per-session", 0),
                "language_name": language.get("name", ""),
                "language_flag": language.get("flag", ""),
                "age_group_name": age_group.get("name", ""),
                "display_order": fields.get("display-order", 9999),
            })

        return sorted(courses, key=lambda c: c["display_order"])

    def get_course_by_slug(self, slug: str) -> dict | None:
        for course in self.get_published_courses():
            if course["slug"] == slug:
                return course
        return None

    def get_sessions_for_course(self, course_airtable_id: str) -> list[dict]:
        topic_map = self.get_topics_map()
        records = self.client.list_records(settings.AIRTABLE_TABLES["sessions"])

        sessions = []
        for record in records:
            fields = record.get("fields", {})
            if fields.get("status") != "published":
                continue

            course_ids = fields.get("course", [])
            if not course_ids or course_ids[0] != course_airtable_id:
                continue

            topic_ids = fields.get("topic", [])
            topic = topic_map.get(topic_ids[0], {}) if topic_ids else {}

            sessions.append({
                "airtable_id": record["id"],
                "session_id": fields.get("session-id"),
                "session_number": fields.get("session-number", 0),
                "title": fields.get("title", ""),
                "full_title": fields.get("full-title", ""),
                "slug": fields.get("slug", ""),
                "topic_name": topic.get("name", ""),
                "grammar_objectives": fields.get("grammar-objectives", ""),
                "action_objectives": fields.get("action-objectives", ""),
                "lexical_objectives": fields.get("lexical-objectives", ""),
                "teacher_notes": fields.get("teacher-notes", ""),
            })

        return sorted(sessions, key=lambda s: s["session_number"])

    def get_session_by_slug(self, slug: str) -> dict | None:
        records = self.client.list_records(settings.AIRTABLE_TABLES["sessions"])
        for record in records:
            fields = record.get("fields", {})
            if fields.get("slug") == slug and fields.get("status") == "published":
                return {
                    "airtable_id": record["id"],
                    "session_id": fields.get("session-id"),
                    "session_number": fields.get("session-number", 0),
                    "title": fields.get("title", ""),
                    "full_title": fields.get("full-title", ""),
                    "slug": fields.get("slug", ""),
                    "grammar_objectives": fields.get("grammar-objectives", ""),
                    "action_objectives": fields.get("action-objectives", ""),
                    "lexical_objectives": fields.get("lexical-objectives", ""),
                    "teacher_notes": fields.get("teacher-notes", ""),
                    "course_ids": fields.get("course", []),
                }
        return None

    def get_games_for_session(self, session_airtable_id: str) -> list[dict]:
        games_map = self.get_games_map()
        records = self.client.list_records(settings.AIRTABLE_TABLES["session_games"])

        session_games = []
        for record in records:
            fields = record.get("fields", {})
            if fields.get("status") != "published":
                continue

            session_ids = fields.get("session", [])
            if not session_ids or session_ids[0] != session_airtable_id:
                continue

            game_ids = fields.get("game", [])
            game = games_map.get(game_ids[0], {}) if game_ids else {}

            session_games.append({
                "airtable_id": record["id"],
                "order_in_session": fields.get("order-in-session", 0),
                "stage_name": fields.get("stage-name", ""),
                "duration_minutes": fields.get("duration-minutes", 0),
                "notes": fields.get("notes", ""),
                "game_name": game.get("name", ""),
                "game_name_fr": game.get("name-fr", ""),
                "game_slug": game.get("slug", ""),
                "game_description": game.get("description", ""),
                "game_description_fr": game.get("description-fr", ""),
                "game_variants": game.get("variants", ""),
                "vocabulary_tags": game.get("vocabulary-tags", []),
            })

        return sorted(session_games, key=lambda g: g["order_in_session"])