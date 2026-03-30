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

    query = (
        Reservation.query.filter_by(idVehicle=vehicle_id)
        .filter(Reservation.idReservationStatus.notin_(ignore_statuses))
    )

    for r in query.all():
        if exclude_reservation_id and getattr(r, "idReservation", None) == exclude_reservation_id:
            continue
        if start_date < r.endDate and end_date > r.startDate:
            return True
    return False


def has_reservation_on(vehicle_id, day, ignore_statuses=(ReservationStates.CANCELLED,)):
    """Return True if there is any reservation that includes `day` for the vehicle."""
    from models.Reservation import Reservation

    query = (
        Reservation.query.filter_by(idVehicle=vehicle_id)
        .filter(Reservation.idReservationStatus.notin_(ignore_statuses))
    )

    for r in query.all():
        if r.startDate <= day < r.endDate:
            return True
    return False
