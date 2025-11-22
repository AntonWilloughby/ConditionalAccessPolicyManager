# Conditional Access Policy Manager - Web Version

A web-based application for managing Microsoft Entra (Azure AD) Conditional Access Policies. This version allows your colleagues to use the tool via a web browser without installing any dependencies on their machines.

## Features

- 🌐 **Web-Based Interface** - Access via browser, no local installation required
- 🔐 **Microsoft Graph Integration** - Full CRUD operations for CA policies
- 📦 **Policy Templates** - Deploy pre-configured enterprise policy templates
- ⚡ **Bulk Operations** - Select and delete multiple policies at once
- 📊 **Security Report Import** - Upload Zero Trust Assessment reports and get policy recommendations
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile devices
- 🔒 **Session Management** - Secure credential storage per user session

## Architecture

```
CA_Policy_Manager_Web/
├── app.py                  # Flask application (backend)
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Main web interface
├── static/
│   ├── css/
│   │   └── style.css      # Custom styling
│   └── js/
│       └── main.js        # Frontend JavaScript
└── uploads/               # Temporary report uploads
```

## Installation

### Option 1: Run on Your Machine (Share via Network)

1. **Install Dependencies**:
```powershell
cd "C:\MyProjects\AV Policy\CA_Policy_Manager_Web"
pip install -r requirements.txt
```

2. **Run the Application**:
```powershell
python app.py
```

3. **Access the Application**:
   - On your machine: http://localhost:5000
   - On network: http://YOUR-IP-ADDRESS:5000
   - Share your IP address with colleagues

### Option 2: Deploy to a Server (Production)

#### Using Gunicorn (Linux Server)

1. **Install on Server**:
```bash
pip install -r requirements.txt
```

2. **Run with Gunicorn**:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. **Setup as Systemd Service** (optional):
```bash
sudo nano /etc/systemd/system/ca-policy-manager.service
```

```ini
[Unit]
Description=CA Policy Manager Web App
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/CA_Policy_Manager_Web
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable ca-policy-manager
sudo systemctl start ca-policy-manager
```

#### Using IIS (Windows Server)

1. Install **HttpPlatformHandler** for IIS
2. Create **web.config**:

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="C:\path\to\python.exe"
                  arguments="C:\path\to\CA_Policy_Manager_Web\app.py"
                  stdoutLogEnabled="true"
                  stdoutLogFile="C:\path\to\logs\stdout.log"
                  startupTimeLimit="60">
    </httpPlatform>
  </system.webServer>
</configuration>
```

3. Configure IIS site to point to the application directory

## Usage

### 1. Connect to Microsoft Graph

1. Click **Connect** button in the top-right corner
2. Enter your credentials:
   - **Tenant ID**: Your Azure AD tenant ID
   - **Client ID**: App registration client ID
   - **Client Secret**: App registration secret
3. Uncheck "Verify SSL" if behind a corporate proxy
4. Click **Connect**

### 2. Manage Policies

**Policies Tab**:
- View all existing Conditional Access policies
- Click policy name to view details
- Delete individual policies
- Select multiple policies for bulk operations

**Deploy Templates Tab**:
- Browse pre-configured policy templates by category
- Deploy individual templates
- Deploy all templates at once

**Bulk Operations Tab**:
- Select/deselect all policies
- Bulk delete selected policies
- View progress and results

### 3. Import Security Reports

**Import Report Tab**:
1. Click **Choose File** and select your Zero Trust Assessment report (HTML)
2. Click **Upload & Analyze**
3. View findings and recommendations
4. Select specific recommendations or deploy all
5. Export findings to Excel for documentation

## Security Considerations

### For Development/Testing
- The app runs with `debug=True` by default
- Session keys are randomly generated on each restart
- Credentials are stored in session memory (cleared when session ends)

### For Production Deployment

1. **Disable Debug Mode**:
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

2. **Set Secure Secret Key** (in app.py):
```python
app.secret_key = 'your-production-secret-key-here'  # Use environment variable
```

3. **Use HTTPS**:
   - Configure SSL certificates
   - Use reverse proxy (nginx/Apache) with HTTPS
   - Redirect HTTP to HTTPS

4. **Implement Authentication**:
   - Add login page for users
   - Use Flask-Login or similar
   - Implement role-based access control

5. **Session Storage**:
   - Use Redis or database for session storage
   - Configure session timeouts
   - Clear old sessions regularly

6. **Rate Limiting**:
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)
```

7. **Input Validation**:
   - Validate file uploads (size, type)
   - Sanitize user inputs
   - Use CSRF protection

## Firewall Configuration

If running on your laptop and sharing with colleagues:

**Windows Firewall**:
```powershell
New-NetFirewallRule -DisplayName "CA Policy Manager Web" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

**Find Your IP Address**:
```powershell
ipconfig | Select-String "IPv4"
```

Share this IP with colleagues: `http://YOUR-IP:5000`

## Troubleshooting

### Port Already in Use
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process
taskkill /PID <PID> /F
```

### Connection Refused
- Check firewall allows inbound connections on port 5000
- Verify Flask is running with `host='0.0.0.0'`
- Ensure colleagues are on the same network

### SSL Certificate Errors
- Uncheck "Verify SSL Certificate" in the connect dialog
- Or set `verify_ssl: false` in the code

### Report Upload Fails
- Check file size (max 50MB by default)
- Ensure `uploads/` directory exists and is writable
- Verify file is a valid HTML report

## API Endpoints

For integration or custom frontends:

- `POST /api/connect` - Authenticate with Microsoft Graph
- `GET /api/policies` - List all policies
- `GET /api/policies/<id>` - Get policy details
- `POST /api/policies` - Create policy
- `PUT /api/policies/<id>` - Update policy
- `DELETE /api/policies/<id>` - Delete policy
- `POST /api/policies/bulk-delete` - Delete multiple policies
- `GET /api/templates` - List templates
- `POST /api/templates/deploy` - Deploy template
- `POST /api/report/upload` - Upload report
- `POST /api/report/analyze` - Analyze report
- `POST /api/report/deploy-recommendations` - Deploy recommendations
- `GET /api/report/export` - Export findings to Excel

## Support

For issues or questions:
1. Check the Flask console output for errors
2. Check browser console (F12) for JavaScript errors
3. Verify Microsoft Graph API permissions are configured correctly

## License

Internal use only. Based on the desktop CA Policy Manager application.

---

**Note**: This is a development/internal tool. For production deployment accessible over the internet, implement proper security measures including authentication, HTTPS, rate limiting, and input validation.
