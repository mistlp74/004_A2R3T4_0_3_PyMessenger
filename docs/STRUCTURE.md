# Messenger — Code Structure

## Main Application Files

- **main.py**
  - Entry point in program

- **StartWindow.py**
    - GUI for user registration (name and phone number)
    - Triggers main window on success

- **MainWindow.py**
    - Main chat interface
    - Shows contact list, chat area, message input
    - Handles chat history and contact management

- **Client.py**
    - All network logic: HTTP requests to the server (register, send message, poll for new messages/requests)
    - Uses background threads for polling

- **File_Manager.py**
    - Reads and writes user info, contacts, and chat messages to local JSON files
    - Handles file validation

- **config.py**
    - Stores the server URL and other global settings

---

## Data Files and Directories

- **contacts.json** — Local list of contacts (name, number)
- **User_Info.json** — Local user credentials (name, number)
- **chats/** — Directory containing chat history files (one per contact, e.g., `chats/1234567890.json`)

---

## Example Data Structure

**contacts.json**
```json
[
    {
        "name": "John Doe",
        "number": "1234567890"
    }
]
```

**User_Info.json**
```json
{
    "name": "Alice",
    "number": "0987654321"
}
```

**chats/1234567890.json**
```json
[
    {"from": "Alice", "text": "Hello!"},
    {"from": "John Doe", "text": "Hi!"}
]
```
