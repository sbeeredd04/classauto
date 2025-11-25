# ASU Class Auto-Enrollment System

A robust, two-part system that monitors ASU class availability and automatically enrolls when seats become available.

## 🏗️ Architecture

The system consists of two independent components:

1. **`class_checker.py`** - Runs headless in the background, monitoring class availability every 2 seconds
2. **`auto_enroller.py`** - Launches with visible browser when triggered, handles enrollment with Duo authentication

This architecture solves the headless authentication problem by running the checker invisibly while the enroller runs visibly for Duo.

## ✨ Features

- **Headless Monitoring**: Checker runs invisibly in background without authentication issues
- **Visual Enrollment**: Enroller runs with visible browser for easy Duo authentication
- **Automatic Triggering**: Checker automatically launches enroller when seats available
- **Robust Error Handling**: Comprehensive logging and error recovery
- **Session Management**: Automatic retries and browser restarts on errors
- **Easy Management**: Simple scripts to start, stop, and check status

## 📋 Prerequisites

```bash
# Install required Python packages
pip3 install selenium python-dotenv pytz
```

## ⚙️ Configuration

### 1. Setup Environment Variables

Edit the `.env` file:

```env
# Credentials
USERNAME=your_asu_username
PASSWORD=your_asu_password

# Class settings
CLASS_NUMBER=22513
TERM_CODE=2261
TERM=2026 Spring
TERM_XPATH_ID=SSR_CART_TRM_FL_TERM_DESCR30$0

# Monitoring settings
CHECK_INTERVAL=2
MAX_RETRIES=3
```

**Important**: Never commit the `.env` file!

### 2. Term Codes Reference

- Spring 2026: `2261`
- Fall 2025: `2257`
- Spring 2025: `2251`

## 🚀 Usage

### Quick Start

```bash
# Start monitoring (runs checker in background)
./start_monitoring.sh

# Check status
./check_status.sh

# Stop monitoring
./stop_monitoring.sh
```

### Detailed Workflow

1. **Start the checker**:
   ```bash
   ./start_monitoring.sh
   ```
   - Checker runs headless in background
   - Monitors class every 2 seconds
   - Logs to `checker.log`

2. **Monitor progress**:
   ```bash
   # View live logs
   tail -f checker.log
   
   # Check system status
   ./check_status.sh
   ```

3. **When seats become available**:
   - Checker automatically triggers `auto_enroller.py`
   - Browser opens visibly for Duo authentication
   - Approve Duo on your phone
   - Enrollment proceeds automatically
   - Browser stays open for verification

4. **Stop monitoring** (if needed):
   ```bash
   ./stop_monitoring.sh
   ```

### Manual Testing

Test the enroller directly without the checker:

```bash
# Run enroller manually
python3 auto_enroller.py
```

Test the checker without triggering enrollment (modify the code temporarily to not call subprocess).

## 📁 File Structure

```
classauto/
├── class_checker.py          # Headless availability monitor
├── auto_enroller.py          # Visual enrollment handler
├── .env                      # Your configuration (NOT in git)
├── .gitignore               # Protects sensitive files
├── README.md                # This file
├── start_monitoring.sh      # Start the system
├── stop_monitoring.sh       # Stop the system
├── check_status.sh          # Check system status
├── checker.log              # Checker logs (created at runtime)
├── enroller.log             # Enroller logs (created at runtime)
└── checker.pid              # Checker process ID (created at runtime)
```

## 🔍 Monitoring & Logs

### View Live Checker Logs

```bash
tail -f checker.log
```

### View Live Enroller Logs

```bash
tail -f enroller.log
```

### Check System Status

```bash
./check_status.sh
```

This shows:
- ✓ Whether checker is running
- ✓ Whether enroller is running
- ✓ Recent logs from both
- ✓ Process IDs and resource usage

## 🐛 Troubleshooting

### Checker Won't Start

```bash
# Check if already running
ps aux | grep class_checker.py

# View error logs
cat checker.log

# Verify ChromeDriver is available
which chromedriver
```

### Credentials Not Loading

```bash
# Verify .env file
cat .env

# Check Python can load it
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('USERNAME'))"
```

### Enroller Fails to Launch

```bash
# Check enroller logs
cat enroller.log

# Test enroller manually
python3 auto_enroller.py
```

### Can't Find Class

```bash
# Verify class number in .env
grep CLASS_NUMBER .env

# Verify term code (2261 = Spring 2026)
grep TERM_CODE .env

# Test URL manually
# https://catalog.apps.asu.edu/catalog/classes/classlist?keywords=22513&term=2261
```

### Process Won't Stop

```bash
# Force stop checker
pkill -9 -f class_checker.py

# Force stop enroller
pkill -9 -f auto_enroller.py

# Remove stale PID file
rm checker.pid
```

### Clean Start (Reset Everything)

```bash
# Stop all processes
./stop_monitoring.sh

# Remove logs and PIDs
rm -f checker.log enroller.log checker.pid enroller.pid

# Remove Chrome user data (forces re-authentication)
rm -rf userdata/

# Start fresh
./start_monitoring.sh
```

## 🔒 Security Best Practices

⚠️ **Never share your `.env` file** - It contains your password!

⚠️ **Never commit `.env` to git** - Already excluded in `.gitignore`

⚠️ **Keep your system updated** - Update Python, Selenium, and ChromeDriver regularly

⚠️ **Use strong credentials** - Your ASU account security is critical

## 📊 How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    MONITORING PHASE                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  class_checker.py (Headless)                                │
│         │                                                     │
│         ├─> Opens catalog page                              │
│         ├─> Checks seat availability                        │
│         ├─> Logs status                                     │
│         └─> Waits 2 seconds                                 │
│                 │                                            │
│                 └─> Repeat                                  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                        │
                        │ Seats Available!
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                   ENROLLMENT PHASE                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  auto_enroller.py (Visible Browser)                         │
│         │                                                     │
│         ├─> Opens login page                                │
│         ├─> Enters credentials                              │
│         ├─> Handles Duo (user approves on phone)           │
│         ├─> Navigates to shopping cart                     │
│         ├─> Selects term (2026 Spring)                     │
│         ├─> Clicks enroll button                           │
│         ├─> Confirms enrollment                             │
│         └─> Keeps browser open for verification            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Best Practices

### For Reliable Monitoring

1. **Run on a stable machine** - Don't let it sleep
2. **Keep power connected** - Prevent unexpected shutdowns
3. **Stable internet** - Required for both checking and enrolling
4. **Monitor the logs** - Check `checker.log` periodically
5. **Test before the rush** - Make sure everything works

### For Successful Enrollment

1. **Have phone nearby** - For Duo authentication
2. **Don't interfere** - Let the browser work when enroller launches
3. **Verify immediately** - Check enrollment status after completion
4. **Keep credentials current** - Update `.env` if password changes

## 🆘 Support & Debugging

### Enable Debug Logging

Edit the script and change:
```python
logging.basicConfig(level=logging.INFO, ...)
```
to:
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

### Common Issues

| Issue | Solution |
|-------|----------|
| "ChromeDriver not found" | Install ChromeDriver or add to PATH |
| "Username/Password not set" | Check `.env` file exists and has credentials |
| "Could not find submit button" | ASU website may have changed, check XPaths |
| "Duo timeout" | Approve Duo faster, or increase timeout |
| "Term not found" | Verify `TERM_XPATH_ID` matches your term |
| "Class not found" | Verify `CLASS_NUMBER` and `TERM_CODE` |

## 📝 Notes

- **First login requires Duo** - Chrome user data is saved after first successful login
- **Checker is invisible** - Runs completely headless, no windows
- **Enroller is visible** - Opens browser for you to see progress
- **Automatic triggering** - No manual intervention needed when seats open
- **Logs everything** - Check logs for detailed information

## ⚖️ Legal & Ethical Use

- This tool is for **personal use only**
- Be aware of ASU's terms of service
- Don't run multiple instances simultaneously
- Don't abuse the system or overload ASU servers
- Use responsibly and ethically

## 🔄 Updates & Maintenance

### Updating Class Number

Edit `.env`:
```env
CLASS_NUMBER=your_new_class_number
```

### Changing Check Interval

Edit `.env` (value in seconds):
```env
CHECK_INTERVAL=5
```

### Updating for New Term

Edit `.env`:
```env
TERM_CODE=2261
TERM=2026 Spring
```

## 🎓 Tips for Success

1. **Test early** - Don't wait until registration day
2. **Check XPaths** - ASU website occasionally changes
3. **Monitor logs** - Know what's happening
4. **Have backup plan** - Manual enrollment if system fails
5. **Keep charged** - Phone battery for Duo
6. **Fast Duo** - Practice approving quickly

## 📞 Getting Help

If you encounter issues:

1. Check the logs: `cat checker.log enroller.log`
2. Check the status: `./check_status.sh`
3. Try a clean start (see Troubleshooting section)
4. Verify all settings in `.env`
5. Test components individually

---

**Good luck with your class enrollment! 🎓**
