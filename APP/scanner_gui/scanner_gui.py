import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import psutil
import os
import time
import datetime
import hashlib
import threading
from scanner_core import analyze_processes

# Lista IOC di esempio
IOC_LIST = [
    {"name": "keylogger.exe", "path": "", "hash": ""}
]

# Colori
BG_COLOR = "#1B1B2F"
TEXT_COLOR = "#E0E0E0"
BUTTON_GREEN = "#00C9A7"
BUTTON_RED = "#B22222"
BUTTON_GOLD = "#FFD700"

class ScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Anti-Keylogger Scanner")
        self.root.geometry("1000x600")
        self.root.configure(bg=BG_COLOR)

        # --- Dark theme Treeview ---
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background=BG_COLOR,
                        foreground=TEXT_COLOR,
                        rowheight=25,
                        fieldbackground=BG_COLOR,
                        font=("Arial", 10))
        style.map("Treeview",
                  background=[("selected", "#00C9A7")],
                  foreground=[("selected", BG_COLOR)])
        style.configure("Treeview.Heading",
                        background="#162447",
                        foreground="#00C9A7",
                        font=("Arial", 10, "bold"))

        self.process_list = []
        self.filtered_list = []

        # --- Frame pulsanti ---
        self.button_frame = tk.Frame(root, bg=BG_COLOR)
        self.button_frame.pack(fill=tk.X, pady=5, padx=5)

        self.scan_btn = tk.Button(self.button_frame, text="🖥️ Scan Processes", bg=BUTTON_GREEN,
                                  fg=BG_COLOR, font=("Arial", 10, "bold"), command=self.scan_processes)
        self.scan_btn.pack(side=tk.LEFT, padx=5)

        self.save_btn = tk.Button(self.button_frame, text="💾 Salva Report", bg=BUTTON_GREEN,
                                  fg=BG_COLOR, font=("Arial", 10, "bold"), command=self.save_report)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.filter_btn = tk.Menubutton(self.button_frame, text="🔍 Filtra", bg=BUTTON_GOLD,
                                        fg=BG_COLOR, font=("Arial", 10, "bold"), relief=tk.RAISED)
        self.filter_menu = tk.Menu(self.filter_btn, tearoff=0)
        self.filter_menu.add_command(label="TUTTO", command=lambda: self.apply_filter("TUTTO"))
        self.filter_menu.add_command(label="SUSPICIOUS", command=lambda: self.apply_filter("SUSPICIOUS"))
        self.filter_menu.add_command(label="NON SUSPICIOUS", command=lambda: self.apply_filter("NON SUSPICIOUS"))
        self.filter_btn.config(menu=self.filter_menu)
        self.filter_btn.pack(side=tk.LEFT, padx=5)

        # --- Barra ricerca ---
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.button_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.RIGHT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.update_search)

        # --- Treeview ---
        columns = ("PID", "Name", "CPU%", "Risk", "Suspicious")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150 if col=="Name" else 80, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree.bind("<Double-1>", self.show_properties)
        self.tree.bind("<Button-3>", self.on_right_click)

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.tree, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # --- Metodo per tasto destro ---
    def on_right_click(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            menu = tk.Menu(self.root, tearoff=0, bg=BG_COLOR, fg=TEXT_COLOR)
            menu.add_command(label="💾 Salva report processo", command=lambda: self.save_single_process(row_id))
            menu.add_command(label="ℹ️ Properties", command=lambda: self.show_properties(event=None, row_id=row_id))
            menu.tk_popup(event.x_root, event.y_root)

    # --- Metodo per salvare singolo processo ---
    def save_single_process(self, row_id):
        item = self.tree.item(row_id)
        values = item['values']
        process = next((p for p in self.process_list if p['pid']==values[0]), None)

        if not process:
            return

        file_path = filedialog.asksaveasfilename(title="Salva report processo",
                                                 defaultextension=".txt",
                                                 filetypes=[("Text file", "*.txt"), ("HTML file", "*.html")])
        if not file_path:
            return

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"Process Report\n")
            f.write(f"PID: {process['pid']}\n")
            f.write(f"Name: {process['name']}\n")
            f.write(f"CPU%: {process['cpu']}\n")
            f.write(f"Risk: {process['risk_score']}\n")
            f.write(f"Suspicious: {process['suspicious']}\n")
            f.write(f"Path: {process.get('path','N/A')}\n")
            f.write(f"Created: {process.get('created','N/A')}\n")
            f.write(f"Modified: {process.get('modified','N/A')}\n")
            f.write(f"File size: {process.get('size','N/A')} bytes\n")
            f.write(f"SHA256: {process.get('sha256','N/A')}\n")
            f.write(f"Run count: {process.get('run_count','N/A')}\n")
            f.write(f"Last run: {process.get('last_run','N/A')}\n")

        tk.messagebox.showinfo("Salvato", f"Report salvato in {file_path}")

    # --- Scan processes ---
    def scan_processes(self):
        def worker():
            self.process_list = analyze_processes(IOC_LIST)
            self.filtered_list = self.process_list.copy()
            self.populate_tree(self.filtered_list)
            loading.destroy()  # chiude animazione quando finisce

        # Finestra caricamento
        loading = tk.Toplevel(self.root)
        loading.title("Caricamento...")
        loading.configure(bg=BG_COLOR)
        loading.geometry("250x100")
        loading.resizable(False, False)
        loading.transient(self.root)
        loading.grab_set()  # impedisce chiusura
        loading.update_idletasks()

        # Centra la finestra sullo schermo
        x = (loading.winfo_screenwidth() // 2) - (loading.winfo_reqwidth() // 2)
        y = (loading.winfo_screenheight() // 2) - (loading.winfo_reqheight() // 2)
        loading.geometry(f"+{x}+{y}")

        label = tk.Label(loading, text="Caricamento...", bg=BG_COLOR, fg=TEXT_COLOR, font=("Arial", 12, "bold"))
        label.pack(expand=True)

        anim_label = tk.Label(loading, text="", bg=BG_COLOR, fg=TEXT_COLOR, font=("Arial", 14, "bold"))
        anim_label.pack()

        def animate():
            chars = "/-\\|"
            i = 0
            while True:
                if not loading.winfo_exists():
                    break
                anim_label.config(text=chars[i % len(chars)])
                i += 1
                time.sleep(0.2)

        t_anim = threading.Thread(target=animate, daemon=True)
        t_anim.start()

        t_worker = threading.Thread(target=worker)
        t_worker.start()


    # --- Popola tree ---
    def populate_tree(self, plist):
        self.tree.delete(*self.tree.get_children())
        for p in plist:
            risk = p['risk_score']
            susp = "Yes" if p['suspicious'] else "No"
            self.tree.insert("", tk.END, values=(p['pid'], p['name'], p['cpu'], risk, susp))

    # --- Filtro ---
    def apply_filter(self, mode):
        if mode=="TUTTO":
            self.filtered_list = self.process_list.copy()
        elif mode=="SUSPICIOUS":
            self.filtered_list = [p for p in self.process_list if p['suspicious'] or p['very_suspicious']]
        elif mode=="NON SUSPICIOUS":
            self.filtered_list = [p for p in self.process_list if not (p['suspicious'] or p['very_suspicious'])]
        self.populate_tree(self.filtered_list)

    # --- Ricerca live ---
    def update_search(self, event=None):
        query = self.search_var.get().lower()
        if not query:
            self.filtered_list = self.process_list.copy()
        else:
            self.filtered_list = [p for p in self.process_list if query in p['name'].lower()]
        self.populate_tree(self.filtered_list)

    # --- Popup Properties ---
    # --- All'interno di show_properties ---
    def show_properties(self, event=None, row_id=None):
        if row_id is None:
            selected = self.tree.selection()
            if not selected:
                return
            row_id = selected[0]

        item = self.tree.item(row_id)
        values = item['values']
        pid = int(values[0])
        process = next((p for p in self.process_list if p['pid'] == pid), None)
        if not process:
            return

        popup = tk.Toplevel(self.root)
        popup.title(f"Properties: {process['name']}")
        popup.configure(bg=BG_COLOR)
        popup.geometry("600x450")
        popup.resizable(True, True)

        main_frame = tk.Frame(popup, bg=BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        info_text = f"""
    PID: {process['pid']}
    Name: {process['name']}
    Path: {process.get('path', 'N/A')}
    Created: {process.get('created', 'N/A')}
    Modified: {process.get('modified', 'N/A')}
    File size: {process.get('size', 'N/A')} bytes
    Run count: {process.get('run_count', 'N/A')}
    Last run: {process.get('last_run', 'N/A')}
    Suspicious: {"Yes" if process.get('suspicious') else "No"}
    """

        # Text widget scrollabile per info
        text_widget = tk.Text(main_frame, wrap=tk.NONE, bg=BG_COLOR, fg=TEXT_COLOR, font=("Consolas", 10))
        text_widget.insert(tk.END, info_text)
        text_widget.config(state="disabled")
        text_widget.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)

        # Frame bottoni
        btn_frame = tk.Frame(popup, bg=BG_COLOR)
        btn_frame.pack(fill=tk.X, pady=5)

        ok_btn = tk.Button(btn_frame, text="OK", command=popup.destroy,
                        bg=BUTTON_GREEN, fg=BG_COLOR, font=("Arial", 10, "bold"))
        ok_btn.pack(side=tk.RIGHT, padx=5)

        # Bottone SHA256 -> apre popup separato
        def open_sha_popup():
            sha_win = tk.Toplevel(self.root)
            sha_win.title(f"SHA256 - {process['name']}")
            sha_win.configure(bg=BG_COLOR)
            sha_win.geometry("600x150")
            sha_win.resizable(True, False)
            sha_win.grab_set()

            sha_text = tk.Text(sha_win, wrap=tk.NONE, bg=BG_COLOR, fg=TEXT_COLOR, font=("Consolas", 10))
            sha_text.insert(tk.END, process.get('sha256','N/A'))
            sha_text.config(state="disabled")
            sha_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            scrollbar = ttk.Scrollbar(sha_win, orient=tk.VERTICAL, command=sha_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            sha_text.config(yscrollcommand=scrollbar.set)

            btn_frame_sha = tk.Frame(sha_win, bg=BG_COLOR)
            btn_frame_sha.pack(fill=tk.X, pady=5)

            def copy_sha():
                self.root.clipboard_clear()
                self.root.clipboard_append(process.get('sha256',''))
                messagebox.showinfo("Copied", "SHA256 copiato negli appunti!")

            copy_btn = tk.Button(btn_frame_sha, text="Copia SHA", command=copy_sha,
                                bg=BUTTON_GREEN, fg=BG_COLOR)
            copy_btn.pack(side=tk.RIGHT, padx=5)
            ok_btn_sha = tk.Button(btn_frame_sha, text="OK", command=sha_win.destroy,
                                bg=BUTTON_GREEN, fg=BG_COLOR)
            ok_btn_sha.pack(side=tk.RIGHT, padx=5)

        sha_btn = tk.Button(btn_frame, text="SHA256", command=open_sha_popup,
                            bg=BUTTON_GOLD, fg=BG_COLOR, font=("Arial", 10, "bold"))
        sha_btn.pack(side=tk.RIGHT, padx=5)



    # --- Salva report HTML ---
    def save_report(self):
        if not self.filtered_list:
            messagebox.showinfo("Info", "Nessun processo da salvare!")
            return
        log_dir = os.path.join(os.path.dirname(__file__), "logs/process_reports")
        os.makedirs(log_dir, exist_ok=True)
        filename = f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(log_dir, filename)
        html_content = "<html><head><style>body{background-color:#1B1B2F;color:#E0E0E0;font-family:Arial;} table{width:100%;border-collapse:collapse;} th, td{border:1px solid #444;padding:5px;text-align:left;} th{background-color:#162447;color:#00C9A7;} tr:nth-child(even){background-color:#1F4068;} tr:nth-child(odd){background-color:#1B1B2F;}</style></head><body>"
        html_content += "<h2>Process Scan Report</h2><table><tr><th>PID</th><th>Name</th><th>CPU%</th><th>Risk</th><th>Suspicious</th></tr>"
        for p in self.filtered_list:
            susp = "Yes" if p['suspicious'] else "No"
            html_content += f"<tr><td>{p['pid']}</td><td>{p['name']}</td><td>{p['cpu']}</td><td>{p['risk_score']}</td><td>{susp}</td></tr>"
        html_content += "</table></body></html>"
        with open(filepath,"w",encoding="utf-8") as f:
            f.write(html_content)
        messagebox.showinfo("Info", f"Report salvato in {filepath}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScannerGUI(root)
    root.mainloop()
