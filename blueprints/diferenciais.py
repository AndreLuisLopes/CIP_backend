from flask import Blueprint, request, jsonify, session

from database import get_db

from models import Diferencial



diferenciais_bp = Blueprint('diferenciais', __name__)



@diferenciais_bp.route('/', methods=['GET'])

def listar_diferenciais():

    """Lista todos os diferenciais"""

    db = get_db()

    diferenciais = db.query(Diferencial).all()

    

    return jsonify([{

        "id": d.id,

        "descricao": d.descricao

    } for d in diferenciais]), 200



@diferenciais_bp.route('/', methods=['POST'])

def criar_diferencial():

    """Cria um novo diferencial"""

    cargo = (session.get('cargo') or '').lower()

    if cargo not in {"admin", "credenciamento", "ti", "ceo"}:

        return jsonify({"error": "Sem permissão para criar"}), 403

    data = request.get_json()

    

    if not data or not data.get('descricao'):

        return jsonify({"error": "Descrição é obrigatória"}), 400

    

    db = get_db()

    db_diferencial = Diferencial(descricao=data['descricao'])

    db.add(db_diferencial)

    db.commit()

    db.refresh(db_diferencial)

    

    return jsonify({

        "message": "Diferencial criado com sucesso",

        "id": db_diferencial.id,

        "descricao": db_diferencial.descricao

    }), 201



@diferenciais_bp.route('/<int:diferencial_id>', methods=['GET'])

def obter_diferencial(diferencial_id):

    """Obtém um diferencial específico"""

    db = get_db()

    diferencial = db.query(Diferencial).filter(Diferencial.id == diferencial_id).first()

    

    if not diferencial:

        return jsonify({"error": "Diferencial não encontrado"}), 404

    

    return jsonify({

        "id": diferencial.id,

        "nome": diferencial.nome

    }), 200



@diferenciais_bp.route('/<int:diferencial_id>', methods=['PUT'])

def atualizar_diferencial(diferencial_id):

    """Atualiza um diferencial"""

    cargo = (session.get('cargo') or '').lower()

    if cargo not in {"admin", "credenciamento", "ti", "ceo"}:

        return jsonify({"error": "Sem permissão para editar"}), 403

    db = get_db()

    db_diferencial = db.query(Diferencial).filter(Diferencial.id == diferencial_id).first()

    

    if not db_diferencial:

        return jsonify({"error": "Diferencial não encontrado"}), 404

    

    data = request.get_json()

    if data.get('nome'):

        db_diferencial.nome = data['nome']

    

    db.commit()

    

    return jsonify({

        "message": "Diferencial atualizado com sucesso",

        "id": db_diferencial.id

    }), 200



@diferenciais_bp.route('/<int:diferencial_id>', methods=['DELETE'])

def deletar_diferencial(diferencial_id):

    """Deleta um diferencial"""

    cargo = (session.get('cargo') or '').lower()

    if cargo not in {"admin", "credenciamento", "ti", "ceo"}:

        return jsonify({"error": "Sem permissão para excluir"}), 403

    db = get_db()

    db_diferencial = db.query(Diferencial).filter(Diferencial.id == diferencial_id).first()

    

    if not db_diferencial:

        return jsonify({"error": "Diferencial não encontrado"}), 404

    

    db.delete(db_diferencial)

    db.commit()

    

    return '', 204

