from datetime import datetime


def this_logger(message, log_type):
    current_time = datetime.now()
    human_time = current_time.strftime("%H:%M:%S")
    if log_type == "debug":
        print(f"[{human_time} - DEBUG] " + message)
    elif log_type == "error":
        print(f"[{human_time} - ERROR!] " + message)
    elif log_type == "critical":
        print(f"{human_time} | CRITICAL NOTE _ {message}")
    else:
        print(f"[{human_time}] " + message)
