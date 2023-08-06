from django.db import models


class Language(models.TextChoices):
    """
    Enumeration class defining various languages and their display names.
    """

    ENGLISH = "ENGLISH", "English"
    ESPAÑOL = "ESPAÑOL", "Español"
    CHINESE = "中国", "中国"
    ARABIC = "العربية", "العربية"
    RUSSIAN = "РУССКИЙ", "Русский"
    JAPANESE = "日本語", "日本語"
    UKRAINIAN = "УКРАЇНСЬКА", "Українська"
    GERMAN = "DEUTSCH", "Deutsch"
    FRENCH = "FRANÇAISE", "Française"
