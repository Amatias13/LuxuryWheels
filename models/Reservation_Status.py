from database import db


class ReservationStatus(db.Model):
    __tablename__ = 'Reservation_Status'
    idReservationStatus = db.Column(db.Integer, primary_key=True)
    statusName = db.Column(db.String, nullable=False, unique=True)

    def to_dict(self):
        return {'id': self.idReservationStatus, 'statusName': self.statusName}
