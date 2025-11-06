from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from server.models import db, User, Turma, Problema, TurmaAluno
import secrets

professor_bp = Blueprint('professor', __name__, url_prefix='/professor')

def check_professor():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user or user.tipo_usuario != 'professor':
        return None
    
    return user

@professor_bp.route('/turmas')
@jwt_required()
def list_turmas():
    professor = check_professor()
    if not professor:
        return jsonify({'error': 'Sem permissão'}), 403
    
    turmas = Turma.query.filter_by(professor_id=professor.id).all()
    return jsonify([{
        'id': t.id,
        'nome': t.nome,
        'descricao': t.descricao,
        'codigo': t.codigo,
        'created_at': t.created_at.isoformat()
    } for t in turmas])

@professor_bp.route('/turmas', methods=['POST'])
@jwt_required()
def criar_turma():
    professor = check_professor()
    if not professor:
        return jsonify({'error': 'Sem permissão'}), 403
    
    data = request.get_json()
    codigo = secrets.token_hex(3).upper()[:6]
    
    turma = Turma(
        nome=data['nome'],
        descricao=data.get('descricao', ''),
        codigo=codigo,
        professor_id=professor.id
    )
    
    db.session.add(turma)
    db.session.commit()
    
    return jsonify({'message': 'Turma criada', 'codigo': codigo})

@professor_bp.route('/turmas/<int:turma_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_turma(turma_id):
    professor = check_professor()
    if not professor:
        return jsonify({'error': 'Sem permissão'}), 403
    
    turma = Turma.query.filter_by(id=turma_id, professor_id=professor.id).first()
    if not turma:
        return jsonify({'error': 'Turma não encontrada'}), 404
    
    if request.method == 'PUT':
        data = request.get_json()
        turma.nome = data.get('nome', turma.nome)
        turma.descricao = data.get('descricao', turma.descricao)
        db.session.commit()
        return jsonify({'message': 'Turma atualizada'})
    
    elif request.method == 'DELETE':
        db.session.delete(turma)
        db.session.commit()
        return jsonify({'message': 'Turma excluída'})

@professor_bp.route('/turmas/<int:turma_id>/problemas')
@jwt_required()
def list_problemas(turma_id):
    professor = check_professor()
    if not professor:
        return jsonify({'error': 'Sem permissão'}), 403
    
    turma = Turma.query.filter_by(id=turma_id, professor_id=professor.id).first()
    if not turma:
        return jsonify({'error': 'Turma não encontrada'}), 404
    
    problemas = Problema.query.filter_by(turma_id=turma_id).all()
    return jsonify([{
        'id': p.id,
        'titulo': p.titulo,
        'enunciado': p.enunciado,
        'entrada': p.entrada,
        'saida': p.saida,
        'restricoes': p.restricoes,
        'resposta_esperada': p.resposta_esperada,
        'linguagem': p.linguagem,
        'created_at': p.created_at.isoformat()
    } for p in problemas])

@professor_bp.route('/turmas/<int:turma_id>/problemas', methods=['POST'])
@jwt_required()
def criar_problema(turma_id):
    professor = check_professor()
    if not professor:
        return jsonify({'error': 'Sem permissão'}), 403
    
    turma = Turma.query.filter_by(id=turma_id, professor_id=professor.id).first()
    if not turma:
        return jsonify({'error': 'Turma não encontrada'}), 404
    
    data = request.get_json()
    problema = Problema(
        titulo=data['titulo'],
        enunciado=data['enunciado'],
        entrada=data.get('entrada'),
        saida=data.get('saida'),
        restricoes=data.get('restricoes'),
        resposta_esperada=data['resposta_esperada'],
        linguagem=data.get('linguagem', 'python'),
        turma_id=turma_id
    )
    
    db.session.add(problema)
    db.session.commit()
    
    return jsonify({'message': 'Problema criado'})

@professor_bp.route('/turmas/<int:turma_id>/problemas/<int:problema_id>', methods=['DELETE'])
@jwt_required()
def delete_problema(turma_id, problema_id):
    professor = check_professor()
    if not professor:
        return jsonify({'error': 'Sem permissão'}), 403
    
    turma = Turma.query.filter_by(id=turma_id, professor_id=professor.id).first()
    if not turma:
        return jsonify({'error': 'Turma não encontrada'}), 404
    
    problema = Problema.query.filter_by(id=problema_id, turma_id=turma_id).first()
    if not problema:
        return jsonify({'error': 'Problema não encontrado'}), 404
    
    db.session.delete(problema)
    db.session.commit()
    
    return jsonify({'message': 'Problema excluído'})

@professor_bp.route('/turmas/<int:turma_id>/alunos')
@jwt_required()
def list_alunos(turma_id):
    professor = check_professor()
    if not professor:
        return jsonify({'error': 'Sem permissão'}), 403
    
    turma = Turma.query.filter_by(id=turma_id, professor_id=professor.id).first()
    if not turma:
        return jsonify({'error': 'Turma não encontrada'}), 404
    
    alunos = db.session.query(User).join(TurmaAluno).filter(TurmaAluno.turma_id == turma_id).all()
    return jsonify([{
        'id': a.id,
        'nome_completo': a.nome_completo,
        'apelido': a.apelido,
        'email': a.email,
        'joined_at': TurmaAluno.query.filter_by(turma_id=turma_id, aluno_id=a.id).first().joined_at.isoformat()
    } for a in alunos])

@professor_bp.route('/turmas/<int:turma_id>/alunos/<int:aluno_id>', methods=['DELETE'])
@jwt_required()
def expulsar_aluno(turma_id, aluno_id):
    professor = check_professor()
    if not professor:
        return jsonify({'error': 'Sem permissão'}), 403
    
    turma = Turma.query.filter_by(id=turma_id, professor_id=professor.id).first()
    if not turma:
        return jsonify({'error': 'Turma não encontrada'}), 404
    
    turma_aluno = TurmaAluno.query.filter_by(turma_id=turma_id, aluno_id=aluno_id).first()
    if turma_aluno:
        db.session.delete(turma_aluno)
        db.session.commit()
        return jsonify({'message': 'Aluno expulso da turma'})
    else:
        return jsonify({'error': 'Aluno não encontrado na turma'}), 404

