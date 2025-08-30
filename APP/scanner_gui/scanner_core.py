import psutil
import hashlib
import os
import time

SESSION_TRACKER = {}  # Tiene run_count e last_run per PID

def hash_file(path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""

WHITELIST = ["System", "svchost.exe", "explorer.exe", "python.exe", "pythonw.exe"]

def analyze_processes(ioc_list):
    processes_info = []
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cpu_percent', 'create_time']):
        try:
            pid = proc.info['pid']
            name = proc.info['name'] or ""
            path = proc.info['exe'] or ""
            cpu = proc.info['cpu_percent'] or 0

            # Aggiorna run_count / last_run in sessione
            now = time.strftime("%d/%m/%Y %H:%M:%S")
            if pid in SESSION_TRACKER:
                SESSION_TRACKER[pid]['run_count'] += 1
                SESSION_TRACKER[pid]['last_run'] = now
            else:
                SESSION_TRACKER[pid] = {'run_count': 1, 'last_run': now}

            # File info
            try:
                created = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(proc.info['create_time'])) if proc.info.get('create_time') else 'N/A'
            except Exception:
                created = 'N/A'
            try:
                modified = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(os.path.getmtime(path))) if os.path.exists(path) else 'N/A'
            except Exception:
                modified = 'N/A'
            try:
                size = os.path.getsize(path) if os.path.exists(path) else 'N/A'
            except Exception:
                size = 'N/A'
            sha256 = hash_file(path) if path else 'N/A'

            # Analisi rischio
            risk_score = 0
            suspicious = False
            very_suspicious = False

            if name not in WHITELIST:
                for ioc in ioc_list:
                    if 'name' in ioc and ioc['name'].lower() in name.lower():
                        risk_score += 50
                        very_suspicious = True
                    if 'path' in ioc and ioc['path'].lower() in path.lower():
                        risk_score += 30
                        very_suspicious = True
                    if 'hash' in ioc and path and sha256 == ioc['hash']:
                        risk_score += 100
                        very_suspicious = True

                if cpu > 20:
                    risk_score += 10
                    suspicious = True

            processes_info.append({
                'pid': pid,
                'name': name,
                'path': path,
                'cpu': cpu,
                'created': created,
                'modified': modified,
                'size': size,
                'sha256': sha256,
                'run_count': SESSION_TRACKER[pid]['run_count'],
                'last_run': SESSION_TRACKER[pid]['last_run'],
                'risk_score': risk_score,
                'suspicious': suspicious,
                'very_suspicious': very_suspicious
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes_info
