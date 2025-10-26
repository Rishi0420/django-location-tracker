from django.apps import AppConfig


class TrackerAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tracker_app'

    def ready(self):
        import tracker_app.models  # If signals.py had been created, it would have been imported
