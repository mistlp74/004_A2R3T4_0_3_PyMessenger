import tkinter as tk
from tkinter import messagebox
import json
import os
import threading
from File_Manager import load_user_info, load_contacts, save_contacts
from Client import (
    start_polling,
    stop_polling,
    send_message as net_send_message,
    send_system_request as net_send_system_request,
)

CONTACTS_FILE = "contacts.json"
CHATS_DIR = "chats"

current_open_chat = {
    "contact": None,
    "scrollable_msg": None,
    "canvas": None,
    "chat_file": None,
    "messages": None,
}

user = None

os.makedirs(CHATS_DIR, exist_ok=True)


def sanitize_contacts():
    contacts = load_contacts()
    cleaned = []
    changed = False
    for c in contacts:
        if not isinstance(c, dict):
            changed = True
            continue
        name = c.get("name")
        number = c.get("number") or c.get("phone") or c.get("num") or c.get("id")
        if not number:
            changed = True
            continue
        if not name:
            name = str(number)
            changed = True
        cleaned.append({"name": str(name), "number": str(number)})
    if changed:
        save_contacts(cleaned)
    return cleaned

def start_main_window():
    global user
    user = load_user_info() or {}

    if not user.get("number") or not user.get("name"):
        msg = "User data (Name/Number) is not founded, try log in in StartWindow first"
        print(msg, "user:", user)
        tk.Tk().withdraw()
        messagebox.showerror("Error", msg)
        return

    contacts = sanitize_contacts()

    root = tk.Tk()
    root.title(f"Chat-Client - {user['name']}")
    root.geometry("1000x700")

    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    sidebar = tk.Frame(main_frame, width=200, bg="#88BBF2")
    sidebar.pack(side=tk.LEFT, fill=tk.Y)
    sidebar.pack_propagate(False)

    chat_area = tk.Frame(main_frame, bg="white")
    chat_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    tk.Button(
        sidebar,
        text="+ Add Contact",
        command=lambda: open_add_user_window(sidebar, chat_area),
    ).pack(fill=tk.X, pady=5, padx=5)

    contact_list = tk.Frame(sidebar)
    contact_list.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(contact_list, bg="#88BBF2")
    scrollbar = tk.Scrollbar(contact_list, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#88BBF2")

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    placeholder_label = tk.Label(
        chat_area,
        text="Chouse a contact to see a cha",
        font=("Arial", 14),
        bg="white",
    )
    placeholder_label.pack(pady=20)

    for contact in contacts:
        add_contact_to_ui(contact, scrollable_frame, chat_area)

    def on_incoming_request(req: dict):
        from_number = req.get("from")
        sender_name = req.get("text", from_number)

        def handle():
            contacts_local = load_contacts()
            if any(c.get("number") == from_number for c in contacts_local):
                return
            new_contact = {"name": sender_name, "number": from_number}
            add_contact_logic(new_contact, scrollable_frame, chat_area, send_request=False)

        root.after(0, handle)

    def on_incoming_message(msg: dict):
        contact_number = msg.get("from")
        text = msg.get("text", "")

        def handle():
            contacts_local = load_contacts()
            if not any(c.get("number") == contact_number for c in contacts_local):
                new_contact = {"name": contact_number, "number": contact_number}
                add_contact_logic(new_contact, scrollable_frame, chat_area, send_request=False)
                contacts_local = load_contacts()

            contact_name = next(
                (c.get("name") for c in contacts_local if c.get("number") == contact_number),
                contact_number,
            )
            chat_file = os.path.join(CHATS_DIR, f"{contact_number}.json")

            if os.path.exists(chat_file):
                with open(chat_file, "r", encoding="utf-8") as f:
                    chat_msgs = json.load(f)
            else:
                chat_msgs = []

            chat_msgs.append({"from": contact_name, "text": text})

            with open(chat_file, "w", encoding="utf-8") as f:
                json.dump(chat_msgs, f, ensure_ascii=False, indent=2)

            if (
                current_open_chat["contact"] is not None
                and current_open_chat["contact"].get("number") == contact_number
                and current_open_chat["scrollable_msg"] is not None
            ):
                tk.Label(
                    current_open_chat["scrollable_msg"],
                    text=f'{contact_name}: "{text}"',
                    bg="white",
                    anchor="w",
                    justify="left",
                    wraplength=600,
                ).pack(anchor="w", padx=10, pady=2)
                current_open_chat["canvas"].after(100, lambda: current_open_chat["canvas"].yview_moveto(1.0))

        root.after(0, handle)

    poller_handle = start_polling(
        number=user["number"],
        on_request=on_incoming_request,
        on_message=on_incoming_message,
        requests_interval=5,
        messages_interval=3,
    )

    def on_close():
        try:
            stop_polling(poller_handle)
        except Exception:
            pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


def open_add_user_window(container_frame, chat_area):
    win = tk.Toplevel()
    win.title("Add a contact")
    win.geometry("200x175")
    win.grab_set()

    tk.Label(win, text="Ім'я:").pack(pady=(10, 0))
    name_entry = tk.Entry(win)
    name_entry.pack(pady=5, padx=10, fill=tk.X)

    tk.Label(win, text="Phone number:").pack(pady=(10, 0))
    number_entry = tk.Entry(win)
    number_entry.pack(pady=5, padx=10, fill=tk.X)

    def submit():
        name = name_entry.get().strip()
        number = number_entry.get().strip()
        if not name or not number:
            messagebox.showerror("Error", "Name and number are necessary")
            return

        new_contact = {"name": name, "number": number}
        add_contact_logic(new_contact, container_frame, chat_area, send_request=True)
        win.destroy()

    tk.Button(win, text="Add", command=submit, font=("Arial", 16)).pack(pady=10)


def add_contact_logic(contact, container, chat_area, send_request=False):
    if not isinstance(contact, dict):
        print("The contact is not correct:", contact)
        return

    to_number = str(contact.get("number", "")).strip()
    if not to_number:
        print("Контакт без 'number':", contact)
        return

    name = contact.get("name") or to_number
    normalized = {"name": str(name), "number": to_number}

    contacts = load_contacts()
    if any(str(c.get("number", "")).strip() == to_number for c in contacts):
        return

    contacts.append(normalized)
    save_contacts(contacts)
    container.after(0, add_contact_to_ui, normalized, container, chat_area)

    if send_request:
        from_number = str(user.get("number", "")).strip()
        from_name = str(user.get("name", "")).strip()
        if not from_number or not from_name:
            print("Its imposible to send the request: user data is nt correct:", user)
            return

        def worker(to_number=to_number, from_number=from_number, from_name=from_name):
            err = net_send_system_request(from_number, from_name, to_number)
            if err:
                print("Error in sending system request:", err)

        threading.Thread(target=worker, daemon=True).start()


def add_contact_to_ui(contact, container, chat_area):
    to_number = contact.get("number")
    if not to_number:
        print("Error in number in contact in UI", contact)
        return

    chat_file = os.path.join(CHATS_DIR, f"{to_number}.json")
    if not os.path.exists(chat_file):
        with open(chat_file, "w", encoding="utf-8") as f:
            json.dump([], f)

    def open_chat():
        for w in chat_area.winfo_children():
            w.destroy()
        load_chat_ui(contact, chat_area)

    btn = tk.Button(container, text=contact.get("name", to_number), anchor="w", command=open_chat)
    btn.pack(fill=tk.X, padx=5, pady=2)


def load_chat_ui(contact, chat_area):
    global current_open_chat
    for widget in chat_area.winfo_children():
        widget.destroy()

    to_number = str(contact.get("number", "")).strip()
    if not to_number:
        tk.Label(chat_area, text="Contact is not correct (no contact)", bg="white").pack(pady=20)
        return

    chat_file = os.path.join(CHATS_DIR, f"{to_number}.json")

    if os.path.exists(chat_file):
        with open(chat_file, "r", encoding="utf-8") as f:
            messages = json.load(f)
    else:
        messages = []

    current_open_chat.update(
        {"contact": contact, "chat_file": chat_file, "messages": messages, "scrollable_msg": None, "canvas": None}
    )

    top_bar = tk.Frame(chat_area, bg="#dddddd")
    top_bar.pack(fill=tk.X)
    tk.Label(
        top_bar,
        text=f"Chat with: {contact.get('name', to_number)} ({to_number})",
        font=("Arial", 14, "bold"),
        bg="#dddddd",
        anchor="w",
    ).pack(padx=10, pady=5, fill=tk.X)

    msg_frame = tk.Frame(chat_area, bg="white")
    msg_frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(msg_frame, bg="white")
    scrollbar = tk.Scrollbar(msg_frame, orient="vertical", command=canvas.yview)
    scrollable_msg = tk.Frame(canvas, bg="white")

    scrollable_msg.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_msg, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    current_open_chat["scrollable_msg"] = scrollable_msg
    current_open_chat["canvas"] = canvas

    for msg in messages:
        sender = "Я" if msg.get("from") == "me" else msg.get("from")
        text = msg.get("text", "")
        tk.Label(scrollable_msg, text=f'{sender}: "{text}"', bg="white", anchor="w", justify="left", wraplength=600).pack(
            anchor="w", padx=10, pady=2
        )

    input_frame = tk.Frame(chat_area, bg="#eeeeee")
    input_frame.pack(fill=tk.X)

    msg_entry = tk.Entry(input_frame, font=("Arial", 12))
    msg_entry.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)

    def do_send_message():
        text = msg_entry.get().strip()
        if not text:
            return

        messages.append({"from": "me", "text": text})
        with open(chat_file, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)

        tk.Label(
            scrollable_msg, text=f'I: "{text}"', bg="white", anchor="w", justify="left", wraplength=600
        ).pack(anchor="w", padx=10, pady=2)

        msg_entry.delete(0, tk.END)
        canvas.yview_moveto(1.0)

        to_number_local = to_number
        from_number_local = str(user.get("number", "")).strip()

        def worker(local_text=text, to_number=to_number_local, from_number=from_number_local):
            err = net_send_message(from_number, to_number, local_text)
            if err:
                print(err)

        threading.Thread(target=worker, daemon=True).start()

    tk.Button(input_frame, text="Send", command=do_send_message).pack(side=tk.RIGHT, padx=10, pady=10)