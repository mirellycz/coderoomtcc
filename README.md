CODEROOM
========

Plataforma educacional para ensino e prática de programação Python.

INSTALAÇÃO
----------

1. Crie um ambiente virtual (venv):

   Windows:
   python -m venv venv

   Linux/Mac:
   python3 -m venv venv

2. Ative o ambiente virtual:

   Windows:
   venv\Scripts\activate

   Linux/Mac:
   source venv/bin/activate

3. Instale as dependências:

   pip install -r server/requirements.txt

EXECUÇÃO
--------

Execute o servidor:

python run.py

O servidor estará rodando em http://localhost:5000

BANCO DE DADOS
--------------

O sistema usa MySQL. Certifique-se de que o MySQL está instalado e rodando.

Configure a conexão em server/config.py ou use a variável de ambiente DATABASE_URL.

As tabelas são criadas automaticamente na primeira execução.

