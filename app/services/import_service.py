"""
Import Service
Handles lead import from CSV/Excel files
"""
import pandas as pd
import io
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any, BinaryIO
from app.models import ImportHistory, ImportStatus, Asset, Campaign, LandingPage, AdminUser
from app.core.database import get_db


class ImportService:
    """Service for importing leads from files"""
    
    # Standard column mappings
    STANDARD_COLUMNS = {
        'mobile': ['mobile', 'phone', 'telephone', 'cell', 'cellphone', 'mobile_number', 'phone_number'],
        'name': ['name', 'full_name', 'fullname', 'customer_name', 'lead_name'],
        'email': ['email', 'e-mail', 'email_address', 'mail'],
        'source': ['source', 'lead_source', 'origin', 'campaign'],
    }
    
    @staticmethod
    def detect_column_mapping(columns: List[str]) -> Dict[str, str]:
        """
        Auto-detect column mapping from file headers
        
        Args:
            columns: List of column names from file
            
        Returns:
            Dictionary mapping standard fields to file columns
        """
        mapping = {}
        columns_lower = [col.lower().strip() for col in columns]
        
        for standard_field, possible_names in ImportService.STANDARD_COLUMNS.items():
            for col_idx, col_name in enumerate(columns_lower):
                if col_name in possible_names:
                    mapping[standard_field] = columns[col_idx]
                    break
        
        return mapping
    
    @staticmethod
    def parse_file(file_content: bytes, filename: str) -> pd.DataFrame:
        """
        Parse CSV or Excel file
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Pandas DataFrame
        """
        file_ext = filename.lower().split('.')[-1]
        
        if file_ext == 'csv':
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                try:
                    df = pd.read_csv(io.BytesIO(file_content), encoding=encoding)
                    return df
                except UnicodeDecodeError:
                    continue
            raise ValueError("Unable to decode CSV file")
        
        elif file_ext in ['xlsx', 'xls']:
            df = pd.read_excel(io.BytesIO(file_content))
            return df
        
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    @staticmethod
    def validate_row(row: Dict[str, Any], row_number: int) -> tuple[bool, Optional[str]]:
        """
        Validate a single row
        
        Args:
            row: Row data as dictionary
            row_number: Row number for error reporting
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Mobile is required
        if not row.get('mobile'):
            return False, f"Row {row_number}: Mobile number is required"
        
        # Basic mobile validation
        mobile = str(row['mobile']).strip()
        if len(mobile) < 10:
            return False, f"Row {row_number}: Invalid mobile number"
        
        return True, None
    
    @staticmethod
    def normalize_mobile(mobile: str) -> str:
        """Normalize mobile number format"""
        # Remove spaces, dashes, parentheses
        mobile = str(mobile).strip()
        mobile = mobile.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # Add + if not present and starts with country code
        if not mobile.startswith('+') and len(mobile) >= 10:
            if mobile.startswith('971'):  # UAE
                mobile = '+' + mobile
            elif mobile.startswith('0'):  # Remove leading 0
                mobile = '+971' + mobile[1:]
            else:
                mobile = '+' + mobile
        
        return mobile
    
    @staticmethod
    def check_duplicate(db: Session, mobile: str) -> bool:
        """
        Check if lead with mobile already exists
        
        Args:
            db: Database session
            mobile: Mobile number
            
        Returns:
            True if duplicate exists
        """
        existing = db.query(Asset).filter(Asset.mobile == mobile).first()
        return existing is not None
    
    @staticmethod
    def import_leads(
        db: Session,
        file_content: bytes,
        filename: str,
        admin_user_id: uuid.UUID,
        campaign_id: Optional[uuid.UUID] = None,
        landing_page_id: Optional[uuid.UUID] = None,
        source: Optional[str] = None,
        skip_duplicates: bool = True
    ) -> ImportHistory:
        """
        Import leads from file
        
        Args:
            db: Database session
            file_content: File content as bytes
            filename: Original filename
            admin_user_id: Admin user performing import
            campaign_id: Optional campaign ID
            landing_page_id: Optional landing page ID
            source: Optional source identifier
            skip_duplicates: Whether to skip duplicate leads
            
        Returns:
            ImportHistory record
        """
        # Create import history record
        import_record = ImportHistory(
            id=uuid.uuid4(),
            admin_user_id=admin_user_id,
            campaign_id=campaign_id,
            landing_page_id=landing_page_id,
            filename=filename,
            file_size=len(file_content),
            file_type=filename.split('.')[-1].lower(),
            source=source,
            status=ImportStatus.PROCESSING,
            started_at=datetime.utcnow()
        )
        
        db.add(import_record)
        db.commit()
        
        error_details = []
        successful_count = 0
        failed_count = 0
        duplicate_count = 0
        
        try:
            # Parse file
            df = ImportService.parse_file(file_content, filename)
            import_record.total_rows = len(df)
            
            # Detect column mapping
            mapping = ImportService.detect_column_mapping(df.columns.tolist())
            import_record.mapping = mapping
            
            # Process each row
            for idx, row in df.iterrows():
                row_number = idx + 2  # +2 because Excel is 1-indexed and has header
                import_record.processed_rows = idx + 1
                
                try:
                    # Map columns
                    lead_data = {}
                    for standard_field, file_column in mapping.items():
                        if file_column in row:
                            value = row[file_column]
                            if pd.notna(value):  # Skip NaN values
                                lead_data[standard_field] = value
                    
                    # Validate
                    is_valid, error_msg = ImportService.validate_row(lead_data, row_number)
                    if not is_valid:
                        error_details.append(error_msg)
                        failed_count += 1
                        continue
                    
                    # Normalize mobile
                    mobile = ImportService.normalize_mobile(lead_data['mobile'])
                    
                    # Check duplicate
                    if skip_duplicates and ImportService.check_duplicate(db, mobile):
                        duplicate_count += 1
                        continue
                    
                    # Create lead
                    lead = Asset(
                        id=uuid.uuid4(),
                        mobile=mobile,
                        name=lead_data.get('name'),
                        email=lead_data.get('email'),
                        campaign_id=campaign_id,
                        landing_id=landing_page_id,  # Note: Asset model uses landing_id, not landing_page_id
                        status='NEW'
                    )

                    db.add(lead)
                    db.flush()  # Flush to catch any database errors
                    successful_count += 1
                    
                except Exception as e:
                    error_details.append(f"Row {row_number}: {str(e)}")
                    failed_count += 1
            
            # Update import record
            import_record.successful_imports = successful_count
            import_record.failed_imports = failed_count
            import_record.duplicate_skipped = duplicate_count
            import_record.error_details = error_details if error_details else None
            
            # Determine final status
            if successful_count == 0:
                import_record.status = ImportStatus.FAILED
                import_record.error_message = "No leads were imported"
            elif failed_count > 0:
                import_record.status = ImportStatus.PARTIAL
            else:
                import_record.status = ImportStatus.COMPLETED
            
            import_record.completed_at = datetime.utcnow()
            import_record.processing_time_seconds = int(
                (import_record.completed_at - import_record.started_at).total_seconds()
            )
            
            db.commit()
            db.refresh(import_record)
            
            return import_record
            
        except Exception as e:
            import_record.status = ImportStatus.FAILED
            import_record.error_message = str(e)
            import_record.completed_at = datetime.utcnow()
            db.commit()
            raise

