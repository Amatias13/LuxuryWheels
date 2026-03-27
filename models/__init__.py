"""Lazy model loader.

Importing this package does not load model modules immediately. Call
`load_models()` after the Flask app and database have been initialized to
import and register SQLAlchemy models.
"""

_MODEL_MAP = {
	'User': 'User',
	'Vehicle': 'Vehicle',
	'Reservation': 'Reservation',
	'Payment': 'Payment',
	'Vehicle_Brand': 'VehicleBrand',
	'Vehicle_Type': 'VehicleType',
	'Vehicle_Category': 'VehicleCategory',
	'Reservation_Status': 'ReservationStatus',
	'Payment_Method': 'PaymentMethod',
	'Payment_Status': 'PaymentStatus',
}

__all__ = list(_MODEL_MAP.values())


def load_models():
	"""Import model modules and populate package attributes.

	Call this after the database (`database.init_db(app)`) has been run so that
	SQLAlchemy `db` is available for model definitions.
	"""
	import importlib
	for module_name, class_name in _MODEL_MAP.items():
		mod = importlib.import_module(f'.{module_name}', package=__name__)
		cls = getattr(mod, class_name)
		globals()[class_name] = cls
	# refresh __all__ to exported class names
	global __all__
	__all__ = list(_MODEL_MAP.values())

