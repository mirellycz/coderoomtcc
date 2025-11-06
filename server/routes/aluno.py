from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from server.models import db, User, Turma, Problema, Tentativa, TurmaAluno
from server.routes.code import executar_codigo_python

aluno_bp = Blueprint('aluno', __name__, url_prefix='/aluno')

def check_aluno():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user or user.tipo_usuario != 'aluno':
        return None
    
    return user

@aluno_bp.route('/entrar-turma', methods=['POST'])
@jwt_required()
def entrar_turma():
    aluno = check_aluno()
    if not aluno:
        return jsonify({'error': 'Sem permissão'}), 403
    
    data = request.get_json()
    codigo = data.get('codigo')
    
    turma = Turma.query.filter_by(codigo=codigo).first()
    if not turma:
        return jsonify({'error': 'Código inválido'}), 404
    
    if TurmaAluno.query.filter_by(turma_id=turma.id, aluno_id=aluno.id).first():
        return jsonify({'error': 'Já está nesta turma'}), 400
    
    turma_aluno = TurmaAluno(turma_id=turma.id, aluno_id=aluno.id)
    db.session.add(turma_aluno)
    db.session.commit()
    
    return jsonify({'message': 'Entrou na turma'})

@aluno_bp.route('/turmas')
@jwt_required()
def list_turmas():
    aluno = check_aluno()
    if not aluno:
        return jsonify({'error': 'Sem permissão'}), 403
    
    turmas = db.session.query(Turma).join(TurmaAluno).filter(TurmaAluno.aluno_id == aluno.id).all()
    return jsonify([{
        'id': t.id,
        'nome': t.nome,
        'descricao': t.descricao,
        'codigo': t.codigo,
        'joined_at': TurmaAluno.query.filter_by(turma_id=t.id, aluno_id=aluno.id).first().joined_at.isoformat()
    } for t in turmas])

@aluno_bp.route('/turmas/<int:turma_id>/problemas')
@jwt_required()
def list_problemas(turma_id):
    aluno = check_aluno()
    if not aluno:
        return jsonify({'error': 'Sem permissão'}), 403
    
    if not TurmaAluno.query.filter_by(turma_id=turma_id, aluno_id=aluno.id).first():
        return jsonify({'error': 'Não está nesta turma'}), 403
    
    problemas = Problema.query.filter_by(turma_id=turma_id).all()
    problemas_data = []
    
    for problema in problemas:
        tentativa_correta = Tentativa.query.filter_by(
            aluno_id=aluno.id, 
            problema_id=problema.id, 
            resultado='correto'
        ).first()
        
        status = 'resolvido' if tentativa_correta else 'atribuido'
        
        problemas_data.append({
            'id': problema.id,
            'titulo': problema.titulo,
            'enunciado': problema.enunciado,
            'entrada': problema.entrada,
            'saida': problema.saida,
            'restricoes': problema.restricoes,
            'status': status,
            'created_at': problema.created_at.isoformat()
        })
    
    return jsonify(problemas_data)

@aluno_bp.route('/problemas/<int:problema_id>/enviar', methods=['POST'])
@jwt_required()
def enviar_resposta(problema_id):
    aluno = check_aluno()
    if not aluno:
        return jsonify({'error': 'Sem permissão'}), 403
    
    data = request.get_json()
    codigo = data.get('codigo')
    
    problema = Problema.query.get(problema_id)
    if not problema:
        return jsonify({'error': 'Problema não encontrado'}), 404
    
    if Tentativa.query.filter_by(aluno_id=aluno.id, problema_id=problema_id, resultado='correto').first():
        return jsonify({'error': 'Já resolveu este problema'}), 400
    
    entrada_teste = problema.entrada if problema.entrada else ""
    
    resultado = executar_codigo_python(codigo, entrada_teste)
    
    resultado_stripped = resultado.strip()
    resposta_esperada_stripped = problema.resposta_esperada.strip()
    
    if resultado_stripped == resposta_esperada_stripped:
        resultado_final = 'correto'
        feedback = 'OK'
    else:
        resultado_final = 'incorreto'
        feedback = f'Esperado: {resposta_esperada_stripped}, obtido: {resultado_stripped}'
    
    tentativa = Tentativa(
        aluno_id=aluno.id,
        problema_id=problema_id,
        codigo=codigo,
        resultado=resultado_final,
        feedback=feedback
    )
    
    db.session.add(tentativa)
    db.session.commit()
    
    return jsonify({
        'resultado': resultado_final,
        'feedback': feedback,
        'saida_obtida': resultado
    })

@aluno_bp.route('/tentativas')
@jwt_required()
def historico_tentativas():
    aluno = check_aluno()
    if not aluno:
        return jsonify({'error': 'Sem permissão'}), 403
    
    tentativas = Tentativa.query.filter_by(aluno_id=aluno.id).order_by(Tentativa.created_at.desc()).all()
    return jsonify([{
        'id': t.id,
        'problema_id': t.problema_id,
        'problema_titulo': Problema.query.get(t.problema_id).titulo,
        'resultado': t.resultado,
        'feedback': t.feedback,
        'created_at': t.created_at.isoformat()
    } for t in tentativas])

