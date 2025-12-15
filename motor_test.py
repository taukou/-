import RPi.GPIO as GPIO
import time

# === GPIO PIN 定義 ===


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#RPWM = 18 
#LPWM = 12  
RPWM = 13  # 正轉 PWM
LPWM = 19  # 反轉 PWM
GPIO.setup(RPWM, GPIO.OUT)
GPIO.setup(LPWM, GPIO.OUT)

# 建立 PWM 控制器 (20kHz)
freq = 1000
pwmR = GPIO.PWM(RPWM, freq)
pwmL = GPIO.PWM(LPWM, freq)

pwmR.start(0)
pwmL.start(0)

def stop():
    pwmR.ChangeDutyCycle(0)
    pwmL.ChangeDutyCycle(0)
    print("STOP")

def forward(speed):
    # speed: 0~100
    pwmR.ChangeDutyCycle(speed)
    pwmL.ChangeDutyCycle(0)
    print(f"FORWARD {speed}%")

def backward(speed):
    pwmR.ChangeDutyCycle(0)
    pwmL.ChangeDutyCycle(speed)
    print(f"BACKWARD {speed}%")

try:
    print("Motor Test Start")

    forward(50)
    time.sleep(5)

    forward(100)
    time.sleep(5)

    stop()
    time.sleep(1)

    backward(40)
    time.sleep(5)

    stop()
    print("Test Done")

except KeyboardInterrupt:
    pass

finally:
    stop()
    pwmR.stop()
    pwmL.stop()
    GPIO.cleanup()
