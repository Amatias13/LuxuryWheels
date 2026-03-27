from database import db


class VehicleBrand(db.Model):
    __tablename__ = 'Vehicle_Brand'
    idBrand = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    def to_dict(self):
        return {'id': self.idBrand, 'name': self.name}
