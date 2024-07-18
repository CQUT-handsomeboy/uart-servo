import cv2
from icecream import ic
from detector import Detector

# from servo import Servo

people_detector = Detector()

cap = cv2.VideoCapture(1)

if cap.isOpened():
    ret, frame = cap.read()

HEIGHT, WIDTH = frame.shape[:2]
MIDDLE_CENTER = (WIDTH // 2, HEIGHT // 2) # 画面正中心

MAX_SAME_PERSON_DELTA = 300  # 标定在多少距离范围以内识别为同一个人

previous_center = None

while ret:
    center = people_detector.detect(frame)
    if center is not None:
        # 检测出了人
        if previous_center is not None:
            # 有前一次中心点位的数据，可以作差
            delta_x = center[0] - previous_center[0]
            delta_y = center[1] - previous_center[1]

            if delta_x > MAX_SAME_PERSON_DELTA or delta_y > MAX_SAME_PERSON_DELTA:
                # 识别到的不是同一个人
                center = previous_center

        cv2.circle(frame, center, 5, (0, 255, 0), -1)
        cv2.line(frame, center, MIDDLE_CENTER, (0, 255, 0), 2)

        delta_x = MIDDLE_CENTER[0] - center[0]
        delta_y = MIDDLE_CENTER[1] - center[1]
        ic(delta_x,delta_y)

    cv2.imshow("win", frame)
    k = cv2.waitKey(10)
    if k == ord("q"):
        break
    ret, frame = cap.read()

cap.release()
cv2.destroyAllWindows()
