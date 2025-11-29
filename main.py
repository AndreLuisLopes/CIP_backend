from flask import Flask, jsonify

from flask_cors import CORS

import os

from flask_jwt_extended import JWTManager

from database import init_db, close_db

from blueprints.auth import auth_bp

from blueprints.credenciados import credenciados_bp

from blueprints.especialidades import especialidades_bp

from blueprints.diferenciais import diferenciais_bp

from blueprints.redes import redes_bp

from blueprints.importacoes import importacoes_bp

from blueprints.dashboard import dashboard_bp



def create_app():

    app = Flask(__name__)

    

    app.config['SECRET_KEY'] = '61c86da07f317fd35c7cc2da5c791f021609dce7ed62e03375e7728384f8c0d3'

    app.config['JWT_SECRET_KEY'] = '526095ffac9eb185180d084ff19565f094eecf218852aa6abb01d18e6a90ccb9'

    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 1800

    

    app.config['JWT_TOKEN_LOCATION'] = ['headers']

    app.config['JWT_HEADER_NAME'] = 'Authorization'

    app.config['JWT_HEADER_TYPE'] = 'Bearer'



    jwt = JWTManager(app)



    

    cors_env = os.getenv('CORS_ORIGIN')

    if cors_env:

        

        origins = [o.strip() for o in cors_env.split(',') if o.strip()]

    else:

        origins = ['http://localhost:3000', 'http://localhost:3001']

    CORS(app, resources={r"/api/*": {"origins": origins}}, supports_credentials=True)

    

    with app.app_context():

        init_db()

    

    app.teardown_appcontext(close_db)

    

    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    app.register_blueprint(credenciados_bp, url_prefix='/api/credenciados')

    app.register_blueprint(especialidades_bp, url_prefix='/api/especialidades')

    app.register_blueprint(diferenciais_bp, url_prefix='/api/diferenciais')

    app.register_blueprint(redes_bp, url_prefix='/api/redes')

    app.register_blueprint(importacoes_bp, url_prefix='/api/importacoes')

    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

    

    @app.route('/')

    def root():

        return jsonify({

            "message": "Sistema de Credenciamento API",

            "version": "1.0.0",

        })

    

    @app.route('/health')

    def health_check():

        return jsonify({"status": "healthy"})

    

    return app



if __name__ == '__main__':

    app = create_app()

    host = os.getenv('API_HOST', '0.0.0.0')

    port = int(os.getenv('API_PORT', 5000))

    debug = os.getenv('FLASK_ENV') == 'development'

    app.run(debug=True, host='0.0.0.0', port=5000)

