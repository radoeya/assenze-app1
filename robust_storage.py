import firebase_admin
from firebase_admin import credentials, firestore

class FirebaseStorage:
    def __init__(self):
        try:
            # Inizializza l'app Firebase usando la chiave di servizio
            cred = credentials.Certificate('firebase-service-account.json')
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            self.collection_name = None
            print("[FIREBASE] Sistema di storage Firebase inizializzato e connesso.")
        except Exception as e:
            print(f"[FIREBASE] ERRORE: Impossibile inizializzare Firebase. Assicurati che il file 'firebase-service-account.json' sia presente e valido. Dettagli: {e}")
            self.db = None

    def set_document_id(self, access_code):
        """Imposta il nome della collezione Firestore basato sul codice d'accesso."""
        # Usiamo il codice d'accesso per definire una "collezione" (come una tabella)
        self.collection_name = f"sbb_assenze_{access_code}"
        print(f"[FIREBASE] Collezione impostata su: {self.collection_name}")

    def get_data(self):
        """Recupera tutti i documenti (assenze) dalla collezione corrente."""
        if not self.db or not self.collection_name:
            return []
        
        assenze = []
        # Recupera tutti i documenti dalla collezione
        docs = self.db.collection(self.collection_name).stream()
        for doc in docs:
            assenza_data = doc.to_dict()
            # Usiamo l'ID del documento di Firestore come 'id' per la nostra app
            assenza_data['id'] = doc.id
            assenze.append(assenza_data)
        
        # Ordina per data di creazione per coerenza
        assenze.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return assenze

    def add_assenza(self, assenza_data):
        """Aggiunge una nuova assenza come un nuovo documento in Firestore."""
        if not self.db or not self.collection_name:
            return None
        
        # Aggiunge un nuovo documento con un ID generato automaticamente
        update_time, doc_ref = self.db.collection(self.collection_name).add(assenza_data)
        print(f"[FIREBASE] Assenza aggiunta con ID: {doc_ref.id}")
        return doc_ref.id

    def update_assenza(self, assenza_id, data_to_update):
        """Aggiorna un'assenza esistente in Firestore."""
        if not self.db or not self.collection_name:
            return False
        
        try:
            self.db.collection(self.collection_name).document(assenza_id).update(data_to_update)
            print(f"[FIREBASE] Assenza {assenza_id} aggiornata.")
            return True
        except Exception as e:
            print(f"[FIREBASE] Errore durante l'aggiornamento dell'assenza {assenza_id}: {e}")
            return False

    def delete_assenza(self, assenza_id):
        """Elimina un'assenza da Firestore."""
        if not self.db or not self.collection_name:
            return False
        
        try:
            self.db.collection(self.collection_name).document(assenza_id).delete()
            print(f"[FIREBASE] Assenza {assenza_id} eliminata.")
            return True
        except Exception as e:
            print(f"[FIREBASE] Errore durante l'eliminazione dell'assenza {assenza_id}: {e}")
            return False

    def validate_access_code(self, access_code):
        """Valida il codice d'accesso (logica invariata)."""
        return access_code and len(access_code.strip()) >= 3

# Istanza globale
firebase_storage = FirebaseStorage()