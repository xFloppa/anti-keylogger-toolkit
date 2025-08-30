import psutil
import threading
import time
from datetime import datetime
import os
import html
import json

# --- Configurazione cartelle ---
LOG_DIR = os.path.join(os.path.dirname(__file__), "../logs/process_reports")
os.makedirs(LOG_DIR, exist_ok=True)

# --- Parole chiave sospette nei percorsi ---
SUSPICIOUS_PATH_KEYWORDS = ["temp", "tmp", "/tmp/"]

# --- Processi legittimi (whitelist) ---
WHITELIST = [
    "explorer.exe", "svchost.exe", "chrome.exe", "firefox.exe",
    "python.exe", "code.exe", "teams.exe", "discord.exe"
]

# --- Caricamento IOC JSON (processi noti keylogger) ---
IOC_FILE = os.path.join(os.path.dirname(__file__), "ioc.json")
if os.path.exists(IOC_FILE):
    with open(IOC_FILE, 'r') as f:
        IOC_LIST = json.load(f)
else:
    IOC_LIST = []

# --- Dizionari per CPU monitoring ---
cpu_data_first = {}
cpu_data_second = {}

def monitor_cpu(pid, storage, interval):
    try:
        proc = psutil.Process(pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return
    storage[pid] = []
    start_time = time.time()
    while time.time() - start_time < interval:
        try:
            usage = proc.cpu_percent(interval=1)
            storage[pid].append(usage)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            break

def run_cpu_monitoring(pids, interval, storage):
    threads = []
    for pid in pids:
        t = threading.Thread(target=monitor_cpu, args=(pid, storage, interval))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

def avg_cpu(data):
    result = {}
    for pid, values in data.items():
        if values:
            result[pid] = sum(values)/len(values)
    return result

def scan_processes():
    processes_list = []
    name_count = {}
    all_pids = psutil.pids()

    # Primo intervallo CPU
    run_cpu_monitoring(all_pids, interval=5, storage=cpu_data_first)
    # Secondo intervallo CPU
    run_cpu_monitoring(all_pids, interval=5, storage=cpu_data_second)

    avg_cpu_first = avg_cpu(cpu_data_first)
    avg_cpu_second = avg_cpu(cpu_data_second)

    for pid in all_pids:
        try:
            proc = psutil.Process(pid)
            name = proc.name() or ""
            path = proc.exe() or ""
            name_count[name] = name_count.get(name, 0) + 1

            risk_score = 0

            # Fattori di rischio
            if any(k.lower() in path.lower() for k in SUSPICIOUS_PATH_KEYWORDS):
                risk_score += 3
            if not path.endswith((".exe", ".bat", ".cmd", ".py")):
                risk_score += 2
            if not name:
                risk_score += 3
            if name_count[name] > 5:
                risk_score += 2
            if name.lower() not in [x.lower() for x in WHITELIST]:
                risk_score += 1

            # Controllo IOC
            very_suspicious = False
            for ioc in IOC_LIST:
                if ioc['name'].lower() in name.lower():
                    risk_score += 5
                    very_suspicious = True
                    break

            # Analisi CPU aumento sospetto
            cpu_increase = avg_cpu_second.get(pid, 0) - avg_cpu_first.get(pid, 0)
            if cpu_increase > 20:  # se aumenta >20%
                risk_score += 2

            processes_list.append({
                'pid': pid,
                'name': name,
                'path': path,
                'risk_score': risk_score,
                'suspicious': risk_score >= 5,
                'very_suspicious': very_suspicious
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return processes_list

def save_report(processes):
    timestamp = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
    filename = f"process_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    filepath = os.path.join(LOG_DIR, filename)

    html_content = f"""
    <html>
    <head>
        <title>Process Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #1B1B2F; color: #E0E0E0; padding: 20px; }}
            h2 {{ color: #00C9A7; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ border: 1px solid #444; padding: 8px; text-align: left; }}
            th {{ background-color: #162447; color: #00C9A7; }}
            tr:nth-child(even) {{ background-color: #1F4068; }}
            tr:nth-child(odd) {{ background-color: #1B1B2F; }}
            .suspicious {{ background-color: #FF4C4C !important; color: #FFFFFF; font-weight: bold; }}
            .very_suspicious {{ background-color: #FF0000 !important; color: #FFFFFF; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h2>Process Report - {timestamp}</h2>
        <table>
            <tr><th>PID</th><th>Name</th><th>Path</th><th>Risk Score</th><th>Suspicious</th></tr>
    """

    for p in processes:
        row_class = ""
        if p['very_suspicious']:
            row_class = "very_suspicious"
        elif p['suspicious']:
            row_class = "suspicious"

        html_content += f"<tr class='{row_class}'>"
        html_content += f"<td>{html.escape(str(p['pid']))}</td>"
        html_content += f"<td>{html.escape(p['name'])}</td>"
        html_content += f"<td>{html.escape(p['path'])}</td>"
        html_content += f"<td>{p['risk_score']}</td>"
        html_content += f"<td>{'YES' if p['suspicious'] else 'NO'}</td></tr>"

    html_content += "</table></body></html>"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"[INFO] Report salvato in {filepath}")

if __name__ == "__main__":
    print("[INFO] Scansione processi in corso...")
    processes = scan_processes()
    save_report(processes)
    print("[INFO] Scansione completata!")
