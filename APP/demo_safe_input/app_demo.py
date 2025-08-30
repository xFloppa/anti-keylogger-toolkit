import tkinter as tk
from datetime import datetime
import os
import html

LOG_DIR = os.path.join(os.path.dirname(__file__), "../logs/demo_logs")
os.makedirs(LOG_DIR, exist_ok=True)

SPECIAL_KEYS = {
    "Control_L": "Ctrl", "Control_R": "Ctrl",
    "Shift_L": "Shift", "Shift_R": "Shift",
    "Alt_L": "Alt", "Alt_R": "Alt",
    "BackSpace": "Backspace", "Return": "Enter",
    "Tab": "Tab", "Escape": "Esc"
}

class KeyLoggerDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Demo Sicura Keylogger")
        self.text = tk.Text(root, width=60, height=20)
        self.text.pack()
        self.log = []
        self.root.bind("<Key>", self.on_key_press)
        self.save_btn = tk.Button(root, text="Salva Log HTML", command=self.save_log)
        self.save_btn.pack(pady=5)

    def on_key_press(self, event):
        # Determina se è tasto speciale o normale
        if event.keysym in SPECIAL_KEYS:
            key = SPECIAL_KEYS[event.keysym]
            display = f"({key})"
        elif event.char and event.char.isprintable():
            key = event.char
            display = key
        else:
            return  # ignora tasti non stampabili

        # Inserisci nella finestra solo la rappresentazione visuale
        self.text.insert(tk.END, display)
        self.text.see(tk.END)

        # Registra nel log con timestamp
        timestamp = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        self.log.append({'time': timestamp, 'key': key})

    def save_log(self):
        filename = f"demo_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(LOG_DIR, filename)

        html_content = """
        <html>
        <head>
            <title>Demo Keylogger Log</title>
            <style>
                body { font-family: Arial, sans-serif; background-color: #1B1B2F; color: #E0E0E0; padding: 20px; }
                h2 { color: #00C9A7; }
                table { border-collapse: collapse; width: 100%; margin-top: 20px; }
                th, td { border: 1px solid #444; padding: 8px; text-align: left; }
                th { background-color: #162447; color: #00C9A7; }
                tr:nth-child(even) { background-color: #1F4068; }
                tr:nth-child(odd) { background-color: #1B1B2F; }
            </style>
        </head>
        <body>
            <h2>Demo Keylogger Log</h2>
            <table>
                <tr><th>Time</th><th>Key</th></tr>
        """

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
