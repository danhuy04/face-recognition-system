import numpy as np
import pickle
import os

class FaceMatcher:
    def __init__(self, db_path="database/embeddings.pkl", threshold=0.45):
        self.db_path = db_path         
        self.threshold = threshold
        self.embeddings = None
        self.ids = []
        self.names = []
        self._load()                   

    def _load(self):
        """Hàm load hoặc reload embeddings"""
        self.embeddings = None
        self.ids = []
        self.names = []

        if not os.path.exists(self.db_path):
            print("Không tìm thấy file embeddings.pkl")
            return

        try:
            with open(self.db_path, "rb") as f:
                data = pickle.load(f)

            if not data:
                print("File embeddings rỗng")
                return

            self.embeddings = np.array([item["embedding"] for item in data])
            self.ids = [item["id"] for item in data]
            self.names = [item["name"] for item in data]

            # Normalize 
            norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
            self.embeddings /= np.maximum(norms, 1e-10)

            print(f"Loaded / Reloaded {len(self.ids)} known faces from {self.db_path}")
        except Exception as e:
            print(f"Lỗi khi load embeddings: {e}")

    def reload(self):
        print("Reloading embeddings sau khi enroll mới...")
        self._load()

    def match(self, query_embedding):
        if self.embeddings is None or len(self.embeddings) == 0:
            return None, None, 0.0

        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)
        similarities = np.dot(self.embeddings, query_norm)

        idx = np.argmax(similarities)
        best_sim = similarities[idx]

        if best_sim >= self.threshold:
            return self.ids[idx], self.names[idx], best_sim
        else:
            return None, None, best_sim