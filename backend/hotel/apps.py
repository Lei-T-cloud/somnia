import threading

from django.apps import AppConfig


class HotelConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hotel"
    verbose_name = "数字孪生"

    def ready(self) -> None:
        from .simulation import start_simulation_thread

        threading.Thread(target=start_simulation_thread, daemon=True).start()
