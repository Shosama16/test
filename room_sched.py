import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry


class Room:
    def __init__(self, name):
        self.name = name
        self.bookings = []

    def is_available(self, start, end):
        for booking in self.bookings:
            if start < booking['end'] and end > booking['start']:
                return False
        return True

    def book(self, user, start, end):
        if self.is_available(start, end):
            self.bookings.append({'user': user, 'start': start, 'end': end})
            return True
        return False

    def get_bookings(self):
        return self.bookings


class RoomScheduler:
    def __init__(self, master):
        self.master = master
        master.title("Room Scheduler")

        # Available buildings and rooms
        self.buildings = ["CECS", "HEB", "GZB", "ABB"]
        self.rooms_by_building = {
            "CECS": ["501", "502", "503"],
            "GZB": ["301", "302", "303"],
            "ABB": ["101", "102", "103"],
            "HEB": ["101", "102", "103"]
        }

        # Initialize Room objects for all combinations
        self.rooms = {}
        for bldg, rooms in self.rooms_by_building.items():
            for room in rooms:
                full_name = f"{bldg} {room}"
                self.rooms[full_name] = Room(full_name)

        self.time_options = [f"{h:02d}:{m:02d}" for h in range(1, 13) for m in (0, 30)]
        self.ampm_options = ["AM", "PM"]

        # Building dropdown
        tk.Label(master, text="Select Building:").grid(row=0, column=0, sticky="e")
        self.building_var = tk.StringVar(value=self.buildings[0])
        self.building_menu = ttk.Combobox(master, textvariable=self.building_var, values=self.buildings, state="readonly")
        self.building_menu.grid(row=0, column=1)
        self.building_menu.bind("<<ComboboxSelected>>", self.update_room_numbers)

        # Room number dropdown
        tk.Label(master, text="Select Room Number:").grid(row=1, column=0, sticky="e")
        self.room_var = tk.StringVar()
        self.room_menu = ttk.Combobox(master, textvariable=self.room_var, state="readonly")
        self.room_menu.grid(row=1, column=1)
        self.update_room_numbers()

        tk.Label(master, text="Type Your Name:").grid(row=2, column=0, sticky="e")
        self.user_entry = tk.Entry(master)
        self.user_entry.grid(row=2, column=1)

        tk.Label(master, text="Select Date:").grid(row=3, column=0, sticky="e")
        self.date_picker = DateEntry(master, width=18, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_picker.grid(row=3, column=1)

        tk.Label(master, text="Start Time:").grid(row=4, column=0, sticky="e")
        self.start_time = ttk.Combobox(master, values=self.time_options, state="readonly", width=10)
        self.start_time.grid(row=4, column=1, sticky="w")
        self.start_ampm = ttk.Combobox(master, values=self.ampm_options, state="readonly", width=5)
        self.start_ampm.grid(row=4, column=1, sticky="e")

        tk.Label(master, text="End Time:").grid(row=5, column=0, sticky="e")
        self.end_time = ttk.Combobox(master, values=self.time_options, state="readonly", width=10)
        self.end_time.grid(row=5, column=1, sticky="w")
        self.end_ampm = ttk.Combobox(master, values=self.ampm_options, state="readonly", width=5)
        self.end_ampm.grid(row=5, column=1, sticky="e")

        self.book_button = tk.Button(master, text="Book Room", command=self.book_room)
        self.book_button.grid(row=6, column=0, columnspan=2, pady=10)

        self.view_button = tk.Button(master, text="View Bookings", command=self.view_bookings)
        self.view_button.grid(row=7, column=0, columnspan=2)

        self.result_text = tk.Text(master, height=10, width=50)
        self.result_text.grid(row=8, column=0, columnspan=2, pady=10)

    def update_room_numbers(self, event=None):
        selected_bldg = self.building_var.get()
        room_list = self.rooms_by_building.get(selected_bldg, [])
        self.room_menu['values'] = room_list
        if room_list:
            self.room_var.set(room_list[0])
        else:
            self.room_var.set("")

    def convert_to_24_hour(self, time_str, ampm):
        hour, minute = map(int, time_str.split(':'))
        if ampm == "PM" and hour != 12:
            hour += 12
        elif ampm == "AM" and hour == 12:
            hour = 0
        return f"{hour:02d}:{minute:02d}"

    def book_room(self):
        bldg = self.building_var.get()
        room_no = self.room_var.get()
        user = self.user_entry.get().strip()
        date = self.date_picker.get_date()

        start_time = self.start_time.get()
        start_ampm = self.start_ampm.get()
        end_time = self.end_time.get()
        end_ampm = self.end_ampm.get()

        if not all([bldg, room_no, user, start_time, start_ampm, end_time, end_ampm]):
            messagebox.showerror("Error", "Please complete all fields.")
            return

        try:
            start_24 = self.convert_to_24_hour(start_time, start_ampm)
            end_24 = self.convert_to_24_hour(end_time, end_ampm)
            start_dt = datetime.strptime(f"{date} {start_24}", "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(f"{date} {end_24}", "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Error", "Invalid date or time.")
            return

        if end_dt <= start_dt:
            messagebox.showerror("Error", "End time must be after start time.")
            return

        full_room = f"{bldg} {room_no}"
        room = self.rooms.get(full_room)
        if room and room.book(user, start_dt, end_dt):
            messagebox.showinfo("Success", f"{full_room} booked successfully!")
            self.user_entry.delete(0, tk.END)
            self.start_time.set('')
            self.start_ampm.set('')
            self.end_time.set('')
            self.end_ampm.set('')
        else:
            messagebox.showwarning("Unavailable", f"{full_room} is not available for that time slot.")

    def view_bookings(self):
        bldg = self.building_var.get()
        room_no = self.room_var.get()
        full_room = f"{bldg} {room_no}"
        room = self.rooms.get(full_room)

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Bookings for {full_room}:\n\n")

        if not room or not room.get_bookings():
            self.result_text.insert(tk.END, "No bookings yet.")
        else:
            for b in room.get_bookings():
                user = b['user']
                date_str = b['start'].strftime("%Y-%m-%d")
                start_str = b['start'].strftime("%I:%M %p")
                end_str = b['end'].strftime("%I:%M %p")
                booking_line = f"{user} - {date_str} - {start_str} to {end_str}\n"
                self.result_text.insert(tk.END, booking_line)


root = tk.Tk()
app = RoomScheduler(root)
root.mainloop()