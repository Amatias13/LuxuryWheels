from database import db


class VehicleCategory(db.Model):
    __tablename__ = 'Vehicle_Category'
    idCategory = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    def to_dict(self):
        return {'id': self.idCategory, 'name': self.name}
