import socket
import time
import datetime

# TeaSpeak Server Settings
HOST = "62.220.120.120"
PORT = 5039
VPORT = 4023
USER = "appi"
PASS = "fpmhzEC9kF4f"

# Existing spacer channel IDs (5 lines)
CLOCK_CHANNEL_IDS = [224, 225, 226, 227, 228]

# 5-line block digits with uniform grid length
DIGITS = {
    '0': ["█████", "█░░░█", "█░░░█", "█░░░█", "█████"],
    '1': ["░░██░", "░███░", "░░░█░", "░░░█░", "░████"],
    '2': ["█████", "░░░░█", "█████", "█░░░░", "█████"],
    '3': ["█████", "░░░░█", "█████", "░░░░█", "█████"],
    '4': ["█░░░█", "█░░░█", "█████", "░░░░█", "░░░░█"],
    '5': ["█████", "█░░░░", "█████", "░░░░█", "█████"],
    '6': ["█████", "█░░░░", "█████", "█░░░█", "█████"],
    '7': ["█████", "░░░░█", "░░░█░", "░░█░░", "░░█░░"],
    '8': ["█████", "█░░░█", "█████", "█░░░█", "█████"],
    '9': ["█████", "█░░░█", "█████", "░░░░█", "█████"],
    ':': ["░░", "██", "░░", "██", "░░"]
}

def escape_ts3_name(text: str) -> str:
    text = text.replace('\\', r'\\')
    text = text.replace('/', r'\/')
    text = text.replace(' ', r'\s')
    text = text.replace('|', r'\p')
    return text

def send_cmd(s, cmd):
    if cmd:
        s.sendall((cmd + "\n").encode('utf-8'))
        time.sleep(0.15)
    
    res = ""
    try:
        while True:
            chunk = s.recv(8192).decode('utf-8', errors='ignore')
            res += chunk
            if "error id=" in chunk or len(chunk) < 8192:
                break
    except:
        pass
    return res

def render_time_lines(time_str: str):
    lines = ["", "", "", "", ""]
    for char in time_str:
        if char in DIGITS:
            glyph = DIGITS[char]
            for i in range(5):
                lines[i] += glyph[i] + "░"
    return lines

def run_clock_bot():
    while True:
        try:
            print(f"[*] Connecting to TeaSpeak server ({HOST}:{PORT})...")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((HOST, PORT))

            time.sleep(0.3)
            try: s.recv(8192)
            except: pass

            login_res = send_cmd(s, f"login {USER} {PASS}")
            use_res = send_cmd(s, f"use port={VPORT}")

            if "error id=0" not in login_res or "error id=0" not in use_res:
                print("[-] Login failed or Virtual Server port is incorrect!")
                s.close()
                time.sleep(10)
                continue

            print("[+] Connected! Updating clock channels (Centered & Fixed)...")
            last_time = ""

            while True:
                current_time = datetime.datetime.now().strftime("%H:%M")

                if current_time != last_time:
                    time_lines = render_time_lines(current_time)
                    
                    for idx, cid in enumerate(CLOCK_CHANNEL_IDS):
                        raw_line = time_lines[idx]
                        # Standard TeaSpeak centered spacer tag: [cspacer1], [cspacer2]...
                        channel_text = f"[cspacer{idx+1}]{raw_line}"
                        safe_name = escape_ts3_name(channel_text)
                        
                        cmd = f"channeledit cid={cid} channel_name={safe_name}"
                        send_cmd(s, cmd)

                    print(f"[+] Clock updated to: {current_time}")
                    last_time = current_time

                time.sleep(10)

        except Exception as e:
            print(f"[!] Error: {e}. Reconnecting in 10 seconds...")
            time.sleep(10)

if __name__ == "__main__":
    run_clock_bot()