from ultralytics import YOLO
import numpy as np
from icecream import ic


class Detector:
    def __init__(
        self, modelfile: str = "./LFS/yolov8n.pt", target_cls: int = 0
    ) -> None:
        self.model = YOLO(modelfile)  # 模型文件
        self.target_cls = target_cls  # 目标标签

    def detect(self, frame: np.array):
        result = self.model(frame)[0]
        if len(result) == 0:
            return None  # 未识别到
        for i, cl in enumerate(result.boxes.cls):
            if cl != self.target_cls:
                continue
            xyxy = result.boxes.xyxy[i]
            center = int((xyxy[0] + xyxy[2]) / 2), int((xyxy[1] + xyxy[3]) / 2)

            return center
        return None
