from flask import Flask, request, Response, json
import os
import mysql.connector
from mysql.connector import Error

# print a nice greeting.


def say_hello(username="World"):
    return '<p>Hello %s!</p>\n' % username


def get_connection():
  # method for return conecction
    if 'RDS_HOSTNAME' in os.environ:
        DATABASES = {'default': {'ENGINE': 'django.db.backends.mysql', 'NAME': os.environ['RDS_DB_NAME'], 'USER': os.environ[
            'RDS_USERNAME'], 'PASSWORD': os.environ['RDS_PASSWORD'], 'HOST': os.environ['RDS_HOSTNAME'], 'PORT': os.environ['RDS_PORT'], }}
        dbname = os.environ['RDS_DB_NAME']
        dbuser = os.environ['RDS_USERNAME']
        dbpwd = os.environ['RDS_PASSWORD']
        dbport = os.environ['RDS_PORT']
        dbhost = os.environ['RDS_HOSTNAME']
        connection = mysql.connector.connect(
            host=dbhost, database=dbname, user=dbuser, password=dbpwd)
        return connection
    else:
        return None


# def connbd(bd1):
#  msg = 'starting '
#  if 'RDS_HOSTNAME' in os.environ:
#   DATABASES = {'default': {'ENGINE': 'django.db.backends.mysql','NAME': os.environ['RDS_DB_NAME'],'USER': os.environ['RDS_USERNAME'],'PASSWORD': os.environ['RDS_PASSWORD'],'HOST': os.environ['RDS_HOSTNAME'],'PORT': os.environ['RDS_PORT'],}}
#   dbname = os.environ['RDS_DB_NAME']
#   dbuser = os.environ['RDS_USERNAME']
#   dbpwd = os.environ['RDS_PASSWORD']
#   dbport = os.environ['RDS_PORT']
#   dbhost = os.environ['RDS_HOSTNAME']
#   try:
#    connection = mysql.connector.connect(host=dbhost, database=dbname, user=dbuser, password=dbpwd)
#    if connection.is_connected():
#     db_Info = connection.get_server_info()
#     print("Connected to MySQL Server version ", db_Info)
#     cursor = connection.cursor()
#     cursor.execute("select database();")
#     record = cursor.fetchone()
#     msg = msg + '--> connected'
#     print("You're connected to database: ", record)
#   except Error as e:
#    print("Error while connecting to MySQL", e)
#   finally:
#    if connection.is_connected():
#     cursor.close()
#     connection.close()
#     msg = msg + ' --> closed'
#     print("MySQL connection is closed")
#  else:
#   DATABASES = 'XX'
#   dbname = 'nodb'
#  return 'Hello '+bd1 + ' --> ' + msg

# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'

# EB looks for an 'application' callable by default.
application = Flask(__name__)

# add a rule for the index page.
application.add_url_rule('/', 'index', (lambda: header_text +
                                        say_hello() + instructions + footer_text))

# application.add_url_rule('/<bd1>', 'hello', (lambda bd1: header_text +
#     say_hello() + instructions + connbd(bd1) + footer_text))


@application.route('/db', methods=['GET'])
def getDbName():
    return os.environ['RDS_DB_NAME']


@application.route('/creartabla', methods=['GET'])
def creartabla():
    try:
        connection = get_connection()
        if connection is None:
            return Response(json.dumps({
                "message": "Error al conectar a la base de datos"
            }), status=500, mimetype='application/json')
        cursor = connection.cursor()
        # crear tabla users con los campos usuario y saldo en double
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS users (usuario VARCHAR(255), saldo DOUBLE)")
        connection.commit()
        cursor.close()
        connection.close()
        return Response(json.dumps({
            "message": "Tabla creada"
        }), status=200, mimetype='application/json')
    except Error as e:
        return  Response(json.dumps({
            "message": "Error al crear tabla"
        }), status=500, mimetype='application/json')


@application.route('/crearusuario/<user>', methods=['GET'])
def crear_usuario(user):
    # data = request.json
    # user = data['usuario']
    # saldo = data['saldo']
    # if user is None or saldo is None:
    #     return Response(json.dumps({
    #         "message": "Error al crear usuario"
    #     }), status=500, mimetype='application/json')
    try:
        connection = get_connection()
        if connection is None:
            return Response(json.dumps(
                {
                    "message": "Error al conectar a la base de datos"
                }
            ), status=500, mimetype='application/json')

        cursor = connection.cursor()

        # validar que el usuario no exista
        cursor.execute(
            "SELECT * FROM users WHERE usuario = %s", (user,))
        result = cursor.fetchone()
        if result is not None:
            return Response(json.dumps({
                "message": "Usuario ya existe"
            }), status=500, mimetype='application/json')

        # insertar en tabla users los campos usuario y saldo
        cursor.execute(
            "INSERT INTO users (usuario, saldo) VALUES (%s, %s)", (user, 100))
        connection.commit()
        cursor.close()
        connection.close()
        result = {
            "message": "Usuario creado"
        }
        return Response(
            json.dumps(result), status=200, mimetype='application/json')
    except Error as e:
        result = {
            "message": "Error al crear usuario"
        }
        return Response(
            json.dumps(result), status=500, mimetype='application/json')


@application.route('/usuarios', methods=['GET'])
def getUsuarios():
    try:
        connection = get_connection()
        if connection is None:
            return Response(json.dumps({
                "message": "Error al conectar a la base de datos"
            }), status=500, mimetype='application/json')
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM users")
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        result = {
            "usuarios": result
        }
        return Response(
            json.dumps(result), status=200, mimetype='application/json')
    except Error as e:
        return Response(json.dumps({
            "message": "Error al consultar usuarios"
        }), status=500, mimetype='application/json')


@application.route('/consultarsaldo/<user>', methods=['GET'])
def getUser(user):
    try:
        connection = get_connection()
        if connection is None:
            return Response(json.dumps({
                "message": "Error al conectar a la base de datos"
            }), status=500, mimetype='application/json')
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE usuario = %s", (user,))
        result = cursor.fetchone()
        if result is None:
            return Response(json.dumps({
                "message": "Usuario no existe"
            }), status=500, mimetype='application/json')
        cursor.close()
        connection.close()
        result = {
            "usuario": result[0],
            "saldo": result[1]
        }
        return Response(
            json.dumps(result), status=200, mimetype='application/json')
    except Error as e:
        return Response(json.dumps({
            "message": "Error al consultar usuario"
        }), status=500, mimetype='application/json')

@application.route('/transferir/<user>', methods=['GET'])
def tranferir(user):
    # ?destino='destino'&valor='monto'
    destino = request.args.get('destino')
    valor = float(request.args.get('valor'))
    if(user is None or destino is None or valor is None):
        return Response(json.dumps({
            "message": "Error al transferir faltan parametros"
        }), status=500, mimetype='application/json')
    
    try:
        connection = get_connection()
        if connection is None:
            return Response(json.dumps({
                "message": "Error al conectar a la base de datos"
            }), status=500, mimetype='application/json')
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE usuario = %s", (user,))
        result = cursor.fetchone()
        if result is None:
            return Response(json.dumps({
                "message": "Usuario no existe"
            }), status=500, mimetype='application/json')
        saldo = result[1]
        if(saldo < valor):
            return Response(json.dumps({
                "message": "Saldo insuficiente"
            }), status=500, mimetype='application/json')
        cursor.execute(
            "SELECT * FROM users WHERE usuario = %s", (destino,))
        result = cursor.fetchone()
        if result is None:
            return Response(json.dumps({
                "message": "Usuario destino no existe"
            }), status=500, mimetype='application/json')
        cursor.execute(
            "UPDATE users SET saldo = saldo - %s WHERE usuario = %s", (valor, user))
        connection.commit()
        cursor.execute(
            "UPDATE users SET saldo = saldo + %s WHERE usuario = %s", (valor, destino))
        connection.commit()
        cursor.close()
        connection.close()
        result = {
            "message": "Transferencia realizada"
        }
        return Response(
            json.dumps(result), status=200, mimetype='application/json')
    except Error as e:
        return Response(json.dumps({
            "message": "Error al transferir"
        }), status=500, mimetype='application/json')
    # destino = request.json['destino']

# @application.route('/actualizarsaldo/:user', methods=['POST'])
# def actualizar_saldo(user):
#     data = request.json
#     # user = data['usuario']
#     saldo = data['saldo']
#     if user is None or saldo is None:
#         return Response(json.dumps({
#             "message": "Error al actualizar saldo"
#         }), status=500, mimetype='application/json')
#     try:
#         connection = get_connection()
#         if connection is None:
#             return Response(json.dumps({
#                 "message": "Error al conectar a la base de datos"
#             }), status=500, mimetype='application/json')
#         cursor = connection.cursor()
#         cursor.execute(
#             "SELECT * FROM users WHERE usuario = %s", (user,))
#         result = cursor.fetchone()
#         if result is None:
#             return Response(json.dumps({
#                 "message": "Usuario no existe"
#             }), status=500, mimetype='application/json')
#         cursor.execute(
#             "UPDATE users SET saldo = %s WHERE usuario = %s", (saldo, user))
#         connection.commit()
#         cursor.close()
#         connection.close()
#         result = {
#             "message": "Saldo actualizado"
#         }
#         return Response(
#             json.dumps(result), status=200, mimetype='application/json')
#     except Error as e:
#         return Response(json.dumps({
#             "message": "Error al actualizar saldo"
#         }), status=500, mimetype='application/json')




# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
