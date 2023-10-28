import cv2
import mediapipe as mp
import pyautogui
import threading
import time
import winsound

def calculate_slope(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    if x2 - x1 == 0:
        return float('inf')
    
    return (y2 - y1) / (x2 - x1)

cap = cv2.VideoCapture(0)
cap.set(3, 240)  # Reduced width to 320
cap.set(4, 180)  # Reduced height to 240

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

hands = mp_hands.Hands()

results = None

# Car movement variables
car_speed = 0  # Initial car speed
max_speed = 10  # Maximum car speed
acceleration = 1  # Acceleration rate
deceleration = 1  # Deceleration rate
hands_visible = True

def process_input():
    global results, car_speed, hands_visible

    while True:
        if results and results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
            landmarks = results.multi_hand_landmarks
            left_hand_landmarks = landmarks[1].landmark
            right_hand_landmarks = landmarks[0].landmark

            left_hand_open = all(point.y < left_hand_landmarks[0].y for point in left_hand_landmarks[5:])
            right_hand_open = all(point.y < right_hand_landmarks[0].y for point in right_hand_landmarks[5:])

            turning_left = False
            turning_right = False
            sensitivity = 0.3

            slope = calculate_slope(
                (left_hand_landmarks[11].x, left_hand_landmarks[11].y),
                (right_hand_landmarks[11].x, right_hand_landmarks[11].y)
            )

            if abs(slope) > sensitivity:
                if slope < 0:
                    turning_left = True
                if slope > 0:
                    turning_right = True

            if turning_left:
                pyautogui.keyDown("left")
                pyautogui.keyUp("right")
            elif turning_right:
                pyautogui.keyDown("right")
                pyautogui.keyUp("left")
            else:
                pyautogui.keyUp("left")
                pyautogui.keyUp("right")

            if left_hand_open and right_hand_open:
                # Accelerate the car
                car_speed = min(car_speed + acceleration, max_speed)
            else:
                # Decelerate the car
                car_speed = max(car_speed - deceleration, 0)

            # Update hands_visible flag
            hands_visible = True

            time.sleep(0.1)

input_thread = threading.Thread(target=process_input)
input_thread.daemon = True
input_thread.start()

while True:
    success, img = cap.read()

    cv2.waitKey(1)
    img = cv2.flip(img, 1)
    img.flags.writeable = False
    results = hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS, mp_drawing.DrawingSpec(color=(0,0,255), thickness=2, circle_radius=2))  # Add a green line for hand landmarks
    
    elif not hands_visible:
        # Play the beep sound continuously when hands become invisible
        winsound.Beep(3000, 5000)

    hands_visible = False

    cv2.imshow("Hand Recognition", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
