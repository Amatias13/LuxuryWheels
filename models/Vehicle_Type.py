from database import db


class VehicleType(db.Model):
    __tablename__ = 'Vehicle_Type'
    idType = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    def to_dict(self):
        return {'id': self.idType, 'name': self.name}
