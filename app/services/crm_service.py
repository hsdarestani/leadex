"""
CRM Integration Service
Handles Salesforce, HubSpot, and Zoho CRM integrations
"""
import hmac
import hashlib
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.integration import CRMIntegration, CRMSyncLog


class CRMService:
    """Service for CRM integrations"""

    def __init__(self, db: Session):
        self.db = db

    # Salesforce Integration
    def sync_to_salesforce(self, integration: CRMIntegration, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync lead to Salesforce CRM

        Args:
            integration: CRM integration configuration
            lead_data: Lead data to sync

        Returns:
            Sync result
        """
        try:
            # Salesforce API endpoint
            url = f"{integration.instance_url}/services/data/v57.0/sobjects/Lead"

            # Map fields based on config
            salesforce_data = self._map_fields(lead_data, integration.config.get('field_mapping', {}))

            # Prepare headers
            headers = {
                'Authorization': f'Bearer {integration.access_token}',
                'Content-Type': 'application/json'
            }

            # Send to Salesforce
            response = requests.post(url, json=salesforce_data, headers=headers, timeout=30)

            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'crm_id': response.json().get('id'),
                    'message': 'Lead synced to Salesforce successfully'
                }
            else:
                return {
                    'success': False,
                    'error': f'Salesforce API error: {response.text}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    # HubSpot Integration
    def sync_to_hubspot(self, integration: CRMIntegration, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync lead to HubSpot CRM

        Args:
            integration: CRM integration configuration
            lead_data: Lead data to sync

        Returns:
            Sync result
        """
        try:
            # HubSpot API endpoint
            url = "https://api.hubapi.com/crm/v3/objects/contacts"

            # Map fields to HubSpot format
            hubspot_properties = self._map_to_hubspot(lead_data, integration.config.get('field_mapping', {}))

            # Prepare payload
            payload = {
                'properties': hubspot_properties
            }

            # Prepare headers
            headers = {
                'Authorization': f'Bearer {integration.api_key}',
                'Content-Type': 'application/json'
            }

            # Send to HubSpot
            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'crm_id': response.json().get('id'),
                    'message': 'Lead synced to HubSpot successfully'
                }
            else:
                return {
                    'success': False,
                    'error': f'HubSpot API error: {response.text}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    # Zoho Integration
    def sync_to_zoho(self, integration: CRMIntegration, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync lead to Zoho CRM

        Args:
            integration: CRM integration configuration
            lead_data: Lead data to sync

        Returns:
            Sync result
        """
        try:
            # Zoho API endpoint
            url = "https://www.zohoapis.com/crm/v3/Leads"

            # Map fields to Zoho format
            zoho_data = self._map_to_zoho(lead_data, integration.config.get('field_mapping', {}))

            # Prepare payload
            payload = {
                'data': [zoho_data]
            }

            # Prepare headers
            headers = {
                'Authorization': f'Zoho-oauthtoken {integration.access_token}',
                'Content-Type': 'application/json'
            }

            # Send to Zoho
            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code in [200, 201]:
                result = response.json()
                if result.get('data') and len(result['data']) > 0:
                    return {
                        'success': True,
                        'crm_id': result['data'][0].get('details', {}).get('id'),
                        'message': 'Lead synced to Zoho successfully'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Zoho sync failed: No data returned'
                    }
            else:
                return {
                    'success': False,
                    'error': f'Zoho API error: {response.text}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    # Generic sync method
    def sync_lead_to_crm(self, integration_id: str, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync lead to configured CRM

        Args:
            integration_id: CRM integration ID
            lead_data: Lead data to sync

        Returns:
            Sync result
        """
        # Get integration
        integration = self.db.query(CRMIntegration).filter(
            CRMIntegration.id == integration_id,
            CRMIntegration.is_active == True,
            CRMIntegration.sync_enabled == True
        ).first()

        if not integration:
            return {
                'success': False,
                'error': 'CRM integration not found or not active'
            }

        # Create sync log
        sync_log = CRMSyncLog(
            integration_id=integration.id,
            sync_type='manual',
            direction='outbound',
            status='pending',
            records_processed=1
        )
        self.db.add(sync_log)
        self.db.commit()

        start_time = datetime.utcnow()

        try:
            # Route to appropriate CRM
            if integration.crm_type == 'salesforce':
                result = self.sync_to_salesforce(integration, lead_data)
            elif integration.crm_type == 'hubspot':
                result = self.sync_to_hubspot(integration, lead_data)
            elif integration.crm_type == 'zoho':
                result = self.sync_to_zoho(integration, lead_data)
            else:
                result = {
                    'success': False,
                    'error': f'Unsupported CRM type: {integration.crm_type}'
                }

            # Update sync log
            sync_log.completed_at = datetime.utcnow()
            sync_log.duration_seconds = int((sync_log.completed_at - start_time).total_seconds())

            if result['success']:
                sync_log.status = 'success'
                sync_log.records_succeeded = 1
                integration.last_sync_at = datetime.utcnow()
                integration.last_sync_status = 'success'
            else:
                sync_log.status = 'failed'
                sync_log.records_failed = 1
                sync_log.error_message = result.get('error', 'Unknown error')
                integration.last_sync_status = 'failed'
                integration.last_error = result.get('error')

            self.db.commit()
            return result

        except Exception as e:
            sync_log.status = 'failed'
            sync_log.error_message = str(e)
            sync_log.completed_at = datetime.utcnow()
            integration.last_sync_status = 'failed'
            integration.last_error = str(e)
            self.db.commit()

            return {
                'success': False,
                'error': str(e)
            }

    # Helper methods for field mapping
    def _map_fields(self, data: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
        """Map fields based on configuration"""
        if not mapping:
            # Default mapping
            return {
                'FirstName': data.get('name', '').split()[0] if data.get('name') else '',
                'LastName': data.get('name', '').split()[-1] if data.get('name') else 'Unknown',
                'Phone': data.get('mobile', ''),
                'Email': data.get('email', ''),
                'LeadSource': data.get('utm_source', 'Web'),
                'Company': data.get('company', 'N/A')
            }

        # Custom mapping
        result = {}
        for target_field, source_field in mapping.items():
            result[target_field] = data.get(source_field, '')
        return result

    def _map_to_hubspot(self, data: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
        """Map fields to HubSpot format"""
        if not mapping:
            name_parts = data.get('name', '').split() if data.get('name') else ['', 'Unknown']
            return {
                'firstname': name_parts[0],
                'lastname': name_parts[-1] if len(name_parts) > 1 else 'Unknown',
                'phone': data.get('mobile', ''),
                'email': data.get('email', ''),
                'hs_lead_status': 'NEW',
                'lifecyclestage': 'lead'
            }

        # Custom mapping
        result = {}
        for target_field, source_field in mapping.items():
            result[target_field] = data.get(source_field, '')
        return result

    def _map_to_zoho(self, data: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
        """Map fields to Zoho format"""
        if not mapping:
            name_parts = data.get('name', '').split() if data.get('name') else ['', 'Unknown']
            return {
                'First_Name': name_parts[0],
                'Last_Name': name_parts[-1] if len(name_parts) > 1 else 'Unknown',
                'Phone': data.get('mobile', ''),
                'Email': data.get('email', ''),
                'Lead_Source': data.get('utm_source', 'Website'),
                'Lead_Status': 'Not Contacted'
            }

        # Custom mapping
        result = {}
        for target_field, source_field in mapping.items():
            result[target_field] = data.get(source_field, '')
        return result

    # Test connection
    def test_crm_connection(self, integration: CRMIntegration) -> Dict[str, Any]:
        """Test CRM connection"""
        try:
            if integration.crm_type == 'salesforce':
                url = f"{integration.instance_url}/services/data/v57.0/"
                headers = {'Authorization': f'Bearer {integration.access_token}'}
            elif integration.crm_type == 'hubspot':
                url = "https://api.hubapi.com/crm/v3/objects/contacts?limit=1"
                headers = {'Authorization': f'Bearer {integration.api_key}'}
            elif integration.crm_type == 'zoho':
                url = "https://www.zohoapis.com/crm/v3/settings/fields?module=Leads"
                headers = {'Authorization': f'Zoho-oauthtoken {integration.access_token}'}
            else:
                return {'success': False, 'error': 'Unsupported CRM type'}

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return {'success': True, 'message': f'{integration.crm_type.title()} connection successful'}
            else:
                return {'success': False, 'error': f'Connection failed: {response.text}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}
