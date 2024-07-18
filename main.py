import cv2
from icecream import ic
from detector import Detector
from pid import IncreasementalPID

my_pid = IncreasementalPID(0.3,0,0)

from servo import Servo

people_detector = Detector(target_cls=39)


def calculate(x):
    return 0.3 * x  # - 5.758


cap = cv2.VideoCapture(1)

if cap.isOpened():
    ret, frame = cap.read()

HEIGHT, WIDTH = frame.shape[:2]
MIDDLE_CENTER = (WIDTH // 2, HEIGHT // 2)  # 画面正中心

MAX_SAME_PERSON_DELTA = 300  # 标定在多少距离范围以内识别为同一个人


previous_center = None

myservo = Servo("COM7")
# myservo = None

if myservo is not None:
    if not myservo.status:
        print("舵机状态异常")
        exit(0)
    assert myservo.ping(1), "舵机1状态异常"
    assert myservo.ping(2), "舵机2状态异常"
if myservo is not None:
    myservo.revolve(1, 512, 0, 0)
    position = 512

fourcc = cv2.VideoWriter_fourcc(*"XVID")
cap1 = cv2.VideoWriter("testwrite.avi", fourcc, 20.0, (WIDTH, HEIGHT), True)

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


        cv2.putText(
            frame,
            f"delta_x:{delta_x}",
            (100, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 255, 0),
            2,
        )

        delta_target = my_pid(delta_x)

        cv2.putText(
            frame,
            f"delta_target:{delta_target}",
            (100, 200),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (255, 0, 0),
            2,
        )

        if abs(delta_x) > 30:
            target = position - delta_target
            myservo.revolve(1,int(target),0,1000)
            position = target

    cap1.write(frame)
    cv2.imshow("win", frame)
    k = cv2.waitKey(10)
    if k == ord("q"):
        break
    ret, frame = cap.read()

cap1.release()
cap.release()
cv2.destroyAllWindows()
