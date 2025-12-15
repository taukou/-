# 自動接垃圾垃圾桶（Smart Moving Trash Can）

---

## 1. 關於專案

本專案為一台**自動接垃圾垃圾桶**，透過樹莓派與攝影機進行影像辨識，當系統偵測到使用者手中持有垃圾時，垃圾桶會自動移動到使用者附近，讓使用者可以更方便地丟垃圾。  
>本專案以乒乓球代替垃圾做模擬
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

### 設置：

- 作業系統：Raspberry Pi OS（Raspberry Pi OS Trixie基於 Debian 13）  
- 使用 Python 進行開發  
- 影像處理使用 OpenCV  
- 攝影機模組使用 Picamera2  

### 環境設置（無虛擬環境）:
> 注意：`libcamera` 在虛擬環境中可能抓不到路徑，建議直接在系統 Python 下安裝。
> 如果測試後沒問題也可在虛擬環境中進行，本專案未在虛擬環境中進行

1.**更新系統套件**
```python  
sudo apt update
sudo apt upgrade -y
```

2.**安裝 Python 與必要套件**
```python
sudo apt install python3-pip python3-dev python3-numpy -y
sudo apt install libatlas-base-dev libjpeg-dev libtiff-dev libjasper-dev libpng-dev -y
sudo apt install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev -y
sudo apt install libxvidcore-dev libx264-dev -y
sudo apt install libgtk-3-dev -y
sudo apt install libatlas-base-dev gfortran -y
```
3.**安裝 OpenCV**
```python
pip3 install opencv-python
```
4.**安裝 Raspberry Pi 專用套件**
```python
pip3 install RPi.GPIO
sudo apt install python3-picamera2 -y
sudo apt install libcamera-apps -y
```
5.**其他必要套件**
```python
pip3 install numpy
```
---
### 程式設計：

#### 1.在開始之前
>本專案判定垃圾的方式是以色彩蒙版辨識，如要使用AI模型判定可忽略1.2部分
#### HSV 色彩蒙版說明

在垃圾桶追蹤專案中，我們使用 HSV 色彩蒙版來辨識手上垃圾的顏色，以下說明其原理與用途。

---

#### (1) HSV 色彩空間是什麼？

HSV 是一種用來描述顏色的方式，由三個部分組成：

| 項目 | 說明 |
|------|------|
| **H (Hue，色相)** | 顏色本身，例如紅、綠、藍。數值通常 0~179（OpenCV 使用範圍 0~179） |
| **S (Saturation，飽和度)** | 顏色的純度，值越高顏色越鮮豔，值低則偏灰 |
| **V (Value，明度/亮度)** | 顏色的亮度或強度，值越高顏色越亮，值低則偏黑 |

**HSV 與 RGB 的差異：**

- **RGB** 表示紅、綠、藍三種光的強度組合，受光線影響較大。
- **HSV** 分離了顏色 (H) 與亮度 (V)，對光線變化不敏感，更符合人眼對顏色的感知。

---

#### (2) 程式中 HSV 蒙版的用途

程式片段：

```python
H_MIN = 100; H_MAX = 127
S_MIN = 175; S_MAX = 255
V_MIN = 110; V_MAX = 255
LOWER_COLOR = np.array([H_MIN, S_MIN, V_MIN])
UPPER_COLOR = np.array([H_MAX, S_MAX, V_MAX])

hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, LOWER_COLOR, UPPER_COLOR)
```
功能說明：

轉換色彩空間
將攝影機捕捉的 BGR 影像轉換成 HSV：
```python
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
```

建立顏色蒙版
```python
mask = cv2.inRange(hsv, LOWER_COLOR, UPPER_COLOR)
```
- 將在指定 HSV 範圍內的像素設為白色 (255)，範圍外設為黑色 (0)。
- 白色部分即目標顏色（例如藍色乒乓球 / 模擬垃圾）。

後續處理

- 使用 cv2.findContours 找到白色區域。
- 計算中心座標 (X, Y)。
- 控制馬達向目標移動。

#### (3) HSV 蒙版示意圖
原始影像：手上拿著垃圾
HSV 蒙版後影像：目標顯示為白色區域

![HSV 蒙版示意圖](path/to/image.jpg)

---

#### 2.目標物顏色測試
#### HSV 顏色範圍測試程式說明

#### (1) 功能
這個程式可以：
- 使用 Picamera2 取得即時影像
- 將 BGR 影像轉換為 HSV 色彩空間
- 利用滑條即時調整 HSV 範圍
- 顯示目標物體的蒙版與追蹤輪廓
- 幫助設定主程式的 `LOWER_COLOR` 與 `UPPER_COLOR` 參數

#### (2) 執行方式
1. 將程式上傳至樹莓派
2. 使用以下指令執行：
```python
python3 hsv_color_test.py
```
#### (3) 調整 HSV 滑條

滑條功能如下：

| 滑條   | 功能       |
|--------|------------|
| H_MIN  | 色相下限   |
| H_MAX  | 色相上限   |
| S_MIN  | 飽和度下限 |
| S_MAX  | 飽和度上限 |
| V_MIN  | 明度下限   |
| V_MAX  | 明度上限   |

操作方式：
- 調整滑條，觀察 `Mask` 視窗中的白色區域是否對應目標顏色。
- 確認後記下對應數值，作為追蹤程式的的預設數值

### (4) 顯示與輪廓

- 程式會自動尋找蒙版中的最大輪廓。
- 以綠色圓圈標記目標物體中心。
- 可視化追蹤效果，方便微調 HSV 範圍。

### (5) 結束程式

- 按下 `q` 鍵或使用 Ctrl+C 結束程式。
- 程式會自動釋放攝影機與關閉視窗。

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
