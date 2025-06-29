from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from datetime import datetime, date
import os
# Importa il sistema di storage Firebase
from firebase_storage import firebase_storage

app = Flask(__name__)
app.secret_key = 'gestione_assenze_robust_2025'

# Abilita CORS per tutte le route
CORS(app)

# MODIFICA: Imposta la password di accesso valida e fissa
VALID_PASSWORD = 'zfrKBC2025'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Se la richiesta è POST, viene gestita dalla funzione di login.
        return login()
    
    # Se l'utente non è loggato, mostra la pagina di login.
    if 'logged_in' not in session or not session.get('logged_in'):
        return render_template('login_professional.html')
    
    # Se l'utente è loggato, invia la pagina principale. 
    # Il JavaScript si occuperà di caricare i dati.
    return render_template('index_firebase.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # MODIFICA: La validazione ora controlla una password specifica e fissa.
        if username == 'xp256' and password == VALID_PASSWORD:
            # La password è corretta. Salva i dati nella sessione.
            session['access_code'] = password
            session['username'] = username
            session['logged_in'] = True
            
            # Imposta il documento/collezione corretto per Firebase.
            # Questa linea assicura che i dati vengano salvati nel posto giusto.
            firebase_storage.set_document_id(password)
            
            print(f"[LOGIN] Accesso utente: {username} con codice: {password}")
            return redirect(url_for('index'))
        else:
            # Se la password o l'username sono sbagliati, non viene creato nessun dato.
            # Mostra un messaggio di errore generico per sicurezza.
            error_msg = 'Username o Password non validi.'
            print(f"[LOGIN FALLITO] Tentativo di accesso con username: '{username}'")
            return render_template('login_professional.html', error=error_msg)
    
    # Se il metodo non è POST, mostra semplicemente la pagina di login.
    return render_template('login_professional.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/assenze', methods=['GET'])
def get_assenze():
    if not session.get('logged_in') or 'access_code' not in session:
        return jsonify({'error': 'Non autorizzato'}), 401
    
    try:
        firebase_storage.set_document_id(session['access_code'])
        assenze = firebase_storage.get_data()
        
        print(f"[API] Recuperate {len(assenze)} assenze per utente: {session.get('username', 'unknown')}")
        return jsonify(assenze)
        
    except Exception as e:
        print(f"Errore nel recupero assenze: {str(e)}")
        return jsonify({'error': 'Errore nel recupero dati'}), 500

@app.route('/api/assenze', methods=['POST'])
def add_assenza():
    if not session.get('logged_in') or 'access_code' not in session:
        return jsonify({'error': 'Non autorizzato'}), 401
    
    try:
        assenza_data = request.get_json()
        
        if not all(k in assenza_data for k in ['nome', 'cognome', 'tipologia']):
            return jsonify({'error': 'Dati mancanti'}), 400
        
        firebase_storage.set_document_id(session['access_code'])
        
        nuova_assenza = {
            'nome': assenza_data.get('nome'),
            'cognome': assenza_data.get('cognome'),
            'tipologia': assenza_data.get('tipologia'),
            'malattia': assenza_data.get('malattia', False),
            'malattia_dal': assenza_data.get('malattia_dal', ''),
            'malattia_al': assenza_data.get('malattia_al', ''),
            'malattia_stato': assenza_data.get('malattia_stato', ''),
            'infortunio': assenza_data.get('infortunio', False),
            'infortunio_dal': assenza_data.get('infortunio_dal', ''),
            'infortunio_al': assenza_data.get('infortunio_al', ''),
            'altro': assenza_data.get('altro', False),
            'altro_dal': assenza_data.get('altro_dal', ''),
            'altro_al': assenza_data.get('altro_al', ''),
            'restrizione': assenza_data.get('restrizione_oraria', False),
            'restrizione_dal': assenza_data.get('restrizione_dal', ''),
            'restrizione_al': assenza_data.get('restrizione_al', ''),
            'commenti': assenza_data.get('commenti', ''),
            'created_at': datetime.now().isoformat()
        }

        new_id = firebase_storage.add_assenza(nuova_assenza)

        if new_id:
            return jsonify({'id': new_id, 'message': 'Assenza aggiunta con successo'})
        else:
            return jsonify({'error': 'Errore nel salvataggio'}), 500
        
    except Exception as e:
        print(f"Errore nell'aggiunta assenza: {str(e)}")
        return jsonify({'error': 'Errore nel salvataggio'}), 500

@app.route('/api/assenze/<string:assenza_id>', methods=['PUT'])
def update_assenza(assenza_id):
    if not session.get('logged_in') or 'access_code' not in session:
        return jsonify({'error': 'Non autorizzato'}), 401
    
    try:
        data = request.get_json()
        data['updated_at'] = datetime.now().isoformat()
        
        firebase_storage.set_document_id(session['access_code'])
        success = firebase_storage.update_assenza(assenza_id, data)
        
        if success:
            return jsonify({'message': 'Assenza aggiornata con successo'}), 200
        else:
            return jsonify({'error': 'Assenza non trovata o errore nell\'aggiornamento'}), 404
            
    except Exception as e:
        print(f"Errore nell'aggiornamento assenza: {str(e)}")
        return jsonify({'error': 'Errore nell\'aggiornamento assenza'}), 500

@app.route('/api/assenze/<string:assenza_id>', methods=['DELETE'])
def delete_assenza(assenza_id):
    if not session.get('logged_in') or 'access_code' not in session:
        return jsonify({'error': 'Non autorizzato'}), 401
    
    try:
        firebase_storage.set_document_id(session['access_code'])
        success = firebase_storage.delete_assenza(assenza_id)
        
        if success:
            return jsonify({'message': 'Rientro confermato, assenza rimossa'}), 200
        else:
            return jsonify({'error': 'Assenza non trovata'}), 404
        
    except Exception as e:
        print(f"Errore nell'eliminazione assenza: {str(e)}")
        return jsonify({'error': 'Errore nell\'eliminazione'}), 500

@app.route('/api/notifiche')
def get_notifiche():
    if not session.get('logged_in') or 'access_code' not in session:
        return jsonify({'error': 'Non autorizzato'}), 401
    
    try:
        firebase_storage.set_document_id(session['access_code'])
        assenze = firebase_storage.get_data()
        
        today = date.today()
        notifiche = {'rientri_urgenti': 0, 'colore_badge': 'verde'}
        
        for assenza in assenze:
            end_date_str = None
            if assenza.get('malattia') and assenza.get('malattia_al'): end_date_str = assenza['malattia_al']
            elif assenza.get('infortunio') and assenza.get('infortunio_al'): end_date_str = assenza['infortunio_al']
            elif assenza.get('altro') and assenza.get('altro_al'): end_date_str = assenza['altro_al']
            elif assenza.get('restrizione') and assenza.get('restrizione_al'): end_date_str = assenza['restrizione_al']
            
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                days_remaining = (end_date - today).days
                if 0 <= days_remaining <= 4:
                    notifiche['rientri_urgenti'] += 1
                    if days_remaining <= 2: notifiche['colore_badge'] = 'rosso'
                    elif days_remaining <= 4 and notifiche['colore_badge'] != 'rosso': notifiche['colore_badge'] = 'arancione'
        
        return jsonify(notifiche)
        
    except Exception as e:
        print(f"Errore nel recupero notifiche: {str(e)}")
        return jsonify({'error': 'Errore nel recupero notifiche'}), 500

if __name__ == '__main__':
    print("[MAIN] Avvio webapp con sistema di storage Firebase")
    # MODIFICA: Aggiornato il messaggio di avvio per non mostrare la password
    print("[MAIN] Sistema di accesso con password specifica pronto.")
    app.run(host='0.0.0.0', port=5003, debug=False)
