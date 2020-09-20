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
    suscriptions = db.relationship("Suscription", backref="contact")


    def __init__(self, full_name, email, address, phone):
        """ crea y devuelve una instancia de esta clase """
        self.full_name = full_name
        self.email = email
        self.address = address
        self.phone = phone
     #  self.suscription = suscription
        

    def serialize(self):
        """ devuelve un diccionario con data del objeto """
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "address": self.address,
            "phone": self.phone,
            "groups": [suscription.group_id for suscription in self.suscriptions]
#           "suscriptions": [suscription.serialize() for suscription in self.suscriptions]
        }

    @classmethod
    # Método Cargar Contactos
    def add_contact():
        if request.method == "GET":
            contact = Contact.query.all()
            contact_list = list(map(lambda contact: contact.serialize(), contact))
            return jsonify(contact_list), 200
        else:
            response_body = {
                "msj":"Metodo request invalido"
            }
            return jsonify(response_body), 400

    # Método Registrar Contactos
    def register(cls, full_name, email, address, phone):
        """
            normaliza insumos full_name, email, address, phone, suscription,
            crea un objeto de la clase Contact con
            esos insumos y devuelve la instancia creada.
        """
        new_contact = cls(
            full_name.lower().capitalize(),
            email,
            address,
            phone
        #    suscription
        )
        return new_contact

    # Método Actualizar Contactos
    def update_contact(self, diccionario):
        """ actualiza propiedades del contact según el contenido del diccionario """
        if "full_name" in diccionario:
            self.full_name = diccionario["full_name"]
        if "email" in diccionario:
            self.email = diccionario["email"]
        if "address" in diccionario:
            self.address = diccionario["address"]
        if "phone" in diccionario:
            self.phone = diccionario["phone"]
       # if "suscription" in diccionario:
        #    self.suscription = diccionario["suscription"]
        return True

    def __repr__(self):
        return '<Contact %r>' % self.full_name

# Clase para Grupos
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100), nullable=False)
    suscriptions = db.relationship("Suscription", backref="group", uselist=False)

    def __init__(self, group_name):
        """ crea y devuelve una instancia de esta clase """
        self.group_name = group_name
#        self.suscription = suscription

    def serialize(self):
        """ devuelve un diccionario con data del objeto """
        return {
            "id": self.id,
            "group_name": self.group_name,
 #           "suscriptions": [suscription.serialize() for suscription in self.suscriptions]
        }

    @classmethod
    def new_group(cls, group_name):
        """ Agregar un nuevo grupo """
        new_group = cls(
            group_name.lower().capitalize())
        return new_group

    def update(self, diccionario):
        """Actualizacion de nombre de Grupo"""
        if "group_name" in diccionario:
            self.group_name = diccionario["group_name"]
        return True 

    def __repr__(self):
        return '<Group %r>' % self.group_name 
    
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