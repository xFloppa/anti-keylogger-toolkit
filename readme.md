# 🛡️ Anti-Keylogger Toolkit

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Contributions welcome](https://img.shields.io/badge/Contributions-welcome-orange.svg)](../../issues)

Toolkit didattico in **Python** per:
- Dimostrare come funziona un *keylogger* **sicuro e controllato** (solo dentro una finestra).
- Creare strumenti di difesa che analizzano processi e comportamenti sospetti.
- Sperimentare con tecniche di **cybersecurity difensiva** in modo etico e legale.

---

## ✨ Features
- ✅ **Demo sicura keylogger**: finestra dedicata che registra input solo all’interno della propria GUI.
- ✅ **Scanner processi attivi**: elenco di tutti i processi in esecuzione con PID e percorso.
- 🔜 **Generazione report HTML/JSON** con i risultati delle scansioni.
- 🔜 **Rilevamento persistenze sospette** (Run keys, Scheduled Tasks, WMI).
- 🔜 **Monitor in tempo reale** di nuove attività sospette.

---

## 📂 Struttura del progetto
```
anti-keylogger-toolkit/
├── README.md # Documentazione principale
├── LICENSE # Licenza MIT
├── requirements.txt # Dipendenze Python
├── .gitignore # File per ignorare cartelle/files locali
├── demo_safe_input/ # Demo sicura di keylogger interno
│ └── app_demo.py # Finestra Tkinter che registra input solo nella GUI
├── scanner/ # Scanner processi e tool difensivi
│ └── scan_processes.py # Script di scansione dei processi attivi
├── tests/ # Test del progetto
│ └── test_scanner.py # Test per scanner
└── docs/ # Documentazione extra
└── architecture.md # Architettura e spiegazioni tecniche
```

---

## 🚀 Uso
1. Clona la repo:
   ```bash
   git clone https://github.com/xFloppa/anti-keylogger-toolkit.git
   cd anti-keylogger-toolkit
   pip install -r requirements.txt
   python demo_safe_input/app_demo.py
   python scanner/scan_processes.py
   ```
2. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   python demo_safe_input/app_demo.py
   python scanner/scan_processes.py
   ```
3. Avvia la demo keylogger (sicuro):
   ```bash
   python demo_safe_input/app_demo.py
   python scanner/scan_processes.py
   ```
3. Scansiona i processi::
   ```bash
   python scanner/scan_processes.py
   ```

## ⚖️ Disclaimer
Questo progetto è puramente didattico e difensivo.
Non intercetta input globali, non gira in background e non ha scopi malevoli.
Utilizzare solo su macchine di test o con consenso esplicito.

## 📄 Licenza
Distribuito sotto MIT License.
