from tkinter import *
from tkinter import ttk
import tkinter.messagebox as messagebox
import mysql.connector


class window:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Panel")
        self.root.geometry("400x250")
        self.root.resizable(False, False)

        self.label = Label(self.root, text="Parking Log",)
        self.label.grid(row=0, column=0, padx=10, pady=10)
        self.text = Entry(self.root)
        self.text.grid(row=0, column=1, padx=10, pady=10)
        self.btn_search = Button(self.root, text="Search", command=self.log_detail)
        self.btn_search.grid(row=1, column=0, padx=10, pady=10)

    
    def log_detail(self):
        window_ = Toplevel(self.root)
        window_.title("Parking Logs")
        window_.geometry("700x400")

        vechicle_number = self.text.get().upper()
        if vechicle_number == "":
            messagebox.showinfo("Message", "Enter the number")
            return

        tree = ttk.Treeview(
            window_,
            columns=("Log ID", "Vehicle Number", "Entry Time", "Exit Time", "Parking Slot"),
            show="headings"
        )
        tree.heading("Log ID", text="Log ID")
        tree.heading("Vehicle Number", text="Vehicle Number")
        tree.heading("Entry Time", text="Entry Time")
        tree.heading("Exit Time", text="Exit Time")
        tree.heading("Parking Slot", text="Parking Slot")

        # Fetch all logs from the database
        conn = mysql.connector.connect(
            host="localhost", user="root", password="1234", database="kar"
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM parking_logs where vehicle_number = %s", (vechicle_number,))
        logs = cursor.fetchall()
        conn.close()

        for log in logs:
            tree.insert(
                "", END,
                values=(
                    log.get("log_id", ""),
                    log.get("vehicle_number", ""),
                    log.get("entry_time", ""),
                    log.get("exit_time", ""),
                    log.get("parking_slot", "")
                )
            )

        tree.pack(fill=BOTH, expand=True)

class IncludeMemberForm:
    def __init__(self, root):
        self.top = Toplevel(root)
        self.top.title("Include Member")
        self.top.geometry("450x450")
        self.top.resizable(False, False)

        Label(self.top, text="Owner Name:").pack(pady=5)
        self.owner_name = Entry(self.top, width=30)
        self.owner_name.pack(pady=5)

        Label(self.top, text="Contact Number:").pack(pady=5)
        self.contact_number = Entry(self.top, width=30)
        self.contact_number.pack(pady=5)

        Label(self.top, text="Vehicle Number:").pack(pady=5)
        self.vehicle_number = Entry(self.top, width=30)
        self.vehicle_number.pack(pady=5)

        Label(self.top, text="Vehicle Type:").pack(pady=5)
        self.vehicle_type = ttk.Combobox(self.top, values=["Car", "Bike", "Truck"], width=27)
        self.vehicle_type.pack(pady=5)

        Button(self.top, text="Submit", command=self.submit).pack(pady=8)
        Button(self.top, text="Delete", command=self.delete_member).pack(pady=8)
        Button(self.top, text="Update", command=self.update_member).pack(pady=8)

    def submit(self):
        name = self.owner_name.get()
        contact = self.contact_number.get()
        vehicle = self.vehicle_number.get().upper()
        vtype = self.vehicle_type.get()
        if not (name and contact and vehicle and vtype):
            messagebox.showerror("Error", "All fields are required", parent=self.top)
            return
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="1234", database="kar")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO vehicles (vehicle_number, owner_name, contact_number, vehicle_type) VALUES (%s, %s, %s, %s)",
                (vehicle, name, contact, vtype)
            )
            conn.commit()
            messagebox.showinfo("Success", "Member included successfully", parent=self.top)
            self.top.destroy()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Failed to include member: {e}", parent=self.top)

    def delete_member(self):
        vehicle = self.vehicle_number.get().upper()
        if not vehicle:
            messagebox.showerror("Error", "Vehicle Number is required", parent=self.top)
            return
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="1234", database="kar")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vehicles WHERE vehicle_number = %s", (vehicle,))
            conn.commit()
            if cursor.rowcount > 0:
                messagebox.showinfo("Success", "Member deleted successfully", parent=self.top)
                self.top.destroy()
            else:
                messagebox.showerror("Error", "No such vehicle found", parent=self.top)
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Failed to delete member: {e}", parent=self.top)

    def update_member(self):
        name = self.owner_name.get()
        contact = self.contact_number.get()
        vehicle = self.vehicle_number.get().upper()
        vtype = self.vehicle_type.get()
        if not (name and contact and vehicle and vtype):
            messagebox.showerror("Error", "All fields are required", parent=self.top)
            return
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="1234", database="kar")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE vehicles SET owner_name=%s, contact_number=%s, vehicle_type=%s WHERE vehicle_number=%s",
                (name, contact, vtype, vehicle)
            )
            conn.commit()
            if cursor.rowcount > 0:
                messagebox.showinfo("Success", "Member updated successfully", parent=self.top)
                self.top.destroy()
            else:
                messagebox.showerror("Error", "No such vehicle found", parent=self.top)
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Failed to update member: {e}", parent=self.top)

class AddParkingSlotForm:
    def __init__(self, root):
        self.top = Toplevel(root)
        self.top.title("Add Parking Slot")
        self.top.geometry("300x150")
        self.top.resizable(False, False)

        Label(self.top, text="Parking Slot Number:").pack(pady=10)
        self.slot_number = Entry(self.top, width=20)
        self.slot_number.pack(pady=5)

        Button(self.top, text="Add Slot", command=self.add_slot).pack(pady=10)

    def add_slot(self):
        slot = self.slot_number.get()
        if not slot.isdigit():
            messagebox.showerror("Error", "Please enter a valid slot number.", parent=self.top)
            return
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="1234", database="kar")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO parking_slots (slot_number, status) VALUES (%s, %s)",
                (slot, "Available")
            )
            conn.commit()
            messagebox.showinfo("Success", "Parking slot added successfully.", parent=self.top)
            self.top.destroy()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Slot number already exists.", parent=self.top)
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Failed to add slot: {e}", parent=self.top)
        finally:
            if 'conn' in locals():
                conn.close()

class AdminPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Dashboard")
        self.root.geometry("400x300")  # Increased height for extra button
        self.root.resizable(False, False)

        frame = Frame(self.root, padx=20, pady=20)
        frame.pack(fill=BOTH, expand=True)

        Label(frame, text="Admin Panel", font=("Arial", 16, "bold")).pack(pady=(0, 20))

        Button(frame, text="Include Member", width=25, command=self.include_member).pack(pady=5)
        Button(frame, text="View Parking Log", width=25, command=self.view_parking_log).pack(pady=5)
        Button(frame, text="User Detail", width=25, command=self.show_vehicles).pack(pady=5)
        Button(frame, text="Add Parking Slot", width=25, command=self.add_parking_slot).pack(pady=5)  # New button
        Button(frame, text="Exit", width=25, command=self.root.quit).pack(pady=5)

    def fetch_vehicles(self):
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="kar"
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vehicles")
        vehicles = cursor.fetchall()
        conn.close()
        return vehicles

    def show_vehicles(self):
        window_ = Toplevel(self.root)
        window_.title("Vehicles")

        tree = ttk.Treeview(
            window_,
            columns=("Vehicle Number", "Owner Name", "Contact Number", "Vehicle Type", "Registered At"),
            show="headings"
        )
        tree.heading("Vehicle Number", text="Vehicle Number")
        tree.heading("Owner Name", text="Owner Name")
        tree.heading("Contact Number", text="Contact Number")
        tree.heading("Vehicle Type", text="Vehicle Type")
        tree.heading("Registered At", text="Registered At")

        vehicles = self.fetch_vehicles()
        for v in vehicles:
            tree.insert(
                "", END,
                values=(
                    v["vehicle_number"],
                    v["owner_name"],
                    v["contact_number"],
                    v["vehicle_type"],
                    v.get("registered_at", "")
                )
            )

        tree.pack(fill=BOTH, expand=True)

    def include_member(self):
        IncludeMemberForm(self.root)

    def view_parking_log(self):
        log_window = Toplevel(self.root)
        window(log_window)

    def add_parking_slot(self):
        AddParkingSlotForm(self.root)

if __name__ == "__main__":
    root = Tk()
    app = AdminPage(root)
    root.mainloop()