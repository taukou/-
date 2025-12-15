import cv2
import numpy as np
import time
from picamera2 import Picamera2

# =========================================================
# 影像與 HSV 設定
# =========================================================
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# 依照你剛剛測試的結果填入
H_MIN = 100    # 藍色低色相
H_MAX = 127    # 藍色高色相
S_MIN = 130    # 飽和度門檻
S_MAX = 255
V_MIN = 125    # 亮度門檻
V_MAX = 255

LOWER_COLOR = np.array([H_MIN, S_MIN, V_MIN])
UPPER_COLOR = np.array([H_MAX, S_MAX, V_MAX])

# =========================================================
# 初始化 Picamera2
# =========================================================
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
# 建立顯示視窗 (可調整大小)
# =========================================================
cv2.namedWindow("Original Frame", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Original Frame", FRAME_WIDTH, FRAME_HEIGHT)
cv2.namedWindow("Mask", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Mask", FRAME_WIDTH, FRAME_HEIGHT)

print("按下 'q' 鍵結束程式。")

# =========================================================
# 主迴圈
# =========================================================
try:
    while True:
        # 捕捉影像
        frame = picam2.capture_array()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 顏色遮罩
        mask = cv2.inRange(hsv, LOWER_COLOR, UPPER_COLOR)

        # 形態學處理 (去除雜訊)
        mask_processed = cv2.erode(mask, None, iterations=2)
        mask_processed = cv2.dilate(mask_processed, None, iterations=2)

        # 尋找輪廓
        contours, _ = cv2.findContours(mask_processed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            if radius > 3:  # 可調整最小半徑
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 0), 2)

        # 顯示影像與遮罩
        cv2.imshow("Original Frame", frame)
        cv2.imshow("Mask", mask_processed)

        # 按 q 鍵退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\n使用者中斷程式。")
finally:
    picam2.stop()
    picam2.close()
    cv2.destroyAllWindows()
    print("程式結束。")
