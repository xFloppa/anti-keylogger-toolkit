import psutil
from datetime import datetime
import os
import json
import html
from prettytable import PrettyTable

LOG_DIR = os.path.join(os.path.dirname(__file__), "../logs/process_reports")
os.makedirs(LOG_DIR, exist_ok=True)

def scan_processes():
    table = PrettyTable(["PID", "Nome", "Percorso"])
    processes_list = []

    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            pid = proc.info['pid']
            name = proc.info['name']
            path = proc.info['exe']
            table.add_row([pid, name, path])
            processes_list.append({'pid': pid, 'name': name, 'path': path})
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    print(table)
    return processes_list

def save_report(processes):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_file = os.path.join(LOG_DIR, f"process_report_{timestamp}.json")
    html_file = os.path.join(LOG_DIR, f"process_report_{timestamp}.html")

    # Salva JSON
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(processes, f, indent=4)

    # Salva HTML
    html_content = "<html><head><title>Process Report</title></head><body>"
    html_content += "<h2>Process Report</h2><table border='1'><tr><th>PID</th><th>Name</th><th>Path</th></tr>"
    for p in processes:
        html_content += f"<tr><td>{html.escape(str(p['pid']))}</td><td>{html.escape(p['name'])}</td><td>{html.escape(str(p['path']))}</td></tr>"
    html_content += "</table></body></html>"

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"[INFO] Report salvato in {json_file} e {html_file}")

if __name__ == "__main__":
    print("[INFO] Scansione processi in corso...\n")
    processes = scan_processes()
    save_report(processes)
