import firebase_admin
from firebase_admin import credentials, firestore
import os
from datetime import datetime

class FirebaseStorage:
    def __init__(self):
        # Controlla se l'app è già inizializzata
        if not firebase_admin._apps:
            try:
                # Questo percorso funzionerà sia in locale che su Render (se il Secret File è impostato)
                cred = credentials.Certificate('firebase-service-account.json')
                firebase_admin.initialize_app(cred)
                print("[Firebase] Inizializzazione completata con successo.")
            except Exception as e:
                print(f"[Firebase] ERRORE: Impossibile inizializzare Firebase. Controlla il file 'firebase-service-account.json'. Errore: {e}")
                # In un ambiente di produzione, potresti voler gestire questo errore diversamente
                # Per ora, la stampa dell'errore è sufficiente per il debug su Render
        
        self.db = firestore.client()
        self.document_id = None

    def set_document_id(self, doc_id):
        """Imposta il documento da usare per questo utente."""
        self.document_id = doc_id

    def _get_collection_ref(self):
        """Metodo privato per ottenere il riferimento alla collezione dell'utente."""
        if not self.document_id:
            raise ValueError("ID del documento non impostato. Accesso negato.")
        return self.db.collection('sbb_assenze_data').document(self.document_id).collection('assenze')

    def get_data(self):
        """Recupera tutte le assenze per l'utente corrente."""
        try:
            docs_stream = self._get_collection_ref().order_by("created_at", direction=firestore.Query.DESCENDING).stream()
            data_list = []
            for doc in docs_stream:
                doc_data = doc.to_dict()
                doc_data['id'] = doc.id
                data_list.append(doc_data)
            return data_list
        except Exception:
            # Se il documento o la collezione non esistono, restituisci una lista vuota.
            # Questo è un comportamento normale per un nuovo utente.
            return []

    def add_assenza(self, data):
        """Aggiunge una nuova assenza."""
        try:
            # Aggiungi timestamp di creazione
            data['created_at'] = datetime.now().isoformat()
            _, doc_ref = self._get_collection_ref().add(data)
            return doc_ref.id
        except Exception as e:
            print(f"Errore durante l'aggiunta del documento: {e}")
            return None

    def update_assenza(self, doc_id, data):
        """Aggiorna un'assenza esistente."""
        try:
            data['updated_at'] = datetime.now().isoformat()
            self._get_collection_ref().document(doc_id).update(data)
            return True
        except Exception as e:
            print(f"Errore durante l'aggiornamento del documento {doc_id}: {e}")
            return False

    def delete_assenza(self, doc_id):
        """Elimina un'assenza."""
        try:
            self._get_collection_ref().document(doc_id).delete()
            return True
        except Exception as e:
            print(f"Errore durante l'eliminazione del documento {doc_id}: {e}")
            return False

# Crea una singola istanza della classe da importare nel resto dell'app
firebase_storage = FirebaseStorage()
