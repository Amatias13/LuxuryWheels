from database import db


class ReservationExtra(db.Model):
    __tablename__ = "Reservation_Extra"
    idExtra = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    dailyPrice = db.Column(db.Float, nullable=False, default=0)
    isActive = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            "id": self.idExtra,
            "name": self.name,
            "dailyPrice": self.dailyPrice,
        }
