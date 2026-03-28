from datetime import datetime, date
from database import db


class Reservation(db.Model):
    __tablename__ = "Reservation"
    idReservation = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, db.ForeignKey("User.idUser"), nullable=False)
    idVehicle = db.Column(
        db.Integer, db.ForeignKey("Vehicle.idVehicle"), nullable=False
    )
    startDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date, nullable=False)
    totalDays = db.Column(db.Integer, nullable=False)
    totalPrice = db.Column(db.Float, nullable=False)
    idReservationStatus = db.Column(
        db.Integer,
        db.ForeignKey("Reservation_Status.idReservationStatus"),
        nullable=False,
        default=1,
    )
    createdAt = db.Column(db.DateTime)
    updatedAt = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.idReservation,
            "user_id": self.idUser,
            "vehicle_id": self.idVehicle,
            "startDate": str(self.startDate),
            "endDate": str(self.endDate),
            "totalDays": self.totalDays,
            "totalPrice": self.totalPrice,
            "status_id": self.idReservationStatus,
        }

    @classmethod
    def create(cls, data):
        """Cria uma reserva calculando totalDays e totalPrice.
        Valida disponibilidade e marca o veiculo como inativo (T4).
        """
        from models.Vehicle import Vehicle
        from models.Payment import Payment
        from models.Payment_Status import PaymentStatus

        sd = datetime.strptime(data["startDate"], "%Y-%m-%d").date()
        ed = datetime.strptime(data["endDate"], "%Y-%m-%d").date()

        if ed <= sd:
            raise ValueError("A data de fim deve ser posterior à data de início")

        total_days = (ed - sd).days

        vehicle = Vehicle.query.get(data["idVehicle"])
        if not vehicle:
            raise ValueError("Veículo não encontrado")
        if not vehicle.is_available():
            raise ValueError("Veículo não disponível para reserva")

        total_price = total_days * vehicle.dailyRate

        # T4: marcar veiculo como inativo
        vehicle.isActive = 0

        reservation = cls(
            idUser=data["idUser"],
            idVehicle=vehicle.idVehicle,
            startDate=sd,
            endDate=ed,
            totalDays=total_days,
            totalPrice=total_price,
            idReservationStatus=1,  # Pendente
        )

        return reservation, vehicle, total_price

    @classmethod
    def cancel(cls, reservation_id, user_id):
        """Cancela uma reserva e recoloca o veiculo disponivel."""
        from models.Vehicle import Vehicle

        reservation = cls.query.filter_by(
            idReservation=reservation_id, idUser=user_id
        ).first()

        if not reservation:
            raise ValueError("Reserva não encontrada")
        if reservation.idReservationStatus == 3:
            raise ValueError("Reserva já cancelada")

        # Recolocar veiculo disponivel
        vehicle = Vehicle.query.get(reservation.idVehicle)
        if vehicle:
            vehicle.isActive = 1

        reservation.idReservationStatus = 3  # Cancelada

        return reservation

    @classmethod
    def update_dates(cls, reservation_id, user_id, start_date, end_date):
        """Altera as datas de uma reserva e recalcula o total."""
        from models.Vehicle import Vehicle

        reservation = cls.query.filter_by(
            idReservation=reservation_id, idUser=user_id
        ).first()

        if not reservation:
            raise ValueError("Reserva não encontrada")
        if reservation.idReservationStatus == 3:
            raise ValueError("Não é possível alterar uma reserva cancelada")

        sd = datetime.strptime(start_date, "%Y-%m-%d").date()
        ed = datetime.strptime(end_date, "%Y-%m-%d").date()

        if ed <= sd:
            raise ValueError("A data de fim deve ser posterior à data de início")

        vehicle = Vehicle.query.get(reservation.idVehicle)
        total_days = (ed - sd).days
        reservation.startDate = sd
        reservation.endDate = ed
        reservation.totalDays = total_days
        reservation.totalPrice = total_days * vehicle.dailyRate

        return reservation
