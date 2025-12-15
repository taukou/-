import cv2
import numpy as np
import time
import sys
import RPi.GPIO as GPIO
from picamera2 import Picamera2
from libcamera import controls 

# =========================================================
# I. GPIO PIN 定義與設定
# =========================================================
L_FWD_PIN = 18
L_BWD_PIN = 12
R_FWD_PIN = 13
R_BWD_PIN = 19

PWM_FREQUENCY = 1000
MAX_SPEED_DUTY = 100

pwm_L_fwd, pwm_L_bwd, pwm_R_fwd, pwm_R_bwd = None, None, None, None

# =========================================================
# II. 校準與追蹤參數 (固定速度 Bang-Bang 控制)
# =========================================================
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# 已確認藍色乒乓球 HSV (保持不變)
H_MIN = 100; H_MAX = 130; S_MIN = 140; S_MAX = 255; V_MIN = 125; V_MAX = 255
LOWER_COLOR = np.array([H_MIN, S_MIN, V_MIN])
UPPER_COLOR = np.array([H_MAX, S_MAX, V_MAX])

FLIP_CODE = 0 # 影像翻轉修正

# P-Control 參數
CENTER_X = FRAME_WIDTH // 2
CENTER_Y = FRAME_HEIGHT // 2 # Y 軸目標: 鎖定在畫面正中心 240 像素處

X_TOLERANCE = 60         # 增加 X 軸容許範圍，減少左右擺頭
Y_TOLERANCE = 0         # Y 軸容許範圍 (停止的門檻)
MAX_SPEED = 80           
MIN_SPEED = 15           # 🎯 關鍵: 固定移動/轉向速度

# P_GAIN 不再用於控制，可以刪除，但為確保程式碼一致性，暫時保留
# P_GAIN = 0.02 
CALIBRATION_FACTOR_R = 0.5

# =========================================================
# III. 馬達控制函式 (分階段控制)
# =========================================================
def init_motor_pins():
    global pwm_L_fwd, pwm_L_bwd, pwm_R_fwd, pwm_R_bwd
    try:
        GPIO.setmode(GPIO.BCM); GPIO.setwarnings(False)
        for pin in [L_FWD_PIN, L_BWD_PIN, R_FWD_PIN, R_BWD_PIN]:
            GPIO.setup(pin, GPIO.OUT)
        pwm_L_fwd = GPIO.PWM(L_FWD_PIN, PWM_FREQUENCY); pwm_L_fwd.start(0)
        pwm_L_bwd = GPIO.PWM(L_BWD_PIN, PWM_FREQUENCY); pwm_L_bwd.start(0)
        pwm_R_fwd = GPIO.PWM(R_FWD_PIN, PWM_FREQUENCY); pwm_R_fwd.start(0)
        pwm_R_bwd = GPIO.PWM(R_BWD_PIN, PWM_FREQUENCY); pwm_R_bwd.start(0)
        print("馬達控制腳位初始化完成。")
    except Exception as e:
        print(f"GPIO 初始化失敗: {e}"); cleanup_gpio(); sys.exit(1)

def stop():
    if pwm_L_fwd: pwm_L_fwd.ChangeDutyCycle(0); pwm_L_bwd.ChangeDutyCycle(0)
    if pwm_R_fwd: pwm_R_fwd.ChangeDutyCycle(0); pwm_R_bwd.ChangeDutyCycle(0)

def _set_speed(speed_L, speed_R):
    speed_R = int(speed_R * CALIBRATION_FACTOR_R)
    speed_L = max(0, min(MAX_SPEED_DUTY, speed_L))
    speed_R = max(0, min(MAX_SPEED_DUTY, speed_R))
    return speed_L, speed_R

def move_forward(speed):
    speed_L, speed_R = _set_speed(speed, speed)
    pwm_L_bwd.ChangeDutyCycle(0); pwm_L_fwd.ChangeDutyCycle(speed_L)
    pwm_R_bwd.ChangeDutyCycle(0); pwm_R_fwd.ChangeDutyCycle(speed_R)

def move_backward(speed):
    speed_L, speed_R = _set_speed(speed, speed)
    pwm_L_fwd.ChangeDutyCycle(0); pwm_L_bwd.ChangeDutyCycle(speed_L)
    pwm_R_fwd.ChangeDutyCycle(0); pwm_R_bwd.ChangeDutyCycle(speed_R)

def turn_left(speed): # 原地左轉
    speed_L, speed_R = _set_speed(speed, speed)
    pwm_L_fwd.ChangeDutyCycle(0); pwm_L_bwd.ChangeDutyCycle(speed_L) # 左輪後退
    pwm_R_bwd.ChangeDutyCycle(0); pwm_R_fwd.ChangeDutyCycle(speed_R) # 右輪前進
    
def turn_right(speed): # 原地右轉
    speed_L, speed_R = _set_speed(speed, speed)
    pwm_L_bwd.ChangeDutyCycle(0); pwm_L_fwd.ChangeDutyCycle(speed_L) # 左輪前進
    pwm_R_fwd.ChangeDutyCycle(0); pwm_R_bwd.ChangeDutyCycle(speed_R) # 右輪後退

def cleanup_gpio():
    try:
        stop()
        if pwm_L_fwd: pwm_L_fwd.stop()
        if pwm_L_bwd: pwm_L_bwd.stop()
        if pwm_R_fwd: pwm_R_fwd.stop()
        if pwm_R_bwd: pwm_R_bwd.stop()
        GPIO.cleanup()
        print("GPIO 資源已清除。")
    except:
        pass 

# =========================================================
# IV. 追蹤主循環 
# =========================================================
def run_tracker():
    init_motor_pins()
    
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(
        main={"size": (FRAME_WIDTH, FRAME_HEIGHT), "format": "BGR888"}
    )
    picam2.configure(config)
    picam2.set_controls({
        'AwbEnable': False,
        'AnalogueGain': 1.0,
        'ColourGains': (1.5, 1.5)
    })
    picam2.start()
    time.sleep(1.0)

    print("--- 分階段追蹤程式啟動 ---")
    
    try:
        while True:
            frame = picam2.capture_array()
            if FLIP_CODE is not None:
                frame = cv2.flip(frame, FLIP_CODE)

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, LOWER_COLOR, UPPER_COLOR)
            
            # 形態學操作 (開運算)
            mask_processed = cv2.erode(mask, None, iterations=2)
            mask_processed = cv2.dilate(mask_processed, None, iterations=2) 

            contours, _ = cv2.findContours(mask_processed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            ball_found = False
            direction_text = "LOST TARGET"
            dx, dy = 0, 0 
            speed_cmd = 0

            if len(contours) > 0:
                c = max(contours, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)

                if radius > 2:
                    area = cv2.contourArea(c)
                    if area > 10: 
                        ball_found = True
                        M = cv2.moments(c)
                        if M["m00"] > 0:
                            center_x = int(M["m10"] / M["m00"])
                            center_y = int(M["m01"] / M["m00"]) 
                            
                            dx = center_x - CENTER_X
                            dy = center_y - CENTER_Y
                            
                            fixed_speed = MIN_SPEED 

                            # A. 判斷 X 軸 (原地轉向優先)
                            if abs(dx) > X_TOLERANCE:
                                # 🎯 修正: 轉向速度固定為 MIN_SPEED
                                speed_cmd = fixed_speed
                                
                                if dx < 0:
                                    
                                    turn_left(speed_cmd)
                                    direction_text = f"TRN L {int(speed_cmd)}%"
                                else :
                                    
                                    turn_right(speed_cmd)
                                    direction_text = f"TRN R {int(speed_cmd)}%"
                            
                            # B. X 軸對齊後，判斷 Y 軸 (固定速度前後移動)
                            else:
                                if abs(dy) > Y_TOLERANCE:
                                    
                                    # 🎯 修正: 前後移動速度固定為 MIN_SPEED
                                    speed_cmd = fixed_speed
                                    
                                    # 鏡頭朝上，目標 Y=240 鎖定邏輯
                                    if dy < 0:
                                        # dy < 0: 球在上方 (Y < 240) -> 太近，需要後退
                                        move_backward(speed_cmd)
                                        direction_text = f"BCK {int(fixed_speed)}%"
                                    else:
                                        # dy > 0: 球在下方 (Y > 240) -> 太遠，需要前進
                                        move_forward(speed_cmd)
                                        direction_text = f"FWD {int(fixed_speed)}%"
                                else:
                                    # X/Y 軸都在容許範圍內
                                    stop()
                                    direction_text = "TARGET LOCKED"

            if not ball_found:
                stop()
                direction_text = "LOST TARGET"
                
            # 6. 輸出資訊到終端機 
            print(f"狀態: {direction_text} | 偏差 X: {dx}, Y: {dy} | Speed: {int(speed_cmd)}", end='\r')

    except KeyboardInterrupt:
        print("\n使用者中斷程式。")
    except Exception as e:
        print(f"程式運行中發生錯誤: {e}")
    finally:
        cleanup_gpio()
        picam2.stop()
        picam2.close()
        print("程式結束。")

if __name__ == '__main__':
    run_tracker()
