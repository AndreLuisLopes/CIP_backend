"""
Script para testar a conexão com o banco de dados e verificar os dados
Execute: python scripts/test_database.py
"""

import sys

import os





sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



from database import engine, db_session

from models import Credenciado, Importacao, Especialidade, Diferencial, Rede

from sqlalchemy import text



def test_connection():

    """Testa a conexão com o banco de dados"""

    print("=" * 50)

    print("TESTE DE CONEXÃO COM BANCO DE DADOS")

    print("=" * 50)

    

    try:

        

        with engine.connect() as conn:

            result = conn.execute(text("SELECT 1"))

            print("✓ Conexão com banco de dados OK")

            print(f"✓ Database URL: {engine.url}")

    except Exception as e:

        print(f"✗ Erro ao conectar: {e}")

        return False

    

    return True



def check_tables():

    """Verifica se as tabelas existem"""

    print("\n" + "=" * 50)

    print("VERIFICAÇÃO DE TABELAS")

    print("=" * 50)

    

    try:

        with engine.connect() as conn:

            

            result = conn.execute(text("SHOW TABLES"))

            tables = [row[0] for row in result]

            

            print(f"\nTabelas encontradas ({len(tables)}):")

            for table in tables:

                print(f"  - {table}")

            

            expected_tables = ['credenciado', 'especialidade', 'diferencial', 'rede', 'importacao']

            missing = [t for t in expected_tables if t not in tables]

            

            if missing:

                print(f"\n⚠ Tabelas faltando: {', '.join(missing)}")

                print("Execute o script SQL de criação do banco!")

            else:

                print("\n✓ Todas as tabelas principais existem")

                

    except Exception as e:

        print(f"✗ Erro ao verificar tabelas: {e}")



def check_data():

    """Verifica os dados nas tabelas"""

    print("\n" + "=" * 50)

    print("VERIFICAÇÃO DE DADOS")

    print("=" * 50)

    

    try:

        

        credenciados_count = db_session.query(Credenciado).count()

        importacoes_count = db_session.query(Importacao).count()

        especialidades_count = db_session.query(Especialidade).count()

        diferenciais_count = db_session.query(Diferencial).count()

        redes_count = db_session.query(Rede).count()

        

        print(f"\nTotal de registros:")

        print(f"  - Credenciados: {credenciados_count}")

        print(f"  - Importações: {importacoes_count}")

        print(f"  - Especialidades: {especialidades_count}")

        print(f"  - Diferenciais: {diferenciais_count}")

        print(f"  - Redes: {redes_count}")

        

        

        if credenciados_count > 0:

            print(f"\nPrimeiros 5 credenciados:")

            credenciados = db_session.query(Credenciado).limit(5).all()

            for c in credenciados:

                print(f"  - ID: {c.id}, Nome: {c.nome}, Tipo: {c.tipo}")

        else:

            print("\n⚠ Nenhum credenciado encontrado no banco!")

            

    except Exception as e:

        print(f"✗ Erro ao verificar dados: {e}")

        import traceback

        traceback.print_exc()



if __name__ == "__main__":

    if test_connection():

        check_tables()

        check_data()

    

    print("\n" + "=" * 50)

    print("TESTE CONCLUÍDO")

    print("=" * 50)

