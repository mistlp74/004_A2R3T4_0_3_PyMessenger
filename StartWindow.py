import tkinter as tk
from tkinter import messagebox
from File_Manager import save_user_info
from Client import register_user

def start_start_window():
    def on_submit():
        name = entry_name.get().strip()
        number = entry_number.get().strip()

        if not name or not number:
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            resp = register_user(name, number)
        except Exception as e:
            messagebox.showerror("Error", f"Network error: {e}")
            return

        if resp.status_code == 200:
            data = resp.json() or {}
            if data.get('status') in ['Registered', 'Already registered']:
                save_user_info(name, number, "User_Info.json")
                from MainWindow import start_main_window
                root.destroy()
                start_main_window()
            else:
                messagebox.showerror("Error", f"Unexpected server response: {data}")
        else:
            messagebox.showerror("Error", f"Registration failed: {resp.text}")

    root = tk.Tk()
    root.geometry("300x200")

    tk.Label(root, text="Name").pack(pady=5)
    entry_name = tk.Entry(root)
    entry_name.pack(pady=5)

    tk.Label(root, text="Phone number").pack(pady=5)
    entry_number = tk.Entry(root)
    entry_number.pack(pady=5)

    tk.Button(root, text="Submit", command=on_submit).pack(pady=20)

    root.mainloop()