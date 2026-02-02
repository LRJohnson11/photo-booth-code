# SMTP Configuration Guide

The SMTP version of the Photo Booth reads email credentials from `smtp_config.json`.

## Quick Setup

1. **Generate a Gmail App Password** (takes 5 minutes):
   - See [SMTP_SETUP.md](SMTP_SETUP.md) for detailed instructions
   - Or quick link: https://myaccount.google.com/apppasswords

2. **Edit `smtp_config.json`** with your credentials:

   ```json
   {
     "email": "youremail@gmail.com",
     "password": "abcd efgh ijkl mnop",
     "server": "smtp.gmail.com",
     "port": 587
   }
   ```

3. **Save the file** and start the application

## Configuration Fields

- **email**: Your full Gmail address (e.g., `photobooth@gmail.com`)
- **password**: Your 16-character Gmail App Password (NOT your regular password!)
- **server**: SMTP server address (leave as `smtp.gmail.com` for Gmail)
- **port**: SMTP port (leave as `587` for Gmail)

## Important Notes

### ⚠️ Use App Password, NOT Regular Password!

The password field requires a **Gmail App Password** - this is a 16-character password that looks like:

```
abcd efgh ijkl mnop
```

**DO NOT** use:

- ❌ Your regular Gmail password
- ❌ Your 2FA authentication code (the 6-digit one that changes)

### Security

- This file contains sensitive credentials - keep it secure
- The `.gitignore` file excludes it from version control
- Never share this file or commit it to a repository
- You can revoke App Passwords anytime at https://myaccount.google.com/apppasswords

### Troubleshooting

**"SMTP Authentication failed"**

- Make sure you're using an App Password, not your regular password
- Verify your email address is correct
- Try generating a new App Password

**File not found or template values**

- The app will create a template `smtp_config.json` on first run
- Edit this file with your real credentials
- Restart the application

**Using a different email provider?**

- Update `server` and `port` for your provider:
  - **Outlook/Hotmail**: `smtp.office365.com`, port `587`
  - **Yahoo**: `smtp.mail.yahoo.com`, port `587`
  - **Other**: Check your email provider's SMTP settings

## Example Configuration

```json
{
  "email": "mychurch.photobooth@gmail.com",
  "password": "abcd efgh ijkl mnop",
  "server": "smtp.gmail.com",
  "port": 587,
  "_comment": "This comment field is optional and ignored by the app"
}
```
