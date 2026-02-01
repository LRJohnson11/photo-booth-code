#!/usr/bin/env python3
"""
Helper script to send archived photos after Gmail API quota recovers.

This script scans the archive directory for unsent photo batches and 
allows you to send them via Gmail API.

Usage:
    python send_archived_photos.py
"""

import os
import sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import base64
import json
import shutil

SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def setup_gmail_api():
    """Set up Gmail API authentication"""
    creds = None
    if os.path.exists('token.json'):
        with open('token.json', 'r') as token:
            token_data = json.load(token)
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists('credentials.json'):
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            else:
                print("ERROR: credentials.json not found!")
                return None
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)


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
    
    return metadata


def send_email_with_attachment(service, to_email, attachment_path):
    """Send email using Gmail API with attachment"""
    
    # TODO: Customize your email subject here
    subject = "Your Photo Booth Pictures!"
    
    # TODO: Customize your email body here  
    body = """Thank you for using our photo booth!

Your photos are attached to this email.

Best regards,
The Photo Booth Team"""
    
    message = MIMEMultipart()
    message['to'] = to_email
    message['subject'] = subject
    
    message.attach(MIMEText(body, 'plain'))
    
    # Add attachment
    with open(attachment_path, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 
                      f'attachment; filename={os.path.basename(attachment_path)}')
        message.attach(part)
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    send_message = {'raw': raw_message}
    
    result = service.users().messages().send(
        userId='me', body=send_message).execute()
    
    if not result or 'id' not in result:
        raise Exception("Gmail API did not return a valid message ID")
    
    return result


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
    print("Photo Booth - Archived Photos Sender")
    print("=" * 60)
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
    
    # Set up Gmail API
    print("\nSetting up Gmail API...")
    service = setup_gmail_api()
    
    if not service:
        print("Failed to set up Gmail API!")
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
            
            send_email_with_attachment(service, email, zip_path)
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