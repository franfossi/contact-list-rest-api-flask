"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Contact, Group, Suscription
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }
    return jsonify(response_body), 200

# ---- Endpoints Contact -----

# ---- 1.- Obtenga una lista de todos los contactos GET /contact/all -----
@app.route("/contact/all", methods=["GET"])
def all_contacts():
    """
        "GET": devolver lista de todos los contacts
    """
    #   seleccionar todos los registros de la tabla contact - usando flask-sqlalchemy
    #   crear una variable lista y asignarle todos los contacts que devuelva la consulta
    contacts = Contact.query.all()
    # verificamos si hay parámetros en la url y filtramos la lista con eso
    full_name = request.args.get("full_name")
    if full_name is not None:
        contacts_filtrados = filter(lambda contact: full_name.lower() in contact.full_name.lower(), contacts)
    else:
        contacts_filtrados = contacts
        #   serializar los objetos de la lista - tendría una lista de diccionarios
        contacts_serializados = list(map(lambda contact: contact.serialize(), contacts_filtrados))
        print(contacts_serializados)
        #   devolver la lista jsonificada y 200_OK
    return jsonify(contacts_serializados), 200


# ---- 2.- Crear un nuevo Contacto POST /contact -----
@app.route("/contact", methods=["POST"])
def register_contact():
    """ 
        "POST": crear un contact y devolver su información 
    """
    #  crear una variable y asignarle diccionario con datos para crear contacto
    data_contact = request.json # request.get_json()
    if data_contact is None:
        return jsonify({
            "resultado": "no envió datos para crear el contacto..."
        }), 400
    #   verificar que el diccionario tenga full_name, email, address, phone
    if (
        "full_name" not in data_contact or
        "email" not in data_contact or
        "address" not in data_contact or
        "phone" not in data_contact
    ):
        return jsonify({
            "resultado": "revise las propiedades de su solicitud"
        }), 400
    #   validar que campos no vengan vacíos 
    if (
        data_contact["full_name"] == "" or
        data_contact["email"] == "" or
        data_contact["address"] == "" or
        data_contact["phone"] == ""
    ):
        return jsonify({
            "resultado": "revise los valores de su solicitud"
            }), 400
    #   crear una variable y asignarle el nuevo contact con los datos validados
    new_contact = Contact(
        full_name=data_contact["full_name"], 
        email=data_contact["email"], 
        address=data_contact["address"], 
        phone=data_contact["phone"],
     #       data_contact["suscription"]
    )
    #   agregar a la sesión de base de datos (sqlalchemy) y hacer commit de la transacción
    db.session.add(new_contact)
    try:
        db.session.commit()
        print(new_contact)
            # devolvemos el nuevo contact serializado y 201_CREATED
        return jsonify(new_contact.serialize()), 201
    except Exception as error:
        db.session.rollback()
        print(f"{error.args} {type(error)}")
            # devolvemos "hay un error..."
        return jsonify({
            "resultado": f"{error.args}"
        }), 500


# ---- 3.- Obtener un contacto específico con los objetos del grupo al que pertenece GET /group/{group_id}, Code (200, 404, 400, 500)-------
@app.route('/contact/<int:contact_id>', methods=["GET"])
def id_contact(contact_id): 

    if request.method == "GET":
        contact = Contact.query.filter(Contact.id == contact_id)
        contact_by_id = list(map(lambda contact: contact.serialize(), contact))

        if contact_by_id == []:
            msj="no se encontro el contacto ingresado"
            return jsonify(msj), 404
        else:
            return jsonify(contact_by_id), 200
    else:
            response_body = {"msj":"Metodo invalido request"}
            return jsonify(response_body), 400


# ----  4.- Eliminar un Contacto DELETE /contact/{contact_id} ----- 
@app.route('/delete/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    contact = Contact.query.get(contact_id)
    if contact is None:
        raise APIException('Contact not found', status_code=404)
    db.session.delete(contact)
    db.session.commit()
    response_body = {
        "msg": "El contacto ha sido eliminado"
    }
    return jsonify(response_body), 200


# ----  5.- Actualiza el Contacto UPDATE /contact/{contact_id} -----     
@app.route('/contact/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    data_contact = request.get_json()
    contact = Contact.query.get(contact_id)
    if contact is None:
        raise APIException('Contact not found', status_code=404)

    if "full_name" in data_contact:
        contact.full_name = data_contact["full_name"]
    if "email" in data_contact:
        contact.email = data_contact["email"]
    if "address" in data_contact:
        contact.address = data_contact['address']
    if "phone" in data_contact:
        contact.phone = data_contact['phone']
        try:    
            db.session.commit()
            return jsonify(contact.serialize()), 200
        except Exception as error:
            db.session.rollback()
            print(f"{error.args} {type(error)}")
            return jsonify({
                "resultado": f"{error.args}"
            }), 500
    

# ---- 6.- Obtener una lista de todos los nombres e IDs del grupo, GET /group/all, Code (200, 404, 500) ----------                          
@app.route('/group/all', methods=["GET"])

def all_groups():
    if request.method == "GET":
        group = Group.query.all()
        group_list = list(map(lambda group: group.serialize(), group))
        return jsonify(group_list), 200
    else:
        response_body = {
            "msj":"Metodo invalido request"
        }
        return jsonify(response_body), 400


# ---- 7.- Crea un nuevo Grupo POST /group, response code (200, 400) -----  
@app.route("/group", methods=["POST"])
def register_group():
    """  "POST": crear un grupo y devolver su información """
    #  crear una variable y asignarle diccionario con datos para crear grupo
    data_group = request.json 
    if data_group is None:
        return jsonify({
            "resultado": "no envió datos para crear el grupo..."
        }), 400
    #   verificar que el diccionario tenga group_name
    if (
        "group_name" not in data_group 
    ):
        return jsonify({
            "resultado": "revise las propiedades de su solicitud"
        }), 400
    #   validar que campos no vengan vacíos 
    if (
        data_group["group_name"] == "" 
    ):
        return jsonify({
            "resultado": "revise los valores de su solicitud"
            }), 400
    #   crear una variable y asignarle el nuevo group con los datos validados
    new_group = Group(group_name=data_group["group_name"])
    #   agregar a la sesión de base de datos (sqlalchemy) y hacer commit de la transacción
    db.session.add(new_group)
    try:
        db.session.commit()
        print(new_group)
            # devolvemos el nuevo contact serializado y 201_CREATED
        return jsonify(new_group.serialize()), 201
    except Exception as error:
        db.session.rollback()
        print(f"{error.args} {type(error)}")
            # devolvemos "hay un error..."
        return jsonify({
            "resultado": f"{error.args}"
        }), 500


 # ----  8.- Obtener un grupo específico (con todos los objetos de contacto relacionados con él) GET /group/{group_id}, Code (200, 404, 400, 500) -----  
@app.route('/group/<int:group_id>', methods=["GET"])
def id_group(group_id):

    if request.method == "GET":
        group = Group.query.filter(Group.id == group_id)
        group_by_id = list(map(lambda group: group.serialize(), group))

        if group_by_id == []:
            msj="no se encontro el grupo ingresado"
            return jsonify(msj), 200
        else:
            print(group_by_id)
            return jsonify(group_by_id), 200
    else:
            response_body = {"msj":"Metodo invalido request"}
            return jsonify(response_body), 400


# ----  9.- Actualizar el nombre de grupo UPDATE /group/{group_id}, response code (200, 400, 404, 500) -----  
@app.route('/group/<int:group_id>', methods=['PUT'])
def update_group(group_id):
    data_group = request.get_json()
    group = Group.query.get(group_id)
    if group is None:
        raise APIException('el grupo no ha sido encontrado', status_code=404)

    if "group_name" in data_group:
        group.group_name = data_group["group_name"]
        db.session.commit()
    return jsonify(group.serialize()), 200


# ----  10.- Elimina un Grupo DELETE /group/{group_id}, response code (200, 400, 500) -----  
@app.route('/group/<int:group_id>', methods=['DELETE'])
def delete_group(group_id):
    group = Group.query.get(group_id)
    if group is None:
        raise APIException('el grupo no ha sido eliminado', status_code=404)
    db.session.delete(group)
    db.session.commit()
    response_body = {
        "msg": "El grupo ha sido eliminado"
    }
    return jsonify(response_body), 200


   
# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
