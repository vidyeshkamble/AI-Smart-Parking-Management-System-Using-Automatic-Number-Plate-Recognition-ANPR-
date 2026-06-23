import cv2
import time
import os

# Output folder to save frames
output_folder = "newimages"
maxFrame = 170     # total number of frames to capture
delay = 0       # delay between frames (in seconds)

# Create the output folder if it doesn’t exist
os.makedirs(output_folder, exist_ok=True)

# Load the video
cap = cv2.VideoCapture(r"C:\Users\vidye\OneDrive\Desktop\DYP Project\PlateDetection\Videos\EntryCar.mp4")

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()
    
cap.set(3, 640)
cap.set(4, 480)

cpt = 0

while cpt < maxFrame:
    ret, frame = cap.read()
    if not ret:
        print("Video has ended or cannot be read.")
        break

    frame = cv2.resize(frame, (1020, 600))

    # Save frame as image
    filename = os.path.join(output_folder, f"NumberPlate_{cpt}.jpg")
    cv2.imwrite(filename, frame)
    print(f"Saved: {filename}")

    cpt += 1
    time.sleep(delay)

cap.release()
cv2.destroyAllWindows()

print(f"✅ {cpt} frames saved successfully in '{output_folder}' folder.")
