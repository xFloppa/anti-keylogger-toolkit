import psutil
from datetime import datetime
import os
import html

LOG_DIR = os.path.join(os.path.dirname(__file__), "../logs/process_reports")
os.makedirs(LOG_DIR, exist_ok=True)

def scan_processes():
    processes_list = []
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            pid = proc.info['pid']
            name = proc.info['name']
            path = proc.info['exe'] if proc.info['exe'] else ""
            processes_list.append({'pid': pid, 'name': name, 'path': path})
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
        </style>
    </head>
    <body>
        <h2>Process Report - {timestamp}</h2>
        <table>
            <tr><th>PID</th><th>Name</th><th>Path</th></tr>
    """

    for p in processes:
        html_content += f"<tr><td>{html.escape(str(p['pid']))}</td><td>{html.escape(p['name'])}</td><td>{html.escape(str(p['path']))}</td></tr>"

    html_content += "</table></body></html>"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"[INFO] Report salvato in {filepath}")

if __name__ == "__main__":
    print("[INFO] Scansione processi in corso...")
    processes = scan_processes()
    save_report(processes)
