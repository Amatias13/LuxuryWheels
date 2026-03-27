from database import db


class Vehicle(db.Model):
    __tablename__ = 'Vehicle'
    idVehicle = db.Column(db.Integer, primary_key=True)
    idBrand = db.Column(db.Integer)
    model = db.Column(db.String, nullable=False)
    idCategory = db.Column(db.Integer)
    idType = db.Column(db.Integer)
    dailyRate = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    imageUrl = db.Column(db.String)

    lastRevisionDate = db.Column(db.Date)
    nextRevisionDate = db.Column(db.Date)
    lastLegalizationDate = db.Column(db.Date)

    isActive = db.Column(db.Integer, default=1)
    createdAt = db.Column(db.DateTime)
    updatedAt = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.idVehicle,
            'model': self.model,
            'dailyRate': self.dailyRate,
            'capacity': self.capacity,
            'imageUrl': self.imageUrl
        }
