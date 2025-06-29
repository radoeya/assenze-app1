from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from datetime import datetime, date
import os
# Importa il nuovo sistema di storage Firebase
from firebase_storage import firebase_storage

app = Flask(__name__)
app.secret_key = 'gestione_assenze_super_segreta_2025' # Chiave cambiata per sicurezza

# Abilita CORS per tutte le route
CORS(app)

# La password di accesso è una sola e fissa
VALID_PASSWORD = 'zfrKBC2025'

@app.route('/', methods=['GET'])
def index():
    if 'logged_in' not in session or not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Invia la pagina. Il JavaScript caricherà i dati.
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
            
            # Imposta il documento/collezione corretto per Firebase
            firebase_storage.set_document_id(password)
            
            print(f"[LOGIN] Accesso utente: {username} con codice: {password}")
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
@app.route('/api/assenze', methods=['GET'])
def get_assenze():
    if not session.get('logged_in'): return jsonify({'error': 'Non autorizzato'}), 401
    try:
        firebase_storage.set_document_id(session['access_code'])
        assenze = firebase_storage.get_data()
        return jsonify(assenze)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/assenze', methods=['POST'])
def add_assenza():
    if not session.get('logged_in'): return jsonify({'error': 'Non autorizzato'}), 401
    try:
        data = request.get_json()
        if not all(k in data for k in ['nome', 'cognome', 'tipologia']):
            return jsonify({'error': 'Dati mancanti'}), 400
        
        firebase_storage.set_document_id(session['access_code'])
        new_id = firebase_storage.add_assenza(data)
        if new_id:
            return jsonify({'id': new_id, 'message': 'Assenza aggiunta con successo'})
        else:
            return jsonify({'error': 'Errore nel salvataggio'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/assenze/<string:assenza_id>', methods=['PUT'])
def update_assenza(assenza_id):
    if not session.get('logged_in'): return jsonify({'error': 'Non autorizzato'}), 401
    try:
        data = request.get_json()
        firebase_storage.set_document_id(session['access_code'])
        if firebase_storage.update_assenza(assenza_id, data):
            return jsonify({'message': 'Assenza aggiornata con successo'}), 200
        else:
            return jsonify({'error': 'Assenza non trovata'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/assenze/<string:assenza_id>', methods=['DELETE'])
def delete_assenza(assenza_id):
    if not session.get('logged_in'): return jsonify({'error': 'Non autorizzato'}), 401
    try:
        firebase_storage.set_document_id(session['access_code'])
        if firebase_storage.delete_assenza(assenza_id):
            return jsonify({'message': 'Rientro confermato'}), 200
        else:
            return jsonify({'error': 'Assenza non trovata'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("[MAIN] Avvio webapp...")
    # debug=True è utile solo in locale per vedere gli errori nel browser
    app.run(host='0.0.0.0', port=5003, debug=True)

