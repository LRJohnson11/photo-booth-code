import os
import time
import shutil
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import zipfile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import json

class PhotoBoothApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Booth Email System (SMTP)")
        self.root.geometry("500x500")
        
        self.watch_directory = None
        self.zip_output_directory = None
        self.archive_directory = None
        self.current_email = None
        self.observer = None
        self.photo_files = []
        self.file_counter = 0
        self.timer = None
        self.storage_mode = False  # Tracks if we're in fallback storage mode
        
        # SMTP configuration
        self.smtp_email = None
        self.smtp_password = None
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        self.setup_ui()
        self.load_smtp_config()
        
    def setup_ui(self):
        # SMTP Configuration Section
        tk.Label(self.root, text="SMTP Email Configuration", font=("Arial", 14, "bold")).pack(pady=10)
        
        smtp_frame = tk.Frame(self.root)
        smtp_frame.pack(pady=5)
        
        tk.Label(smtp_frame, text="Gmail Address:", font=("Arial", 10)).grid(row=0, column=0, sticky='e', padx=5)
        self.smtp_email_entry = tk.Entry(smtp_frame, width=30, font=("Arial", 10))
        self.smtp_email_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(smtp_frame, text="App Password:", font=("Arial", 10)).grid(row=1, column=0, sticky='e', padx=5)
        self.smtp_password_entry = tk.Entry(smtp_frame, width=30, font=("Arial", 10), show="*")
        self.smtp_password_entry.grid(row=1, column=1, padx=5)
        
        tk.Button(smtp_frame, text="Save SMTP Config", command=self.save_smtp_config,
                 bg="#2196F3", fg="white", font=("Arial", 10)).grid(row=2, column=0, columnspan=2, pady=5)
        
        tk.Label(self.root, text="─" * 50, font=("Arial", 8)).pack(pady=5)
        
        # Directory selection
        tk.Label(self.root, text="Select Directory to Monitor:", font=("Arial", 12)).pack(pady=10)
        
        dir_frame = tk.Frame(self.root)
        dir_frame.pack(pady=5)
        
        self.dir_label = tk.Label(dir_frame, text="No directory selected", fg="gray")
        self.dir_label.pack(side=tk.LEFT, padx=5)
        
        tk.Button(dir_frame, text="Browse", command=self.select_directory).pack(side=tk.LEFT)
        
        # Zip output directory selection
        tk.Label(self.root, text="Select Folder for Zip Files:", font=("Arial", 12)).pack(pady=10)
        
        zip_frame = tk.Frame(self.root)
        zip_frame.pack(pady=5)
        
        self.zip_label = tk.Label(zip_frame, text="No directory selected", fg="gray")
        self.zip_label.pack(side=tk.LEFT, padx=5)
        
        tk.Button(zip_frame, text="Browse", command=self.select_zip_directory).pack(side=tk.LEFT)
        
        # Archive directory selection (for failed sends)
        tk.Label(self.root, text="Select Archive Folder (for unsent photos):", font=("Arial", 12)).pack(pady=10)
        
        archive_frame = tk.Frame(self.root)
        archive_frame.pack(pady=5)
        
        self.archive_label = tk.Label(archive_frame, text="No directory selected", fg="gray")
        self.archive_label.pack(side=tk.LEFT, padx=5)
        
        tk.Button(archive_frame, text="Browse", command=self.select_archive_directory).pack(side=tk.LEFT)
        
        # Email input
        tk.Label(self.root, text="Enter Recipient Email Address:", font=("Arial", 12)).pack(pady=10)
        
        self.email_entry = tk.Entry(self.root, width=40, font=("Arial", 12))
        self.email_entry.pack(pady=5)
        self.email_entry.bind('<Return>', lambda e: self.update_email())
        
        tk.Button(self.root, text="Update Email", command=self.update_email, 
                 bg="#4CAF50", fg="white", font=("Arial", 11)).pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Status: Configure SMTP settings first...", 
                                     font=("Arial", 10), fg="blue")
        self.status_label.pack(pady=10)
        
    def load_smtp_config(self):
        """Load SMTP configuration from file"""
        if os.path.exists('smtp_config.json'):
            try:
                with open('smtp_config.json', 'r') as f:
                    config = json.load(f)
                    self.smtp_email = config.get('email')
                    self.smtp_password = config.get('password')
                    self.smtp_server = config.get('server', 'smtp.gmail.com')
                    self.smtp_port = config.get('port', 587)
                    
                    if self.smtp_email:
                        self.smtp_email_entry.insert(0, self.smtp_email)
                    if self.smtp_password:
                        self.smtp_password_entry.insert(0, self.smtp_password)
                        
                    self.status_label.config(text="SMTP config loaded. Ready to start!", fg="green")
            except Exception as e:
                print(f"Error loading SMTP config: {e}")
    
    def save_smtp_config(self):
        """Save SMTP configuration to file"""
        email = self.smtp_email_entry.get().strip()
        password = self.smtp_password_entry.get().strip()
        
        if not email or not password:
            messagebox.showwarning("Warning", "Please enter both email and password")
            return
        
        if '@' not in email:
            messagebox.showwarning("Warning", "Please enter a valid email address")
            return
        
        self.smtp_email = email
        self.smtp_password = password
        
        config = {
            'email': self.smtp_email,
            'password': self.smtp_password,
            'server': self.smtp_server,
            'port': self.smtp_port
        }
        
        try:
            with open('smtp_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            messagebox.showinfo("Success", "SMTP configuration saved!")
            self.status_label.config(text="SMTP configured. Select directories and enter recipient email.", fg="green")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {str(e)}")
    
    def select_directory(self):
        directory = filedialog.askdirectory(title="Select Directory to Monitor")
        if directory:
            self.watch_directory = directory
            self.dir_label.config(text=f"...{directory[-30:]}", fg="black")
            self.start_monitoring()
            
    def select_zip_directory(self):
        directory = filedialog.askdirectory(title="Select Directory for Zip Files")
        if directory:
            self.zip_output_directory = directory
            self.zip_label.config(text=f"...{directory[-30:]}", fg="black")
    
    def select_archive_directory(self):
        directory = filedialog.askdirectory(title="Select Archive Directory for Unsent Photos")
        if directory:
            self.archive_directory = directory
            self.archive_label.config(text=f"...{directory[-30:]}", fg="black")
            
    def update_email(self):
        new_email = self.email_entry.get().strip()
        
        if not new_email:
            messagebox.showwarning("Warning", "Please enter a valid email address")
            return
            
        if '@' not in new_email:
            messagebox.showwarning("Warning", "Please enter a valid email address")
            return
        
        # If email changed and we have pending photos, send them first
        if self.current_email and self.current_email != new_email and self.photo_files:
            self.status_label.config(text=f"Email changed. Sending photos to {self.current_email}...")
            self.send_photos()
        
        self.current_email = new_email
        self.status_label.config(text=f"Monitoring for: {self.current_email}")
        
    def start_monitoring(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        event_handler = PhotoEventHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.watch_directory, recursive=False)
        self.observer.start()
        self.status_label.config(text="Monitoring directory for new photos...")
        
    def reset_timer(self):
        """Reset the 20-second timer"""
        if self.timer:
            self.timer.cancel()
        
        if self.photo_files:  # Only set timer if we have photos
            self.timer = threading.Timer(20.0, self.on_timer_expire)
            self.timer.start()
    
    def on_timer_expire(self):
        """Called when 20 seconds pass with no new photos"""
        if self.photo_files:
            self.status_label.config(text="Timer expired. Sending photos...")
            self.send_photos()
    
    def handle_new_photo(self, filepath):
        """Handle a new photo file"""
        if not self.current_email:
            self.status_label.config(text="Please enter an email address first!", fg="red")
            return
        
        if not self.zip_output_directory:
            self.status_label.config(text="Please select a zip output directory first!", fg="red")
            return
        
        if not self.archive_directory:
            self.status_label.config(text="Please select an archive directory first!", fg="red")
            return
        
        if not self.smtp_email or not self.smtp_password:
            self.status_label.config(text="Please configure SMTP settings first!", fg="red")
            return
        
        # Extract username from email
        username = self.current_email.split('@')[0]
        
        # Generate new filename with counter to avoid duplicates
        self.file_counter += 1
        new_filename = f"{username}_{self.file_counter}.jpg"
        new_filepath = os.path.join(self.watch_directory, new_filename)
        
        # Wait a moment to ensure file is fully written
        time.sleep(0.5)
        
        # Rename the file
        try:
            os.rename(filepath, new_filepath)
            self.photo_files.append(new_filepath)
            self.status_label.config(
                text=f"Captured photo {self.file_counter} for {self.current_email}", 
                fg="green"
            )
            
            # Reset the 20-second timer
            self.reset_timer()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rename file: {str(e)}")
    
    def send_photos(self):
        """Zip photos and send via SMTP, or archive if sending fails"""
        if not self.photo_files or not self.current_email:
            return
        
        try:
            # Create zip file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_filename = f"photos_{self.current_email.split('@')[0]}_{timestamp}.zip"
            zip_path = os.path.join(self.zip_output_directory, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for photo in self.photo_files:
                    zipf.write(photo, os.path.basename(photo))
            
            # Attempt to send email via SMTP
            send_success = False
            try:
                self.send_email_with_attachment(self.current_email, zip_path)
                send_success = True
                
                # If we were in storage mode but this send succeeded, try to recover
                if self.storage_mode:
                    self.status_label.config(
                        text=f"SMTP recovered! Sent to {self.current_email}. Check archive for unsent photos.",
                        fg="green"
                    )
                    self.storage_mode = False
                else:
                    self.status_label.config(
                        text=f"Sent {len(self.photo_files)} photos to {self.current_email}!", 
                        fg="blue"
                    )
                
            except Exception as e:
                # SMTP failed - enter storage mode
                print(f"SMTP Error: {str(e)}")
                self.storage_mode = True
                
                # Archive the zip file with metadata
                self.archive_unsent_photos(zip_path, self.current_email)
                
                self.status_label.config(
                    text=f"SMTP failed! Photos archived for {self.current_email}. Storage mode active.",
                    fg="orange"
                )
                
                messagebox.showwarning(
                    "Storage Mode Active",
                    f"SMTP sending failed. Photos have been archived to:\n{self.archive_directory}\n\n"
                    f"Email address and metadata saved. You'll need to manually send these later.\n\n"
                    f"Error: {str(e)}"
                )
            
            # Clean up: delete original photos from watch directory
            for photo in self.photo_files:
                try:
                    os.remove(photo)
                except Exception as e:
                    print(f"Error deleting {photo}: {e}")
            
            # Reset for next session
            self.photo_files = []
            self.file_counter = 0
            if self.timer:
                self.timer.cancel()
                self.timer = None
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process photos: {str(e)}")
            self.status_label.config(text=f"Error processing photos: {str(e)}", fg="red")
    
    def archive_unsent_photos(self, zip_path, email_address):
        """Archive unsent photos with metadata about recipient"""
        try:
            # Create a unique archive folder for this batch
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_batch_folder = os.path.join(
                self.archive_directory, 
                f"unsent_{email_address.split('@')[0]}_{timestamp}"
            )
            os.makedirs(archive_batch_folder, exist_ok=True)
            
            # Move zip file to archive
            archive_zip_path = os.path.join(archive_batch_folder, os.path.basename(zip_path))
            shutil.move(zip_path, archive_zip_path)
            
            # Create metadata file with recipient info
            metadata_path = os.path.join(archive_batch_folder, "SEND_TO.txt")
            with open(metadata_path, 'w') as f:
                f.write(f"RECIPIENT EMAIL: {email_address}\n")
                f.write(f"TIMESTAMP: {timestamp}\n")
                f.write(f"ZIP FILE: {os.path.basename(zip_path)}\n")
                f.write(f"NUMBER OF PHOTOS: {len(self.photo_files)}\n")
                f.write(f"METHOD: SMTP\n")
                f.write(f"\nINSTRUCTIONS:\n")
                f.write(f"SMTP sending failed when trying to send these photos.\n")
                f.write(f"Please manually send the zip file to: {email_address}\n")
            
            print(f"Archived unsent photos to: {archive_batch_folder}")
            
        except Exception as e:
            print(f"Error archiving photos: {str(e)}")
            messagebox.showerror("Archive Error", f"Failed to archive photos: {str(e)}")
    
    def send_email_with_attachment(self, to_email, attachment_path):
        """Send email using SMTP with attachment - raises exception on failure"""
        
        # TODO: Customize your email subject here
        subject = "Your Photo Booth Pictures!"
        
        # TODO: Customize your email body here
        body = """Thank you for using our photo booth!

Your photos are attached to this email.

Best regards,
The Photo Booth Team"""
        
        # Create message
        message = MIMEMultipart()
        message['From'] = self.smtp_email
        message['To'] = to_email
        message['Subject'] = subject
        
        # Add body
        message.attach(MIMEText(body, 'plain'))
        
        # Add attachment
        with open(attachment_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 
                          f'attachment; filename={os.path.basename(attachment_path)}')
            message.attach(part)
        
        # Send the email via SMTP
        try:
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Secure the connection
            
            # Login
            server.login(self.smtp_email, self.smtp_password)
            
            # Send email
            server.send_message(message)
            
            # Close connection
            server.quit()
            
            print(f"Email sent successfully to {to_email} via SMTP")
            return True
            
        except smtplib.SMTPAuthenticationError:
            raise Exception("SMTP Authentication failed. Check your email and app password.")
        except smtplib.SMTPRecipientsRefused:
            raise Exception(f"Recipient {to_email} was refused by the server.")
        except smtplib.SMTPSenderRefused:
            raise Exception("Sender email was refused by the server.")
        except smtplib.SMTPDataError as e:
            raise Exception(f"SMTP Data error: {str(e)}")
        except Exception as e:
            raise Exception(f"SMTP error: {str(e)}")
    
    def on_closing(self):
        """Clean up when closing the application"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        if self.timer:
            self.timer.cancel()
        self.root.destroy()


class PhotoEventHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app
        
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.jpg'):
            # Run in a separate thread to avoid blocking the observer
            threading.Thread(target=self.app.handle_new_photo, 
                           args=(event.src_path,)).start()


def main():
    root = tk.Tk()
    app = PhotoBoothApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
