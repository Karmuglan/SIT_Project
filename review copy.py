from tkinter import *
from tkinter import ttk
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk
import os
import re
import pytesseract
import cv2
import mysql.connector as mysql

class WebcamApp:
    def __init__(self, root, container):
        self.root = root
        self.container = container
        self.video_label = Label(self.container)
        self.video_label.grid(row=0, column=0, sticky="nsew")
        self.capture_btn_in = Button(self.container, text="Capture Photo", command=self.capture_photo_in)
        self.capture_btn_in.grid(row=1, column=0)
        self.cap = cv2.VideoCapture(0)
        self.con=mysql.connect(host="localhost",user="root",password="",database="p_f")
        self.cursor=self.con.cursor()
           
        self.update_video_frame()

    def update_video_frame(self):
        self.car_cascade = cv2.CascadeClassifier('haarcascade_car.xml')
        if self.car_cascade.empty():
            print("Error: Unable to load 'haarcascade_car.xml'.")
            print("Please ensure the file exists in the current directory or provide the correct path.")
            return
        ret, frame = self.cap.read()  # Assuming `video` is your existing cv2.VideoCapture object
        if not ret:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Car Detection
        cars = self.car_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(60, 60))
        for i, (x, y, w, h) in enumerate(cars):
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            label = f"Car #{i + 1}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            label_w, label_h = label_size
            cv2.rectangle(frame, (x, y - label_h - 10), (x + label_w + 10, y), (0, 255, 0), -1)
            cv2.putText(frame, label, (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

        # Convert to Tkinter image and show
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.config(image=imgtk)

        self.video_label.after(10, self.update_video_frame)


    def capture_photo_in(self):
        ret, frame = self.cap.read()
        if ret:
            # Save the captured image in the script's directory
            script_directory = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_directory, "captured_photo.png")
            cv2.imwrite(file_path, frame)
            print(f"Photo captured and saved as '{file_path}'")
            self.extract_text()

    def stop_webcam(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()

    def close_connection(self):
        # Close the database connection.
        if self.con.is_connected():
            self.cursor.close()
            self.con.close()
            print("Database connection closed.")

    def __del__(self):
        self.stop_webcam()
        self.close_connection()
    
    def extract_text(self):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_directory, "captured_photo.png")
        img = cv2.imread(file_path)

        # Extract text using Tesseract
        pytesseract.pytesseract.tesseract_cmd ="C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        text = pytesseract.image_to_string(img)
        print(text," 1")
        text=text.replace(" ","").replace("|","").replace("{}","").replace("(","").replace(")","").replace("[","").replace("]","").replace("/","").replace("\\","").replace(".","").replace(",","").replace(":","").replace(";","")
        text=text.rstrip()
        print(text," 2")
        pattern = re.compile(r'\b[A-Z]{2}\d{2}[A-Z]{1}\d{4}\b')  # Example pattern for vehicle number plate
        matches = pattern.findall(text)
        print(matches," 3")
        if matches:
            filtered_text = matches[0]
            self.insert_data_cam(filtered_text)
        else:
            filtered_text = "No valid text found"

        print(f"Extracted text: {filtered_text}")

    def insert_data_cam(self, vehicle_num):
        messagebox.showinfo("Vehicle Detected", f"Detected Vehicle Number: {vehicle_num}")
        vec_num = vehicle_num.upper()
        try:
            # Reconnect if the connection is lost
            if not self.con.is_connected():
                self.con = mysql.connect(host="localhost", user="root", password="", database="p_f")
                self.cursor = self.con.cursor()

            # Check if the vehicle exists in the vehicles table
            check_vehicle_query = "SELECT * FROM vehicles WHERE vehicle_number = %s"
            self.cursor.execute(check_vehicle_query, (vec_num,))
            vehicle_exists = self.cursor.fetchone()

            if not vehicle_exists:
                messagebox.showerror("Error", f"Vehicle number {vec_num} does not exist. Please register the vehicle first.")
                return

            # Check if the vehicle is already parked (i.e., has no exit_time)
            select_query = "SELECT * FROM parking_logs WHERE vehicle_number = %s AND exit_time IS NULL"
            self.cursor.execute(select_query, (vec_num,))
            result = self.cursor.fetchone()  # Fetch a single row

            if result:  # If a record exists, the vehicle is exiting
                query = "UPDATE parking_logs SET exit_time = NOW() WHERE vehicle_number = %s AND exit_time IS NULL"
                self.cursor.execute(query, (vec_num,))
                self.con.commit()
                messagebox.showinfo("Message", f"Vehicle number {vec_num} exited successfully")
            else:  # If no record exists, the vehicle is entering
                # Check for an available parking slot
                slot_query = "SELECT slot_number FROM parking_slots WHERE status = 'Available' LIMIT 1"
                self.cursor.execute(slot_query)
                slot_result = self.cursor.fetchone()

                if slot_result:  # If a parking slot is available
                    parking_slot = slot_result[0]
                    insert_query = """
                        INSERT INTO parking_logs (vehicle_number, parking_slot, entry_time)
                        VALUES (%s, %s, NOW())
                    """
                    self.cursor.execute(insert_query, (vec_num, parking_slot))
                    # Mark the parking slot as occupied
                    update_slot_query = "UPDATE parking_slots SET status = 'Occupied' WHERE slot_number = %s"
                    self.cursor.execute(update_slot_query, (parking_slot,))
                    self.con.commit()
                    messagebox.showinfo("Message", f"Vehicle number {vec_num} parked successfully\nParking slot allocated: {parking_slot}")
                else:  # No parking slots available
                    messagebox.showerror("Error", "No available parking slots")
        except mysql.Error as e:
            print(f"Error processing vehicle data: {e}")
            self.con.rollback()
            messagebox.showerror("Error", f"Database error: {e}")

class Include_member:
    def __init__(self, root, container):
        self.frame = Frame(container)
        self.frame.grid(row=0, column=0, sticky="nsew")

        # Creating Input Fields
        self.lab_Name = Label(self.frame, text="Enter Owner Name")
        self.lab_Name.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.txt_Name = Entry(self.frame, width=30)
        self.txt_Name.grid(row=0, column=1, padx=10, pady=5)

        self.lab_Mobile_no = Label(self.frame, text="Enter Mobile Number")
        self.lab_Mobile_no.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.txt_Mobile_no = Entry(self.frame, width=30)
        self.txt_Mobile_no.grid(row=1, column=1, padx=10, pady=5)

        self.lab_Vec_no = Label(self.frame, text="Enter Vehicle Number")
        self.lab_Vec_no.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.txt_Vec_no = Entry(self.frame, width=30)
        self.txt_Vec_no.grid(row=2, column=1, padx=10, pady=5)

        self.lab_Vec_type = Label(self.frame, text="Select Vehicle Type")
        self.lab_Vec_type.grid(row=3, column=0, sticky="w", padx=10, pady=5)
        vehicle_type = ['Car', 'Bike', 'Truck']
        self.vec_type = ttk.Combobox(self.frame, values=vehicle_type, width=27)
        self.vec_type.grid(row=3, column=1, padx=10, pady=5)

        # Submit Button
        btn_Submit = Button(self.frame, text="Submit", command=self.insert_data_manual, width=15)
        btn_Submit.grid(row=4, column=0, padx=2, pady=10)

        # Edit Button
        btn_edit = Button(self.frame, text="Edit", command=self.edit_data, width=15)
        btn_edit.grid(row=4, column=1, padx=5, pady=10)

        # Delete Button
        btn_delete = Button(self.frame, text="Delete", command=self.delete_data, width=15)
        btn_delete.grid(row=4, column=2, padx=5, pady=10)

        # Add a "View Data" button in the Include_member class
        btn_view_data = Button(self.frame, text="View Data", command=self.view_data, width=15)
        btn_view_data.grid(row=5, column=1, padx=5, pady=10)

    # Add the view_data method to display data from the vehicles table
    def view_data(self):
        try:
            conn = mysql.connect(host="localhost", user="root", password="", database="p_f")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM vehicles")
            rows = cursor.fetchall()

            # Create a new window to display the data
            view_window = Toplevel(self.frame)
            view_window.title("Vehicles Data")
            view_window.geometry("600x400")

            # Create a Treeview widget to display the data
            tree = ttk.Treeview(view_window, columns=("Vehicle Number", "Owner Name", "Contact Number", "Vehicle Type"), show="headings")
            tree.heading("Vehicle Number", text="Vehicle Number")
            tree.heading("Owner Name", text="Owner Name")
            tree.heading("Contact Number", text="Contact Number")
            tree.heading("Vehicle Type", text="Vehicle Type")
            tree.pack(fill=BOTH, expand=True)

            # Insert data into the Treeview
            for row in rows:
                tree.insert("", END, values=row)

            conn.close()
        except mysql.Error as e:
            messagebox.showerror("Error", f"Failed to fetch data: {e}")

    # Inser user data
    def insert_data_manual(self):
        if self.txt_Name.get() == "" or self.txt_Mobile_no.get() == "" or self.txt_Vec_no.get() == "" or self.vec_type.get() == "":
            messagebox.showerror("Error", "All fields are required")
            return
        try:
            conn = mysql.connect(host="localhost", user="root", password="", database="p_f")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO vehicles (vehicle_number, owner_name, contact_number, vehicle_type) VALUES (%s, %s, %s, %s)",
                (self.txt_Vec_no.get().upper(), self.txt_Name.get(), self.txt_Mobile_no.get(), self.vec_type.get())
            )
            conn.commit()
            messagebox.showinfo("Success", "Data inserted successfully")
        except mysql.Error as e:
            conn.rollback()
            messagebox.showerror("Error", f"Data insertion failed: {e}")

    # Editing user data
    def edit_data(self):
        if self.txt_Name.get() == "" or self.txt_Mobile_no.get() == "" or self.txt_Vec_no.get() == "" or self.vec_type.get() == "":
            messagebox.showerror("Error", "All fields are required")
            return
        try:
            conn = mysql.connect(host="localhost", user="root", password="", database="p_f")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE vehicles SET owner_name=%s, contact_number=%s, vehicle_type=%s WHERE vehicle_number=%s",
                (self.txt_Name.get(), self.txt_Mobile_no.get(), self.vec_type.get(), self.txt_Vec_no.get().upper())
            )
            conn.commit()
            messagebox.showinfo("Success", "Data updated successfully")
        except mysql.Error as e:
            conn.rollback()
            messagebox.showerror("Error", f"Data update failed: {e}")

    # Delete user data
    def delete_data(self):
        if self.txt_Vec_no.get() == "":
            messagebox.showerror("Error", "Vehicle Number is required")
            return
        try:
            conn = mysql.connect(host="localhost", user="root", password="", database="p_f")
            cursor = conn.cursor()
            vehicle_number = self.txt_Vec_no.get().upper()
            cursor.execute("DELETE FROM vehicles WHERE vehicle_number=%s", (vehicle_number,))
            conn.commit()
            if cursor.rowcount > 0:
                messagebox.showinfo("Success", "Data deleted successfully")
            else:
                messagebox.showerror("Error", "No record found with the given Vehicle Number")
        except mysql.Error as e:
            messagebox.showerror("Error", f"Data deletion failed: {e}")

class ManualInput:
    def __init__(self, root, container):
        self.frame = Frame(container)
        self.frame.grid(row=0, column=0, sticky="nsew")

        # Label for input field
        self.label = Label(self.frame, text="Enter Vehicle Number:")
        self.label.grid(row=0, column=0, padx=10, pady=10)

        # Input field
        self.input_field = Entry(self.frame, width=30)
        self.input_field.grid(row=0, column=1, padx=10, pady=10)

        # Submit button
        self.submit_button = Button(self.frame, text="Submit", command=self.submit_value)
        self.submit_button.grid(row=1, column=0, columnspan=2, pady=10)

    def submit_value(self):
        vehicle_num = self.input_field.get().upper()
        if not vehicle_num:
            messagebox.showerror("Error", "Vehicle Number is required")
            return

        try:
            # Database connection
            self.con = mysql.connect(host="localhost", user="root", password="", database="p_f")
            self.cursor = self.con.cursor()

            # Check if the vehicle exists in the vehicles table
            check_vehicle_query = "SELECT * FROM vehicles WHERE vehicle_number = %s"
            self.cursor.execute(check_vehicle_query, (vehicle_num,))
            vehicle_exists = self.cursor.fetchone()

            if not vehicle_exists:
                messagebox.showerror("Error", f"Vehicle number {vehicle_num} does not exist. Please register the vehicle first.")
                return

            # Check if the vehicle is already parked (i.e., has no exit_time)
            select_query = "SELECT * FROM parking_logs WHERE vehicle_number = %s AND exit_time IS NULL"
            self.cursor.execute(select_query, (vehicle_num,))
            result = self.cursor.fetchone()

            if result:  # If a record exists, the vehicle is exiting
                query = "UPDATE parking_logs SET exit_time = NOW() WHERE vehicle_number = %s AND exit_time IS NULL"
                self.cursor.execute(query, (vehicle_num,))
                self.con.commit()
                messagebox.showinfo("Message", f"Vehicle number {vehicle_num} exited successfully")
            else:  # If no record exists, the vehicle is entering
                # Check for an available parking slot
                slot_query = "SELECT slot_number FROM parking_slots WHERE status = 'Available' LIMIT 1"
                self.cursor.execute(slot_query)
                slot_result = self.cursor.fetchone()

                if slot_result:  # If a parking slot is available
                    parking_slot = slot_result[0]
                    insert_query = """
                        INSERT INTO parking_logs (vehicle_number, parking_slot, entry_time)
                        VALUES (%s, %s, NOW())
                    """
                    self.cursor.execute(insert_query, (vehicle_num, parking_slot))
                    # Mark the parking slot as occupied
                    update_slot_query = "UPDATE parking_slots SET status = 'Occupied' WHERE slot_number = %s"
                    self.cursor.execute(update_slot_query, (parking_slot,))
                    self.con.commit()
                    messagebox.showinfo("Message", f"Vehicle number {vehicle_num} parked successfully\nParking slot allocated: {parking_slot}")
                else:  # No parking slots available
                    messagebox.showerror("Error", "No available parking slots")
        except mysql.Error as e:
            print(f"Error processing vehicle data: {e}")
            self.con.rollback()
            messagebox.showerror("Error", f"Database error: {e}")

class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart parking")
        self.root.geometry("600x600")

        # Creating container for pages
        self.container = Frame(self.root)
        self.container.grid(row=0, column=0, sticky="nsew")

        # Configure the grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Initialize WebcamApp
        self.cam = WebcamApp(self.root, self.container)

        # Include Member page
        self.include_member = Include_member(self.root, self.container)

        # Manual Input page
        self.manual_input = ManualInput(self.root, self.container)

        # Create a menu bar
        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Add "Mode" menu
        self.auto_mode_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Auto", menu=self.auto_mode_menu)
        self.auto_mode_menu.add_command(label="Auto In", command=self.show_camera_in)
        self.auto_mode_menu.add_separator()
        self.auto_mode_menu.add_command(label="Exit", command=self.root.quit)

        # Add "Include Member" menu
        self.include_member_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Include Member", menu=self.include_member_menu)
        self.include_member_menu.add_command(label="Include Member", command=self.show_include_member)

        # Add "Manual Input" menu
        self.manual_input_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Manual Input", menu=self.manual_input_menu)
        self.manual_input_menu.add_command(label="Manual Input", command=self.show_manual_input)

        # Start with the camera view
        self.show_camera_in()

    def show_camera_in(self):
        self.cam.video_label.grid()
        self.cam.capture_btn_in.grid()
        self.cam.video_label.tkraise()

    def show_include_member(self):
        self.cam.video_label.grid_remove()
        self.cam.capture_btn_in.grid_remove()
        self.manual_input.frame.grid_remove()
        self.include_member.frame.grid()
        self.include_member.frame.tkraise()

    def show_manual_input(self):
        self.cam.video_label.grid_remove()
        self.cam.capture_btn_in.grid_remove()
        self.include_member.frame.grid_remove()
        self.manual_input.frame.grid()
        self.manual_input.frame.tkraise()

if __name__ == "__main__":
    root = Tk()
    app = Application(root)
    root.mainloop()