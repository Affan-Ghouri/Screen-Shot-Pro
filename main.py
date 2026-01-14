import os
import json
import asyncio
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import uuid
from tkinter import ttk, messagebox
from calendar import Calendar as TkCalendar
from datetime import date

import customtkinter as ctk 
from PIL import Image
from playwright.async_api import async_playwright
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

COLORS = {
    "primary": "#1a5fb4",
    "secondary": "#3584e4",
    "accent": "#e01b24",
    "success": "#26a269",
    "warning": "#e5a50a",
    "bg_card": "#2d2d2d",
    "bg_card_light": "#383838",
    "text_primary": "#ffffff",
    "text_secondary": "#cccccc",
}


@dataclass
class ScreenshotTask:
    id: str
    url: str
    cron_schedule: str
    output_path: str
    width: int = 1920
    height: int = 1080
    full_page: bool = True
    enabled: bool = True
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ScreenshotTask':
        return cls(**data)


class ConfigManager:
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_dir = Path.home() / ".screenshot_app"
            config_dir.mkdir(exist_ok=True)
            config_path = config_dir / "config.json"
        
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return self.get_default_config()
    
    def get_default_config(self) -> dict:
        output_dir = Path.home() / "Documents" / "Screenshots"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        return {
            "tasks": [],
            "dark_mode": True,
            "output_directory": str(output_dir),
            "default_width": 1920,
            "default_height": 1080,
            "window_width": 1280,
            "window_height": 720
        }
    
    def save_config(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_tasks(self) -> List[ScreenshotTask]:
        return [ScreenshotTask.from_dict(t) for t in self.config.get("tasks", [])]
    
    def add_task(self, task: ScreenshotTask):
        tasks = self.get_tasks()
        tasks.append(task)
        self.config["tasks"] = [t.to_dict() for t in tasks]
        self.save_config()
    
    def remove_task(self, task_id: str):
        tasks = self.get_tasks()
        tasks = [t for t in tasks if t.id != task_id]
        self.config["tasks"] = [t.to_dict() for t in tasks]
        self.save_config()
    
    def update_task(self, task: ScreenshotTask):
        tasks = self.get_tasks()
        for i, t in enumerate(tasks):
            if t.id == task.id:
                tasks[i] = task
                break
        self.config["tasks"] = [t.to_dict() for t in tasks]
        self.save_config()


class ScreenshotCapture:
    def __init__(self):
        self._capture_lock = threading.Lock()
    
    async def capture(self, task: ScreenshotTask) -> bool:
        playwright = None
        browser = None
        page = None
        try:
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.set_viewport_size({"width": task.width, "height": task.height})
            
            print(f"Capturing: {task.url}")
            await page.goto(task.url, wait_until="networkidle", timeout=30000)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{task.id}_{timestamp}.png"
            output_file = Path(task.output_path) / filename
            
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            await page.screenshot(
                path=str(output_file),
                full_page=task.full_page
            )
            
            print(f"Saved: {output_file}")
            return True
            
        except Exception as e:
            print(f"Error capturing {task.url}: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if page:
                try:
                    await page.close()
                except:
                    pass
            if browser:
                try:
                    await browser.close()
                except:
                    pass
            if playwright:
                try:
                    await playwright.stop()
                except:
                    pass
    
    def close(self):
        pass


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.config_manager = ConfigManager()
        self.capture = ScreenshotCapture()
        self.scheduler = BackgroundScheduler()
        
        self.init_ui()
        self.schedule_option.set("Every Hour")
        self.update_cron_preview()
        self.load_saved_config()
        self.load_scheduled_tasks()
        self.scheduler.start()
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        print("Application started")
    
    def init_ui(self):
        self.title("Screenshot Scheduler Pro")
        self.geometry(f"1400x800+100+100")
        self.minsize(1000, 700)
        self.resizable(True, True)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.main_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"])
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        self.create_header()
        self.create_tab_view()
        self.create_status_bar()
    
    def create_header(self):
        header_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color=COLORS["primary"],
            corner_radius=12
        )
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_frame.grid_columnconfigure(1, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📸 Screenshot Scheduler Pro",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        title_label.grid(row=0, column=0, padx=20, pady=15)
        
        dark_mode_btn = ctk.CTkButton(
            header_frame,
            text="🌙",
            width=50,
            height=35,
            fg_color=COLORS["bg_card_light"],
            hover_color=COLORS["bg_card"],
            text_color=COLORS["text_primary"],
            corner_radius=8,
            command=self.toggle_dark_mode
        )
        dark_mode_btn.grid(row=0, column=2, padx=20, pady=15)
    
    def create_tab_view(self):
        self.tab_view = ctk.CTkTabview(
            self.main_frame, 
            fg_color=COLORS["bg_card"],
            segmented_button_fg_color=COLORS["bg_card_light"],
            segmented_button_selected_color=COLORS["primary"],
            segmented_button_selected_hover_color=COLORS["secondary"],
            segmented_button_unselected_color=COLORS["bg_card"],
            segmented_button_unselected_hover_color=COLORS["bg_card_light"]
        )
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self.tab_view.add("Dashboard")
        self.tab_view.add("Tasks")
        self.tab_view.add("Settings")
        
        self.create_dashboard_tab()
        self.create_tasks_tab()
        self.create_settings_tab()
    
    def create_dashboard_tab(self):
        tab = self.tab_view.tab("Dashboard")
        tab.configure(fg_color="transparent")
        
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        stats_frame = ctk.CTkFrame(
            tab, 
            fg_color=COLORS["bg_card_light"],
            corner_radius=10
        )
        stats_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15), padx=10)
        
        self.total_tasks_label = ctk.CTkLabel(
            stats_frame,
            text="📊 Total Tasks: 0",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.total_tasks_label.pack(side="left", padx=25, pady=15)
        
        scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll_frame.grid(row=1, column=0, sticky="nsew", padx=10)
        
        self.dashboard_tasks_frame = scroll_frame
    
    def create_tasks_tab(self):
        tab = self.tab_view.tab("Tasks")
        tab.configure(fg_color="transparent")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        left_scroll = ctk.CTkScrollableFrame(
            tab, 
            width=400,
            label_text=""
        )
        left_scroll.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        left_frame = ctk.CTkFrame(
            left_scroll, 
            fg_color=COLORS["bg_card_light"],
            corner_radius=12
        )
        left_frame.pack(fill="both", expand=True, pady=5)
        
        ctk.CTkLabel(
            left_frame,
            text="✨ Add New Task",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=20)
        
        ctk.CTkLabel(
            left_frame, 
            text="URL:", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(10, 5))
        self.url_entry = ctk.CTkEntry(
            left_frame, 
            placeholder_text="https://example.com",
            height=40,
            corner_radius=8,
            border_color=COLORS["primary"],
            placeholder_text_color=COLORS["text_secondary"]
        )
        self.url_entry.pack(fill="x", padx=20)
        
        ctk.CTkLabel(
            left_frame, 
            text="Schedule:", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(20, 5))
        
        schedule_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        schedule_frame.pack(fill="x", padx=20, pady=5)
        
        self.schedule_option = ctk.CTkOptionMenu(
            schedule_frame,
            values=["Every Minute", "Every Hour", "Daily", "Weekly", "Custom"],
            command=self.on_schedule_change,
            height=40,
            corner_radius=8,
            fg_color=COLORS["bg_card"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["secondary"],
            dropdown_fg_color=COLORS["bg_card"]
        )
        self.schedule_option.pack(fill="x", padx=5, pady=5)
        self.schedule_option.set("Every Hour")
        
        self.custom_schedule_frame = ctk.CTkFrame(
            left_frame, 
            fg_color=COLORS["bg_card"],
            corner_radius=8
        )
        
        date_time_frame = ctk.CTkFrame(self.custom_schedule_frame, fg_color="transparent")
        date_time_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            date_time_frame, 
            text="Date:", 
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=5)
        self.date_entry = ctk.CTkEntry(
            date_time_frame, 
            width=100,
            placeholder_text="YYYY-MM-DD",
            height=35,
            corner_radius=6
        )
        self.date_entry.pack(side="left", padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        date_btn = ctk.CTkButton(
            date_time_frame,
            text="📅",
            width=40,
            height=35,
            corner_radius=6,
            fg_color=COLORS["secondary"],
            hover_color=COLORS["primary"],
            command=self.open_calendar
        )
        date_btn.pack(side="left", padx=5)
         
        time_frame = ctk.CTkFrame(self.custom_schedule_frame, fg_color="transparent")
        time_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        ctk.CTkLabel(
            time_frame, 
            text="Hour:", 
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=5)
        self.hour_spinbox = ctk.CTkOptionMenu(
            time_frame,
            values=[f"{i:02d}" for i in range(24)],
            width=80,
            height=35,
            corner_radius=6,
            fg_color=COLORS["bg_card_light"],
            button_color=COLORS["bg_card_light"],
            button_hover_color=COLORS["primary"],
            dropdown_fg_color=COLORS["bg_card"]
        )
        self.hour_spinbox.pack(side="left", padx=5)
        self.hour_spinbox.set("00")
        self.hour_spinbox.configure(command=lambda v: self.update_cron_preview())
        
        ctk.CTkLabel(
            time_frame, 
            text="Minute:", 
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=5)
        self.minute_spinbox = ctk.CTkOptionMenu(
            time_frame,
            values=[f"{i:02d}" for i in range(60)],
            width=80,
            height=35,
            corner_radius=6,
            fg_color=COLORS["bg_card_light"],
            button_color=COLORS["bg_card_light"],
            button_hover_color=COLORS["primary"],
            dropdown_fg_color=COLORS["bg_card"]
        )
        self.minute_spinbox.pack(side="left", padx=5)
        self.minute_spinbox.set("00")
        self.minute_spinbox.configure(command=lambda v: self.update_cron_preview())
        
        self.cron_preview_label = ctk.CTkLabel(
            left_frame,
            text="⏰ Cron: 0 * * * *",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        )
        self.cron_preview_label.pack(pady=10)
        
        dimensions_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        dimensions_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            dimensions_frame, 
            text="W:", 
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=5)
        self.width_entry = ctk.CTkEntry(
            dimensions_frame, 
            width=100,
            height=35,
            corner_radius=6
        )
        self.width_entry.pack(side="left", padx=5)
        self.width_entry.insert(0, "1920")
        
        ctk.CTkLabel(
            dimensions_frame, 
            text="H:", 
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=5)
        self.height_entry = ctk.CTkEntry(
            dimensions_frame, 
            width=100,
            height=35,
            corner_radius=6
        )
        self.height_entry.pack(side="left", padx=5)
        self.height_entry.insert(0, "1080")
        
        self.full_page_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            left_frame,
            text="📄 Full Page Screenshot",
            variable=self.full_page_var,
            corner_radius=6,
            border_color=COLORS["primary"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["secondary"]
        ).pack(pady=10)
        
        add_btn = ctk.CTkButton(
            left_frame,
            text="➕ Add Task",
            command=self.add_task,
            height=45,
            corner_radius=8,
            fg_color=COLORS["success"],
            hover_color="#2ea070",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        add_btn.pack(pady=20, padx=20, fill="x")
        
        right_frame = ctk.CTkFrame(
            tab, 
            fg_color=COLORS["bg_card_light"],
            corner_radius=12
        )
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        ctk.CTkLabel(
            right_frame,
            text="📋 Existing Tasks",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=20)
        
        self.tasks_list_frame = ctk.CTkScrollableFrame(
            right_frame, 
            fg_color="transparent"
        )
        self.tasks_list_frame.pack(fill="both", expand=True, padx=15, pady=10)
    
    def create_settings_tab(self):
        tab = self.tab_view.tab("Settings")
        tab.configure(fg_color="transparent")
        
        tab.grid_columnconfigure(0, weight=1)
        
        settings_frame = ctk.CTkFrame(
            tab, 
            fg_color=COLORS["bg_card_light"],
            corner_radius=12
        )
        settings_frame.grid(row=0, column=0, sticky="ew", pady=10, padx=20)
        
        ctk.CTkLabel(
            settings_frame,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=20)
        
        ctk.CTkLabel(
            settings_frame, 
            text="Output Directory:", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(15, 5))
        self.output_path_entry = ctk.CTkEntry(
            settings_frame,
            height=40,
            corner_radius=8,
            border_color=COLORS["primary"],
            placeholder_text_color=COLORS["text_secondary"]
        )
        self.output_path_entry.pack(fill="x", padx=20, pady=5)
        
        path_btn_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        path_btn_frame.pack(pady=15)
        
        ctk.CTkButton(
            path_btn_frame,
            text="📁 Browse...",
            command=self.browse_output_dir,
            width=120,
            height=40,
            fg_color=COLORS["secondary"],
            hover_color=COLORS["primary"],
            corner_radius=8
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            path_btn_frame,
            text="💾 Save Settings",
            command=self.save_settings,
            width=140,
            height=40,
            fg_color=COLORS["success"],
            hover_color="#2ea070",
            corner_radius=8
        ).pack(side="left", padx=5)
    
    def create_status_bar(self):
        self.status_frame = ctk.CTkFrame(
            self.main_frame, 
            height=35,
            fg_color=COLORS["bg_card_light"],
            corner_radius=8
        )
        self.status_frame.grid(row=2, column=0, sticky="ew", pady=(15, 0))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="✓ Ready",
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        self.status_label.pack(side="left", padx=15, pady=8)
    
    def open_calendar(self):
        from tkinter import Toplevel, Spinbox
        from calendar import monthcalendar, month_name
        
        calendar_window = Toplevel(self)
        calendar_window.title("Select Date")
        calendar_window.geometry("320x380")
        calendar_window.transient(self)
        calendar_window.grab_set()
        
        calendar_window.configure(bg=COLORS["bg_card"])
        
        selected_date = [datetime.now()]
        
        header_frame = ctk.CTkFrame(calendar_window, fg_color=COLORS["primary"], corner_radius=0)
        header_frame.pack(fill="x")
        
        month_var = ctk.StringVar(value=month_name[selected_date[0].month])
        year_var = ctk.StringVar(value=str(selected_date[0].year))
        
        month_spin = ctk.CTkOptionMenu(
            header_frame,
            values=[month_name[i] for i in range(1, 13)],
            variable=month_var,
            command=lambda v: update_calendar(),
            width=120,
            fg_color=COLORS["secondary"],
            button_color=COLORS["secondary"],
            button_hover_color=COLORS["primary"]
        )
        month_spin.pack(side="left", padx=10, pady=10)
        month_spin.set(month_name[selected_date[0].month])
        
        year_entry = ctk.CTkEntry(
            header_frame,
            width=80,
            placeholder_text="Year"
        )
        year_entry.pack(side="left", padx=10, pady=10)
        year_entry.insert(0, str(selected_date[0].year))
        
        def update_calendar():
            try:
                m = [i for i in range(1, 13) if month_name[i] == month_var.get()][0]
                y = int(year_entry.get())
                selected_date[0] = selected_date[0].replace(year=y, month=m)
                draw_calendar()
            except:
                pass
        
        def draw_calendar():
            for widget in cal_frame.winfo_children():
                widget.destroy()
            
            days = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
            for i, day in enumerate(days):
                ctk.CTkLabel(
                    cal_frame, 
                    text=day, 
                    width=40, 
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=COLORS["text_secondary"]
                ).grid(row=0, column=i, pady=5)
            
            cal_days = monthcalendar(selected_date[0].year, selected_date[0].month)
            for week_idx, week in enumerate(cal_days):
                for day_idx, day in enumerate(week):
                    if day == 0:
                        ctk.CTkLabel(cal_frame, text="", width=40).grid(row=week_idx+1, column=day_idx)
                    else:
                        is_today = (day == datetime.now().day and 
                                   selected_date[0].month == datetime.now().month and 
                                   selected_date[0].year == datetime.now().year)
                        
                        btn = ctk.CTkButton(
                            cal_frame,
                            text=str(day),
                            width=40,
                            height=35,
                            corner_radius=6,
                            fg_color=COLORS["primary"] if is_today else COLORS["bg_card_light"],
                            hover_color=COLORS["secondary"] if is_today else COLORS["primary"],
                            text_color="white" if is_today else COLORS["text_primary"],
                            command=lambda d=day: select_day(d)
                        )
                        btn.grid(row=week_idx+1, column=day_idx, pady=2, padx=2)
        
        def select_day(day):
            selected_date[0] = selected_date[0].replace(day=day)
            self.date_entry.delete(0, "end")
            self.date_entry.insert(0, selected_date[0].strftime("%Y-%m-%d"))
            self.update_cron_preview()
            calendar_window.destroy()
        
        cal_frame = ctk.CTkFrame(calendar_window, fg_color=COLORS["bg_card"])
        cal_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        draw_calendar()
        
        def on_cancel():
            calendar_window.destroy()
        
        ctk.CTkButton(
            calendar_window,
            text="Cancel",
            command=on_cancel,
            height=35,
            fg_color=COLORS["accent"],
            hover_color="#d91e24",
            corner_radius=6
        ).pack(pady=10, padx=10, fill="x")

    def on_schedule_change(self, option):
        if option == "Custom":
            self.custom_schedule_frame.pack(fill="x", padx=20, pady=5)
        else:
            self.custom_schedule_frame.pack_forget()
        
        self.update_cron_preview()
    
    def update_cron_preview(self):
        option = self.schedule_option.get()
        cron = ""
        
        if option == "Every Minute":
            cron = "* * * * *"
        elif option == "Every Hour":
            cron = "0 * * * *"
        elif option == "Daily":
            cron = "0 0 * * *"
        elif option == "Weekly":
            cron = "0 0 * * 0"
        elif option == "Custom":
            try:
                hour = int(self.hour_spinbox.get()) % 24
                minute = int(self.minute_spinbox.get()) % 60
                cron = f"{minute} {hour} * * *"
            except ValueError:
                cron = "Invalid"
        
        self.cron_preview_label.configure(text=f"⏰ Cron: {cron}")
    
    def load_saved_config(self):
        config = self.config_manager.config
        
        dark_mode = config.get("dark_mode", True)
        ctk.set_appearance_mode("Dark" if dark_mode else "Light")
        
        output_dir = config.get("output_directory", "")
        self.output_path_entry.delete(0, "end")
        self.output_path_entry.insert(0, output_dir)
    
    def load_scheduled_tasks(self):
        tasks = self.config_manager.get_tasks()
        self.update_tasks_list(tasks)
        self.update_dashboard(tasks)
        
        for task in tasks:
            if task.enabled:
                self.schedule_task(task)
    
    def update_tasks_list(self, tasks: List[ScreenshotTask]):
        for widget in self.tasks_list_frame.winfo_children():
            widget.destroy()
        
        for task in tasks:
            task_frame = ctk.CTkFrame(
                self.tasks_list_frame, 
                fg_color=COLORS["bg_card"],
                corner_radius=10
            )
            task_frame.pack(fill="x", pady=8, padx=5)
            
            ctk.CTkLabel(
                task_frame,
                text=f"🔗 {task.url}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS["text_primary"],
                wraplength=500
            ).pack(anchor="w", padx=12, pady=(10, 5))
            
            ctk.CTkLabel(
                task_frame,
                text=f"⏱️ {task.cron_schedule} | 📐 {task.width}x{task.height}",
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_secondary"]
            ).pack(anchor="w", padx=12, pady=(0, 5))
            
            status_text = "✅ Enabled" if task.enabled else "❌ Disabled"
            status_color = COLORS["success"] if task.enabled else COLORS["accent"]
            
            ctk.CTkLabel(
                task_frame,
                text=f"Status: {status_text}",
                font=ctk.CTkFont(size=11),
                text_color=status_color
            ).pack(anchor="w", padx=12, pady=(0, 5))
            
            btn_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
            btn_frame.pack(fill="x", padx=12, pady=(8, 12))
            
            capture_btn = ctk.CTkButton(
                btn_frame,
                text="📷 Capture Now",
                width=130,
                height=35,
                fg_color=COLORS["secondary"],
                hover_color=COLORS["primary"],
                corner_radius=6,
                command=lambda t=task: self.run_capture(t)
            )
            capture_btn.pack(side="left", padx=(0, 5))
            
            remove_btn = ctk.CTkButton(
                btn_frame,
                text="🗑️ Delete",
                width=110,
                height=35,
                fg_color=COLORS["accent"],
                hover_color="#d91e24",
                corner_radius=6,
                command=lambda t=task: self.remove_task(t.id)
            )
            remove_btn.pack(side="right", padx=(5, 0))
    
    def update_dashboard(self, tasks: List[ScreenshotTask]):
        for widget in self.dashboard_tasks_frame.winfo_children():
            widget.destroy()
        
        self.total_tasks_label.configure(text=f"📊 Total Tasks: {len(tasks)}")
        
        if not tasks:
            ctk.CTkLabel(
                self.dashboard_tasks_frame,
                text="📭 No tasks scheduled. Add a task in the Tasks tab.",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"]
            ).pack(pady=30)
            return
        
        for task in tasks:
            task_card = ctk.CTkFrame(
                self.dashboard_tasks_frame, 
                fg_color=COLORS["bg_card_light"],
                corner_radius=10
            )
            task_card.pack(fill="x", pady=8, padx=5)
            
            ctk.CTkLabel(
                task_card,
                text=f"🔗 {task.url}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["text_primary"],
                wraplength=1100
            ).pack(anchor="w", padx=15, pady=(12, 6))
            
            ctk.CTkLabel(
                task_card,
                text=f"⏱️ Schedule: {task.cron_schedule} | 📐 Size: {task.width}x{task.height}",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_secondary"]
            ).pack(anchor="w", padx=15, pady=(0, 6))
            
            status_text = "✅ Enabled" if task.enabled else "❌ Disabled"
            status_color = COLORS["success"] if task.enabled else COLORS["accent"]
            
            ctk.CTkLabel(
                task_card,
                text=f"Status: {status_text}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=status_color
            ).pack(anchor="w", padx=15, pady=(0, 12))
    
    def add_task(self):
        url = self.url_entry.get().strip()
        cron = self.get_cron_schedule()
        width = int(self.width_entry.get())
        height = int(self.height_entry.get())
        
        if not url or cron == "Invalid":
            self.show_error("Please enter a valid URL and schedule")
            return
        
        output_path = self.output_path_entry.get()
        if not output_path:
            output_path = str(Path.home() / "Documents" / "Screenshots")
        
        task = ScreenshotTask(
            id=str(uuid.uuid4()),
            url=url,
            cron_schedule=cron,
            output_path=output_path,
            width=width,
            height=height,
            full_page=self.full_page_var.get(),
            enabled=True
        )
        
        self.config_manager.add_task(task)
        self.load_scheduled_tasks()
        
        self.clear_task_inputs()
        self.show_success("Task added successfully")
    
    def get_cron_schedule(self):
        option = self.schedule_option.get()
        
        if option == "Every Minute":
            return "* * * * *"
        elif option == "Every Hour":
            return "0 * * * *"
        elif option == "Daily":
            return "0 0 * * *"
        elif option == "Weekly":
            return "0 0 * * 0"
        elif option == "Custom":
            try:
                hour = int(self.hour_spinbox.get()) % 24
                minute = int(self.minute_spinbox.get()) % 60
                return f"{minute} {hour} * * *"
            except ValueError:
                return "Invalid"
        return "0 * * * *"
    
    def remove_task(self, task_id: str):
        self.config_manager.remove_task(task_id)
        self.load_scheduled_tasks()
        self.show_success("Task removed successfully")
    
    def clear_task_inputs(self):
        self.url_entry.delete(0, "end")
        self.schedule_option.set("Every Hour")
        self.hour_spinbox.set("00")
        self.minute_spinbox.set("00")
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.custom_schedule_frame.pack_forget()
        self.update_cron_preview()
    
    def schedule_task(self, task: ScreenshotTask):
        try:
            cron_parts = task.cron_schedule.split()
            if len(cron_parts) != 5:
                raise ValueError("Invalid cron format")
            
            minute, hour, day, month, day_of_week = cron_parts
            
            def capture_wrapper():
                acquired = self.capture._capture_lock.acquire(blocking=False)
                if not acquired:
                    print(f"Capture already in progress for {task.url}, skipping")
                    return
                
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(self.capture_task(task))
                    finally:
                        loop.close()
                finally:
                    self.capture._capture_lock.release()
            
            self.scheduler.add_job(
                capture_wrapper,
                trigger=CronTrigger(
                    minute=minute,
                    hour=hour,
                    day=day,
                    month=month,
                    day_of_week=day_of_week
                ),
                id=task.id,
                max_instances=1,
                replace_existing=True
            )
            print(f"Scheduled task: {task.url} at {task.cron_schedule}")
        except Exception as e:
            print(f"Failed to schedule task: {e}")
    
    async def capture_task(self, task: ScreenshotTask):
        self.status_label.configure(text=f"📸 Capturing: {task.url}...")
        self.update()
        
        success = await self.capture.capture(task)
        
        if success:
            self.status_label.configure(text=f"✅ Capture successful: {task.url}")
        else:
            self.status_label.configure(text=f"❌ Capture failed: {task.url}")
        
        self.update()
    
    def run_capture(self, task: ScreenshotTask):
        def capture():
            acquired = self.capture._capture_lock.acquire(blocking=False)
            if not acquired:
                print(f"Capture already in progress for {task.url}, skipping")
                return
            
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.capture_task(task))
                finally:
                    loop.close()
            finally:
                self.capture._capture_lock.release()
        
        thread = threading.Thread(target=capture)
        thread.start()
    
    def browse_output_dir(self):
        from tkinter import filedialog
        path = filedialog.askdirectory()
        if path:
            self.output_path_entry.delete(0, "end")
            self.output_path_entry.insert(0, path)
    
    def save_settings(self):
        output_dir = self.output_path_entry.get()
        if output_dir:
            self.config_manager.config["output_directory"] = output_dir
            self.config_manager.save_config()
            self.show_success("Settings saved")
    
    def toggle_dark_mode(self):
        current = ctk.get_appearance_mode()
        new_mode = "Light" if current == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
        
        is_dark = new_mode == "Dark"
        self.config_manager.config["dark_mode"] = is_dark
        self.config_manager.save_config()
    
    def show_success(self, message: str):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Success")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            dialog, 
            text=f"✅ {message}", 
            font=ctk.CTkFont(size=16),
            text_color=COLORS["success"]
        ).pack(pady=40, padx=20)
        ctk.CTkButton(
            dialog, 
            text="OK", 
            command=dialog.destroy,
            width=100,
            height=40,
            fg_color=COLORS["success"],
            hover_color="#2ea070",
            corner_radius=8
        ).pack(pady=20)
    
    def show_error(self, message: str):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Error")
        dialog.geometry("450x220")
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            dialog,
            text=f"❌ {message}",
            font=ctk.CTkFont(size=15),
            text_color=COLORS["accent"],
            wraplength=400
        ).pack(pady=40, padx=20)
        ctk.CTkButton(
            dialog, 
            text="OK", 
            command=dialog.destroy,
            width=100,
            height=40,
            fg_color=COLORS["accent"],
            hover_color="#d91e24",
            corner_radius=8
        ).pack(pady=20)
    
    def on_close(self):
        self.scheduler.shutdown()
        
        def close_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.capture.close())
            finally:
                loop.close()
        
        close_async()
        super().destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
