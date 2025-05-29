import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import time
import csv
import os
import threading
from datetime import datetime, timedelta
from collections import defaultdict
import pystray
from PIL import Image
import io
import plyer

# Path for the CSV file in the same folder as the script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(BASE_DIR, exist_ok=True)
USAGE_REPORT = os.path.join(BASE_DIR, "usage_report.csv")

# Theme Presets
THEMES = {
    "Classic Dark": {"bg": "#1e1e1e", "fg": "#ffffff", "bar": "#00ffcc"},
    "Solarized Light": {"bg": "#fdf6e3", "fg": "#657b83", "bar": "#268bd2"},
    "Cool Blue": {"bg": "#001f3f", "fg": "#ffffff", "bar": "#0074D9"},
    "Matrix": {"bg": "#000000", "fg": "#00ff00", "bar": "#00ff00"},
    "Warm Sunset": {"bg": "#ffcccb", "fg": "#660000", "bar": "#ff4500"},
}
current_theme = "Classic Dark"

# Global state
running = True
gb_alert_count = 0
daily_data = 0
daily_data_reset = datetime.now().date()
five_gb_alerted = False
app_data = defaultdict(lambda: [0, 0, 0, 0])  # app: [last_sent, last_recv, delta_sent, delta_recv]
running_apps = set()
session_start_time = datetime.now()
start_sent = psutil.net_io_counters().bytes_sent
start_recv = psutil.net_io_counters().bytes_recv
last_sent = start_sent
last_recv = start_recv
daily_start_sent = start_sent
daily_start_recv = start_recv
app = None

# Load daily usage state from CSV on startup
def load_daily_state():
    global daily_data, daily_start_sent, daily_start_recv, daily_data_reset
    if os.path.exists(USAGE_REPORT):
        with open(USAGE_REPORT, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["Record Type"] == "DailyState":
                    daily_data = float(row["Total (MB)"]) / 1024  # Convert MB to GB
                    daily_start_sent = int(float(row["Upload (MB)"]) * (1024 ** 2))  # Convert MB to bytes
                    daily_start_recv = int(float(row["Download (MB)"]) * (1024 ** 2))  # Convert MB to bytes
                    daily_data_reset = datetime.strptime(row["Date"], "%Y-%m-%d").date()
                    break

# Save daily usage state to CSV
def save_daily_state():
    write_to_usage_report("DailyState", {
        "Record Type": "DailyState",
        "Date": str(daily_data_reset),
        "Time (system on)": "",
        "Time (system off)": "",
        "Upload (MB)": round(daily_start_sent / (1024 ** 2), 2),
        "Download (MB)": round(daily_start_recv / (1024 ** 2), 2),
        "Total (MB)": round(daily_data * 1024, 2),  # Convert GB to MB
        "Apps Used": "",
        "Application": "",
        "Month": ""
    })

# Estimate per-app usage (rough)
def estimate_app_usage():
    try:
        connections = psutil.net_connections(kind='inet')
        current_app_data = defaultdict(lambda: [0, 0])
        for conn in connections:
            try:
                pid = conn.pid
                if pid:
                    proc = psutil.Process(pid)
                    name = proc.name()
                    running_apps.add(name)
                    net = psutil.net_io_counters(pernic=False)
                    current_app_data[name][0] += net.bytes_sent
                    current_app_data[name][1] += net.bytes_recv
            except Exception:
                continue

        for app_name, (current_sent, current_recv) in current_app_data.items():
            last_sent, last_recv, delta_sent, delta_recv = app_data[app_name]
            delta_sent += max(0, current_sent - last_sent)
            delta_recv += max(0, current_recv - last_recv)
            app_data[app_name] = [current_sent, current_recv, delta_sent, delta_recv]
    except Exception:
        pass

# Write to the consolidated usage report
def write_to_usage_report(record_type, data):
    with open(USAGE_REPORT, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Record Type", "Date", "Time (system on)", "Time (system off)",
            "Upload (MB)", "Download (MB)", "Total (MB)", "Apps Used", "Application", "Month"
        ])
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow(data)

# Write session log
def write_session_log():
    end_time = datetime.now()
    end_sent = psutil.net_io_counters().bytes_sent
    end_recv = psutil.net_io_counters().bytes_recv
    total_sent = (end_sent - start_sent) / (1024 ** 2)
    total_recv = (end_recv - start_recv) / (1024 ** 2)

    write_to_usage_report("Session", {
        "Record Type": "Session",
        "Date": str(session_start_time.date()),
        "Time (system on)": session_start_time.strftime("%H:%M:%S"),
        "Time (system off)": end_time.strftime("%H:%M:%S"),
        "Upload (MB)": round(total_sent, 2),
        "Download (MB)": round(total_recv, 2),
        "Total (MB)": round(total_sent + total_recv, 2),
        "Apps Used": ', '.join(sorted(running_apps)),
        "Application": "",
        "Month": ""
    })

# Write app-level usage
def write_app_log():
    now = datetime.now()
    for app_name, data in app_data.items():
        write_to_usage_report("App", {
            "Record Type": "App",
            "Date": str(now.date()),
            "Time (system on)": "",
            "Time (system off)": "",
            "Upload (MB)": round(data[2] / (1024**2), 2),
            "Download (MB)": round(data[3] / (1024**2), 2),
            "Total (MB)": "",
            "Apps Used": "",
            "Application": app_name,
            "Month": ""
        })

# Generate monthly report
def generate_monthly_report():
    monthly_data = defaultdict(lambda: {"upload": 0, "download": 0})
    app_monthly_data = defaultdict(lambda: {"upload": 0, "download": 0})

    if os.path.exists(USAGE_REPORT):
        with open(USAGE_REPORT, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["Record Type"] == "Session":
                    date = datetime.strptime(row["Date"], "%Y-%m-%d").date()
                    if date.month == datetime.now().month and date.year == datetime.now().year:
                        month_key = f"{date.year}-{date.month}"
                        monthly_data[month_key]["upload"] += float(row["Upload (MB)"])
                        monthly_data[month_key]["download"] += float(row["Download (MB)"])
                elif row["Record Type"] == "App":
                    date = datetime.strptime(row["Date"], "%Y-%m-%d").date()
                    if date.month == datetime.now().month and date.year == datetime.now().year:
                        app_name = row["Application"]
                        app_monthly_data[app_name]["upload"] += float(row["Upload (MB)"])
                        app_monthly_data[app_name]["download"] += float(row["Download (MB)"])

    for month, data in monthly_data.items():
        write_to_usage_report("Monthly", {
            "Record Type": "Monthly",
            "Date": "",
            "Time (system on)": "",
            "Time (system off)": "",
            "Upload (MB)": round(data["upload"], 2),
            "Download (MB)": round(data["download"], 2),
            "Total (MB)": round(data["upload"] + data["download"], 2),
            "Apps Used": "",
            "Application": "",
            "Month": month
        })

    for app_name, data in app_monthly_data.items():
        write_to_usage_report("MonthlyApp", {
            "Record Type": "MonthlyApp",
            "Date": "",
            "Time (system on)": "",
            "Time (system off)": "",
            "Upload (MB)": round(data["upload"], 2),
            "Download (MB)": round(data["download"], 2),
            "Total (MB)": "",
            "Apps Used": "",
            "Application": app_name,
            "Month": f"{datetime.now().year}-{datetime.now().month}"
        })

# Background monitoring thread
def monitor():
    global gb_alert_count, daily_data, daily_data_reset, five_gb_alerted, last_sent, last_recv, daily_start_sent, daily_start_recv
    last_app_log_time = time.time()
    last_daily_save_time = time.time()

    while running:
        cpu_usage = psutil.cpu_percent(interval=None)
        sleep_time = 0.5 if cpu_usage < 80 else 1
        time.sleep(sleep_time)

        try:
            net = psutil.net_io_counters()
            current_sent = net.bytes_sent
            current_recv = net.bytes_recv
            down_rate = (current_recv - last_recv) / (1024 ** 2) / sleep_time
            up_rate = (current_sent - last_sent) / (1024 ** 2) / sleep_time
            last_sent = current_sent
            last_recv = current_recv

            estimate_app_usage()

            now = datetime.now()
            if now.date() != daily_data_reset:
                daily_start_sent = current_sent
                daily_start_recv = current_recv
                daily_data = 0
                daily_data_reset = now.date()
                five_gb_alerted = False
                save_daily_state()
                generate_monthly_report()

            total_used = (current_sent + current_recv - start_sent - start_recv) / (1024 ** 3)
            daily_data = (current_sent + current_recv - daily_start_sent - daily_start_recv) / (1024 ** 3)

            if int(total_used) > gb_alert_count:
                gb_alert_count += 1
                plyer.notification.notify(
                    title="Data Usage Alert",
                    message=f"You have used {gb_alert_count} GB of data!",
                    app_name="SysNetMonitor",
                    timeout=5
                )

            if daily_data >= 5 and not five_gb_alerted:
                plyer.notification.notify(
                    title="Daily Limit Warning",
                    message="You have used 5 GB today! Be mindful of your usage.",
                    app_name="SysNetMonitor",
                    timeout=5
                )
                five_gb_alerted = True

            # Save daily state every minute
            if time.time() - last_daily_save_time >= 60:
                save_daily_state()
                last_daily_save_time = time.time()

            # Log app usage every 5 minutes
            if time.time() - last_app_log_time >= 300:
                write_app_log()
                last_app_log_time = time.time()

            if app:
                app.update_usage(down_rate, up_rate, daily_data)

        except Exception:
            pass

# System Tray Setup
def create_tray_icon():
    image = Image.new('RGB', (64, 64), color='black')
    menu = (
        pystray.MenuItem("Show", lambda: show_window()),
        pystray.MenuItem("Exit", lambda: exit_app())
    )
    icon = pystray.Icon("SysNetMonitor", image, "SysNetMonitor", menu)
    return icon

def show_window():
    global app
    if app is None:
        app = DataMonitorApp()
        app.mainloop()

def exit_app():
    global running, app
    running = False
    write_app_log()
    write_session_log()
    save_daily_state()
    generate_monthly_report()
    if app:
        app.destroy()
    tray_icon.stop()

# GUI Application
class DataMonitorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SysNet Monitor")
        self.geometry("500x600")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.on_minimize)

        self.style = ttk.Style(self)
        self.theme_var = tk.StringVar(value=current_theme)

        self.download_var = tk.StringVar(value="Download: 0.00 MB/s")
        self.upload_var = tk.StringVar(value="Upload: 0.00 MB/s")
        self.daily_var = tk.StringVar(value="Daily Usage: 0.00 GB")
        self.cpu_var = tk.StringVar(value="CPU: 0.0%")
        self.ram_var = tk.StringVar(value="RAM: 0.0/0.0 GB")
        self.disk_var = tk.StringVar(value="Disk: 0.0%")
        self.uptime_var = tk.StringVar(value="Uptime: 00:00:00")
        self.hud_mode = tk.BooleanVar(value=False)

        self.create_widgets()
        self.apply_theme(current_theme)

    def create_widgets(self):
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.label_download = tk.Label(self.main_frame, textvariable=self.download_var, font=("Helvetica", 14, "bold"))
        self.label_download.pack(pady=5)
        self.label_upload = tk.Label(self.main_frame, textvariable=self.upload_var, font=("Helvetica", 14, "bold"))
        self.label_upload.pack(pady=5)
        self.label_daily = tk.Label(self.main_frame, textvariable=self.daily_var, font=("Helvetica", 14, "bold"))
        self.label_daily.pack(pady=5)

        self.separator1 = ttk.Separator(self.main_frame, orient="horizontal")
        self.separator1.pack(fill="x", pady=10)

        self.label_cpu = tk.Label(self.main_frame, textvariable=self.cpu_var, font=("Helvetica", 12))
        self.label_cpu.pack(pady=5)
        self.label_ram = tk.Label(self.main_frame, textvariable=self.ram_var, font=("Helvetica", 12))
        self.label_ram.pack(pady=5)
        self.label_disk = tk.Label(self.main_frame, textvariable=self.disk_var, font=("Helvetica", 12))
        self.label_disk.pack(pady=5)
        self.label_uptime = tk.Label(self.main_frame, textvariable=self.uptime_var, font=("Helvetica", 12))
        self.label_uptime.pack(pady=5)

        self.separator2 = ttk.Separator(self.main_frame, orient="horizontal")
        self.separator2.pack(fill="x", pady=10)

        self.label_theme = ttk.Label(self.main_frame, text="Select Theme:")
        self.label_theme.pack(pady=5)
        self.theme_menu = ttk.Combobox(self.main_frame, textvariable=self.theme_var, values=list(THEMES.keys()), state="readonly")
        self.theme_menu.pack()
        self.theme_menu.bind("<<ComboboxSelected>>", self.change_theme)

        self.hud_check = ttk.Checkbutton(self.main_frame, text="Enable HUD Mode (Always On Top)", variable=self.hud_mode, command=self.toggle_hud)
        self.hud_check.pack(pady=10)

        self.label_app_usage = tk.Label(self.main_frame, text="Top Data-Consuming Apps:", font=("Helvetica", 12, "bold"))
        self.label_app_usage.pack(pady=5)
        self.app_usage_text = tk.Text(self.main_frame, height=5, width=50, font=("Helvetica", 10))
        self.app_usage_text.pack()

    def apply_theme(self, theme_name):
        theme = THEMES[theme_name]
        self.configure(bg=theme["bg"])
        self.main_frame.configure(bg=theme["bg"])

        self.label_download.configure(bg=theme["bg"], fg=theme["fg"])
        self.label_upload.configure(bg=theme["bg"], fg=theme["fg"])
        self.label_daily.configure(bg=theme["bg"], fg=theme["fg"])
        self.label_cpu.configure(bg=theme["bg"], fg=theme["fg"])
        self.label_ram.configure(bg=theme["bg"], fg=theme["fg"])
        self.label_disk.configure(bg=theme["bg"], fg=theme["fg"])
        self.label_uptime.configure(bg=theme["bg"], fg=theme["fg"])
        self.label_app_usage.configure(bg=theme["bg"], fg=theme["fg"])
        self.app_usage_text.configure(bg=theme["bg"], fg=theme["fg"], insertbackground=theme["fg"])

        self.style.configure("TLabel", background=theme["bg"], foreground=theme["fg"])
        self.style.configure("TCombobox", fieldbackground=theme["bg"], background=theme["bg"], foreground=theme["fg"])
        self.style.map("TCombobox", fieldbackground=[("readonly", theme["bg"])], background=[("readonly", theme["bg"])], foreground=[("readonly", theme["fg"])])
        self.style.configure("TSeparator", background=theme["fg"])
        self.style.configure("TCheckbutton", background=theme["bg"], foreground=theme["fg"])

    def change_theme(self, event=None):
        selected_theme = self.theme_var.get()
        self.apply_theme(selected_theme)

    def toggle_hud(self):
        if self.hud_mode.get():
            self.attributes("-topmost", True)
            self.geometry("270x50")
            self.resizable(True, True)
        else:
            self.attributes("-topmost", False)
            self.geometry("500x600")
            self.resizable(False, False)

    def update_usage(self, down_rate, up_rate, daily_data):
        self.download_var.set(f"Download: {down_rate:.2f} MB/s")
        self.upload_var.set(f"Upload: {up_rate:.2f} MB/s")
        self.daily_var.set(f"Daily Usage: {daily_data:.2f} GB")

        try:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            uptime = timedelta(seconds=int(time.time() - psutil.boot_time()))
            self.cpu_var.set(f"CPU: {cpu:.1f}%")
            self.ram_var.set(f"RAM: {ram.used/(1024**3):.1f}/{ram.total/(1024**3):.1f} GB")
            self.disk_var.set(f"Disk: {disk.percent:.1f}%")
            self.uptime_var.set(f"Uptime: {str(uptime)}")

            self.app_usage_text.delete(1.0, tk.END)
            sorted_apps = sorted(app_data.items(), key=lambda x: x[1][2] + x[1][3], reverse=True)[:5]
            for app_name, data in sorted_apps:
                delta_sent_mb = data[2] / (1024**2)
                delta_recv_mb = data[3] / (1024**2)
                self.app_usage_text.insert(tk.END, f"{app_name}: {delta_sent_mb:.2f} MB up, {delta_recv_mb:.2f} MB down\n")
        except Exception:
            pass

    def on_minimize(self):
        global app
        self.withdraw()
        app = None

# Main execution
if __name__ == "__main__":
    load_daily_state()  # Load daily usage state on startup
    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()

    tray_icon = create_tray_icon()
    app = DataMonitorApp()
    tray_icon.run_detached()
    app.mainloop()

    running = False
    write_app_log()
    write_session_log()
    save_daily_state()
    generate_monthly_report()
    show_window()