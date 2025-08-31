import threading
import requests
from typing import Callable, Optional, Dict, Any
from config import SERVER_URL


def register_user(name: str, number: str) -> requests.Response:
    payload = {"number": number, "name": name}
    return requests.post(f"{SERVER_URL}/register", json=payload, timeout=15)


def send_message(from_number: str, to_number: str, text: str) -> Optional[str]:
    try:
        payload = {"from": from_number, "to": to_number, "text": text}
        r = requests.post(f"{SERVER_URL}/send", json=payload, timeout=15)
        if r.status_code != 200:
            return f"Failed to send messege: {r.text}"
        return None
    except Exception as e:
        return f"Network Error while sending messege: {e}"


def send_system_request(from_number: str, from_name: str, to_number: str) -> Optional[str]:
    try:
        payload = {
            "from": from_number,
            "to": to_number,
            "text": from_name,
            "type": "request",
        }
        r = requests.post(f"{SERVER_URL}/send", json=payload, timeout=15)
        if r.status_code != 200:
            return f"System request failed: {r.text}"
        return None
    except Exception as e:
        return f"Network error in send_system_request: {e}"


def start_polling(
    number: str,
    on_request: Optional[Callable[[Dict[str, Any]], None]] = None,
    on_message: Optional[Callable[[Dict[str, Any]], None]] = None,
    requests_interval: int = 5,
    messages_interval: int = 3,
    ) -> Dict[str, Any]:
    stop_event = threading.Event()

    t_req = threading.Thread(
        target=_poll_requests_loop,
        args=(number, on_request, stop_event, requests_interval),
        daemon=True,
    )
    t_msg = threading.Thread(
        target=_poll_messages_loop,
        args=(number, on_message, stop_event, messages_interval),
        daemon=True,
    )

    t_req.start()
    t_msg.start()

    return {
        "stop_event": stop_event,
        "requests_thread": t_req,
        "messages_thread": t_msg,
    }


def stop_polling(handle: Dict[str, Any]):
    stop_event = handle.get("stop_event")
    if stop_event:
        stop_event.set()

    for key in ("requests_thread", "messages_thread"):
        t = handle.get(key)
        if t and t.is_alive():
            # Потік може бути всередині довгого запиту; потоки daemon=True, тому жорстке очікування не обов'язкове
            t.join(timeout=2)


def _poll_requests_loop(number: str, on_request, stop_event: threading.Event, interval: int):
    while not stop_event.is_set():
        try:
            resp = requests.get(
                f"{SERVER_URL}/check_requests",
                params={"number": number},
                timeout=20,
            )
            if resp.status_code == 200:
                data = resp.json() or {}
                for req in data.get("requests", []):
                    if on_request:
                        on_request(req)
            else:
                print("Failed check_requests:", resp.text)
        except Exception as e:
            print("Network Error in check_requests:", e)

        stop_event.wait(interval)


def _poll_messages_loop(number: str, on_message, stop_event: threading.Event, interval: int):
    while not stop_event.is_set():
        try:
            resp = requests.get(
                f"{SERVER_URL}/receive",
                params={"number": number},
                timeout=20,
            )
            if resp.status_code == 200:
                data = resp.json() or {}
                for msg in data.get("messages", []):
                    if msg.get("to") == number and on_message:
                        on_message(msg)
            else:
                print("Failed getting messege:", resp.text)
        except Exception as e:
            print("Network Error in checking messege:", e)

        stop_event.wait(interval)