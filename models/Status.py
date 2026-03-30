"""Constants for reservation and payment states.

Keep simple integer constants to match values stored in the DB.
"""

class ReservationStates:
    PENDING = 1
    CONFIRMED = 2
    CANCELLED = 3
    COMPLETED = 4


class PaymentStates:
    PENDING = 1
    COMPLETED = 2
    FAILED = 3
