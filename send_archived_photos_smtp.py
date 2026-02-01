#!/usr/bin/env python3
"""
Helper script to send archived photos via SMTP after sending failures.

This script scans the archive directory for unsent photo batches and 
allows you to send them via SMTP.

Usage:
    python send_archived_photos_smtp.py
"""

import os
import sys
from pathlib import Path
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import json
import shutil

def load_smtp_config():
    """Load SMTP configuration from file"""
    if not os.path.exists('smtp_config.json'):
        print("ERROR: smtp_config.json not found!")
        print("Please run the main photo booth application first and configure SMTP settings.")
        return None
    
    try:
        with open('smtp_config.json', 'r') as f:
            config = json.load(f)
            return config
    except Exception as e:
        print(f"ERROR: Failed to load SMTP config: {e}")
        return None


def send_email_with_attachment(smtp_config, to_email, attachment_path):
    """Send email using SMTP with attachment"""
    
    # TODO: Customize your email subject here
    subject = "Your Photo Booth Pictures!"
    
    # TODO: Customize your email body here  
    body = """Thank you for using our photo booth!

Your photos are attached to this email.

Best regards,
The Photo Booth Team"""
    
    # Create message
    message = MIMEMultipart()
    message['From'] = smtp_config['email']
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
    server = smtplib.SMTP(smtp_config.get('server', 'smtp.gmail.com'), 
                          smtp_config.get('port', 587))
    server.starttls()
    server.login(smtp_config['email'], smtp_config['password'])
    server.send_message(message)
    server.quit()
    
    return True


def read_metadata(folder_path):
    """Read the SEND_TO.txt metadata file"""
    metadata_path = os.path.join(folder_path, "SEND_TO.txt")
    
    if not os.path.exists(metadata_path):
        return None
    
    metadata = {}
    with open(metadata_path, 'r') as f:
        for line in f:
            if line.startswith("RECIPIENT EMAIL:"):
                metadata['email'] = line.split(":", 1)[1].strip()
            elif line.startswith("ZIP FILE:"):
                metadata['zip_file'] = line.split(":", 1)[1].strip()
            elif line.startswith("NUMBER OF PHOTOS:"):
                metadata['photo_count'] = line.split(":", 1)[1].strip()
            elif line.startswith("METHOD:"):
                metadata['method'] = line.split(":", 1)[1].strip()
    
    return metadata


def find_archived_batches(archive_directory):
    """Find all unsent photo batches in the archive directory"""
    batches = []
    
    if not os.path.exists(archive_directory):
        print(f"Archive directory not found: {archive_directory}")
        return batches
    
    for item in os.listdir(archive_directory):
        item_path = os.path.join(archive_directory, item)
        if os.path.isdir(item_path) and item.startswith('unsent_'):
            metadata = read_metadata(item_path)
            if metadata:
                batches.append({
                    'folder': item_path,
                    'folder_name': item,
                    'metadata': metadata
                })
    
    return batches


def main():
    print("=" * 60)
    print("Photo Booth - Archived Photos Sender (SMTP)")
    print("=" * 60)
    print()
    
    # Load SMTP configuration
    print("Loading SMTP configuration...")
    smtp_config = load_smtp_config()
    
    if not smtp_config:
        return
    
    print(f"Using SMTP account: {smtp_config['email']}")
    print()
    
    # Get archive directory from user
    archive_dir = input("Enter the path to your archive directory: ").strip()
    
    if not os.path.exists(archive_dir):
        print(f"ERROR: Directory not found: {archive_dir}")
        return
    
    # Find all archived batches
    batches = find_archived_batches(archive_dir)
    
    if not batches:
        print("No archived photo batches found!")
        return
    
    print(f"\nFound {len(batches)} archived batch(es):")
    print()
    
    for i, batch in enumerate(batches, 1):
        meta = batch['metadata']
        print(f"{i}. Folder: {batch['folder_name']}")
        print(f"   Email: {meta.get('email', 'Unknown')}")
        print(f"   Photos: {meta.get('photo_count', 'Unknown')}")
        print(f"   Zip: {meta.get('zip_file', 'Unknown')}")
        print(f"   Method: {meta.get('method', 'Unknown')}")
        print()
    
    # Ask user what to do
    print("Options:")
    print("1. Send all archived batches")
    print("2. Send specific batch")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '3':
        print("Exiting...")
        return
    
    # Determine which batches to send
    batches_to_send = []
    
    if choice == '1':
        batches_to_send = batches
    elif choice == '2':
        batch_num = input(f"Enter batch number (1-{len(batches)}): ").strip()
        try:
            idx = int(batch_num) - 1
            if 0 <= idx < len(batches):
                batches_to_send = [batches[idx]]
            else:
                print("Invalid batch number!")
                return
        except ValueError:
            print("Invalid input!")
            return
    else:
        print("Invalid choice!")
        return
    
    # Create a 'sent' subdirectory in archive
    sent_dir = os.path.join(archive_dir, '_sent')
    os.makedirs(sent_dir, exist_ok=True)
    
    # Send the batches
    print(f"\nSending {len(batches_to_send)} batch(es)...")
    print()
    
    success_count = 0
    fail_count = 0
    
    for batch in batches_to_send:
        meta = batch['metadata']
        email = meta.get('email')
        zip_file = meta.get('zip_file')
        zip_path = os.path.join(batch['folder'], zip_file)
        
        print(f"Sending to {email}... ", end='', flush=True)
        
        try:
            if not os.path.exists(zip_path):
                print(f"FAILED - Zip file not found!")
                fail_count += 1
                continue
            
            send_email_with_attachment(smtp_config, email, zip_path)
            print("SUCCESS!")
            success_count += 1
            
            # Move the folder to 'sent' subdirectory
            sent_folder_path = os.path.join(sent_dir, os.path.basename(batch['folder']))
            shutil.move(batch['folder'], sent_folder_path)
            
        except Exception as e:
            print(f"FAILED - {str(e)}")
            fail_count += 1
    
    print()
    print("=" * 60)
    print(f"Results: {success_count} sent, {fail_count} failed")
    print("=" * 60)
    
    if success_count > 0:
        print(f"\nSent batches have been moved to: {sent_dir}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        print(f"\nERROR: {str(e)}")
