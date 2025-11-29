from flask import Blueprint, request, jsonify, session

from database import get_db

import datetime

from sqlalchemy.orm import joinedload

from models import (

    Credenciado, CredenciadoEspecialidade, CredenciadoDiferencial, CredenciadoRede, CredenciadoComplexidade

)



credenciados_bp = Blueprint('credenciados', __name__)



@credenciados_bp.route('/', methods=['GET'])

def listar_credenciados():

    """Lista todos os credenciados com filtros opcionais"""

    db = get_db()

    

    skip = request.args.get('skip', 0, type=int)

    limit = request.args.get('limit', 100, type=int)

    

    nome = request.args.get('nome')

    status_filter = request.args.get('status')

    cidade = request.args.get('cidade')

    tipo = request.args.get('tipo')

    

    

    query = db.query(Credenciado).options(

        joinedload(Credenciado.especialidades),

        joinedload(Credenciado.diferenciais),

        joinedload(Credenciado.redes),

        joinedload(Credenciado.complexidades).joinedload(CredenciadoComplexidade.especialidade),

    )

    

    if nome:

        query = query.filter(Credenciado.nome.ilike(f"%{nome}%"))

    if status_filter:

        query = query.filter(Credenciado.status == status_filter)

    if cidade:

        query = query.filter(Credenciado.cidade.ilike(f"%{cidade}%"))

    if tipo:

        query = query.filter(Credenciado.tipo == tipo)

    

    credenciados = query.offset(skip).limit(limit).all()

    

    return jsonify([{

        "id": c.id,

        "credenciamento": getattr(c, 'credenciamento', None),

        "nome": c.nome,

        "tipo": c.tipo,

        "status": c.status,

        "cidade": c.cidade,

        "estado": c.estado,

        "telefone": c.telefone,

        "email": c.email,

        

        "tempo_medio_agendamento": getattr(c, 'tempo_medio_agendamento', None),

        "tempo_medio_procedimento": getattr(c, 'tempo_medio_procedimento', None),

        

        "latitude": float(c.latitude) if getattr(c, 'latitude', None) is not None else None,

        "longitude": float(c.longitude) if getattr(c, 'longitude', None) is not None else None,

        "parceiro_estrategico": c.parceiro_estrategico if hasattr(c, 'parceiro_estrategico') else False,

        

        "complexidade": getattr(c, 'complexidade', None),

        

        "especialidades": [

            {"id": e.id, "descricao": e.descricao}

            for e in getattr(c, 'especialidades', [])

        ],

        "diferenciais": [

            {"id": d.id, "descricao": d.descricao}

            for d in getattr(c, 'diferenciais', [])

        ],

        "redes": [

            {"id": r.id, "nome": r.nome}

            for r in getattr(c, 'redes', [])

        ],

        

        "complexidades": [

            {

                "id": cc.id,

                "id_especialidade": cc.id_especialidade,

                "especialidade": getattr(cc.especialidade, 'descricao', None)

            }

            for cc in getattr(c, 'complexidades', [])

        ],

    } for c in credenciados]), 200



@credenciados_bp.route('/', methods=['POST'])

def criar_credenciado():

    """Cria um novo credenciado"""

    

    cargo = (session.get('cargo') or '').lower()

    if cargo not in {"admin", "credenciamento", "ti", "ceo"}:

        return jsonify({"error": "Sem permissão para criar"}), 403

    data = request.get_json()

    

    if not data or not data.get('nome'):

        return jsonify({"error": "Nome é obrigatório"}), 400

    

    db = get_db()

    

    especialidades_ids = data.pop('especialidades_ids', [])

    diferenciais_ids = data.pop('diferenciais_ids', [])

    redes_ids = data.pop('redes_ids', [])

    complexidades_especialidades_ids = data.pop('complexidades_especialidades_ids', [])

    

    db_credenciado = Credenciado(**data)

    db.add(db_credenciado)

    db.flush()

    

    for esp_id in especialidades_ids:

        db.add(CredenciadoEspecialidade(

            id_credenciado=db_credenciado.id,

            id_especialidade=esp_id

        ))

    

    for dif_id in diferenciais_ids:

        db.add(CredenciadoDiferencial(

            id_credenciado=db_credenciado.id,

            id_diferencial=dif_id

        ))

    

    for rede_id in redes_ids:

        db.add(CredenciadoRede(

            id_credenciado=db_credenciado.id,

            id_rede=rede_id

        ))

    

    for esp_id in complexidades_especialidades_ids:

        db.add(CredenciadoComplexidade(

            id_credenciado=db_credenciado.id,

            id_especialidade=esp_id,

            id_credenciamento=None

        ))

    

    db.commit()

    db.refresh(db_credenciado)

    

    return jsonify({

        "message": "Credenciado criado com sucesso",

        "id": db_credenciado.id

    }), 201



@credenciados_bp.route('/<int:credenciado_id>', methods=['GET'])

def obter_credenciado(credenciado_id):

    """Obtém um credenciado específico por ID"""

    db = get_db()

    credenciado = db.query(Credenciado).options(

        joinedload(Credenciado.complexidades).joinedload(CredenciadoComplexidade.especialidade)

    ).filter(Credenciado.id == credenciado_id).first()

    

    if not credenciado:

        return jsonify({"error": "Credenciado não encontrado"}), 404

    

    

    lat = float(credenciado.latitude) if credenciado.latitude is not None else None

    lng = float(credenciado.longitude) if credenciado.longitude is not None else None

    

    

    especialidades = [

        {"id": e.id, "descricao": e.descricao}

        for e in getattr(credenciado, 'especialidades', [])

    ]

    diferenciais = [

        {"id": d.id, "descricao": d.descricao}

        for d in getattr(credenciado, 'diferenciais', [])

    ]

    redes = [

        {"id": r.id, "nome": r.nome}

        for r in getattr(credenciado, 'redes', [])

    ]

    complexidades = [

        {

            "id": cc.id,

            "id_especialidade": cc.id_especialidade,

            "especialidade": getattr(cc.especialidade, 'descricao', None)

        }

        for cc in getattr(credenciado, 'complexidades', [])

    ]



    return jsonify({

        "id": credenciado.id,

        "credenciamento": getattr(credenciado, 'credenciamento', None),

        "nome": credenciado.nome,

        "tipo": credenciado.tipo,

        "status": credenciado.status,

        "complexidade": credenciado.complexidade,

        "crm": credenciado.crm,

        "logradouro": credenciado.logradouro,

        "numero": credenciado.numero,

        "bairro": credenciado.bairro,

        "cidade": credenciado.cidade,

        "estado": credenciado.estado,

        "cep": credenciado.cep,

        "telefone": credenciado.telefone,

        "email": credenciado.email,

        "latitude": lat,

        "longitude": lng,

        "parceiro_estrategico": credenciado.parceiro_estrategico,

        "tempo_medio_agendamento": credenciado.tempo_medio_agendamento,

        "tempo_medio_procedimento": credenciado.tempo_medio_procedimento,

        "data_contrato": credenciado.data_contrato.isoformat() if credenciado.data_contrato else None,

        "ultima_atualizacao": credenciado.ultima_atualizacao.isoformat() if credenciado.ultima_atualizacao else None,

        "especialidades": especialidades,

        "diferenciais": diferenciais,

        "redes": redes,

        "complexidades": complexidades,

    }), 200



@credenciados_bp.route('/<int:credenciado_id>', methods=['PUT'])

def atualizar_credenciado(credenciado_id):

    """Atualiza um credenciado existente"""

    

    cargo = (session.get('cargo') or '').lower()

    if cargo not in {"admin", "credenciamento", "ti", "ceo"}:

        return jsonify({"error": "Sem permissão para editar"}), 403

    db = get_db()

    db_credenciado = db.query(Credenciado).filter(Credenciado.id == credenciado_id).first()

    

    if not db_credenciado:

        return jsonify({"error": "Credenciado não encontrado"}), 404

    

    data = request.get_json()

    

    

    especialidades_ids = data.pop('especialidades_ids', None)

    diferenciais_ids = data.pop('diferenciais_ids', None)

    redes_ids = data.pop('redes_ids', None)

    complexidades_especialidades_ids = data.pop('complexidades_especialidades_ids', None)

    

    

    protected_fields = {"id", "ultima_atualizacao"}

    for field, value in data.items():

        if field in protected_fields:

            continue

        if not hasattr(db_credenciado, field):

            continue

        if field == 'data_contrato':

            

            if value in (None, '', 'null', 'NULL'):

                continue

            if isinstance(value, str):

                try:

                    

                    value = datetime.date.fromisoformat(value[:10])

                except Exception:

                    

                    continue

            

            setattr(db_credenciado, field, value)

            continue

        setattr(db_credenciado, field, value)

    

    

    if especialidades_ids is not None:

        db.query(CredenciadoEspecialidade).filter(

            CredenciadoEspecialidade.id_credenciado == credenciado_id

        ).delete()

        for esp_id in especialidades_ids:

            db.add(CredenciadoEspecialidade(

                id_credenciado=credenciado_id,

                id_especialidade=esp_id

            ))

    

    

    if diferenciais_ids is not None:

        db.query(CredenciadoDiferencial).filter(

            CredenciadoDiferencial.id_credenciado == credenciado_id

        ).delete()

        for dif_id in diferenciais_ids:

            db.add(CredenciadoDiferencial(

                id_credenciado=credenciado_id,

                id_diferencial=dif_id

            ))

    

    

    if redes_ids is not None:

        db.query(CredenciadoRede).filter(

            CredenciadoRede.id_credenciado == credenciado_id

        ).delete()

        for rede_id in redes_ids:

            db.add(CredenciadoRede(

                id_credenciado=credenciado_id,

                id_rede=rede_id

            ))

    

    if complexidades_especialidades_ids is not None:

        db.query(CredenciadoComplexidade).filter(

            CredenciadoComplexidade.id_credenciado == credenciado_id

        ).delete()

        for esp_id in complexidades_especialidades_ids:

            db.add(CredenciadoComplexidade(

                id_credenciado=credenciado_id,

                id_especialidade=esp_id,

                id_credenciamento=None

            ))

    

    db.commit()

    db.refresh(db_credenciado)



    

    especialidades = [

        {"id": e.id, "descricao": e.descricao}

        for e in getattr(db_credenciado, 'especialidades', [])

    ]

    diferenciais = [

        {"id": d.id, "descricao": d.descricao}

        for d in getattr(db_credenciado, 'diferenciais', [])

    ]

    redes = [

        {"id": r.id, "nome": r.nome}

        for r in getattr(db_credenciado, 'redes', [])

    ]



    complexidades = [

        {

            "id": cc.id,

            "id_especialidade": cc.id_especialidade,

            "especialidade": getattr(cc.especialidade, 'descricao', None)

        }

        for cc in getattr(db_credenciado, 'complexidades', [])

    ]



    return jsonify({

        "message": "Credenciado atualizado com sucesso",

        "id": db_credenciado.id,

        "nome": db_credenciado.nome,

        "telefone": db_credenciado.telefone,

        "email": db_credenciado.email,

        "status": db_credenciado.status,

        "tipo": db_credenciado.tipo,

        "cidade": db_credenciado.cidade,

        "estado": db_credenciado.estado,

        "complexidade": db_credenciado.complexidade,

        "especialidades": especialidades,

        "diferenciais": diferenciais,

        "redes": redes,

        "complexidades": complexidades,

        "data_contrato": db_credenciado.data_contrato.isoformat() if db_credenciado.data_contrato else None,

        "ultima_atualizacao": db_credenciado.ultima_atualizacao.isoformat() if db_credenciado.ultima_atualizacao else None,

    }), 200



@credenciados_bp.route('/<int:credenciado_id>', methods=['DELETE'])

def deletar_credenciado(credenciado_id):

    """Deleta um credenciado"""

    

    cargo = (session.get('cargo') or '').lower()

    if cargo not in {"admin", "credenciamento", "ti", "ceo"}:

        return jsonify({"error": "Sem permissão para excluir"}), 403

    db = get_db()

    db_credenciado = db.query(Credenciado).filter(Credenciado.id == credenciado_id).first()

    

    if not db_credenciado:

        return jsonify({"error": "Credenciado não encontrado"}), 404

    

    db.delete(db_credenciado)

    db.commit()

    

    return '', 204



@credenciados_bp.route('/count', methods=['GET'])

def contar_credenciados():

    """Conta o total de credenciados no banco"""

    db = get_db()

    total = db.query(Credenciado).count()

    

    return jsonify({

        "total_credenciados": total,

        "message": f"Existem {total} credenciados no banco de dados"

    }), 200



@credenciados_bp.route('/test-insert', methods=['POST'])

def test_insert():

    """Endpoint de teste para inserir um credenciado diretamente no banco"""

    try:

        print("[v0] ========== TESTE DE INSERÇÃO ==========")

        db = get_db()

        print("[v0] ✓ Conexão com banco obtida")

        

        

        credenciado_teste = Credenciado(

            nome="Teste de Importação",

            crm="12345-SP",

            telefone="(11) 99999-9999",

            email="teste@exemplo.com",

            status="Ativo",

            tipo="Médico",

            cidade="São Paulo",

            estado="SP"

        )

        

        print(f"[v0] Credenciado criado: {credenciado_teste.nome}")

        

        db.add(credenciado_teste)

        print("[v0] ✓ Credenciado adicionado à sessão")

        

        db.flush()

        print(f"[v0] ✓ Flush executado - ID gerado: {credenciado_teste.id}")

        

        db.commit()

        print("[v0] ✓ Commit executado com sucesso!")

        

        

        total = db.query(Credenciado).count()

        print(f"[v0] Total de credenciados no banco: {total}")

        

        return jsonify({

            "message": "Credenciado de teste inserido com sucesso!",

            "id": credenciado_teste.id,

            "nome": credenciado_teste.nome,

            "total_no_banco": total

        }), 201

        

    except Exception as e:

        print(f"[v0] ✗ ERRO: {str(e)}")

        import traceback

        traceback.print_exc()

        return jsonify({"error": str(e)}), 500

