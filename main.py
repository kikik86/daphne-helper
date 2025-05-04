
import cv2
import numpy as np
import mss
import pyautogui
import keyboard
import time

# 螢幕解析度固定為 1920x1080
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# 小遊戲節奏區域 (可手動調整)
GAME_REGION = {"top": 480, "left": 710, "width": 500, "height": 120}
CLICK_POSITION = (960, 640)  # 「解除」按鈕的大致位置

# HSV 色域：橘色區塊
LOWER_ORANGE = np.array([10, 150, 150])
UPPER_ORANGE = np.array([30, 255, 255])

# 白色指針：亮度高、幾乎純白
LOWER_WHITE = np.array([0, 0, 200])
UPPER_WHITE = np.array([180, 30, 255])

def detect_zones(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # 偵測橘色
    mask_orange = cv2.inRange(hsv, LOWER_ORANGE, UPPER_ORANGE)
    contours_o, _ = cv2.findContours(mask_orange, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    orange_boxes = [cv2.boundingRect(cnt) for cnt in contours_o if cv2.contourArea(cnt) > 100]

    # 偵測白色指針
    mask_white = cv2.inRange(hsv, LOWER_WHITE, UPPER_WHITE)
    contours_w, _ = cv2.findContours(mask_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    white_boxes = [cv2.boundingRect(cnt) for cnt in contours_w if cv2.contourArea(cnt) > 10]

    return orange_boxes, white_boxes

def boxes_overlap(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)

def main():
    print("🔧 Wizardry Daphne 小遊戲輔助已啟動（按 ESC 結束）")
    time.sleep(1)

    with mss.mss() as sct:
        while True:
            if keyboard.is_pressed("esc"):
                print("🛑 已手動結束")
                break

            frame = np.array(sct.grab(GAME_REGION))
            image = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            orange_boxes, white_boxes = detect_zones(image)

            # 逐一比對是否有交集
            for o_box in orange_boxes:
                for w_box in white_boxes:
                    if boxes_overlap(o_box, w_box):
                        print("✅ 命中！執行點擊")
                        pyautogui.click(*CLICK_POSITION)
                        time.sleep(0.3)  # 防止重複點擊
                        break

            time.sleep(0.01)  # 降低 CPU 負載

if __name__ == "__main__":
    main()
    # Trigger GitHub Actions build 4

