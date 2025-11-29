from flask import Blueprint, request, jsonify, session

from database import get_db

from models import Especialidade



especialidades_bp = Blueprint('especialidades', __name__)



@especialidades_bp.route('/', methods=['GET'])

def listar_especialidades():

    """Lista todas as especialidades"""

    db = get_db()

    especialidades = db.query(Especialidade).all()

    

    return jsonify([{

        "id": e.id,

        "descricao": e.descricao

    } for e in especialidades]), 200



@especialidades_bp.route('/<int:especialidade_id>', methods=['GET'])

def obter_especialidade(especialidade_id):

    """Obtém uma especialidade específica"""

    db = get_db()

    especialidade = db.query(Especialidade).filter(Especialidade.id == especialidade_id).first()

    

    if not especialidade:

        return jsonify({"error": "Especialidade não encontrada"}), 404

    

    return jsonify({

        "id": especialidade.id,

        "descricao": especialidade.descricao

    }), 200



@especialidades_bp.route('/', methods=['POST'])

def criar_especialidade():

    """Cria uma nova especialidade"""

    cargo = (session.get('cargo') or '').lower()

    if cargo not in {"admin", "credenciamento", "ti", "ceo"}:

        return jsonify({"error": "Sem permissão para criar"}), 403

    data = request.get_json()

    

    if not data or not data.get('descricao'):

        return jsonify({"error": "Descrição é obrigatória"}), 400

    

    db = get_db()

    db_especialidade = Especialidade(descricao=data['descricao'])

    db.add(db_especialidade)

    db.commit()

    db.refresh(db_especialidade)

    

    return jsonify({

        "message": "Especialidade criada com sucesso",

        "id": db_especialidade.id,

        "descricao": db_especialidade.descricao

    }), 201



@especialidades_bp.route('/<int:especialidade_id>', methods=['PUT'])

def atualizar_especialidade(especialidade_id):

    """Atualiza uma especialidade"""

    cargo = (session.get('cargo') or '').lower()

    if cargo not in {"admin", "credenciamento", "ti", "ceo"}:

        return jsonify({"error": "Sem permissão para editar"}), 403

    db = get_db()

    db_especialidade = db.query(Especialidade).filter(Especialidade.id == especialidade_id).first()

    

    if not db_especialidade:

        return jsonify({"error": "Especialidade não encontrada"}), 404

    

    data = request.get_json()

    if data.get('descricao'):

        db_especialidade.descricao = data['descricao']

    

    db.commit()

    

    return jsonify({

        "message": "Especialidade atualizada com sucesso",

        "id": db_especialidade.id

    }), 200



@especialidades_bp.route('/<int:especialidade_id>', methods=['DELETE'])

def deletar_especialidade(especialidade_id):

    """Deleta uma especialidade"""

    cargo = (session.get('cargo') or '').lower()

    if cargo not in {"admin", "credenciamento", "ti", "ceo"}:

        return jsonify({"error": "Sem permissão para excluir"}), 403

    db = get_db()

    db_especialidade = db.query(Especialidade).filter(Especialidade.id == especialidade_id).first()

    

    if not db_especialidade:

        return jsonify({"error": "Especialidade não encontrada"}), 404

    

    db.delete(db_especialidade)

    db.commit()

    

    return '', 204

