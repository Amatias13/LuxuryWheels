from datetime import datetime
from database import db
from models.Status import ReservationStates, PaymentStates


class Payment(db.Model):
    __tablename__ = "Payment"
    idPayment = db.Column(db.Integer, primary_key=True)
    idReservation = db.Column(
        db.Integer, db.ForeignKey("Reservation.idReservation"), nullable=False
    )
    idPaymentMethod = db.Column(
        db.Integer, db.ForeignKey("Payment_Method.idPaymentMethod"), nullable=False
    )
    amount = db.Column(db.Float, nullable=False)
    paymentDate = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    idPaymentStatus = db.Column(
        db.Integer,
        db.ForeignKey("Payment_Status.idPaymentStatus"),
        nullable=False,
        default=PaymentStates.PENDING,
    )

    def to_dict(self):
        return {
            "id": self.idPayment,
            "reservation_id": self.idReservation,
            "payment_method_id": self.idPaymentMethod,
            "amount": self.amount,
            "paymentDate": str(self.paymentDate),
            "payment_status_id": self.idPaymentStatus,
        }

    @classmethod
    def create(cls, reservation_id, payment_method_id, amount):
        """Cria um pagamento para uma reserva e confirma a reserva."""
        from models.Reservation import Reservation

        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            raise ValueError("Reserva não encontrada")

        payment = cls(
            idReservation=reservation_id,
            idPaymentMethod=int(payment_method_id),
            amount=amount,
            idPaymentStatus=PaymentStates.COMPLETED,  # Concluído
        )
        # Confirmar reserva
        reservation.idReservationStatus = ReservationStates.CONFIRMED  # Confirmada

        return payment, reservation
