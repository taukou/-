import cv2
import numpy as np
import time
from picamera2 import Picamera2

# =========================================================
# 視窗與滑條回呼函式
# =========================================================
def nothing(x):
    pass

# =========================================================
# 初始化 Picamera2
# =========================================================
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (FRAME_WIDTH, FRAME_HEIGHT), "format": "BGR888"}
)
picam2.configure(config)
picam2.set_controls({
    'AwbEnable': False,       # 關閉自動白平衡
    'AnalogueGain': 1.0,
    'ColourGains': (1.5, 1.5)
})
picam2.start()
time.sleep(0.5)  # 等待自動曝光穩定

# =========================================================
# 建立控制滑條視窗
# =========================================================
cv2.namedWindow("Mask")
cv2.createTrackbar("H_MIN", "Mask", 0, 179, nothing)
cv2.createTrackbar("H_MAX", "Mask", 179, 179, nothing)
cv2.createTrackbar("S_MIN", "Mask", 0, 255, nothing)
cv2.createTrackbar("S_MAX", "Mask", 255, 255, nothing)
cv2.createTrackbar("V_MIN", "Mask", 0, 255, nothing)
cv2.createTrackbar("V_MAX", "Mask", 255, 255, nothing)

print("按下 'q' 鍵結束程式。")

try:
    while True:
        frame = picam2.capture_array()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 讀取滑條數值
        h_min = cv2.getTrackbarPos("H_MIN", "Mask")
        h_max = cv2.getTrackbarPos("H_MAX", "Mask")
        s_min = cv2.getTrackbarPos("S_MIN", "Mask")
        s_max = cv2.getTrackbarPos("S_MAX", "Mask")
        v_min = cv2.getTrackbarPos("V_MIN", "Mask")
        v_max = cv2.getTrackbarPos("V_MAX", "Mask")

        lower_color = np.array([h_min, s_min, v_min])
        upper_color = np.array([h_max, s_max, v_max])

        mask = cv2.inRange(hsv, lower_color, upper_color)

        # 形態學處理
        mask_processed = cv2.erode(mask, None, iterations=2)
        mask_processed = cv2.dilate(mask_processed, None, iterations=2)

        # 尋找輪廓
        contours, _ = cv2.findContours(mask_processed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            if radius > 3:
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 0), 2)

        cv2.imshow("Original Frame", frame)
        cv2.imshow("Mask", mask_processed)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\n使用者中斷程式。")
finally:
    picam2.stop()
    picam2.close()
    cv2.destroyAllWindows()
    print("程式結束。")
