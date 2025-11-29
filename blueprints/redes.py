from flask import Blueprint, request, jsonify, session

from database import get_db

from models import Rede



redes_bp = Blueprint('redes', __name__)



@redes_bp.route('/', methods=['GET'])

def listar_redes():

    """Lista todas as redes"""

    db = get_db()

    redes = db.query(Rede).all()

    

    return jsonify([{

        "id": r.id,

        "nome": r.nome,

        "descricao": r.descricao

    } for r in redes]), 200



@redes_bp.route('/<int:rede_id>', methods=['GET'])

def obter_rede(rede_id):

    """Obtém uma rede específica"""

    db = get_db()

    rede = db.query(Rede).filter(Rede.id == rede_id).first()

    

    if not rede:

        return jsonify({"error": "Rede não encontrada"}), 404

    

    return jsonify({

        "id": rede.id,

        "nome": rede.nome

    }), 200



@redes_bp.route('/', methods=['POST'])

def criar_rede():

    """Cria uma nova rede"""

    cargo = (session.get('cargo') or '').lower()

    if cargo not in {"admin", "credenciamento", "ti", "ceo"}:

        return jsonify({"error": "Sem permissão para criar"}), 403

    data = request.get_json()

    

    if not data or not data.get('nome'):

        return jsonify({"error": "Nome é obrigatório"}), 400

    

    db = get_db()

    db_rede = Rede(

        nome=data['nome'],

        descricao=data.get('descricao')

    )

    db.add(db_rede)

    db.commit()

    db.refresh(db_rede)

    

    return jsonify({

        "message": "Rede criada com sucesso",

        "id": db_rede.id,

        "nome": db_rede.nome

    }), 201



@redes_bp.route('/<int:rede_id>', methods=['PUT'])

def atualizar_rede(rede_id):

    """Atualiza uma rede"""

    cargo = (session.get('cargo') or '').lower()

    if cargo not in {"admin", "credenciamento", "ti", "ceo"}:

        return jsonify({"error": "Sem permissão para editar"}), 403

    db = get_db()

    db_rede = db.query(Rede).filter(Rede.id == rede_id).first()

    

    if not db_rede:

        return jsonify({"error": "Rede não encontrada"}), 404

    

    data = request.get_json()

    if data.get('nome'):

        db_rede.nome = data['nome']

    

    db.commit()

    

    return jsonify({

        "message": "Rede atualizada com sucesso",

        "id": db_rede.id

    }), 200



@redes_bp.route('/<int:rede_id>', methods=['DELETE'])

def deletar_rede(rede_id):

    """Deleta uma rede"""

    cargo = (session.get('cargo') or '').lower()

    if cargo not in {"admin", "credenciamento", "ti", "ceo"}:

        return jsonify({"error": "Sem permissão para excluir"}), 403

    db = get_db()

    db_rede = db.query(Rede).filter(Rede.id == rede_id).first()

    

    if not db_rede:

        return jsonify({"error": "Rede não encontrada"}), 404

    

    db.delete(db_rede)

    db.commit()

    

    return '', 204
