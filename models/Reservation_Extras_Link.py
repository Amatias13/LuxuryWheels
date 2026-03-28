from database import db


class ReservationExtrasLink(db.Model):
    __tablename__ = "Reservation_Extras_Link"
    id = db.Column(db.Integer, primary_key=True)
    idReservation = db.Column(db.Integer, db.ForeignKey("Reservation.idReservation"), nullable=False)
    idExtra = db.Column(db.Integer, db.ForeignKey("Reservation_Extra.idExtra"), nullable=False)
    dailyPrice = db.Column(db.Float, nullable=False, default=0.0)
    totalPrice = db.Column(db.Float, nullable=False, default=0.0)

    def to_dict(self):
        return {
            "id": self.id,
            "idReservation": self.idReservation,
            "idExtra": self.idExtra,
            "dailyPrice": self.dailyPrice,
            "totalPrice": self.totalPrice,
        }
