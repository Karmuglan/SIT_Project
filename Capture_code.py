import cv2
from tkinter import Tk, Button, Label
from PIL import Image, ImageTk

class WebcamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Webcam Capture")

        # Initialize webcam
        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            raise Exception("Could not open webcam")

        # Create a label for video feed
        self.video_label = Label(root)
        self.video_label.pack()

        # Button to capture photo
        self.capture_button = Button(root, text="Capture Photo", command=self.capture_photo)
        self.capture_button.pack()

        # Display video feed
        self.update_frame()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Convert frame to RGB for Tkinter
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(Image.fromarray(frame))
            self.video_label.imgtk = img
            self.video_label.configure(image=img)

        # Repeat after 10 ms
        self.root.after(10, self.update_frame)

    def capture_photo(self):
        ret, frame = self.cap.read()
        if ret:
            # Save the captured image
            cv2.imwrite("captured_photo.jpg", frame)
            print("Photo captured and saved as 'captured_photo.jpg'")

    def __del__(self):
        # Release the webcam when done
        if self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    root = Tk()
    app = WebcamApp(root)
    root.mainloop()
