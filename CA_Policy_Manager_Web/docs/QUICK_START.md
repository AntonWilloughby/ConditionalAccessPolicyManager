# Quick Start Guide - CA Policy Manager Web

## ✅ Your Web Application is Ready!

The web-based version of the CA Policy Manager is now available at:

- **On Your Machine**: http://localhost:5000
- **On Your Network**: http://192.168.1.242:5000

Share the network URL with your colleagues so they can access the application from their browsers!

## 🚀 How to Start the Application

### Windows PowerShell:
```powershell
cd "C:\MyProjects\AV Policy\CA_Policy_Manager_Web"
& "C:/MyProjects/AV Policy/.venv/Scripts/python.exe" app.py
```

### Keep It Running:
The application will run until you press `Ctrl+C`. Keep the PowerShell window open while colleagues are using it.

## 👥 Sharing with Colleagues

### Option 1: Same Network (Easiest)
1. **Find Your IP Address**:
   ```powershell
   ipconfig | Select-String "IPv4"
   ```

2. **Open Windows Firewall** (if needed):
   ```powershell
   New-NetFirewallRule -DisplayName "CA Policy Manager Web" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
   ```

3. **Share the URL** with colleagues:
   - Example: `http://192.168.1.242:5000`
   - They just need a web browser - no installation required!

### Option 2: Deploy to a Server
See the full README.md for deployment instructions using:
- Windows Server + IIS
- Linux Server + Gunicorn
- Azure App Service
- AWS Elastic Beanstalk

## 📋 Usage Instructions for Your Colleagues

### 1. Open the Application
Go to the URL you provided (e.g., `http://192.168.1.242:5000`)

### 2. Connect to Microsoft Graph
1. Click the **Connect** button (top-right)
2. Enter credentials:
   - **Tenant ID**: `[Provide this]`
   - **Client ID**: `[Provide this]`
   - **Client Secret**: `[Provide this]`
3. Click **Connect**

**Note**: For security, each user needs to enter credentials. Consider creating separate app registrations for different users or teams.

### 3. Manage Policies
- **Policies Tab**: View, delete, or inspect existing policies
- **Deploy Templates Tab**: Deploy pre-configured policy templates
- **Bulk Operations Tab**: Select multiple policies for bulk deletion
- **Import Report Tab**: Upload Zero Trust Assessment reports and deploy recommended policies

## 🔒 Security Notes

### Current Setup (Development Mode)
- ✅ Works great for internal use on your network
- ✅ No installation required for colleagues
- ⚠️ Not secure for internet access
- ⚠️ Session data stored in memory (lost on restart)

### For Production/Internet Access
Implement these security measures:
1. **Add User Authentication** - Login page with passwords
2. **Enable HTTPS** - SSL certificates
3. **Use Production Server** - Gunicorn or IIS (not Flask dev server)
4. **Set SECRET_KEY** - Use environment variable
5. **Add Rate Limiting** - Prevent abuse
6. **Implement Logging** - Track who does what

See README.md for detailed production deployment instructions.

## 🛠️ Troubleshooting

### Colleagues Can't Connect

**Check Firewall**:
```powershell
# Test if port is open
Test-NetConnection -ComputerName localhost -Port 5000
```

**Verify Flask is Running**:
- Look for "Running on http://192.168.1.242:5000" in your PowerShell window
- App must be running with `host='0.0.0.0'` (already configured)

**Same Network Required**:
- Colleagues must be on the same WiFi/LAN
- VPN users may need special configuration

### Port Already in Use
```powershell
# Find what's using port 5000
netstat -ano | findstr :5000

# Kill the process
taskkill /PID [PID_NUMBER] /F

# Or change port in app.py:
app.run(host='0.0.0.0', port=5001, debug=True)  # Use port 5001 instead
```

### Graph API Connection Fails
- Verify app registration has correct permissions
- Check if client secret has expired
- Try unchecking "Verify SSL Certificate" if behind proxy

## 📱 Features Your Colleagues Will Love

### No Installation Required
- Just open a web browser
- Works on Windows, Mac, Linux
- Works on mobile devices too!

### Modern Interface
- Clean, responsive design
- Bootstrap-based UI
- Real-time updates
- Toast notifications for actions

### All Desktop Features Included
- List and manage policies
- Deploy templates
- Bulk operations
- Import security reports
- Export findings to Excel

## 🎯 Next Steps

1. **Test It Now**: Open http://localhost:5000 in your browser
2. **Share with a Colleague**: Have them try http://192.168.1.242:5000
3. **Consider Production Deployment**: If you need:
   - Internet access (not just local network)
   - User authentication and permissions
   - Persistent sessions
   - Better performance

## 📞 Support

If issues arise:
1. Check the PowerShell window for error messages
2. Press F12 in browser to see JavaScript console errors
3. Verify Microsoft Graph API permissions are correct
4. Check the README.md for detailed troubleshooting

---

**🎉 Enjoy your web-based CA Policy Manager!**

Your colleagues will appreciate not having to install Python, dependencies, or deal with configuration files. They just open a browser and go!
