"""
Google Sheets Delivery Service
Appends lead data to Google Sheets
"""
import logging
import requests
from typing import Dict, Optional, List
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.utils.time import to_tehran_iso
logger = logging.getLogger(__name__)


class SheetsDeliveryService:
    """Service for delivering leads to Google Sheets"""
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    @staticmethod
    def deliver(
        spreadsheet_id: str,
        credentials_file: str,
        lead_data: List,
        sheet_name: str = "Leads"
    ) -> Dict[str, any]:
        """
        Append lead data to Google Sheet

        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            credentials_file: Path to service account credentials JSON (optional)
            lead_data: List of values to append as a row
            sheet_name: Sheet name/tab (default: "Leads")

        Returns:
            Dictionary with delivery result
        """
        try:
            logger.info(f"Appending to Google Sheet: {spreadsheet_id}")

            # Try to load credentials if file exists, otherwise use API key
            import os
            credentials = None

            if credentials_file and os.path.exists(credentials_file):
                # Load credentials
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_file,
                    scopes=SheetsDeliveryService.SCOPES
                )
                # Build service with credentials
                service = build('sheets', 'v4', credentials=credentials)
            else:
                # No credentials - try using Google Apps Script Web App approach
                # This requires the user to have set up a Web App script
                logger.info("No credentials found. Attempting Google Apps Script Web App method...")
                return SheetsDeliveryService._deliver_via_webapp(spreadsheet_id, lead_data)
            
            # Prepare the range
            range_name = f"{sheet_name}!A:Z"
            
            # Prepare the values
            values = [lead_data]
            
            body = {
                'values': values
            }
            
            # Append the data
            result = service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            updates = result.get('updates', {})
            updated_cells = updates.get('updatedCells', 0)
            
            success = updated_cells > 0
            
            response = {
                "success": success,
                "status_code": 200,
                "response_body": f"Updated {updated_cells} cells",
                "updated_range": updates.get('updatedRange'),
                "delivery_method": "google_sheets",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if success:
                logger.info(f"Google Sheets delivery successful: {updated_cells} cells updated")
            else:
                logger.warning("Google Sheets delivery failed: No cells updated")
            
            return response
            
        except HttpError as e:
            logger.error(f"Google Sheets HTTP error: {str(e)}")
            return {
                "success": False,
                "status_code": e.resp.status if hasattr(e, 'resp') else 0,
                "response_body": f"HTTP Error: {str(e)}",
                "delivery_method": "google_sheets",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except FileNotFoundError as e:
            logger.error(f"Credentials file not found: {credentials_file}")
            return {
                "success": False,
                "status_code": 0,
                "response_body": (
                    "Google Sheets credentials.json file not found!\n\n"
                    f"Expected location: {credentials_file}\n\n"
                    "Setup guide: /root/leadex-project/GOOGLE_SHEETS_SETUP.md\n\n"
                    "Follow the 5-minute setup to enable Google Sheets delivery."
                ),
                "delivery_method": "google_sheets",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Google Sheets error: {str(e)}", exc_info=True)
            return {
                "success": False,
                "status_code": 0,
                "response_body": f"Error: {str(e)}",
                "delivery_method": "google_sheets",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def format_row_data(lead, client) -> List:
        """
        Format lead data as a row for Google Sheets

        Sends only essential client-facing fields (7 fields total).
        Full data is still stored in database and visible in admin panel.

        Args:
            lead: Asset (Lead) object
            client: Client object

        Returns:
            List of values for spreadsheet row (7 fields)
        """
        return [
            str(lead.id),
            lead.mobile,
            lead.name or "",
            lead.email or "",
            client.name,
            to_tehran_iso(lead.created_at) if lead.created_at else "",
            lead.ip or ""
        ]
    
    @staticmethod
    def get_header_row() -> List[str]:
        """
        Get the header row for Google Sheets

        Returns:
            List of column headers (7 fields)
        """
        return [
            "Lead ID",
            "Mobile",
            "Name",
            "Email",
            "Client",
            "Date",
            "IP"
        ]

    @staticmethod
    def _deliver_via_webapp(spreadsheet_id: str, lead_data: List) -> Dict[str, any]:
        """
        Deliver lead to Google Sheets via Google Apps Script Web App

        This method uses a webhook approach that doesn't require service account credentials.
        The user must set up a Google Apps Script Web App that accepts POST requests.

        Instructions for user:
        1. Open your Google Sheet
        2. Go to Extensions > Apps Script
        3. Create a new script with this code:

        function doPost(e) {
          var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Leads');
          if (!sheet) {
            sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
          }

          var data = JSON.parse(e.postData.contents);
          sheet.appendRow(data.values);

          return ContentService.createTextOutput(JSON.stringify({
            'success': true,
            'message': 'Lead added successfully'
          })).setMimeType(ContentService.MimeType.JSON);
        }

        4. Deploy as Web App (Anyone can access)
        5. Copy the Web App URL and save it in your client's webhook_url field

        Args:
            spreadsheet_id: Not used in this method (kept for compatibility)
            lead_data: List of values to append as a row

        Returns:
            Dictionary with delivery result
        """
        try:
            # For now, return an instructive error
            # The user needs to set up the Web App and use webhook_url instead
            return {
                "success": False,
                "status_code": 0,
                "response_body": (
                    "Google Sheets authentication required!\n\n"
                    "Setup guide: /root/leadex-project/GOOGLE_SHEETS_SETUP.md\n\n"
                    "Quick steps:\n"
                    "1. Create Google Cloud service account\n"
                    "2. Download credentials.json to /root/leadex-project/\n"
                    "3. Share your Google Sheet with service account email\n"
                    "4. Restart server\n\n"
                    "Setup time: ~5 minutes"
                ),
                "delivery_method": "google_sheets",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Google Sheets webapp error: {str(e)}")
            return {
                "success": False,
                "status_code": 0,
                "response_body": f"Error: {str(e)}",
                "delivery_method": "google_sheets",
                "timestamp": datetime.utcnow().isoformat()
            }

