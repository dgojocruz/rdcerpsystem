# RHODECO ERP System v2.0
## Philippine HR, Payroll & Timekeeping

### Installation (Windows)
1. Unzip this package
2. Double-click `installer\INSTALL.bat`
3. Follow the on-screen prompts
4. A shortcut "RHODECO ERP" appears on your Desktop

### Manual start
Double-click `START_ERP.bat`  
Or: `python run.py` in Command Prompt from this folder

**Default login:** admin / admin123  
**URL:** http://127.0.0.1:5000

### What's new in v2.0
- Payroll Config Panel — edit all rates without touching code
- Loan Tracker — SSS, Pag-IBIG, Personal loans with auto-deduction
- Shift Management — define shifts, assign schedules, rotating shifts
- Interactive Calendar — view who's on shift or leave (FullCalendar)
- Custom Fields — admin-defined fields on employee profiles
- Settings → Payroll Rules accessible from sidebar

### Multi-client usage
```
python run.py --client rhodeco
python run.py --client client2 --setup "Second Company" --port 5001
python run.py --list-clients
```

### Backup
Each client database is one file:
`clients\<client_id>\data\erp.db`
Copy this file to back up all data.

### Requirements
- Windows 10/11 (64-bit)
- Python 3.10 or higher (free from python.org)
- Internet for first setup (to download packages)
