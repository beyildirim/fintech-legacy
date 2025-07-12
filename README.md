# Legacy FinTech Platform

This is a deliberately insecure legacy fintech platform built for educational and testing purposes. It contains numerous security vulnerabilities and bad practices that should never be used in production.

## ⚠️ WARNING ⚠️

**DO NOT DEPLOY THIS APPLICATION IN A PRODUCTION ENVIRONMENT**

This application is intentionally vulnerable and should only be used for:
- Security training
- Vulnerability research
- Educational demonstrations
- Security tool testing

## 🚀 Features

- User authentication (with hardcoded credentials)
- Money transfers between accounts
- Basic transaction history
- Admin panel with dangerous functionality
- Multiple security vulnerabilities

## 🔒 Known Vulnerabilities

1. **SQL Injection** in multiple endpoints
2. **Cross-Site Scripting (XSS)** in search functionality
3. **Command Injection** in admin panel
4. **Insecure Deserialization** in backup/restore
5. **Broken Authentication** with hardcoded credentials
6. **Sensitive Data Exposure** (passwords in plaintext)
7. **Missing CSRF Protection**
8. **Insecure Direct Object References (IDOR)**
9. **Security Misconfiguration**
10. **Insufficient Logging & Monitoring**

## 🛠️ Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   cd api
   python app.py
   ```
4. Access the web interface at `http://localhost:5000`

## 🔑 Default Credentials

- **Admin**: `admin` / `admin123`

## 🧪 Testing

This application is designed to be used with security testing tools like:
- OWASP ZAP
- Burp Suite
- SQLMap
- Nmap

## 📝 License

This project is for educational purposes only. Use at your own risk.

## 🙏 Credits

Created for security research and educational purposes.

<!-- Added by Lazy Developer at 2025-07-13 01:09:01.393353 -->

<!-- Added by Lazy Developer at 2025-07-13 01:09:06.597614 -->

<!-- Added by Lazy Developer at 2025-07-13 01:09:13.431623 -->

<!-- Added by Lazy Developer at 2025-07-13T01:10:52.602298 -->

<!-- Added by Lazy Developer at 2025-07-13T01:11:17.476487 -->

<!-- Added by Lazy Developer at 2025-07-13T01:11:44.654882 -->

<!-- Added by Lazy Developer at 2025-07-13T01:12:30.949540 -->

<!-- Added by Lazy Developer at 2025-07-13T01:12:40.756039 -->

<!-- Added by Lazy Developer at 2025-07-13T01:12:57.425095 -->

<!-- Added by Lazy Developer at 2025-07-13T01:13:04.378648 -->

<!-- Added by Lazy Developer at 2025-07-13T01:13:19.887657 -->

<!-- Added by Lazy Developer at 2025-07-13T01:18:47.169086 -->

<!-- Added by Lazy Developer at 2025-07-13T01:19:18.096517 -->

<!-- Added by Lazy Developer at 2025-07-13T01:19:36.063780 -->

<!-- Added by Lazy Developer at 2025-07-13T01:20:31.957392 -->

<!-- Added by Lazy Developer at 2025-07-13T01:21:55.182385 -->

<!-- Added by Lazy Developer at 2025-07-13T01:22:02.385177 -->
