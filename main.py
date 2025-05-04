import cv2
import numpy as np
import pyautogui
import winsound
import time

# 參考手掌圖案（請準備手掌截圖）
reference_image = cv2.imread("hand_icon_template.png", cv2.IMREAD_GRAYSCALE)

def play_alert():
    """ 播放鈴鐺聲 """
    winsound.PlaySound("bell.wav", winsound.SND_FILENAME)

def is_chest_ui_present():
    """ 偵測開箱 UI """
    screenshot = pyautogui.screenshot()
    image = np.array(screenshot)
    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # 手掌圖案匹配1
    result = cv2.matchTemplate(gray_image, reference_image, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)

    # 圓形偵測
    circles = cv2.HoughCircles(gray_image, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=30, maxRadius=100)

    return max_val > 0.8 and circles is not None

def track_pointer():
    """ 追蹤指針並判斷是否進入橘色區域 """
    while is_chest_ui_present():
        screenshot = pyautogui.screenshot()
        image = np.array(screenshot)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # 指針偵測
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        pointer_position = None
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w < 20 and h > 30:  # 指針大小範圍
                pointer_position = (x, y, w, h)
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # 橘色範圍偵測
        lower_orange = np.array([5, 150, 150])
        upper_orange = np.array([20, 255, 255])
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)
        orange_contours, _ = cv2.findContours(mask_orange, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 指針進入橘色區域時播放提示音
        if pointer_position:
            px, py, pw, ph = pointer_position
            for oc in orange_contours:
                ox, oy, ow, oh = cv2.boundingRect(oc)
                if px >= ox and px + pw <= ox + ow:
                    print("指針進入橘色範圍！")
                    play_alert()
                    time.sleep(0.5)  # 短暫延遲避免連續觸發

        # 顯示畫面
        cv2.imshow("Detected Pointer", image)
        cv2.waitKey(10)

# 主執行迴圈
while True:
    if is_chest_ui_present():
        print("偵測到開箱畫面，開始輔助程式...")
        track_pointer()
    else:
        print("未偵測到開箱畫面，程式保持待機")
        time.sleep(1)  # 每秒檢查一次
