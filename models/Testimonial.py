from database import db


class Testimonial(db.Model):
    __tablename__ = "Testimonial"
    idTestimonial = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    designation = db.Column(db.String)
    description = db.Column(db.String, nullable=False)
    imageUrl = db.Column(db.String)
    isActive = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            "id": self.idTestimonial,
            "name": self.name,
            "designation": self.designation,
            "description": self.description,
            "imageUrl": self.imageUrl,
        }
