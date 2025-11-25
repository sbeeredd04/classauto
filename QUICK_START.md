# Quick Start Guide

## 🚀 First Time Setup

1. **Configure credentials** (edit `.env`):
   ```bash
   USERNAME=your_username
   PASSWORD=your_password
   CLASS_NUMBER=22513
   ```

2. **Start monitoring**:
   ```bash
   ./start_monitoring.sh
   ```

3. **That's it!** The system will:
   - Monitor class 22513 every 2 seconds (headless/invisible)
   - Automatically open visible browser when seats available
   - Wait for you to approve Duo on your phone
   - Complete enrollment automatically

## 📊 Common Commands

| Command | Purpose |
|---------|---------|
| `./start_monitoring.sh` | Start the checker |
| `./check_status.sh` | See what's running |
| `./stop_monitoring.sh` | Stop everything |
| `tail -f checker.log` | Watch checker logs |
| `tail -f enroller.log` | Watch enroller logs |

## 🔍 What's Happening?

```
[Background - Invisible]              [Triggered - Visible]
                                     
class_checker.py                     auto_enroller.py
     │                                    │
     ├─ Opens catalog                    ├─ Opens browser
     ├─ Checks seats                     ├─ Logs in
     ├─ Waits 2 sec                      ├─ Duo (you approve)
     └─ Repeat                           ├─ Navigates
         │                               ├─ Enrolls
         └─> Seats found! ──triggers──> └─ Done!
```

## ✅ Verify It's Working

```bash
# Check status
./check_status.sh

# Should show:
# ✓ Checker: RUNNING
# ✗ Enroller: NOT RUNNING (waiting for seats)
```

## 🆘 Problems?

```bash
# Stop everything
./stop_monitoring.sh

# Clean logs
rm -f *.log *.pid

# Start fresh
./start_monitoring.sh
```

## 📝 Important Notes

- **Checker is invisible** - Runs in background, no window
- **Enroller is visible** - Opens browser when seats found
- **Have phone ready** - For Duo authentication
- **Don't close terminal** - Keep it running
- **Check logs** - If nothing happens, check `checker.log`

## ⚡ Quick Test

Want to test the enroller without waiting?

```bash
# Run enroller directly
python3 auto_enroller.py
```

This will open the browser and try to enroll immediately.

---

**Need more help?** See `README.md` for detailed documentation.

