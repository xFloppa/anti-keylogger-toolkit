import tkinter as tk
from datetime import datetime
import os
import html

LOG_DIR = os.path.join(os.path.dirname(__file__), "../logs/demo_logs")
os.makedirs(LOG_DIR, exist_ok=True)

class KeyLoggerDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Demo Sicura Keylogger (solo finestra)")
        self.text = tk.Text(root, width=60, height=20)
        self.text.pack()
        self.log = []
        self.root.bind("<Key>", self.on_key_press)
        self.save_btn = tk.Button(root, text="Salva Log HTML", command=self.save_log)
        self.save_btn.pack(pady=5)

    def on_key_press(self, event):
        # Salta tasti non stampabili
        if event.char and event.char.isprintable():
            key = event.char
            self.log.append({'time': datetime.now().isoformat(), 'key': key})
            self.text.insert(tk.END, key)

    def save_log(self):
        filename = f"demo_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(LOG_DIR, filename)
        html_content = "<html><head><title>Demo Keylogger Log</title></head><body>"
        html_content += "<h2>Demo Keylogger Log</h2><table border='1'><tr><th>Time</th><th>Key</th></tr>"
        for entry in self.log:
            html_content += f"<tr><td>{html.escape(entry['time'])}</td><td>{html.escape(entry['key'])}</td></tr>"
        html_content += "</table></body></html>"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"[INFO] Log salvato in {filepath}")

if __name__ == "__main__":
    root = tk.Tk()
    app = KeyLoggerDemo(root)
    root.mainloop()
# APP/demo_safe_input/app_demo.py