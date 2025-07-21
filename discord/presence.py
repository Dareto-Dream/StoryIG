import time
from pypresence import Presence
import threading

CLIENT_ID = "1396705942132887642"  # Replace with your actual client ID
START_TIME = int(time.time())

rpc = None
connected = False


def _connect():
    global rpc, connected
    try:
        rpc = Presence(CLIENT_ID)
        rpc.connect()
        connected = True
    except Exception as e:
        print(f"[presence.py] Discord not available: {e}")
        connected = False


def set_presence(details="In Menu", state="Cadence Collapse", large_image="logo", large_text="Cadence Collapse", small_image=None, small_text=None):
    global connected
    wait_time = 0
    while not connected and wait_time < 5:
        time.sleep(0.1)
        wait_time += 0.1

    kwargs = {
        "details": details,
        "state": state,
        "large_image": large_image,
        "large_text": large_text,
        "start": START_TIME
    }

    if small_image:
        kwargs["small_image"] = small_image
    if small_text:
        kwargs["small_text"] = small_text

    try:
        rpc.update(**kwargs)
    except Exception as e:
        print(f"[presence.py] Failed to update presence: {e}")


# Run connection in a thread to avoid blocking
threading.Thread(target=_connect, daemon=True).start()

if __name__ == "__main__":
    set_presence()
    while True:
        time.sleep(15)
