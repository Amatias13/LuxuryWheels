"""Lazy model loader."""

_MODEL_MAP = {
    "User": "User",
    "Vehicle": "Vehicle",
    "Reservation": "Reservation",
    "Payment": "Payment",
    "Vehicle_Brand": "VehicleBrand",
    "Vehicle_Type": "VehicleType",
    "Vehicle_Category": "VehicleCategory",
    "Reservation_Status": "ReservationStatus",
    "Payment_Method": "PaymentMethod",
    "Payment_Status": "PaymentStatus",
    "Testimonial": "Testimonial",
    "Reservation_Extra": "ReservationExtra",
    "Reservation_Extras_Link": "ReservationExtrasLink",
}

__all__ = list(_MODEL_MAP.values())


def load_models():
    import importlib

    for module_name, class_name in _MODEL_MAP.items():
        mod = importlib.import_module(f".{module_name}", package=__name__)
        cls = getattr(mod, class_name)
        globals()[class_name] = cls
    global __all__
    __all__ = list(_MODEL_MAP.values())


_LOADED = False


def ensure_loaded():
    """Ensure models are loaded into the `models` package globals.

    Call this at the top of modules that import from `models` (only
    necessary if you're encountering circular imports). Prefer calling
    once (e.g. from `app.py` at startup) and then using `from models import X`.
    """
    global _LOADED
    if _LOADED:
        return
    load_models()
    _LOADED = True
