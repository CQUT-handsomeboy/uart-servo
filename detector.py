import numpy as np
from icecream import ic


class YOLODetector:
    def __init__(
        self, modelfile: str = "./LFS/yolov8n.pt", target_cls: int = 0
    ) -> None:
        from ultralytics import YOLO

        self.model = YOLO(modelfile)  # 模型文件
        self.target_cls = target_cls  # 目标标签

    def __call__(self, frame: np.array):
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


class MoveNetDetector:
    def __init__(
        self, modelname: str = "movenet_lightning", target_point: int = 0
    ) -> None:
        import tensorflow_hub as hub
        import tensorflow as tf

        self.tf = tf

        assert 0 <= target_point <= 16
        self.target_poinit = target_point

        match modelname:
            case "movenet_lightning":
                self.module = hub.load(
                    "https://tfhub.dev/google/movenet/singlepose/lightning/4"
                )
                self.input_size = 192
            case "movenet_thunder":
                self.module = hub.load(
                    "https://tfhub.dev/google/movenet/singlepose/thunder/4"
                )
                self.input_size = 256

    def movenet(self, input_image):
        model = self.module.signatures["serving_default"]
        input_image = self.tf.cast(input_image, dtype=self.tf.int32)
        outputs = model(input_image)
        keypoints_with_scores = outputs["output_0"].numpy()
        return keypoints_with_scores

    def __call__(self, image: np.array):
        width, height, _ = image.shape
        input_image = self.tf.expand_dims(image, axis=0)
        input_image = self.tf.image.resize_with_pad(
            input_image, self.input_size, self.input_size
        )

        keypoints_with_scores = self.movenet(input_image)

        k = np.reshape(keypoints_with_scores, (-1, 3))

        keypoints = [(int(y * width), int(x * height)) for x, y, _ in k]

        keypoint = keypoints[self.target_poinit]

        return keypoint


if __name__ == "__main__":
    import cv2

    sample_image = cv2.imread("./sample_image.jpg")
    movenet = MoveNetDetector()
    result = movenet(sample_image)

    print(result)
