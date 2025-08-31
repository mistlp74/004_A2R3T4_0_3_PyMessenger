# PyMessenger

## Description

**PyMessenger** is a simple Python-based client-server application for real-time text messaging between users. The client features an intuitive Tkinter graphical interface for registration, managing contacts, and live chatting. All communication with the server is performed via HTTP requests.

---

## Features

- User registration by phone number and name
- Adding contacts by phone number
- Sending and receiving messages in real time
- Chat history with each contact (stored locally)
- Automatic polling for incoming messages and contact requests
- Friendly and extendable user interface

---

## Requirements

- Python 3.8+
- `requests` library
- `tkinter` (included with most Python installations)

---

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/mistlp74/004_A2R3T4_0_3_PyMessenger.git
    cd Pymessenger
    ```

2. **Install dependencies:**
    ```bash
    pip install requests
    ```
    *(If `tkinter` is missing, install it via your OS package manager, e.g., `sudo apt install python3-tk` for Ubuntu/Debian.)*

---

## Usage

1. **Start the server**  
   (Move `__ServerPart__` to your server and run `server.py`

2. **Run the client:**
    ```bash
    python main.py
    ```

3. **Register** with your name and phone number.

4. **Add contacts** by their phone number.

5. **Select a contact** to open a chat window and start messaging.

---

## Project Structure

- `StartWindow.py` — Registration UI
- `MainWindow.py` — Main chat interface
- `Client.py` — Handles all server communication (network logic, polling)
- `File_Manager.py` — Local file operations (user info, contacts, chat history)
- `config.py` — Server address and parameters

---

## Troubleshooting

- **KeyError: 'number'**  
  Your contacts list contains entries without the `number` field.  
  *Solution:* Delete or fix `contacts.json`.

- **Empty user data `{}`**  
  User not registered.  
  *Solution:* Register using `StartWindow.py`.

---

## Author

Developed by [mistlp74](https://github.com/mistlp74)