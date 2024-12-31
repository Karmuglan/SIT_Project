import cv2

# Open a connection to the webcam (default is 0 for the first camera, 1 for the second, etc.)
cap = cv2.VideoCapture(0)

# Check if the camera is opened successfully
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Capture frames from the webcam in a loop
while True:
    ret, frame = cap.read()  # Read the frame from the webcam
    if not ret:
        print("Error: Failed to grab frame.")
        break

    # Display the frame
    cv2.imshow("Webcam Feed", frame)

    # Press 'q' to exit the video feed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()