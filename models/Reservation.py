from datetime import datetime
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
        }

    @classmethod
    def create(cls, data):
        """Create a reservation, automatically calculating totalDays and totalPrice.
        Called by generic_api on POST /api/reservation
        """
        from models.Vehicle import Vehicle

        sd = datetime.strptime(data["startDate"], "%Y-%m-%d").date()
        ed = datetime.strptime(data["endDate"], "%Y-%m-%d").date()
        total_days = (ed - sd).days or 1

        vehicle = Vehicle.query.get(data["idVehicle"])
        if not vehicle:
            raise ValueError("Veiculo nao encontrado")

        data["startDate"] = sd
        data["endDate"] = ed
        data["totalDays"] = total_days
        data["totalPrice"] = total_days * vehicle.dailyRate

        cols = {c.name for c in cls.__table__.columns}
        return cls(**{k: v for k, v in data.items() if k in cols})
