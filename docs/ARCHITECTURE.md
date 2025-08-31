# Messenger — Architecture Overview

## Overview

Messenger is a basic client-server messaging system where each client communicates with a central server using HTTP requests. The client is implemented as a desktop GUI application using Python's Tkinter.

---

## Main Components

### 1. Client (Desktop Application)
- **Written in Python using Tkinter**
- Handles user registration, contact management, message sending and receiving, and chat history
- Stores user data and chat history locally in JSON files
- Communicates with the server using HTTP endpoints (via the `requests` library)
- Uses background threads for polling the server for new messages and requests

### 2. Server
- Not included in this repository — assumed to be a REST API
- Handles user registration, message delivery, and storing user data
- Exposes endpoints such as `/register`, `/send`, `/receive`, `/check_requests`

---

## Data Flow

1. **Registration**
   - User enters their name and phone number
   - Client sends a POST request to `/register`
   - Upon success, user info is saved locally

2. **Adding Contacts**
   - User provides a contact's phone number and name
   - Contact is saved locally and a system request is sent to the server

3. **Messaging**
   - Users send messages via the GUI
   - Messages are POSTed to `/send` and stored locally
   - The server relays messages to the intended recipient

4. **Polling**
   - The client runs background threads to poll for new messages (`/receive`) and requests (`/check_requests`)
   - New data is displayed in the GUI and saved to local files

---

## Error Handling

- All network operations are performed with exception handling
- Local data is validated before use (e.g., checking for missing fields)
- GUI operations are performed in the main thread, with updates from background threads synchronized via `after()` calls

---

## Extending the System

- New features can be added by extending the GUI modules (`MainWindow.py`, `StartWindow.py`)
- Server communication logic can be expanded in `Client.py`
- Data storage and management logic can be modified in `File_Manager.py`
- The system is designed to be modular and easy to understand for new contributors

---

## Security Considerations

- This is a demonstration project and does not implement encryption or authentication beyond basic registration
- For production use, HTTPS and proper authentication/authorization should be added

---

## Diagram

```plaintext
+-------------+           HTTP           +------------+
|  Messenger  | <----------------------> |  Server    |
|   Client    |    (requests/responses)  | (REST API) |
+-------------+                         +------------+
      |
  Local storage
  (contacts, chats, user info in JSON files)
```