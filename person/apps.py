from django.apps import AppConfig


class PersonConfig(AppConfig):
    name = 'person'

    def ready(self):
        import person.signals
