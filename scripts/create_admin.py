from werkzeug.security import generate_password_hash

from database import get_db

from models import Login

from datetime import datetime



"""
Script para criar/atualizar um usuário admin rapidamente.
Uso: execute dentro do venv do backend com `python backend/scripts/create_admin.py`.
Altere as constantes USUARIO, SENHA e CARGO conforme necessário.
"""



USUARIO = 1  

SENHA = "admin123"  

CARGO = "admin"



def main():

    db = get_db()

    user = db.query(Login).filter(Login.usuario == USUARIO).first()

    if user:

        user.senha = generate_password_hash(SENHA)

        user.cargo = CARGO

        user.ultima_atualizacao = datetime.now().date()

        print(f"Atualizando usuário existente com usuario={USUARIO} para cargo={CARGO}")

    else:

        user = Login(

            usuario=USUARIO,

            senha=generate_password_hash(SENHA),

            cargo=CARGO,

            ultima_atualizacao=datetime.now().date()

        )

        db.add(user)

        print(f"Criando novo usuário admin com usuario={USUARIO}")

    db.commit()

    print("Feito.")



if __name__ == "__main__":

    main()

