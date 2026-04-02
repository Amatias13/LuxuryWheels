"""Helper utilities for model-related operations.

Contains functions to check reservation overlaps and similar shared logic.
"""
from models.Status import ReservationStates


def has_reservation_overlap(vehicle_id, start_date, end_date, exclude_reservation_id=None, ignore_statuses=(ReservationStates.CANCELLED,)):
    """Return True if there is any reservation for `vehicle_id` that overlaps
    the [start_date, end_date) interval, ignoring the given statuses and
    optionally excluding a reservation by id.
    """
    if not (start_date and end_date):
        return False

    # Import here to avoid circular imports at module import time.
    from models.Reservation import Reservation
    from datetime import datetime

    # Normalize inputs to datetimes for precise overlap checks. Accept
    # `date` or `datetime` for start_date/end_date.
    def to_dt(v, is_end=False):
        if isinstance(v, datetime):
            return v
        # assume date
        return datetime.combine(v, datetime.min.time()) if not is_end else datetime.combine(v, datetime.min.time())

    start_dt = to_dt(start_date)
    end_dt = to_dt(end_date)

    query = (
        Reservation.query.filter_by(idVehicle=vehicle_id)
        .filter(Reservation.idReservationStatus.notin_(ignore_statuses))
    )

    for r in query.all():
        if exclude_reservation_id and getattr(r, "idReservation", None) == exclude_reservation_id:
            continue
        # Reservation model now stores datetimes in startDate/endDate
        r_start = r.startDate
        r_end = r.endDate
        if start_dt < r_end and end_dt > r_start:
            return True
    return False


def has_reservation_on(vehicle_id, day, ignore_statuses=(ReservationStates.CANCELLED,)):
    """Return True if there is any reservation that includes `day` for the vehicle."""
    from models.Reservation import Reservation
    from datetime import datetime

    query = (
        Reservation.query.filter_by(idVehicle=vehicle_id)
        .filter(Reservation.idReservationStatus.notin_(ignore_statuses))
    )

    # Treat `day` as a date; check if any reservation interval intersects that day
    day_start = datetime.combine(day, datetime.min.time())
    day_end = datetime.combine(day, datetime.max.time())

    for r in query.all():
        r_start = r.startDate
        r_end = r.endDate
        if day_start < r_end and day_end > r_start:
            return True
    return False
