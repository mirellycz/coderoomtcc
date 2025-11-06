from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    nome_completo = db.Column(db.String(100), nullable=False)
    apelido = db.Column(db.String(50), nullable=False)
    tipo_usuario = db.Column(db.String(20), nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.senha_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.senha_hash, password)

class Turma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    codigo = db.Column(db.String(6), unique=True, nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TurmaAluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    aluno_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

class Problema(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    enunciado = db.Column(db.Text, nullable=False)
    entrada = db.Column(db.Text)
    saida = db.Column(db.Text)
    restricoes = db.Column(db.Text)
    resposta_esperada = db.Column(db.Text, nullable=False)
    linguagem = db.Column(db.String(20), default='python')
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Tentativa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    problema_id = db.Column(db.Integer, db.ForeignKey('problema.id'), nullable=False)
    codigo = db.Column(db.Text, nullable=False)
    resultado = db.Column(db.String(20), nullable=False)
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

