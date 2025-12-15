import RPi.GPIO as GPIO
import time
import sys

# =========================================================
# I. GPIO PIN 定義與設定
# =========================================================

# 左輪馬達
L_RPWM_PIN = 18 
L_LPWM_PIN = 12  

# 右輪馬達
R_RPWM_PIN = 13  
R_LPWM_PIN = 19  

PWM_FREQUENCY = 2000  # 使用 1000 Hz 解決 lgpio 錯誤

# PWM 實例 (全域變數)
pwm_L_R, pwm_L_L, pwm_R_R, pwm_R_L = None, None, None, None

# =========================================================
# II. 校準參數 (請修改此處的兩個參數)
# =========================================================

# 【參數 1】 測試直線時使用的基礎速度 (0-100)
BASE_SPEED = 50


# 【參數 2】 右輪校正因子 (初始值 1.0)
# 若車子往右偏，代表左輪太快，應調降左輪或提高右輪。
# 這裡我們將以左輪 (1.0) 為基準，調整右輪的速度。
CALIBRATION_FACTOR_R = 0.6 

# =========================================================
# III. 馬達控制核心函式
# =========================================================

def init_motor_pins():
    """初始化 GPIO 腳位和 PWM 實例"""
    global pwm_L_R, pwm_L_L, pwm_R_R, pwm_R_L
    
    # [初始化程式碼與您之前成功運行的程式碼相同，略]
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for pin in [L_RPWM_PIN, L_LPWM_PIN, R_RPWM_PIN, R_LPWM_PIN]:
            GPIO.setup(pin, GPIO.OUT)
        
        pwm_L_R = GPIO.PWM(L_RPWM_PIN, PWM_FREQUENCY)
        pwm_L_L = GPIO.PWM(L_LPWM_PIN, PWM_FREQUENCY)
        pwm_R_R = GPIO.PWM(R_RPWM_PIN, PWM_FREQUENCY)
        pwm_R_L = GPIO.PWM(R_LPWM_PIN, PWM_FREQUENCY)
        
        pwm_L_R.start(0)
        pwm_L_L.start(0)
        pwm_R_R.start(0)
        pwm_R_L.start(0)
        print("馬達控制腳位初始化完成。")
        
    except Exception as e:
        print(f"GPIO 初始化失敗: {e}")
        sys.exit(1)

def stop():
    """停止所有馬達運動"""
    # [程式碼與您之前成功的 stop 函式相同，略]
    pwm_L_R.ChangeDutyCycle(0)
    pwm_L_L.ChangeDutyCycle(0)
    pwm_R_R.ChangeDutyCycle(0)
    pwm_R_L.ChangeDutyCycle(0)

def move_forward_straight(base_speed, factor_R):
    """
    自走車前進，應用右輪校正因子。
    左輪速度 = base_speed
    右輪速度 = base_speed * factor_R
    """
    speed_L = base_speed
    speed_R = int(base_speed * factor_R)
    
    # 確保速度在 0-100 範圍
    speed_L = max(0, min(100, speed_L))
    speed_R = max(0, min(100, speed_R))

    # 左輪前進 (RPWM)
    pwm_L_L.ChangeDutyCycle(0)
    pwm_L_R.ChangeDutyCycle(speed_L)
    
    # 右輪前進 (RPWM)
    pwm_R_L.ChangeDutyCycle(0)
    pwm_R_R.ChangeDutyCycle(speed_R)
    
    print(f"L_Speed: {speed_L}% | R_Speed: {speed_R}%")


def cleanup_gpio():
    """程式結束時清理 GPIO 資源"""
    # [程式碼與您之前成功的 cleanup 函式相同，略]
    try:
        stop()
        if pwm_L_R: pwm_L_R.stop()
        if pwm_L_L: pwm_L_L.stop()
        if pwm_R_R: pwm_R_R.stop()
        if pwm_R_L: pwm_R_L.stop()
        GPIO.cleanup()
        print("GPIO 資源已清除。")
    except:
        pass 

# =========================================================
# IV. 校準主程式
# =========================================================

def main_calibrate():
    """主校準流程"""
    
    print("--- 自走車直線校準工具 ---")
    print(f"基礎速度: {BASE_SPEED}%")
    print(f"右輪校正因子 (CALIBRATION_FACTOR_R): {CALIBRATION_FACTOR_R}")
    print("-" * 30)
    
    try:
        init_motor_pins()
        
        input("請將自走車放在平坦地面，面向前方。按 Enter 鍵開始測試...")
        
        print("-> 執行直線前進 5 秒...")
        
        # 執行直線前進
        move_forward_straight(BASE_SPEED, CALIBRATION_FACTOR_R)
        time.sleep(3)
        stop()
        
        print("-> 測試完成。")
        print("-" * 30)
        print(f"請觀察車輛偏向哪一側。")
        
    except KeyboardInterrupt:
        print("\n使用者中斷校準。")
    except Exception as e:
        print(f"校準發生錯誤: {e}")
    finally:
        cleanup_gpio()

if __name__ == '__main__':
    main_calibrate()
