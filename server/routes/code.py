from flask import Blueprint, request, jsonify
import subprocess
import sys

code_bp = Blueprint('code', __name__, url_prefix='/api')

@code_bp.route('/execute-code', methods=['POST'])
def execute_code():
    try:
        data = request.get_json()
        code = data.get('code', '')
        input_data = data.get('input', '')
        
        if not code.strip():
            return jsonify({
                'success': False,
                'output': '',
                'error': 'Código vazio'
            })
        
        try:
            imports = """import sys
import os
import math
import random
import datetime
from datetime import datetime, date, time

"""
            full_code = imports + code
            
            process = subprocess.Popen(
                ['python', '-u', '-c', full_code],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            if input_data:
                formatted_input = input_data
                if not formatted_input.endswith('\n'):
                    formatted_input += '\n'
                stdout, stderr = process.communicate(input=formatted_input, timeout=10)
            else:
                process.stdin.close()
                try:
                    stdout, stderr = process.communicate(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()
                    return jsonify({
                        'success': False,
                        'output': stdout if stdout else '',
                        'error': 'Timeout: código excedeu 10 segundos. Verifique se precisa de input().'
                    })
            
            if process.returncode == 0:
                return jsonify({
                    'success': True,
                    'output': stdout if stdout else '',
                    'error': ''
                })
            else:
                return jsonify({
                    'success': False,
                    'output': stdout if stdout else '',
                    'error': stderr if stderr else 'Erro desconhecido'
                })
                
        except subprocess.TimeoutExpired:
            return jsonify({
                'success': False,
                'output': '',
                'error': 'Timeout: código excedeu 10 segundos'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'output': '',
                'error': f'Erro: {str(e)}'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'output': '',
            'error': f'Erro: {str(e)}'
        }), 500

def executar_codigo_python(codigo, entrada):
    try:
        if entrada:
            process = subprocess.run(
                ['python', '-c', codigo],
                input=entrada,
                text=True,
                capture_output=True,
                timeout=5,
                encoding='utf-8',
                errors='replace'
            )
        else:
            process = subprocess.run(
                ['python', '-c', codigo],
                text=True,
                capture_output=True,
                timeout=5,
                encoding='utf-8',
                errors='replace'
            )
        
        if process.returncode == 0:
            return process.stdout
        else:
            return f"Erro: {process.stderr}"
    
    except subprocess.TimeoutExpired:
        return "Erro: timeout"
    except Exception as e:
        return f"Erro: {str(e)}"

