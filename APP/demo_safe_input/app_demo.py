import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os
import html

# --- Configurazione cartelle ---
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs/demo_logs")
os.makedirs(LOG_DIR, exist_ok=True)

# --- Mappatura tasti speciali ---
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
        self.root.geometry("850x650")
        self.root.configure(bg="#1B1B2F")
        # Icona finestra (puoi sostituire con un file .ico a tua scelta)
        # self.root.iconbitmap("icon.ico")

        self.log = []

        # Text widget tipo Notepad
        self.text = tk.Text(root, bg="#1B1B2F", fg="#E0E0E0", insertbackground="#00C9A7",
                            font=("Consolas", 12), wrap=tk.WORD)
        self.text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.text.bind("<Key>", self.on_key_press)

        # Frame pulsanti
        button_frame = tk.Frame(root, bg="#1B1B2F")
        button_frame.pack(fill=tk.X, pady=(0,10))

        self.save_btn = tk.Button(button_frame, text="💾 Salva Log", command=self.save_log,
                                  bg="#00C9A7", fg="#1B1B2F", font=("Arial", 10, "bold"),
                                  relief=tk.FLAT, padx=10, pady=5)
        self.save_btn.pack(side=tk.LEFT, padx=10)

        self.clear_btn = tk.Button(button_frame, text="🧹 Cancella", command=self.clear_text,
                                   bg="#FF4C4C", fg="#1B1B2F", font=("Arial", 10, "bold"),
                                   relief=tk.FLAT, padx=10, pady=5)
        self.clear_btn.pack(side=tk.LEFT, padx=10)

        self.close_btn = tk.Button(button_frame, text="❌ Chiudi", command=self.on_close,
                           bg="#FFAA00", fg="#1B1B2F", font=("Arial", 10, "bold"),
                           relief=tk.FLAT, padx=10, pady=5)
        self.close_btn.pack(side=tk.LEFT, padx=10)


        # Firma in basso
        self.signature = tk.Label(root, text="- xFloppa", bg="#1B1B2F", fg="#00C9A7",
                                  font=("Arial", 10, "italic"))
        self.signature.pack(side=tk.BOTTOM, pady=5)

        # Salvataggio automatico alla chiusura
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_key_press(self, event):
        # Determina tasto speciale o normale
        if event.keysym in SPECIAL_KEYS:
            key = SPECIAL_KEYS[event.keysym]
            display = f"({key})"
        elif event.char and event.char.isprintable():
            key = event.char
            display = key
        else:
            return "break"  # Blocca tasti non stampabili

        # Inserisci solo display
        self.text.insert(tk.END, display)
        self.text.see(tk.END)

        # Registra con timestamp
        timestamp = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        self.log.append({'time': timestamp, 'key': key})

        return "break"  # Impedisce al Text widget di inserire automaticamente il carattere

    def save_log(self):
        if not self.log:
            messagebox.showinfo("Info", "Nessun tasto da salvare!")
            return

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

        messagebox.showinfo("Info", f"Log salvato in {filepath}")
        print(f"[INFO] Log salvato in {filepath}")

    def clear_text(self):
        self.text.delete("1.0", tk.END)

    def on_close(self):
        # Salva automaticamente prima di chiudere
        #if self.log:
        #   self.save_log()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = KeyLoggerDemo(root)
    root.mainloop()
