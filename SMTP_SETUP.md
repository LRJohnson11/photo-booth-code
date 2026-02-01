# Gmail SMTP Setup Guide for Photo Booth Application

This guide will walk you through setting up Gmail SMTP access using an App Password so the photo booth can send emails.

## Overview

**Why use SMTP instead of Gmail API?**
- **Higher daily limit:** 500 emails/day vs 100 emails/day (unverified API)
- **Simpler setup:** Just email + app password, no OAuth
- **No verification needed:** Works immediately for personal use
- **Same security:** App passwords are secure and revocable

**Time required:** About 5 minutes

---

## Prerequisites

You need a Gmail account with 2-Factor Authentication (2FA) enabled.

If you don't have 2FA enabled yet, you'll need to set it up first (App Passwords require it).

---

## Step-by-Step Instructions

### Step 1: Enable 2-Factor Authentication (if not already enabled)

1. Go to your Google Account: https://myaccount.google.com/

2. Click **"Security"** in the left sidebar

3. Under "How you sign in to Google", click **"2-Step Verification"**

4. Follow the prompts to set up 2FA (usually via phone)

5. Once enabled, continue to Step 2

---

### Step 2: Generate an App Password

1. Go to your Google Account: https://myaccount.google.com/

2. Click **"Security"** in the left sidebar

3. Under "How you sign in to Google", click **"2-Step Verification"**

4. Scroll down to the bottom and click **"App passwords"**
   - If you don't see this option, make sure 2FA is fully enabled
   - You may need to re-enter your Google password

5. You'll see the "App passwords" page

6. In the dropdown or text field:
   - **App name:** Type "Photo Booth" (or any name you'll remember)
   - Click **"Create"**

7. Google will generate a 16-character password that looks like: `abcd efgh ijkl mnop`

8. **IMPORTANT:** Copy this password immediately!
   - You won't be able to see it again
   - You can always generate a new one if you lose it

---

### Step 3: Configure the Photo Booth Application

1. Run the photo booth application in SMTP mode:
   - **Windows:** `start_photobooth.bat` → Select option 2 (SMTP)
   - **Linux/Mac:** `./start_photobooth.sh` → Select option 2 (SMTP)

2. The application window will open with SMTP configuration fields at the top

3. Enter your information:
   - **Gmail Address:** Your full Gmail address (e.g., `yourname@gmail.com`)
   - **App Password:** The 16-character password from Step 2
     - You can include or remove the spaces - both work
     - Example: `abcdefghijklmnop` or `abcd efgh ijkl mnop`

4. Click **"Save SMTP Config"**

5. You should see: "SMTP configuration saved!"

---

### Step 4: Test the Configuration

1. Continue with the normal setup:
   - Select your monitoring directory
   - Select your zip output directory
   - Select your archive directory
   - Enter a recipient email address

2. Take a test photo (or copy a .jpg file into the monitored directory)

3. Wait 20 seconds or change the email address to trigger sending

4. Check if the email arrives at the recipient address

**If successful:**
- You're all set! The configuration is saved in `smtp_config.json`
- You won't need to enter it again

**If it fails:**
- Double-check your Gmail address
- Make sure you copied the App Password correctly
- Verify 2FA is enabled on your Google account
- See Troubleshooting section below

---

## Important Information

### Email Sending Limits

**Gmail SMTP limits:**
- **500 emails per day** for regular Gmail accounts
- **2,000 emails per day** for Google Workspace accounts
- Limits reset at midnight Pacific Time

For most church events, 500 emails/day is plenty!

### Security

**App Passwords are secure:**
- They only work for SMTP access (not full account access)
- You can revoke them anytime
- Each app can have its own password

**Best Practices:**
1. Use a dedicated Gmail account for the photo booth
2. Don't share your app password
3. Revoke the app password after the event if desired
4. The password is stored in `smtp_config.json` - keep this file secure

### Configuration File

The SMTP configuration is saved in `smtp_config.json`:
```json
{
  "email": "yourname@gmail.com",
  "password": "your-app-password",
  "server": "smtp.gmail.com",
  "port": 587
}
```

**IMPORTANT:** This file contains your app password. Don't commit it to git or share it.
The `.gitignore` file is configured to exclude it automatically.

---

## Troubleshooting

### "SMTP Authentication failed"
- **Cause:** Wrong email or app password
- **Solution:** 
  - Verify your Gmail address is correct
  - Generate a new app password and try again
  - Make sure you're using an App Password, not your regular Gmail password

### "App passwords" option not showing
- **Cause:** 2FA not enabled
- **Solution:** Enable 2-Step Verification first (see Step 1)

### Email not arriving
- **Check spam folder:** Gmail might flag it
- **Check recipient address:** Make sure it's typed correctly
- **Check sending limits:** Have you hit 500 emails today?
- **Check error message:** The app will show specific errors

### "Connection refused" or "Network error"
- **Cause:** Firewall or network blocking SMTP
- **Solution:** 
  - Check your firewall settings
  - Try a different network
  - Make sure port 587 is not blocked

### Storage Mode activating unexpectedly
- **Cause:** SMTP sending failed for some reason
- **Solution:** 
  - Check the error message in the popup
  - Verify your credentials are still valid
  - Check if you've hit daily sending limits
  - Use the send_archived script later to retry

---

## Revoking Access After the Event

To revoke the app password after your event:

1. Go to https://myaccount.google.com/apppasswords

2. Find "Photo Booth" in the list

3. Click the trash/delete icon next to it

4. Confirm deletion

The app password is now revoked and cannot be used.

---

## Switching Between SMTP and Gmail API

You can switch between modes anytime:

**To use SMTP:**
- Run startup script and choose option 2
- Configure SMTP settings (one time)

**To use Gmail API:**
- Run startup script and choose option 1
- Follow Gmail API setup guide
- Configure OAuth credentials

Both configurations can coexist - the app uses whichever mode you select at startup.

---

## Quick Reference

**Important URLs:**
- Google Account Security: https://myaccount.google.com/security
- App Passwords: https://myaccount.google.com/apppasswords
- 2-Step Verification: https://myaccount.google.com/signinoptions/two-step-verification

**SMTP Settings (don't change these):**
- **Server:** smtp.gmail.com
- **Port:** 587
- **Security:** STARTTLS

**Important Files:**
- `smtp_config.json` - Your SMTP credentials (keep secret!)
- `photo_booth_smtp.py` - SMTP version of the app

**Daily Limits:**
- Regular Gmail: 500 emails/day
- Google Workspace: 2,000 emails/day
- Resets: Midnight Pacific Time
