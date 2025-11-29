from flask import Blueprint, request, jsonify, session

from flask_jwt_extended import jwt_required, get_jwt

from datetime import datetime

from werkzeug.utils import secure_filename

import os

import pandas as pd

from database import get_db, engine

from models import Importacao, Credenciado, Especialidade, Diferencial, Rede

from sqlalchemy import text



importacoes_bp = Blueprint('importacoes', __name__)



UPLOAD_FOLDER = 'uploads'

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}



if not os.path.exists(UPLOAD_FOLDER):

    os.makedirs(UPLOAD_FOLDER)



def allowed_file(filename):

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@importacoes_bp.route('/', methods=['GET'])

def listar_importacoes():

    """Lista todas as importações"""

    db = get_db()

    importacoes = db.query(Importacao).all()

    

    return jsonify([{

        "id": i.id,

        "descricao": i.descricao

    } for i in importacoes]), 200



@importacoes_bp.route('/<int:importacao_id>', methods=['GET'])

def obter_importacao(importacao_id):

    """Obtém uma importação específica"""

    db = get_db()

    importacao = db.query(Importacao).filter(Importacao.id == importacao_id).first()

    

    if not importacao:

        return jsonify({"error": "Importação não encontrada"}), 404

    

    return jsonify({

        "id": importacao.id,

        "descricao": importacao.descricao

    }), 200



@importacoes_bp.route('/', methods=['POST'])

def criar_importacao():

    """Registra uma nova importação"""

    cargo = (session.get('cargo') or '').lower()

    if cargo not in {"admin", "credenciamento", "ti", "ceo"}:

        return jsonify({"error": "Sem permissão para registrar"}), 403

    data = request.get_json()

    

    db = get_db()

    db_importacao = Importacao(

        descricao=data.get('descricao')

    )

    db.add(db_importacao)

    db.commit()

    db.refresh(db_importacao)

    

    return jsonify({

        "message": "Importação registrada com sucesso",

        "id": db_importacao.id,

        "descricao": db_importacao.descricao

    }), 201



@importacoes_bp.route('/upload', methods=['POST'])

def upload_arquivo():

    """Faz upload e processa arquivo de importação"""

    cargo = (session.get('cargo') or '').lower()

    if cargo not in {"admin", "credenciamento", "ti", "ceo"}:

        return jsonify({"error": "Sem permissão para importar"}), 403

    

    print("[v0] ========== INICIANDO UPLOAD ==========")

    

    

    if 'file' not in request.files:

        print("[v0] ✗ Nenhum arquivo no request")

        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    

    file = request.files['file']

    print(f"[v0] Arquivo recebido: {file.filename}")

    

    if file.filename == '':

        return jsonify({"error": "Nenhum arquivo selecionado"}), 400

    

    if not allowed_file(file.filename):

        return jsonify({"error": "Formato de arquivo não permitido. Use CSV ou Excel"}), 400

    

    try:

        

        filename = secure_filename(file.filename)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        filename = f"{timestamp}_{filename}"

        filepath = os.path.join(UPLOAD_FOLDER, filename)

        file.save(filepath)

        print(f"[v0] ✓ Arquivo salvo em: {filepath}")

        

        

        if filename.endswith('.csv'):

            try:

                df = pd.read_csv(filepath, encoding='utf-8')

            except UnicodeDecodeError:

                df = pd.read_csv(filepath, encoding='latin-1')

        else:

            df = pd.read_excel(filepath)

        

        print(f"[v0] ✓ Arquivo lido com sucesso. Total de linhas: {len(df)}")

        print(f"[v0] Colunas originais: {df.columns.tolist()}")

        

        df.columns = df.columns.str.strip().str.lower()

        print(f"[v0] Colunas normalizadas: {df.columns.tolist()}")

        

        

        colunas_obrigatorias = ['nome']

        colunas_faltando = [col for col in colunas_obrigatorias if col not in df.columns]

        

        if colunas_faltando:

            return jsonify({

                "error": f"Colunas obrigatórias faltando: {', '.join(colunas_faltando)}",

                "colunas_encontradas": df.columns.tolist(),

                "colunas_esperadas": ['nome', 'crm', 'telefone', 'email', 'status', 'tipo', 'logradouro', 'bairro', 'numero', 'cidade', 'estado', 'cep', 'complexidade']

            }), 400

        

        db = get_db()

        print("[v0] ✓ Conexão com banco obtida")



        

        try:

            with engine.connect() as conn:

                exists = conn.execute(

                    text(

                        """
                        SELECT COUNT(*)
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = DATABASE()
                          AND TABLE_NAME = 'credenciado'
                          AND COLUMN_NAME = 'credenciamento'
                        """

                    )

                ).scalar()

                if not exists:

                    print("[v0] Coluna 'credenciamento' não existe. Criando coluna...")

                    conn.execute(text("ALTER TABLE credenciado ADD COLUMN credenciamento VARCHAR(50) NULL"))

                    

                    try:

                        conn.execute(text("CREATE INDEX idx_credenciado_credenciamento ON credenciado(credenciamento)"))

                    except Exception:

                        pass

                    print("[v0] ✓ Coluna 'credenciamento' criada")

        except Exception as e:

            

            print(f"[v0] Aviso: não foi possível garantir coluna 'credenciamento': {e}")

        

        

        db_importacao = Importacao(

            descricao=f"Importação de arquivo: {file.filename} ({len(df)} registros)"

        )

        db.add(db_importacao)

        db.commit()

        db.refresh(db_importacao)

        

        print(f"[v0] ✓ Importação registrada com ID: {db_importacao.id}")

        

        registros_importados = 0

        registros_atualizados = 0

        registros_ignorados_duplicados = 0

        erros = []

        vistos_no_arquivo = set()



        def normaliza_codigo(valor):

            if pd.isna(valor):

                return None

            s = str(valor).strip()

            if s == "":

                return None

            

            

            try:

                

                if s.isdigit():

                    return s

                f = float(s)

                i = int(f)

                if f == float(i):

                    return str(i)

            except Exception:

                pass

            return s

        

        for index, row in df.iterrows():

            try:

                print(f"[v0] Processando linha {index + 1}/{len(df)}")

                

                nome = str(row.get('nome', '')).strip() if pd.notna(row.get('nome')) else None

                if not nome:

                    erros.append(f"Linha {index + 2}: Nome é obrigatório")

                    continue

                

                codigo = None

                for alias in ['credenciamento', 'codigo', 'cod', 'id_credenciamento', 'id']:

                    if alias in df.columns:

                        codigo = normaliza_codigo(row.get(alias))

                        if codigo:

                            break

                if codigo and codigo in vistos_no_arquivo:

                    registros_ignorados_duplicados += 1

                    print(f"[v0] • Duplicado no arquivo detectado para código {codigo}; ignorando esta linha")

                    continue

                

                

                payload = dict(

                    nome=nome,

                    crm=str(row.get('crm', '')).strip() if pd.notna(row.get('crm')) else None,

                    telefone=str(row.get('telefone', '')).strip() if pd.notna(row.get('telefone')) else None,

                    email=str(row.get('email', '')).strip() if pd.notna(row.get('email')) else None,

                    status=str(row.get('status', '')).strip() if pd.notna(row.get('status')) else None,

                    tipo=str(row.get('tipo', '')).strip() if pd.notna(row.get('tipo')) else None,

                    logradouro=str(row.get('logradouro', '')).strip() if pd.notna(row.get('logradouro')) else None,

                    bairro=str(row.get('bairro', '')).strip() if pd.notna(row.get('bairro')) else None,

                    numero=str(row.get('numero', '')).strip() if pd.notna(row.get('numero')) else None,

                    cidade=str(row.get('cidade', '')).strip() if pd.notna(row.get('cidade')) else None,

                    estado=str(row.get('estado', '')).strip() if pd.notna(row.get('estado')) else None,

                    cep=str(row.get('cep', '')).strip() if pd.notna(row.get('cep')) else None,

                    complexidade=str(row.get('complexidade', '')).strip() if pd.notna(row.get('complexidade')) else None,

                )



                

                if codigo:

                    vistos_no_arquivo.add(codigo)

                    existente = None

                    try:

                        existente = db.query(Credenciado).filter(Credenciado.credenciamento == codigo).first()

                    except Exception as qerr:

                        

                        print(f"[v0] Aviso na consulta por 'credenciamento': {qerr}")



                    

                    if not existente:

                        crm = payload.get('crm')

                        email = payload.get('email')

                        telefone = payload.get('telefone')

                        cidade = payload.get('cidade')

                        

                        if crm:

                            cand = db.query(Credenciado).filter(Credenciado.crm == crm).all()

                            if len(cand) == 1:

                                existente = cand[0]

                        

                        if not existente and email:

                            cand = db.query(Credenciado).filter(Credenciado.email == email).all()

                            if len(cand) == 1:

                                existente = cand[0]

                        

                        if not existente and telefone:

                            cand = db.query(Credenciado).filter(Credenciado.telefone == telefone).all()

                            if len(cand) == 1:

                                existente = cand[0]

                        

                        if not existente and nome:

                            q = db.query(Credenciado).filter(Credenciado.nome == nome)

                            if cidade:

                                q = q.filter(Credenciado.cidade == cidade)

                            cand = q.all()

                            if len(cand) == 1:

                                existente = cand[0]



                    if existente:

                        

                        for k, v in payload.items():

                            setattr(existente, k, v)

                        existente.credenciamento = codigo

                        print(f"[v0] ↻ Atualizado credenciado existente (ID {existente.id}) para código {codigo}")

                        registros_atualizados += 1

                    else:

                        credenciado = Credenciado(credenciamento=codigo, **payload)

                        db.add(credenciado)

                        db.flush()

                        print(f"[v0] ✓ Inserido novo credenciado (código {codigo}) com ID {credenciado.id}")

                        registros_importados += 1

                else:

                    

                    existente = None

                    crm = payload.get('crm')

                    email = payload.get('email')

                    if crm:

                        cand = db.query(Credenciado).filter(Credenciado.crm == crm).all()

                        if len(cand) == 1:

                            existente = cand[0]

                    if not existente and email:

                        cand = db.query(Credenciado).filter(Credenciado.email == email).all()

                        if len(cand) == 1:

                            existente = cand[0]

                    if existente:

                        for k, v in payload.items():

                            setattr(existente, k, v)

                        print(f"[v0] ↻ Atualizado credenciado existente (sem código) ID {existente.id}")

                        registros_atualizados += 1

                    else:

                        credenciado = Credenciado(**payload)

                        db.add(credenciado)

                        db.flush()

                        print(f"[v0] ✓ Inserido novo credenciado (sem código) com ID {credenciado.id}")

                        registros_importados += 1

                

            except Exception as e:

                erro_msg = f"Linha {index + 2}: {str(e)}"

                print(f"[v0] ✗ ERRO: {erro_msg}")

                erros.append(erro_msg)

                continue

        

        print(f"[v0] Executando commit final de {registros_importados} novos e {registros_atualizados} atualizados...")

        db.commit()

        print(f"[v0] ✓ Commit realizado com sucesso!")

        

        

        total_no_banco = db.query(Credenciado).count()

        print(f"[v0] ========== RESULTADO ==========")

        print(f"[v0] Total de credenciados no banco após importação: {total_no_banco}")

        print(f"[v0] Registros importados nesta operação: {registros_importados}")

        

        return jsonify({

            "message": "Arquivo importado com sucesso",

            "importacao_id": db_importacao.id,

            "total_registros": len(df),

            "registros_importados": registros_importados,

            "registros_atualizados": registros_atualizados,

            "duplicados_ignorados_no_arquivo": registros_ignorados_duplicados,

            "total_no_banco": total_no_banco,

            "erros": erros[:10] if erros else []

        }), 201

        

    except Exception as e:

        print(f"[v0] ✗ ERRO GERAL: {str(e)}")

        import traceback

        traceback.print_exc()

        return jsonify({"error": f"Erro ao processar arquivo: {str(e)}"}), 500

