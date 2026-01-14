# Screenshot Scheduler Pro

A modern Python application for automatically capturing screenshots of websites on a scheduled basis.

## Features

- 📸 Automated screenshot capture
- ⏰ Flexible scheduling (minute, hourly, daily, weekly, custom)
- 📅 Built-in calendar for custom date/time selection
- 🎨 Modern, responsive UI with dark mode
- 🔧 Configurable screenshot dimensions
- 📄 Full page or viewport screenshots
- 📋 Task management dashboard
- ✨ Clean, professional interface

## Requirements

```bash
pip install customtkinter pillow playwright apscheduler
playwright install
```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. Add a new task:
   - Enter URL
   - Select schedule (Every Minute/Hour/Daily/Weekly/Custom)
   - For custom schedule, use calendar to pick date and dropdown for time
   - Set dimensions (default: 1920x1080)
   - Click "Add Task"

3. Capture screenshot:
   - Click "📷 Capture Now" on any task
   - Or wait for scheduled capture

## Screenshots

Features a modern, card-based UI with:
- Scrollable task management panels
- Calendar picker for date selection
- Dropdown menus for time selection
- Real-time cron schedule preview
- Dark/Light mode toggle
- Responsive window resizing

## Output

Screenshots are saved to:
- `Documents/Screenshots/` (default)
- Or your custom output directory

## License

MIT
