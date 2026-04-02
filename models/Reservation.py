from datetime import datetime, date, time
from database import db
from utils import parse_date
from models.Status import ReservationStates
from utils import parse_time
import math


class Reservation(db.Model):
    __tablename__ = "Reservation"
    idReservation = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, db.ForeignKey("User.idUser"), nullable=False)
    idVehicle = db.Column(
        db.Integer, db.ForeignKey("Vehicle.idVehicle"), nullable=False
    )
    # store full datetimes (date + optional time)
    startDate = db.Column(db.DateTime, nullable=False)
    endDate = db.Column(db.DateTime, nullable=False)
    totalDays = db.Column(db.Integer, nullable=False)
    totalPrice = db.Column(db.Float, nullable=False)
    idReservationStatus = db.Column(
        db.Integer,
        db.ForeignKey("Reservation_Status.idReservationStatus"),
        nullable=False,
        default=ReservationStates.PENDING,
    )
    createdAt = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.idReservation,
            "user_id": self.idUser,
            "vehicle_id": self.idVehicle,
            # ISO datetimes
            "startDate": self.startDate.isoformat() if self.startDate else None,
            "endDate": self.endDate.isoformat() if self.endDate else None,
            # separate time strings for templates
            "startTime": (self.startDate.strftime('%I:%M %p') if self.startDate else None),
            "endTime": (self.endDate.strftime('%I:%M %p') if self.endDate else None),
            "totalDays": self.totalDays,
            "totalPrice": self.totalPrice,
            "status_id": self.idReservationStatus,
        }

    @classmethod
    def create(cls, data, extras=None):
        """Cria uma reserva calculando totalDays e totalPrice.
        Valida disponibilidade e marca o veiculo como inativo (T4).
        """
        from models.Vehicle import Vehicle

        # aceitar formatos comuns: ISO YYYY-MM-DD ou DD/MM/YYYY (UI pode enviar local format)
        sd = parse_date(data["startDate"])
        ed = parse_date(data["endDate"])
        # Optional times
        st = None
        et = None
        try:
            if data.get("startTime"):
                st = parse_time(data.get("startTime"))
        except ValueError:
            st = None
        try:
            if data.get("endTime"):
                et = parse_time(data.get("endTime"))
        except ValueError:
            et = None

        # Build datetimes for precise comparison
        sd_dt = datetime.combine(sd, st if st else time.min)
        ed_dt = datetime.combine(ed, et if et else time.min)

        if ed_dt <= sd_dt:
            raise ValueError("A data de fim deve ser posterior à data de início")

        # Charge by whole days; a 24-hour period counts as 1 day. Use ceil
        total_days = math.ceil((ed_dt - sd_dt).total_seconds() / 86400)

        vehicle = Vehicle.query.get(data["idVehicle"])
        if not vehicle:
            raise ValueError("Veículo não encontrado")

        # Check availability using datetimes for accurate validation, especially if times are provided
        if not vehicle.is_available(sd_dt, ed_dt):
            raise ValueError("Veículo não disponível para o intervalo solicitado")

        total_price = total_days * vehicle.dailyRate

        # Includes extras (dailyPrice) if provided: each extra is charged per day
        extras_total = 0.0
        if extras:
            from models.Reservation_Extra import ReservationExtra

            # extras can be a list of ids (int) or strings
            for ex_id in extras:
                try:
                    ex_id_int = int(ex_id)
                except (TypeError, ValueError):
                    continue
                extra_obj = ReservationExtra.query.get(ex_id_int)
                if extra_obj:
                    extras_total += extra_obj.dailyPrice * total_days

        total_price += extras_total

        reservation = cls(
            idUser=data["idUser"],
            idVehicle=vehicle.idVehicle,
            startDate=sd_dt,
            endDate=ed_dt,
            totalDays=total_days,
            totalPrice=total_price,
            idReservationStatus=ReservationStates.PENDING,  # PENDING
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
        if reservation.idReservationStatus == ReservationStates.CANCELLED:
            raise ValueError("Reserva já cancelada")

        # Rule: do not allow cancellation if the reservation has already started
        from datetime import date
        today = date.today()
        if reservation.startDate and today >= reservation.startDate.date():
            raise ValueError("Não é possível cancelar uma reserva que já começou")
        # Additional rule: do not allow cancellation within 24 hours of the start date
        if reservation.startDate and (reservation.startDate.date() - today).days < 1:
            raise ValueError(
                "Cancelamento não permitido nas 24 horas anteriores ao início da reserva"
            )

        # Do not change `isActive` on cancel — just mark reservation as cancelled. The vehicle's availability logic should ignore cancelled reservations.
        vehicle = Vehicle.query.get(reservation.idVehicle)

        reservation.idReservationStatus = ReservationStates.CANCELLED  # Cancelled

        return reservation

    @classmethod
    def update_dates(cls, reservation_id, user_id, start_date, end_date, start_time=None, end_time=None):
        """Altera as datas de uma reserva e recalcula o total."""
        from models.Vehicle import Vehicle

        reservation = cls.query.filter_by(
            idReservation=reservation_id, idUser=user_id
        ).first()

        if not reservation:
            raise ValueError("Reserva não encontrada")
        if reservation.idReservationStatus == ReservationStates.CANCELLED:
            raise ValueError("Não é possível alterar uma reserva cancelada")

        sd = parse_date(start_date)
        ed = parse_date(end_date)
        # parse optional time parameters (prefer explicit args)
        st = None
        et = None
        try:
            if start_time:
                st = parse_time(start_time)
        except Exception:
            st = None
        try:
            if end_time:
                et = parse_time(end_time)
        except Exception:
            et = None

        sd_dt = datetime.combine(sd, st if st else time.min)
        ed_dt = datetime.combine(ed, et if et else time.min)

        if ed_dt <= sd_dt:
            raise ValueError("A data de fim deve ser posterior à data de início")

        # Rule: do not allow changes within 24 hours of the current start date
        from datetime import date
        today = date.today()
        if reservation.startDate and (reservation.startDate.date() - today).days < 1:
            raise ValueError("Alterações não permitidas nas 24 horas anteriores ao início da reserva")

        vehicle = Vehicle.query.get(reservation.idVehicle)

        # Check availability for the new interval, excluding the current reservation to allow changes within the same slot
        if not vehicle.is_available(sd_dt, ed_dt, exclude_reservation_id=reservation_id):
            raise ValueError("Veículo não disponível para o novo intervalo solicitado")

        total_days = math.ceil((ed_dt - sd_dt).total_seconds() / 86400)
        reservation.startDate = sd_dt
        reservation.endDate = ed_dt
        reservation.totalDays = total_days
        reservation.totalPrice = total_days * vehicle.dailyRate

        return reservation
