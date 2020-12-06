from django.apps import AppConfig


class BookingsConfig(AppConfig):
    name = 'bookings'

    def ready(self):
        import bookings.signals
