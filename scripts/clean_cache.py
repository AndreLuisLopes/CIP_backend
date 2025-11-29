"""
Script para limpar cache do Python e reiniciar o servidor
"""

import os

import shutil

import sys



def limpar_cache():

    """Remove todos os arquivos de cache do Python"""

    print("🧹 Limpando cache do Python...")

    

    

    diretorios = ['backend', 'scripts']

    

    arquivos_removidos = 0

    diretorios_removidos = 0

    

    for diretorio in diretorios:

        if not os.path.exists(diretorio):

            continue

            

        for root, dirs, files in os.walk(diretorio):

            

            for file in files:

                if file.endswith('.pyc'):

                    filepath = os.path.join(root, file)

                    try:

                        os.remove(filepath)

                        arquivos_removidos += 1

                        print(f"  ✓ Removido: {filepath}")

                    except Exception as e:

                        print(f"  ✗ Erro ao remover {filepath}: {e}")

            

            

            if '__pycache__' in dirs:

                pycache_path = os.path.join(root, '__pycache__')

                try:

                    shutil.rmtree(pycache_path)

                    diretorios_removidos += 1

                    print(f"  ✓ Removido diretório: {pycache_path}")

                except Exception as e:

                    print(f"  ✗ Erro ao remover {pycache_path}: {e}")

    

    print(f"\n✅ Limpeza concluída!")

    print(f"   - {arquivos_removidos} arquivos .pyc removidos")

    print(f"   - {diretorios_removidos} diretórios __pycache__ removidos")

    print(f"\n💡 Agora execute: python backend/run.py")



if __name__ == '__main__':

    limpar_cache()

