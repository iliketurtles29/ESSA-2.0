from django.apps import AppConfig


class EssaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'essa'

    def ready(self):
        import essa.signals  # noqa: F401

    
