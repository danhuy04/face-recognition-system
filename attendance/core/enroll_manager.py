from datetime import datetime
import os
import pickle
import numpy as np
from core.insightface_singleton import InsightFaceSingleton


class EnrollManager:
    # ================= CONFIG =================
    MIN_CONFIDENCE = 0.60
    MIN_SAMPLE_SIMILARITY = 0.80  # 0.7
    MAX_OUTLIER_DISTANCE = 0.40
    # =========================================

    def __init__(self, db_path="database/embeddings.pkl", max_samples=15):
        self.db_path = db_path
        self.max_samples = max_samples
        self.samples = []           # list[np.ndarray]
        self.last_embedding = None
        self.app = InsightFaceSingleton.get_instance(
            name="buffalo_l",
            providers=["CPUExecutionProvider"],
            det_size=(320, 320),
            ctx_id=0
        )
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        print(f"✓ EnrollManager ready")
        print(f"  - Max samples: {max_samples}")
        print(f"  - Similarity threshold: {self.MIN_SAMPLE_SIMILARITY}")
        print(f"  - Min confidence: {self.MIN_CONFIDENCE}")

    # =====================================================
    def add_frame(self, rgb_frame):
        """Thêm frame vào danh sách mẫu"""
        faces = self.app.get(rgb_frame)
        if len(faces) != 1:
            if len(faces) > 1:
                print(f"⚠ Multiple faces detected ({len(faces)})")
            return False

        face = faces[0]
        if face.det_score < self.MIN_CONFIDENCE:
            print(
                f"⚠ Low confidence: {face.det_score:.3f} < {self.MIN_CONFIDENCE}")
            return False

        emb = face.normed_embedding
        if emb is None:
            print("⚠ No embedding extracted")
            return False

        # ===== Chống sample trùng =====
        if self.last_embedding is not None:
            sim = float(np.dot(emb, self.last_embedding))
            if sim > self.MIN_SAMPLE_SIMILARITY:
                print(
                    f"⚠ Too similar to last sample: {sim:.3f} > {self.MIN_SAMPLE_SIMILARITY}")
                return False
            print(f"✓ Diversity OK: similarity={sim:.3f}")

        self.samples.append(emb)
        self.last_embedding = emb

        print(
            f"✅ Sample #{len(self.samples)} added! ({len(self.samples)}/{self.max_samples})")
        return True

    # =====================================================
    def is_complete(self):
        """Kiểm tra đã đủ số lượng mẫu chưa"""
        complete = len(self.samples) >= self.max_samples
        if complete:
            print(
                f"🎉 Enrollment complete! {len(self.samples)}/{self.max_samples} samples collected")
        return complete

    # =====================================================
    def get_progress(self):
        """Trả về tiến độ thu thập (0.0 - 1.0)"""
        return len(self.samples) / self.max_samples

    # =====================================================
    def _remove_outliers(self, embeddings):
        """Loại bỏ các embedding lệch khỏi trung bình"""
        if len(embeddings) < 5:
            print(
                f"ℹ Too few samples ({len(embeddings)}) to remove outliers, keeping all")
            return embeddings

        mean = np.mean(embeddings, axis=0)
        mean /= (np.linalg.norm(mean) + 1e-10)

        filtered = []
        removed_indices = []

        for i, emb in enumerate(embeddings):
            dist = 1.0 - float(np.dot(emb, mean))  # cosine distance
            if dist <= self.MAX_OUTLIER_DISTANCE:
                filtered.append(emb)
            else:
                removed_indices.append(i)

        if len(filtered) < 5:
            print(
                f"⚠ Too many outliers ({len(removed_indices)}), keeping all samples")
            return embeddings

        print(
            f"✓ Outlier removal: kept {len(filtered)}/{len(embeddings)} samples")
        if removed_indices:
            print(f"  Removed sample indices: {removed_indices}")

        return filtered

    # =====================================================
    def _calculate_quality_score(self, embeddings):
        """Tính điểm chất lượng của tập embeddings"""
        if len(embeddings) < 2:
            return 0.0

        # Tính độ phân tán (variance) - cao hơn = đa dạng hơn
        mean = np.mean(embeddings, axis=0)
        variances = []
        for emb in embeddings:
            dist = 1.0 - float(np.dot(emb, mean))
            variances.append(dist)

        avg_variance = np.mean(variances)
        quality_score = min(1.0, avg_variance / 0.2)  # Normalize to 0-1

        return quality_score

    # =====================================================
    def save(self, student_id, name):
        if not self.samples:
            print("❌ Không có mẫu để lưu")
            return False

        print(f"\n{'='*60}")
        print(f"💾 Saving enrollment for: {name} ({student_id})")
        print(f"{'='*60}")

        # ===== Remove outliers =====
        embeddings = self._remove_outliers(self.samples)

        # ===== Calculate quality =====
        quality = self._calculate_quality_score(embeddings)
        print(f"📊 Quality score: {quality:.2%}")

        # ===== Mean + normalize =====
        mean_emb = np.mean(embeddings, axis=0)
        mean_emb /= (np.linalg.norm(mean_emb) + 1e-10)

        # Thời điểm hiện tại
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ===== Load existing database =====
        data = []
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "rb") as f:
                    data = pickle.load(f)
                print(f"✓ Loaded existing database ({len(data)} records)")
            except Exception as e:
                print(f"⚠ Error loading database: {e}")
                data = []

        # ===== Update or append =====
        updated = False
        for i, item in enumerate(data):
            if item["id"] == student_id:
                # GIỮ created_date cũ
                record = {
                    "id": student_id,
                    "name": name,
                    "embedding": mean_emb,
                    "num_samples": len(embeddings),
                    "quality_score": quality,
                    "model": "buffalo_l",
                    "created_date": item.get("created_date", now)
                }
                data[i] = record
                updated = True
                print(f"✓ Updated existing record for {student_id}")
                break

        if not updated:
            # Nhân viên mới → tạo created_date
            record = {
                "id": student_id,
                "name": name,
                "embedding": mean_emb,
                "num_samples": len(embeddings),
                "quality_score": quality,
                "model": "buffalo_l",
                "created_date": now
            }
            data.append(record)
            print(f"✓ Added new record for {student_id}")

        # ===== Save to file =====
        try:
            with open(self.db_path, "wb") as f:
                pickle.dump(data, f)
            print(f"✅ SUCCESS!")
            print(f"   Student: {name} ({student_id})")
            print(f"   Samples: {len(embeddings)}/{len(self.samples)}")
            print(f"   Quality: {quality:.2%}")
            print(f"   Created: {record['created_date']}") # type: ignore
            print(f"   Location: {self.db_path}")
            print(f"{'='*60}\n")
        except Exception as e:
            print(f"❌ Lỗi lưu embedding: {e}")
            return False

        # ===== Clear samples =====
        self.samples.clear()
        self.last_embedding = None

        return True

    # =====================================================
    def reset(self):
        self.samples.clear()
        self.last_embedding = None
        print("♻️  EnrollManager reset")
