import imaplib
import email
import os
import time
from pathlib import Path
from typing import List, Tuple
from loguru import logger
from app.core.config import settings
import httpx
import asyncio

class EmailMonitor:
    """Email monitoring service for CSV attachments"""
    
    def __init__(self):
        self.host = settings.EMAIL_HOST
        self.port = settings.EMAIL_PORT
        self.username = settings.EMAIL_USERNAME
        self.password = settings.EMAIL_PASSWORD
        self.use_ssl = settings.EMAIL_USE_SSL
        self.storage_path = Path(settings.CSV_STORAGE_PATH)
        self.api_url = f"http://csv-processor:{settings.API_PORT}"
        
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def start_monitoring(self):
        """Start monitoring emails for CSV attachments"""
        logger.info("Starting email monitoring service")
        
        while True:
            try:
                await self.check_for_new_emails()
                logger.info(f"Sleeping for {settings.EMAIL_CHECK_INTERVAL} seconds")
                await asyncio.sleep(settings.EMAIL_CHECK_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in email monitoring: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def check_for_new_emails(self):
        """Check for new emails with CSV attachments"""
        try:
            # Connect to email server
            if self.use_ssl:
                mail = imaplib.IMAP4_SSL(self.host, self.port)
            else:
                mail = imaplib.IMAP4(self.host, self.port)
            
            # Login
            mail.login(self.username, self.password)
            logger.info("Connected to email server")
            
            # Select inbox
            mail.select('inbox')
            
            # Search for unread emails
            status, messages = mail.search(None, 'UNSEEN')
            
            if status == 'OK':
                message_ids = messages[0].split()
                logger.info(f"Found {len(message_ids)} unread emails")
                
                for msg_id in message_ids:
                    await self.process_email(mail, msg_id)
            
            # Close connection
            mail.close()
            mail.logout()
            
        except Exception as e:
            logger.error(f"Error checking emails: {str(e)}")
    
    async def process_email(self, mail: imaplib.IMAP4_SSL, msg_id: bytes):
        """Process individual email for CSV attachments"""
        try:
            # Fetch email
            status, msg_data = mail.fetch(msg_id, '(RFC822)')
            
            if status != 'OK':
                return
            
            # Parse email
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            subject = email_message['subject'] or "No Subject"
            from_address = email_message['from'] or "Unknown Sender"
            
            logger.info(f"Processing email: '{subject}' from {from_address}")
            
            # Look for CSV attachments
            csv_files = self.extract_csv_attachments(email_message)
            
            if csv_files:
                logger.info(f"Found {len(csv_files)} CSV files in email")
                
                for csv_file in csv_files:
                    # Save CSV file
                    file_path = self.storage_path / csv_file['filename']
                    
                    with open(file_path, 'wb') as f:
                        f.write(csv_file['content'])
                    
                    logger.info(f"Saved CSV file: {file_path}")
                    
                    # Process CSV via API
                    await self.process_csv_via_api(file_path)
            
        except Exception as e:
            logger.error(f"Error processing email {msg_id}: {str(e)}")
    
    def extract_csv_attachments(self, email_message) -> List[dict]:
        """Extract CSV attachments from email"""
        csv_files = []
        
        try:
            for part in email_message.walk():
                content_disposition = str(part.get("Content-Disposition"))
                
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    
                    if filename and filename.lower().endswith('.csv'):
                        content = part.get_payload(decode=True)
                        
                        if content:
                            csv_files.append({
                                'filename': filename,
                                'content': content
                            })
                            logger.info(f"Found CSV attachment: {filename}")
                        
        except Exception as e:
            logger.error(f"Error extracting attachments: {str(e)}")
        
        return csv_files
    
    async def process_csv_via_api(self, file_path: Path):
        """Send CSV to processing API"""
        try:
            logger.info(f"Sending {file_path} to processing API")
            
            async with httpx.AsyncClient() as client:
                with open(file_path, 'rb') as f:
                    files = {'file': (file_path.name, f, 'text/csv')}
                    
                    response = await client.post(
                        f"{self.api_url}/process-csv",
                        files=files,
                        timeout=300  # 5 minutes timeout
                    )
                
                if response.status_code == 200:
                    # Save processed file
                    output_path = file_path.parent / f"enriched_{file_path.name}"
                    
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    
                    logger.info(f"Successfully processed and saved: {output_path}")
                else:
                    logger.error(f"API processing failed: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"Error processing CSV via API: {str(e)}")

async def main():
    """Main function for email monitoring"""
    monitor = EmailMonitor()
    await monitor.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main()) 