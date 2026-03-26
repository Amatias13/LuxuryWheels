from database import db


# Generic CRUD operations base class using Flask-SQLAlchemy session
class CRUDBase:
    def __init__(self, model):
        self.model = model

    def getModel(self):
        return self.model

    def getById(self, id):
        return db.session.get(self.model, id)

    def getByFilter(self, **filters):
        return db.session.query(self.model).filter_by(**filters).all()

    def get_all(self):
        return db.session.query(self.model).all()

    def create(self, obj_in):
        db.session.add(obj_in)
        db.session.commit()
        db.session.refresh(obj_in)
        return obj_in

    def update(self, id, obj_in):
        obj = db.session.get(self.model, id)
        for key, value in obj_in.items():
            setattr(obj, key, value)
        db.session.commit()
        db.session.refresh(obj)
        return obj

    def delete(self, id):
        obj = db.session.get(self.model, id)
        db.session.delete(obj)
        db.session.commit()