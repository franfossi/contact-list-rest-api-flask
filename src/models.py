from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

# clase para Contactos
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), unique=True)
    address = db.Column(db.String(250))
    phone = db.Column(db.String(20))
    suscription = db.relationship("Suscription", backref="contact")


    def __init__(self, full_name, email, address):
        """ crea y devuelve una instancia de esta clase """
        self.full_name = full_name
        self.email = email
        self.address = address
        

    def serialize(self):
        """ devuelve un diccionario con data del objeto """
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "address": self.address,
            "phone": self.phone,
            "suscripciones": [suscription.serialize() for suscriptions in self.suscriptions]
        }

# Clase para Grupos
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100), nullable=False)
    suscription = db.relationship("Suscription", backref="group", uselist=False)

    def __init__(self, group_name, suscription):
        """ crea y devuelve una instancia de esta clase """
        self.group_name = group_name
        self.suscription = suscription

    def serialize(self):
        """ devuelve un diccionario con data del objeto """
        return {
            "id": self.id,
            "group_name": self.group_name,
            "suscription": self.suscription
        }
    
# Clase para Suscripciones
class Suscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey("contact.id"))
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    
    def __init__(self, contact_id, group_id):
        """ crea y devuelve una instancia de esta clase """
        self.group_id = group_id
        self.contact_id = contact_id

    def serialize(self):
        """ devuelve un diccionario con data del objeto """
        return {
            "id": self.id,
            "contact_id": self.contact_id,
            "group_id": self.group_id,
            "contact_name": self.contact.full_name
           
        }