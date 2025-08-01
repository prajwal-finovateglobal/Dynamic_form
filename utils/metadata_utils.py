"""
Metadata Utilities for CBS Submission System

This module handles automatic injection of metadata attributes (created_at, updated_at, ip_address, etc.)
into form submissions based on metadata_attribute_ids configured in forms and subforms.

How it works:
1. Forms and subforms have a metadata_attribute_ids column that contains attribute IDs
2. These attribute IDs correspond to attributes in cbs_master_form_attributes table
3. The system validates that all metadata attributes exist in the database before injection
4. The system automatically injects appropriate values for these metadata attributes:
   - created_at: Current timestamp
   - updated_at: Current timestamp  
   - ip_address: Client IP address from request
   - user_id: User ID from authentication context

Validation:
- All metadata_attribute_ids are cross-checked against the database
- Only valid metadata attributes (created_at, updated_at, ip_address, user_id) are processed
- Missing or invalid attributes are logged as warnings
- The system continues processing even if some metadata attributes are invalid

Usage:
1. Configure metadata_attribute_ids in your forms/subforms with the appropriate attribute IDs
2. Ensure the corresponding attributes exist in cbs_master_form_attributes table
3. The system will automatically inject metadata during submission processing
4. No changes needed to your submission payload - metadata is injected transparently

Example:
- Form has metadata_attribute_ids: [1, 2, 3]
- Attribute 1 = "created_at", Attribute 2 = "updated_at", Attribute 3 = "ip_address"
- During submission, these values will be automatically injected into the form's table records
- If any attribute IDs don't exist in the database, they will be skipped with a warning
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from db.dependencies import DB_dependency
from repositories.form import get_form_by_id
from repositories.subForm import get_sub_forms_by_ids
from repositories.attribute import get_attributes_by_ids
from utils.logger import get_logger
from utils.exceptions import (
    MetadataConfigurationError,
    AttributeNotFoundException,
    FormNotFoundException,
    SubFormNotFoundException
)

logger = get_logger("metadata_utils_logger")


class MetadataHandler:
    """
    Handles metadata attributes (created_at, updated_at, ip_address, etc.) 
    based on metadata_attribute_ids from forms and subforms.
    """
    
    def __init__(self, db: DB_dependency):
        self.db = db
        self.metadata_attributes_cache = {}
    
    def _validate_metadata_attributes(self, metadata_attribute_ids: List[int]) -> Dict[str, Any]:
        """
        Validate metadata attributes against the database and return valid attribute mappings.
        """
        if not metadata_attribute_ids:
            return {}
            
        # Get attribute details from database
        attributes = get_attributes_by_ids(self.db, metadata_attribute_ids)
        if not attributes:
            logger.warning(f"No attributes found in database for metadata_attribute_ids: {metadata_attribute_ids}")
            return {}
            
        # Validate that all requested attributes exist
        found_attr_ids = {attr.attribute_id for attr in attributes}
        missing_attr_ids = set(metadata_attribute_ids) - found_attr_ids
        
        if missing_attr_ids:
            logger.warning(f"Missing metadata attributes in database: {missing_attr_ids}")
            
        # Create attribute_id to name mapping for valid attributes only
        attr_map = {str(attr.attribute_id): attr.name for attr in attributes}
        
        # Validate that attributes are configured as metadata attributes
        valid_metadata_attrs = {}
        for attr_id, attr_name in attr_map.items():
            # Check if this is a valid metadata attribute
            if attr_name in ["created_at", "updated_at", "ip_address", "user_id"]:
                valid_metadata_attrs[attr_id] = attr_name
                logger.debug(f"Valid metadata attribute found: {attr_id} -> {attr_name}")
            else:
                logger.warning(f"Attribute {attr_id} ({attr_name}) is not a valid metadata attribute")
                
        return valid_metadata_attrs
    
    def _get_metadata_values(self, metadata_attribute_ids: List[int]) -> Dict[str, Any]:
        """
        Get metadata values for given attribute IDs with proper validation.
        """
        # Validate attributes against database
        valid_attrs = self._validate_metadata_attributes(metadata_attribute_ids)
        if not valid_attrs:
            logger.warning(f"No valid metadata attributes found for IDs: {metadata_attribute_ids}")
            return {}
            
        # Generate metadata values for valid attributes only
        metadata_values = {}
        current_time = datetime.now()
        
        for attr_id, attr_name in valid_attrs.items():
            if attr_name == "created_at":
                metadata_values[attr_id] = current_time
            elif attr_name == "updated_at":
                metadata_values[attr_id] = current_time
            elif attr_name == "ip_address":
                # This will be set later when we have the IP address
                metadata_values[attr_id] = None
            elif attr_name == "user_id":
                # This will be set later when we have the user ID
                metadata_values[attr_id] = None
            else:
                logger.warning(f"Unknown metadata attribute: {attr_name}")
                
        return metadata_values
        
    def get_metadata_attributes_for_form(self, form_id: int) -> Dict[str, Any]:
        """
        Get metadata attributes for a specific form based on its metadata_attribute_ids.
        Validates that the form exists and has valid metadata_attribute_ids.
        """
        form = get_form_by_id(self.db, form_id)
        if not form:
            logger.warning(f"Form with ID {form_id} not found in database")
            return {}
            
        if not form.metadata_attribute_ids:
            logger.debug(f"No metadata attributes configured for form_id: {form_id}")
            return {}
            
        logger.info(f"Form {form_id} has metadata_attribute_ids: {form.metadata_attribute_ids}")
        return self._get_metadata_values(form.metadata_attribute_ids)
    
    def get_metadata_attributes_for_subforms(self, sub_form_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """
        Get metadata attributes for multiple subforms based on their metadata_attribute_ids.
        Validates that subforms exist and have valid metadata_attribute_ids.
        """
        sub_forms = get_sub_forms_by_ids(self.db, sub_form_ids)
        if not sub_forms:
            logger.warning(f"No subforms found in database for sub_form_ids: {sub_form_ids}")
            return {}
            
        result = {}
        for sub_form in sub_forms:
            if sub_form.metadata_attribute_ids:
                logger.info(f"Subform {sub_form.sub_form_id} has metadata_attribute_ids: {sub_form.metadata_attribute_ids}")
                result[sub_form.sub_form_id] = self._get_metadata_values(sub_form.metadata_attribute_ids)
            else:
                logger.debug(f"No metadata attributes configured for subform_id: {sub_form.sub_form_id}")
                result[sub_form.sub_form_id] = {}
                
        return result
    
    
    
    def validate_metadata_configuration(self, form_id: int, sub_form_ids: List[int]) -> Dict[str, Any]:
        """
        Validate the entire metadata configuration for a form and its subforms.
        Returns validation results and any issues found.
        """
        validation_result = {
            "valid": True,
            "form_validation": {},
            "subform_validation": {},
            "issues": []
        }
        
        # Validate form
        form = get_form_by_id(self.db, form_id)
        if not form:
            validation_result["valid"] = False
            validation_result["issues"].append(f"Form with ID {form_id} not found in database")
            validation_result["form_validation"] = {"exists": False, "metadata_configured": False}
        else:
            validation_result["form_validation"] = {
                "exists": True,
                "metadata_configured": bool(form.metadata_attribute_ids),
                "metadata_attribute_ids": form.metadata_attribute_ids or []
            }
            
            if form.metadata_attribute_ids:
                # Validate form metadata attributes
                valid_attrs = self._validate_metadata_attributes(form.metadata_attribute_ids)
                missing_attrs = set(form.metadata_attribute_ids) - set(int(attr_id) for attr_id in valid_attrs.keys())
                if missing_attrs:
                    validation_result["valid"] = False
                    validation_result["issues"].append(f"Form {form_id} has invalid metadata attributes: {missing_attrs}")
        
        # Validate subforms
        sub_forms = get_sub_forms_by_ids(self.db, sub_form_ids)
        found_subform_ids = {sub_form.sub_form_id for sub_form in sub_forms}
        missing_subform_ids = set(sub_form_ids) - found_subform_ids
        
        if missing_subform_ids:
            validation_result["valid"] = False
            validation_result["issues"].append(f"Subforms not found in database: {missing_subform_ids}")
        
        for sub_form in sub_forms:
            subform_validation = {
                "exists": True,
                "metadata_configured": bool(sub_form.metadata_attribute_ids),
                "metadata_attribute_ids": sub_form.metadata_attribute_ids or []
            }
            
            if sub_form.metadata_attribute_ids:
                # Validate subform metadata attributes
                valid_attrs = self._validate_metadata_attributes(sub_form.metadata_attribute_ids)
                missing_attrs = set(sub_form.metadata_attribute_ids) - set(int(attr_id) for attr_id in valid_attrs.keys())
                if missing_attrs:
                    validation_result["valid"] = False
                    validation_result["issues"].append(f"Subform {sub_form.sub_form_id} has invalid metadata attributes: {missing_attrs}")
            
            validation_result["subform_validation"][sub_form.sub_form_id] = subform_validation
        
        return validation_result

    def inject_metadata_into_records(
        self, 
        table_records_map: Dict[str, Dict[str, List[Dict[str, Any]]]],
        form_id: int,
        sub_form_ids: List[int],
        ip_address: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        Inject metadata attributes into the records based on form and subform metadata_attribute_ids.
        Includes validation to ensure all metadata attributes exist in the database.
        """
        logger.info(f"Injecting metadata for form_id={form_id}, sub_form_ids={sub_form_ids}")
        
        # Validate metadata configuration first
        validation_result = self.validate_metadata_configuration(form_id, sub_form_ids)
        if not validation_result["valid"]:
            logger.warning(f"Metadata configuration validation failed: {validation_result['issues']}")
            # Continue with injection but log warnings
        
        # Get metadata attributes for form and subforms
        form_metadata = self.get_metadata_attributes_for_form(form_id)
        subform_metadata = self.get_metadata_attributes_for_subforms(sub_form_ids)
        
        # Get form and subform to table mapping
        form = get_form_by_id(self.db, form_id)
        form_table = form.table_name if form else None
        
        sub_forms = get_sub_forms_by_ids(self.db, sub_form_ids)
        subform_to_table = {sub_form.sub_form_id: sub_form.table_name for sub_form in sub_forms if sub_form.table_name}
        
        # Get attribute mappings for all metadata attributes
        all_metadata_attr_ids = set()
        if form_metadata:
            all_metadata_attr_ids.update(form_metadata.keys())
        for subform_meta in subform_metadata.values():
            all_metadata_attr_ids.update(subform_meta.keys())
            
        if not all_metadata_attr_ids:
            logger.info("No valid metadata attributes to inject")
            return table_records_map
            
        # Get attribute details for all metadata attributes
        attributes = get_attributes_by_ids(self.db, [int(attr_id) for attr_id in all_metadata_attr_ids])
        attr_id_to_name = {str(attr.attribute_id): attr.name for attr in attributes}
        
        # Prepare metadata values
        current_time = datetime.now()
        metadata_values = {}
        
        for attr_id, attr_name in attr_id_to_name.items():
            if attr_name == "created_at":
                metadata_values[attr_id] = current_time
            elif attr_name == "updated_at":
                metadata_values[attr_id] = current_time
            elif attr_name == "ip_address":
                metadata_values[attr_id] = ip_address
            elif attr_name == "user_id":
                metadata_values[attr_id] = user_id
            else:
                logger.warning(f"Unknown metadata attribute: {attr_name}")
        
        # Inject metadata into records
        modified_records_map = {}
        
        for table_name, table_data in table_records_map.items():
            records = table_data.get("records", [])
            modified_records = []
            
            for record in records:
                modified_record = record.copy()
                
                # Inject form metadata (only for the form's own table)
                if form_table == table_name:
                    logger.debug(f"Injecting form metadata for table {table_name}")
                    for attr_id, value in form_metadata.items():
                        if value is not None:  # Skip None values (like ip_address that will be set later)
                            modified_record[attr_id] = metadata_values.get(attr_id, value)
                
                # Inject subform metadata (only for tables that correspond to subforms)
                for sub_form_id, subform_meta in subform_metadata.items():
                    subform_table = subform_to_table.get(sub_form_id)
                    if subform_table == table_name:
                        logger.debug(f"Injecting subform metadata for table {table_name} from sub_form_id {sub_form_id}")
                        for attr_id, value in subform_meta.items():
                            if value is not None:
                                modified_record[attr_id] = metadata_values.get(attr_id, value)
                
                modified_records.append(modified_record)
            
            modified_records_map[table_name] = {
                "records": modified_records
            }
        
        logger.info(f"Metadata injection completed. Modified {len(modified_records_map)} tables")
        return modified_records_map


def create_metadata_handler(db: DB_dependency) -> MetadataHandler:
    """
    Factory function to create a MetadataHandler instance.
    """
    return MetadataHandler(db) 