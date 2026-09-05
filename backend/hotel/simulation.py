import time

from django.db.utils import OperationalError


def start_simulation_thread() -> None:
    time.sleep(1.5)
    while True:
        try:
            from .services import tick_hotel

            tick_hotel()
        except OperationalError:
            pass
        except Exception:
            pass
        time.sleep(1.2)
