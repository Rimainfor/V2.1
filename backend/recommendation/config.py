import pickle

# Chemin d'accès aux fichiers
EMBEDDINGS_PATH = "backend/bin/word2vec_embeddings.pkl"
MODEL_PATH = "backend/bin/knn_model.pkl"

# Algorithm constantes de réglage
THRESHOLD = 0.3
N_SIMILAR = 6
GRAPH_LEVEL = 3

# Load binary data
def load_data(path):
    """
    Description : Chargement des données à partir du chemin. 
    
    Attribut : 
    ------------
        - path : Chaîne. Emplacement du fichier à charger.
    """
    with open(path, 'rb') as f:
        return pickle.load(f)
