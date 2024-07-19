import cv2
from icecream import ic
from detector import YOLODetector, MoveNetDetector

from filter import KalmanFilter

kf = KalmanFilter()

from pickle import dump

target_data = []
data = []

"""
下方舵机
"""

kp0, ki0, kd0 = 0.16, 0, 0

prev_error0, prev_prev_error0 = 0, 0


def pid0(error0):
    global prev_error0, prev_prev_error0

    P = error0
    D = prev_error0 - prev_prev_error0

    output = kp0 * P + kd0 * D
    # output = kf(output)

    # output = 100 * (1 if output > 0 else -1) if abs(output) > 100 else output
    data.append(output)

    prev_error0 = error0
    prev_prev_error0 = prev_prev_error0

    return output


"""
上方舵机
"""

kp1, ki1, kd1 = 0.008, 0, 0

prev_error1, prev_prev_error1 = 0, 0


def pid1(error1):
    global prev_error1, prev_prev_error1

    P = error1
    D = prev_error1 - prev_prev_error1

    output = kp1 * P + kd1 * D
    data.append(output)

    prev_error1 = error1
    prev_prev_error1 = prev_prev_error1

    return output


from servo import Servo

detector = YOLODetector(target_cls=0)

cap = cv2.VideoCapture(0)

if cap.isOpened():
    ret, frame = cap.read()

HEIGHT, WIDTH = frame.shape[:2]
MIDDLE_CENTER = (WIDTH // 2, HEIGHT // 2)  # 画面正中心

myservo = Servo("COM7")

if myservo is not None:
    if not myservo.status:
        print("舵机状态异常")
        exit(0)
    assert myservo.ping(1), "舵机1状态异常"
    assert myservo.ping(2), "舵机2状态异常"
if myservo is not None:
    xposition = 604
    myservo.revolve(1, xposition, 0, 0)
    yposition = 536
    myservo.revolve(2, yposition, 0, 0)


cv2.namedWindow("win")


def on_kp_change(x):
    global kp1
    kp1 = x / 1000 * 0.5


def on_ki_change(x):
    global ki1
    ki1 = x / 1000 * 0.5


def on_kd_change(x):
    global kd1
    kd1 = x / 1000 * 0.5


string_x = range(0, WIDTH, 5)


def show_pid_args(img):

    cv2.putText(
        img,
        f"kp:{kp1}",
        (100, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (0, 0, 255),
        2,
    )

    cv2.putText(
        img,
        f"ki:{ki1}",
        (100, 200),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (0, 0, 255),
        2,
    )

    cv2.putText(
        img,
        f"kd:{kd1}",
        (100, 300),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (0, 0, 255),
        2,
    )


cv2.createTrackbar("kP", "win", 0, 1000, on_kp_change)
cv2.createTrackbar("kI", "win", 0, 1000, on_ki_change)
cv2.createTrackbar("kD", "win", 0, 1000, on_kd_change)


while ret:
    center = detector(frame)
    show_pid_args(frame)
    if center is not None:  # 检测出了人
        cv2.circle(frame, center, 5, (0, 255, 0), -1)
        cv2.line(frame, center, MIDDLE_CENTER, (0, 255, 0), 2)

        # x
        center_x, center_y = center

        delta_x = MIDDLE_CENTER[0] - center_x
        delta_x = 0 if abs(delta_x) < 10 else delta_x

        cv2.putText(
            frame,
            f"delta_x:{delta_x}",
            (100, 400),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 0, 255),
            2,
        )

        delta_target_xpostion = pid0(delta_x)
        cv2.putText(
            frame,
            f"delta_target_postion:{delta_target_xpostion}",
            (100, 500),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (255, 0, 0),
            2,
        )
        target_xposition = xposition - delta_target_xpostion
        myservo.revolve(1, int(target_xposition), 0, 0)
        xposition = target_xposition

        # y

        delta_y = MIDDLE_CENTER[1] - center_y
        delta_y = 0 if abs(delta_y) < 50 else delta_y

        delta_target_ypostion = pid0(delta_y)
        cv2.putText(
            frame,
            f"delta_y:{delta_y}",
            (200, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 0, 255),
            2,
        )
        target_yposition = yposition - delta_target_ypostion

        target_yposition = 600 if target_yposition > 600 else target_yposition
        target_yposition = 350 if target_yposition < 350 else target_yposition

        myservo.revolve(2, int(target_yposition), 0, 0)
        yposition = target_yposition

    else:
        cv2.putText(
            frame,
            "No detection",
            (200, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (255, 255, 0),
            2,
        )

    cv2.imshow("win", frame)
    k = cv2.waitKey(10)
    if k == ord("q"):
        break
    ret, frame = cap.read()

cap.release()
cv2.destroyAllWindows()

with open("./data.pkl", "wb") as f:
    dump(data, f)
