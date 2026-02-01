# Photo Booth Email Automation

Python application that monitors a directory for new .jpg files, renames them based on email addresses, and automatically emails batches of photos to users.

## Two Email Sending Modes

This application supports two different methods for sending emails:

### 1. Gmail API Mode

- **Limit:** 100 emails/day (unverified) or billions/day (verified)
- **Setup:** Requires Google Cloud project and OAuth credentials
- **Best for:** Long-term use, verified applications, or if you plan to scale
- **Setup guide:** See [GMAIL_API_SETUP.md](GMAIL_API_SETUP.md)

### 2. SMTP Mode (Recommended for Most Users)

- **Limit:** 500 emails/day (Gmail) or 2,000/day (Google Workspace)
- **Setup:** Just email + app password (5 minutes)
- **Best for:** Church events, personal use, quick setup
- **Setup guide:** See [SMTP_SETUP.md](SMTP_SETUP.md)

**For a typical church event with 200-500 people, SMTP mode is recommended!**

## Installation

### Quick Start (Recommended)

The startup scripts handle everything automatically - virtual environment creation, dependency installation, and running the app.

**Windows:**

```bash
start_photobooth.bat
```

**Linux/Mac:**

```bash
./start_photobooth.sh
```

### Python Version Configuration

The default Python version is 3.13.9, but you can easily change it:

1. Edit `config.env`
2. Change the `PYTHON_VERSION` line to your desired version:
   ```
   PYTHON_VERSION=3.11.5
   ```
3. Delete the `venv` folder if it already exists
4. Run the startup script again

The script will automatically detect and use the specified Python version if available on your system.

### Manual Installation (Optional)

If you prefer to set things up manually:

1. Install Python 3.7 or higher

2. Create a virtual environment:

```bash
python3 -m venv venv
```

3. Activate the virtual environment:
   - **Windows:** `venv\Scripts\activate`
   - **Linux/Mac:** `source venv/bin/activate`

4. Install required packages:

```bash
pip install -r requirements.txt
```

5. Run the application:

```bash
python photo_booth.py
```

## Gmail API Setup

Since you're handling the Gmail API setup yourself, here's what you need:

1. **Google Cloud Console Setup:**
   - Create a project at https://console.cloud.google.com
   - Enable the Gmail API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download the credentials as `credentials.json`

2. **File Placement:**
   - Place `credentials.json` in the same directory as `photo_booth.py`

3. **First Run:**
   - The first time you run the program, it will open a browser window
   - Log in and authorize the application
   - A `token.json` file will be created for future use

## Usage

### File Structure

```
photo_booth/
├── config.env                       # Configuration (Python version, etc.)
├── credentials.json                 # Gmail API credentials (download from Google Cloud)
├── token.json                       # OAuth tokens (auto-generated on first run)
├── smtp_config.json                 # SMTP credentials (auto-generated when configured)
├── requirements.txt                 # Python dependencies
├── photo_booth.py                   # Main application (Gmail API mode)
├── photo_booth_smtp.py              # Main application (SMTP mode)
├── send_archived_photos.py          # Helper script (Gmail API mode)
├── send_archived_photos_smtp.py     # Helper script (SMTP mode)
├── start_photobooth.sh              # Linux/Mac startup script
├── start_photobooth.bat             # Windows startup script
├── send_archived.sh                 # Linux/Mac script for archived photos
├── send_archived.bat                # Windows script for archived photos
├── GMAIL_API_SETUP.md               # Gmail API setup guide
├── SMTP_SETUP.md                    # SMTP setup guide
├── venv/                            # Virtual environment (auto-created)
└── README.md                        # This file
```

### Running the Application

1. Run the program using the startup script:

**Windows:**

```bash
start_photobooth.bat
```

**Linux/Mac:**

```bash
./start_photobooth.sh
```

2. **Choose your email sending mode:**
   - Option 1: Gmail API (requires OAuth setup)
   - Option 2: SMTP (requires app password)

3. The appropriate version will start based on your selection

**Or manually (if virtual environment is already set up):**

```bash
# Activate virtual environment first
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# For Gmail API mode:
python photo_booth.py

# For SMTP mode:
python photo_booth_smtp.py
```

2. **Setup Steps:**

   **If using SMTP mode (recommended):**
   - Configure SMTP settings in the application (email + app password)
   - See [SMTP_SETUP.md](SMTP_SETUP.md) for detailed instructions

   **If using Gmail API mode:**
   - Place `credentials.json` in the application folder
   - See [GMAIL_API_SETUP.md](GMAIL_API_SETUP.md) for detailed instructions

   **Then, for both modes:**
   - Click "Browse" next to "Select Directory to Monitor" and choose the folder where photos will appear
   - Click "Browse" next to "Select Folder for Zip Files" and choose where you want zip files saved
   - Click "Browse" next to "Select Archive Folder" and choose where unsent photos should be archived (in case of sending failures)
   - Enter a recipient email address and click "Update Email"

3. **Operation:**
   - Place .jpg files in the monitored directory (or have your photo booth save them there)
   - Files will automatically be renamed to `<username>_<number>.jpg`
   - After 20 seconds of no new photos OR when email address changes, photos will be:
     - Zipped together
     - Emailed to the user
     - Deleted from the original directory
     - Zip file saved in the output directory

## Customization

### Email Content

Edit these sections in `photo_booth.py` (around line 265):

```python
# TODO: Customize your email subject here
subject = "Your Photo Booth Pictures!"

# TODO: Customize your email body here
body = """Thank you for using our photo booth!

Your photos are attached to this email.

Best regards,
The Photo Booth Team"""
```

## How It Handles Multiple Users

When a new email address is entered:

- Any pending photos from the previous email are immediately sent
- The counter resets and monitoring continues for the new email
- This prevents photos from getting mixed between different users

## Email Sending Failure Protection (Storage Mode)

The program automatically handles email sending failures (quota limits, authentication issues, network problems):

**When email sending fails:**

1. The program enters "Storage Mode"
2. Photos are still zipped but saved to the Archive directory instead of being sent
3. Each archived batch gets its own folder named: `unsent_<username>_<timestamp>`
4. A `SEND_TO.txt` file is created with:
   - Recipient email address
   - Timestamp
   - Number of photos
   - Sending method (API or SMTP)
   - Instructions for manual sending

**Archive folder structure:**

```
archive/
├── unsent_john_20240115_143022/
│   ├── photos_john_20240115_143022.zip
│   └── SEND_TO.txt
├── unsent_mary_20240115_143545/
│   ├── photos_mary_20240115_143545.zip
│   └── SEND_TO.txt
```

**Recovery:**

- When email sending recovers, the next successful send will notify you
- Use the helper scripts to send archived photos:
  - Run `send_archived.bat` (Windows) or `./send_archived.sh` (Linux/Mac)
  - Choose the same mode you used originally (API or SMTP)
- The program will continue working normally for new photo sessions

### Using the Helper Script to Send Archived Photos

When email sending is working again, use the startup script:

**Windows:**

```bash
send_archived.bat
```

**Linux/Mac:**

```bash
./send_archived.sh
```

**Select the mode that matches your setup:**

- Option 1: Gmail API
- Option 2: SMTP

**Or manually:**

```bash
# Activate virtual environment first
# For Gmail API mode:
python send_archived_photos.py

# For SMTP mode:
python send_archived_photos_smtp.py
```

The script will:

1. Scan your archive directory for unsent batches
2. Show you all archived batches with recipient info
3. Let you send all or specific batches
4. Move successfully sent batches to an `_sent` subfolder

## Troubleshooting

- **"credentials.json not found"**: Make sure you've downloaded your Gmail API credentials
- **Timer issues**: The 20-second timer resets each time a new photo is detected
- **File access errors**: Ensure the program has read/write permissions for both directories
- **Gmail API errors**: Check that the Gmail API is enabled in your Google Cloud project
- **"Storage Mode Active" warning**: Gmail API quota has been exceeded. Photos are being archived with recipient info. Check your archive folder and manually send when quota resets (usually daily)

## Notes

- The program must stay running for monitoring to work
- Zip files are kept in the output directory (not deleted)
- Original photos are deleted after successful email send
- Each photo gets a unique number suffix to prevent filename conflicts
