import sys
import time
import socket
import threading
import webbrowser

import requests
import uvicorn

import main as app_module


HOST = "127.0.0.1"
PORT = 8000

BASE_URL = f"http://{HOST}:{PORT}"
HEALTH_URL = f"{BASE_URL}/health"


def is_port_available(host: str, port: int) -> bool:
    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as sock:
        return sock.connect_ex((host, port)) != 0


def wait_for_server(timeout: int = 30) -> bool:
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(
                HEALTH_URL,
                timeout=1
            )

            if response.ok:
                return True

        except requests.RequestException:
            pass

        time.sleep(0.5)

    return False


def start_server():
    config = uvicorn.Config(
        app_module.app,
        host=HOST,
        port=PORT,
        log_level="info"
    )

    server = uvicorn.Server(config)

    thread = threading.Thread(
        target=server.run,
        daemon=True
    )

    thread.start()

    return server, thread


def main():
    if not is_port_available(HOST, PORT):
        webbrowser.open(BASE_URL)
        return

    print("Starting Ramma Sorter...")

    server, server_thread = start_server()

    try:
        print("Waiting for server...")

        if not wait_for_server():
            print(
                "Failed to start Ramma Sorter."
            )

            server.should_exit = True

            return

        print("Ramma Sorter is ready.")

        webbrowser.open(BASE_URL)

        while server_thread.is_alive():
            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopping Ramma Sorter...")

    finally:
        server.should_exit = True

        server_thread.join(
            timeout=5
        )


if __name__ == "__main__":
    main()