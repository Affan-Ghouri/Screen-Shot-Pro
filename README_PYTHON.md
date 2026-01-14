# 📸 Python Screenshot App

Modern screenshot capture application built with Python! Features automated scheduling, beautiful dark/light mode GUI, and is very easy to install and run.

## ✨ Features

- 🎨 **Beautiful Modern UI** - CustomTkinter with dark/light mode
- 📅 **Cron Scheduling** - Schedule captures at specific times
- 🖼️ **Full Page Support** - Capture entire web pages or viewport
- 🚀 **Fast Captures** - Using Playwright for speed
- ⚙️ **Easy Configuration** - JSON-based, user-friendly settings
- 🔄 **Immediate Capture** - Take screenshots on demand
- 🌐 **Cross-Platform** - Windows, Linux, macOS

## 🛠️ Installation

### Quick Setup (Windows)

Just run the setup script:

```batch
setup.bat
```

This will:
1. Check Python is installed
2. Install all dependencies
3. Install Playwright browsers
4. Get you ready to run

### Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install chromium

# Run the app
python main.py
```

## 📖 Usage

### Adding Tasks

1. Click on **Tasks** tab
2. Enter **URL**: The website you want to capture
3. Enter **Cron Schedule**: When to capture (see examples below)
4. Set **Dimensions**: Width and height in pixels
5. Check **Full Page Screenshot** if you want entire page
6. Click **Add Task**

### Capturing Screenshots

**Manual Capture:**
1. Go to **Tasks** tab
2. Find your task in the list
3. Click **📷 Capture Now**
4. Screenshot saved to output folder

**Scheduled Capture:**
1. Add task with cron schedule
2. Task runs automatically
3. Check **Dashboard** to view status

### Cron Schedule Examples

```
0 * * * *       Every hour at minute 0
0 0 * * *       Daily at midnight
0 9 * * *       Daily at 9 AM
0 0 * * MON     Every Monday at midnight
*/5 * * * *       Every 5 minutes
0 0 1 * *       Monthly on 1st at midnight
0 9,17 * * *     Daily at 9 AM and 5 PM
```

### Settings

- **Output Directory**: Where screenshots are saved (default: Documents/Screenshots)
- **Dark Mode**: Toggle between dark and light theme
- Settings are saved automatically

## 📂 Configuration

Config stored in:
- **Windows**: `C:\Users\<Username>\.screenshot_app\config.json`
- **Linux/macOS**: `~/.screenshot_app/config.json`

Example config:
```json
{
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "url": "https://example.com",
      "cron_schedule": "0 * * * *",
      "output_path": "C:/Users/User/Documents/Screenshots",
      "width": 1920,
      "height": 1080,
      "full_page": true,
      "enabled": true
    }
  ],
  "dark_mode": true,
  "output_directory": "C:/Users/User/Documents/Screenshots",
  "default_width": 1920,
  "default_height": 1080,
  "window_width": 1280,
  "window_height": 720
}
```

## 🏗️ Project Structure

```
screenshot-go/
├── main.py              # Python application
├── requirements.txt      # Python dependencies
├── setup.bat          # Windows setup script
└── README_PYTHON.md   # This file
```

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| playwright | 1.41.0 | Headless browser automation |
| customtkinter | 5.2.1 | Modern GUI framework |
| apscheduler | 3.10.4 | Cron scheduling |
| Pillow | 10.2.0 | Image processing |

## 📊 Performance

| Metric | Value |
|--------|--------|
| Memory Usage | 50-100 MB |
| Startup Time | < 2 seconds |
| Screenshot Speed | 1-3 seconds |
| Binary Size | N/A (Python script) |

## 🚀 Running the App

### Windows

```batch
# After setup
python main.py

# Or double-click main.py file
```

### Linux/macOS

```bash
# After setup
python3 main.py

# Or make executable and run directly
chmod +x main.py
./main.py
```

## 🎯 Use Cases

- **Dashboard Monitoring**: Regular captures of analytics dashboards
- **Change Detection**: Visual monitoring of web pages
- **Reporting**: Generate visual reports on schedule
- **Archiving**: Keep historical records of web pages
- **Testing**: Automated UI testing verification
- **Compliance**: Capture regulated data at intervals

## 🐛 Troubleshooting

### Dependencies not found

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Reinstall packages
pip install -r requirements.txt --force-reinstall
```

### Playwright browsers missing

```bash
# Reinstall browsers
python -m playwright install chromium
python -m playwright install-deps chromium
```

### Screenshot blank

- Check if URL is accessible
- Wait for page load (2 second delay built-in)
- Try with a simpler URL first
- Check if JavaScript is required

### Dark mode not working

- Check config file
- Toggle dark mode from Settings
- Restart the application

## 🔧 Advanced Features

### Custom Schedule

You can use any valid cron expression:

```
# Seconds Minutes Hours Day Month DayOfWeek
# *     *        *     *   *     *

# Every 30 seconds
*/30 * * * * *

# Every Monday at 9 AM
0 9 * * MON

# Every weekday at 9 AM and 5 PM
0 9,17 * * MON-FRI
```

### Multiple Tasks

You can schedule multiple screenshots for different URLs:
- Homepage: Every hour
- Analytics page: Every 6 hours
- Reports page: Daily at 9 AM

## 📄 Creating Executable (Optional)

To create a standalone EXE file:

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed main.py

# Find executable in dist/main.exe
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork repository
2. Create feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with [Python](https://www.python.org/)
- UI: [CustomTkinter](https://customtkinter.com/)
- Screenshots: [Playwright](https://playwright.dev/)
- Scheduling: [APScheduler](https://apscheduler.readthedocs.io/)

---

**Made by Jerry with ❤️ using Python**

Version: 1.0.0
