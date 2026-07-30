import threading
from insightface.app import FaceAnalysis

class InsightFaceSingleton:
    _instance = None
    _lock = threading.Lock()  

    @classmethod
    def get_instance(cls, name='buffalo_l', providers=None, det_size=(640, 640), ctx_id=0):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    print("Khởi tạo InsightFace singleton lần đầu... (có thể mất vài giây)")
                    if providers is None:
                        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']  

                    app = FaceAnalysis(name=name, providers=providers)
                    app.prepare(ctx_id=ctx_id, det_size=det_size)
                    cls._instance = app
                    print("InsightFace singleton đã sẵn sàng!")
        return cls._instance