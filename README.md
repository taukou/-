# 自動接垃圾垃圾桶（Smart Moving Trash Can）

---

## 1. 關於專案

本專案為一台**自動接垃圾垃圾桶**，透過樹莓派與攝影機進行影像辨識，當系統偵測到使用者手中持有垃圾時，垃圾桶會自動移動到使用者附近，讓使用者可以更方便地丟垃圾。  

---

## 2. 專案緣由

日常生活中常常遇到手上有垃圾、但垃圾桶距離太遠或不方便靠近的情況。  
本專案希望透過機器人與影像辨識技術，讓垃圾桶能主動靠近人，提升生活便利性。

---

## 3. 專案構想

按照以下步驟，逐步完成智慧垃圾桶的雛型：

1. 建立可移動的車輛底盤  
2. 使用直流馬達與馬達驅動板控制前進、後退與轉向  
3. 安裝攝影機擷取即時影像  
4. 透過影像處理辨識垃圾或特定顏色物體  
5. 根據物體位置，自動控制垃圾桶移動靠近使用者  

---

## 4. 所需材料

1. 車輛底盤＋輪組  
2. 24V 直流減速馬達 × 2  
3. BTS7960 馬達控制板 × 2  
4. 電池模組（供應馬達電源）  
5. Raspberry Pi 4  
6. Raspberry Pi 4 不斷電 5V 供電系統(或是行動電源)  
7. 樹莓派 OV5647 攝影鏡頭模組  
   - 500 萬像素  
   - 160 度廣角  
   - 可調焦（魚眼）  
8. 垃圾桶或容器（安裝於車體上）  
9. 杜邦線、固定材料（螺絲、支架等）

---

## 5. 實體照片、各裝置細節照片

整體外觀照片：  
![整體外觀](path/to/image.jpg)

車輛底盤裝置細節：  
![底盤細節](path/to/image.jpg)

攝影機安裝位置：  
![攝影機安裝](path/to/image.jpg)

---

## 6. 電路配置

車輛底盤電路配置圖：  
![電路配置](path/to/image.jpg)

樹莓派 GPIO 接線示意圖：  
![GPIO 接線圖](path/to/image.jpg)

---

## 7. 程式設計、環境設置

### 環境設置：

- 作業系統：Raspberry Pi OS（Raspberry Pi OS Trixie基於 Debian 13）  
- 使用 Python 進行開發  
- 影像處理使用 OpenCV  
- 攝影機模組使用 Picamera2  

參考連結：  
- [Raspberry Pi GPIO 控制](https://randomnerdtutorials.com/raspberry-pi-gpio-setup/)  
- [Picamera2 使用教學](https://picamera.readthedocs.io/en/release-1.13/quickstart.html)  
- [OpenCV Python 文件](https://docs.opencv.org/)

---

### 程式設計：

#### 馬達移動控制

透過 BTS7960 馬達驅動板控制左右馬達，可實現：

- 前進  
- 後退  
- 左轉  
- 右轉  

```python
# 範例程式碼
def move_forward(speed):
    pwm_L_fwd.ChangeDutyCycle(speed)
    pwm_R_fwd.ChangeDutyCycle(speed)
