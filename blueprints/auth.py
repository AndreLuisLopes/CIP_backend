from flask import Blueprint, request, jsonify, session

from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime

from database import get_db

from models import Login

from schemas import LoginRequest, UserCreate



auth_bp = Blueprint('auth', __name__)



@auth_bp.route('/register', methods=['POST'])

def register():

    """Registra um novo usuário"""

    data = request.get_json()

    

    if not data or not data.get('usuario') or not data.get('senha'):

        return jsonify({"error": "Usuário e senha são obrigatórios"}), 400

    try:

        usuario_num = int(data['usuario'])

    except Exception:

        return jsonify({"error": "Usuário deve ser numérico"}), 400

    

    db = get_db()

    

    existing_user = db.query(Login).filter(Login.usuario == usuario_num).first()

    if existing_user:

        return jsonify({"error": "Usuário já cadastrado"}), 400

    

    hashed_password = generate_password_hash(data['senha'])

    db_user = Login(

        usuario=usuario_num,

        senha=hashed_password,

        cargo=data.get('cargo', 'usuario'),

        ultima_atualizacao=datetime.now().date()

    )

    db.add(db_user)

    db.commit()

    db.refresh(db_user)

    

    

    session['usuario'] = db_user.usuario

    session['cargo'] = db_user.cargo

    return jsonify({

        "message": "Usuário criado com sucesso",

        "id": db_user.id,

        "usuario": db_user.usuario,

        "cargo": db_user.cargo

    }), 201



@auth_bp.route('/login', methods=['POST'])

def login():

    """Autentica um usuário e retorna token JWT"""

    data = request.get_json()

    

    if not data or not data.get('usuario') or not data.get('senha'):

        return jsonify({"error": "Usuário e senha são obrigatórios"}), 400

    try:

        usuario_num = int(data['usuario'])

    except Exception:

        return jsonify({"error": "Usuário deve ser numérico"}), 400

    

    db = get_db()

    user = db.query(Login).filter(Login.usuario == usuario_num).first()

    

    if not user:

        return jsonify({"error": "Credenciais inválidas"}), 401



    

    

    

    if not check_password_hash(user.senha, data['senha']):

        if user.senha == data['senha']:

            try:

                user.senha = generate_password_hash(data['senha'])

                db.commit()

            except Exception:

                db.rollback()

        else:

            return jsonify({"error": "Credenciais inválidas"}), 401

    

    

    session['usuario'] = user.usuario

    session['cargo'] = user.cargo

    return jsonify({

        "id": user.id,

        "usuario": user.usuario,

        "cargo": user.cargo

    }), 200



@auth_bp.route('/me', methods=['GET'])

def get_current_user():

    """Obtém informações do usuário atual"""

    usuario = session.get('usuario')

    if not usuario:

        return jsonify({"error": "Não autenticado"}), 401

    db = get_db()

    user = db.query(Login).filter(Login.usuario == int(usuario)).first()

    

    if not user:

        return jsonify({"error": "Usuário não encontrado"}), 404

    

    return jsonify({

        "id": user.id,

        "usuario": user.usuario,

        "cargo": user.cargo

    }), 200



@auth_bp.route('/logout', methods=['POST'])

def logout():

    session.clear()

    return jsonify({"message": "Sessão encerrada"}), 200

