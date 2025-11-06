from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from server.models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(senha):
        token = create_access_token(identity=str(user.id))
        return jsonify({'token': token, 'tipo_usuario': user.tipo_usuario})
    else:
        return jsonify({'error': 'Email ou senha incorretos'}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email já cadastrado'}), 400
    
    user = User(
        email=data['email'],
        nome_completo=data['nome_completo'],
        apelido=data['apelido'],
        tipo_usuario=data['tipo_usuario']
    )
    user.set_password(data['senha'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'Usuário criado'})

@auth_bp.route('/profile')
@jwt_required()
def profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
            
        return jsonify({
            'id': user.id,
            'email': user.email,
            'nome_completo': user.nome_completo,
            'apelido': user.apelido,
            'tipo_usuario': user.tipo_usuario,
            'created_at': user.created_at.isoformat() if user.created_at else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

