from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from server.models import db, User, Turma

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def check_admin():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user or user.tipo_usuario != 'administrador':
        return None
    
    return user

@admin_bp.route('/users')
@jwt_required()
def list_users():
    admin = check_admin()
    if not admin:
        return jsonify({'error': 'Sem permissão'}), 403
    
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'email': u.email,
        'nome_completo': u.nome_completo,
        'apelido': u.apelido,
        'tipo_usuario': u.tipo_usuario,
        'created_at': u.created_at.isoformat()
    } for u in users])

@admin_bp.route('/users/<int:user_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_user(user_id):
    admin = check_admin()
    if not admin:
        return jsonify({'error': 'Sem permissão'}), 403
    
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    if request.method == 'PUT':
        data = request.get_json()
        user.email = data.get('email', user.email)
        user.nome_completo = data.get('nome_completo', user.nome_completo)
        user.apelido = data.get('apelido', user.apelido)
        user.tipo_usuario = data.get('tipo_usuario', user.tipo_usuario)
        
        if 'senha' in data:
            user.set_password(data['senha'])
        
        db.session.commit()
        return jsonify({'message': 'Usuário atualizado'})
    
    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'Usuário excluído'})

@admin_bp.route('/turmas')
@jwt_required()
def list_turmas():
    admin = check_admin()
    if not admin:
        return jsonify({'error': 'Sem permissão'}), 403
    
    turmas = Turma.query.all()
    return jsonify([{
        'id': t.id,
        'nome': t.nome,
        'descricao': t.descricao,
        'codigo': t.codigo,
        'professor_id': t.professor_id,
        'professor_nome': User.query.get(t.professor_id).nome_completo,
        'created_at': t.created_at.isoformat()
    } for t in turmas])

