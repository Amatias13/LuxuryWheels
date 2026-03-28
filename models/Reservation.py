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
    createdAt = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

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
    def create(cls, data, extras=None):
        """Cria uma reserva calculando totalDays e totalPrice.
        Valida disponibilidade e marca o veiculo como inativo (T4).
        """
        from models.Vehicle import Vehicle
        from models.Payment import Payment
        from models.Payment_Status import PaymentStatus

        # aceitar formatos comuns: ISO YYYY-MM-DD ou DD/MM/YYYY (UI pode enviar local format)
        def parse_date(s):
            from datetime import datetime
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    return datetime.strptime(s, fmt).date()
                except Exception:
                    continue
            raise ValueError("Formato de data inválido")

        sd = parse_date(data["startDate"])
        ed = parse_date(data["endDate"])

        if ed <= sd:
            raise ValueError("A data de fim deve ser posterior à data de início")

        total_days = (ed - sd).days

        vehicle = Vehicle.query.get(data["idVehicle"])
        if not vehicle:
            raise ValueError("Veículo não encontrado")

        # Verificar disponibilidade no intervalo solicitado
        if not vehicle.is_available(sd, ed):
            raise ValueError("Veículo não disponível para o intervalo solicitado")

        total_price = total_days * vehicle.dailyRate

        # Incluir extras (dailyPrice) se fornecidos: cada extra é cobrada por dia
        extras_total = 0.0
        if extras:
            from models.Reservation_Extra import ReservationExtra

            # extras pode ser lista de ids (int) ou strings
            for ex_id in extras:
                try:
                    ex_id_int = int(ex_id)
                except (TypeError, ValueError):
                    continue
                extra_obj = ReservationExtra.query.get(ex_id_int)
                if extra_obj:
                    extras_total += extra_obj.dailyPrice * total_days

        total_price += extras_total

        # Nota: não marcar `isActive` aqui — disponibilidade é determinada por
        # reservas nos intervalos de data. Manter `isActive` para indicar se o
        # veículo existe/está ativo no catálogo, não para bloquear por reservas.

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

        # Regra: não permitir cancelamento com menos de 24 horas para o início
        from datetime import date
        today = date.today()
        if reservation.startDate and (reservation.startDate - today).days < 1:
            raise ValueError("Cancelamento não permitido nas 24 horas anteriores ao início da reserva")

        # Não alterar `isActive` ao cancelar — apenas marcar reserva como cancelada.
        vehicle = Vehicle.query.get(reservation.idVehicle)

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

        # aceitar formatos YYYY-MM-DD ou DD/MM/YYYY
        def parse_date(s):
            from datetime import datetime
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    return datetime.strptime(s, fmt).date()
                except Exception:
                    continue
            raise ValueError("Formato de data inválido")

        sd = parse_date(start_date)
        ed = parse_date(end_date)

        if ed <= sd:
            raise ValueError("A data de fim deve ser posterior à data de início")

        # Regra: não permitir alterações com menos de 24 horas para o início atual
        from datetime import date
        today = date.today()
        if reservation.startDate and (reservation.startDate - today).days < 1:
            raise ValueError("Alterações não permitidas nas 24 horas anteriores ao início da reserva")

        vehicle = Vehicle.query.get(reservation.idVehicle)

        # Verificar disponibilidade no novo intervalo, ignorando a própria reserva
        if not vehicle.is_available(sd, ed, exclude_reservation_id=reservation_id):
            raise ValueError("Veículo não disponível para o novo intervalo solicitado")

        total_days = (ed - sd).days
        reservation.startDate = sd
        reservation.endDate = ed
        reservation.totalDays = total_days
        reservation.totalPrice = total_days * vehicle.dailyRate

        return reservation
