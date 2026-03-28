from werkzeug.security import generate_password_hash, check_password_hash
from database import db


class User(db.Model):
    __tablename__ = "User"
    idUser = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String, nullable=False)
    lastName = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    passwordHash = db.Column(db.String, nullable=False)
    phone = db.Column(db.String)
    createdAt = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.idUser,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "email": self.email,
            "phone": self.phone,
        }

    @classmethod
    def create(cls, data):
        """create a new user, automatically hashing the password.
        Called by generic_api on POST /api/user
        """
        password = data.pop("password", None)
        if not password:
            raise ValueError("Password e obrigatoria")
        if cls.query.filter_by(email=data.get("email")).first():
            raise ValueError("Email ja registado")
        data["passwordHash"] = generate_password_hash(password)
        cols = {c.name for c in cls.__table__.columns}
        return cls(**{k: v for k, v in data.items() if k in cols})

    @classmethod
    def login(cls, email, password):
        """Verifica credenciais e devolve o utilizador ou None.
        Equivalente JS a: User.findOne({ email }) + bcrypt.compare()
        """
        user = cls.query.filter_by(email=email).first()
        if user and check_password_hash(user.passwordHash, password):
            return user
        return None
