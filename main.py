from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from datetime import datetime, date
import os
# Importa il sistema di storage Firebase
from firebase_storage import firebase_storage

app = Flask(__name__)
app.secret_key = 'gestione_assenze_super_segreta_2025' # Chiave cambiata per sicurezza

CORS(app)

VALID_PASSWORD = 'zfrKBC2025'

@app.route('/', methods=['GET'])
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('index_firebase.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if username == 'xp256' and password == VALID_PASSWORD:
            session['access_code'] = password
            session['username'] = username
            session['logged_in'] = True
            print(f"[LOGIN] Accesso utente: {username}")
            return redirect(url_for('index'))
        else:
            error_msg = 'Username o Password non validi.'
            print(f"[LOGIN FALLITO] Tentativo di accesso con username: '{username}'")
            return render_template('login_professional.html', error=error_msg)
    
    return render_template('login_professional.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- API Endpoints ---
def check_auth():
    return 'logged_in' in session and session.get('logged_in')

@app.route('/api/assenze', methods=['GET'])
def get_assenze():
    if not check_auth(): return jsonify({'error': 'Non autorizzato'}), 401
    try:
        firebase_storage.set_document_id(session['access_code'])
        assenze = firebase_storage.get_data()
        return jsonify(assenze)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/assenze', methods=['POST'])
def add_assenza():
    if not check_auth(): return jsonify({'error': 'Non autorizzato'}), 401
    try:
        data = request.get_json()
        if not all(k in data for k in ['nome', 'cognome', 'tipologia']):
            return jsonify({'error': 'Dati mancanti'}), 400
        
        firebase_storage.set_document_id(session['access_code'])
        new_id = firebase_storage.add_assenza(data)
        if new_id:
            return jsonify({'id': new_id, 'message': 'Assenza aggiunta con successo'})
        return jsonify({'error': 'Errore nel salvataggio'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/assenze/<string:assenza_id>', methods=['PUT'])
def update_assenza(assenza_id):
    if not check_auth(): return jsonify({'error': 'Non autorizzato'}), 401
    try:
        data = request.get_json()
        firebase_storage.set_document_id(session['access_code'])
        if firebase_storage.update_assenza(assenza_id, data):
            return jsonify({'message': 'Assenza aggiornata con successo'}), 200
        return jsonify({'error': 'Assenza non trovata'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/assenze/<string:assenza_id>', methods=['DELETE'])
def delete_assenza(assenza_id):
    if not check_auth(): return jsonify({'error': 'Non autorizzato'}), 401
    try:
        firebase_storage.set_document_id(session['access_code'])
        if firebase_storage.delete_assenza(assenza_id):
            return jsonify({'message': 'Rientro confermato'}), 200
        return jsonify({'error': 'Assenza non trovata'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("[MAIN] Avvio webapp...")
    app.run(host='0.0.0.0', port=5003, debug=True)
