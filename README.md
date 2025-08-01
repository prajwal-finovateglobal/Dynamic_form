# CBS Submission System

A FastAPI-based submission processing system that handles form submissions with complex table relationships and foreign key mappings.

## Features

- **Dynamic Form Processing**: Handles submissions with multiple forms and subforms
- **Intelligent Table Mapping**: Maps form data to database tables with proper relationships
- **Foreign Key Management**: Automatically manages foreign key relationships between tables
- **Topological Insertion**: Inserts records in the correct order based on table dependencies
- **Attribute Mapping**: Converts attribute IDs to actual column names
- **Automatic Metadata Injection**: Automatically injects metadata attributes (created_at, updated_at, ip_address, user_id) based on form configuration
- **Comprehensive Exception Handling**: Custom exceptions with appropriate HTTP status codes and detailed error responses
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## Project Structure

```
CBS/
├── core/                          # Core configuration
│   └── config.py
├── db/                           # Database configuration
│   ├── dependencies.py
│   └── session.py
├── models/                       # SQLAlchemy models
│   ├── address.py
│   ├── attribute.py
│   ├── country.py
│   ├── customer.py
│   ├── document.py
│   ├── entity.py
│   ├── fk_mapping.py
│   ├── form.py
│   ├── location.py
│   └── pincode.py
├── repositories/                 # Data access layer
│   ├── attribute.py
│   ├── base.py
│   ├── fk_mapping.py
│   ├── form.py
│   └── subForm.py
├── routers/                      # API routes
│   ├── debug_router.py
│   └── submission.py
├── schemas/                      # Pydantic schemas
│   ├── submission.py
│   └── table_graph_schema.py
├── services/                     # Business logic
│   ├── submission_helpers/
│   │   ├── db_inserter.py       # Database insertion logic
│   │   ├── graph_builder.py     # Table dependency graph
│   │   ├── payload_mapper.py    # Form to table mapping
│   │   ├── table_lookup.py      # Table extraction from payload
│   │   ├── topo_sort.py         # Topological sorting
│   │   └── validator.py         # Form validation
│   └── submission_service.py
├── utils/                        # Utilities
│   ├── exceptions.py             # Custom exception classes
│   ├── exception_handlers.py     # Global exception handlers
│   ├── insert_utils.py
│   ├── logger.py
│   └── metadata_utils.py        # Metadata injection utilities
├── logs/                         # Application logs
├── main.py                       # FastAPI application entry point
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd CBS
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file with your database configuration.

5. **Run the application**:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

### Submit Form Data
```
POST /submit/
```

Processes form submissions and inserts data into appropriate database tables.

**Request Body**:
```json
{
  "form_id": 1,
  "values": {
    "attribute_id": "value"
  },
  "sub_forms": [
    {
      "sub_form_id": 1,
      "values": {
        "attribute_id": "value"
      }
    }
  ]
}
```

## Key Components

### Submission Service
The main service that orchestrates the submission process:
1. Validates required attributes
2. Extracts table names from payload
3. Builds table dependency graph
4. Performs topological sort for insertion order
5. Maps payload to table records
6. Inserts records with proper FK relationships

### Database Inserter
Handles the actual database insertion with:
- Attribute ID to column name conversion
- Foreign key injection from parent tables
- Primary key generation and tracking
- FK target mapping for child tables

### Metadata Handler
Automatically injects metadata attributes into submissions:
- Supports created_at, updated_at, ip_address, user_id metadata
- Configurable via metadata_attribute_ids in forms and subforms
- Transparent injection - no changes needed to submission payloads
- Form-level and subform-level metadata support

### Exception Handler
Comprehensive error handling with appropriate HTTP status codes:
- Custom CBS exceptions for different error types
- Automatic conversion to HTTP responses
- Detailed error messages and debugging information
- Graceful handling of database and validation errors

### Payload Mapper
Converts submission payload into table-wise grouped records:
- Groups data by target tables
- Handles form and subform data
- Attaches FK target information
- Manages record merging for same tables

## Metadata System

The CBS submission system includes an automatic metadata injection feature that handles common metadata attributes like `created_at`, `updated_at`, `ip_address`, and `user_id`.

### How Metadata Injection Works

1. **Configuration**: Forms and subforms have a `metadata_attribute_ids` column that contains attribute IDs
2. **Database Validation**: The system cross-checks all metadata_attribute_ids against the `cbs_master_form_attributes` table
3. **Attribute Mapping**: Only valid metadata attributes are processed (created_at, updated_at, ip_address, user_id)
4. **Automatic Injection**: During submission processing, the system automatically injects appropriate values:
   - `created_at`: Current timestamp
   - `updated_at`: Current timestamp
   - `ip_address`: Client IP address from request
   - `user_id`: User ID from authentication context
5. **Error Handling**: Invalid or missing metadata attributes are logged as warnings but don't stop processing

### Setup Example

```sql
-- 1. Create metadata attributes
INSERT INTO cbs_master_form_attributes (attribute_id, name, description) VALUES
(1, 'created_at', 'Record creation timestamp'),
(2, 'updated_at', 'Record update timestamp'),
(3, 'ip_address', 'Client IP address'),
(4, 'user_id', 'User who created the record');

-- 2. Configure form metadata
UPDATE cbs_master_forms 
SET metadata_attribute_ids = [1, 2, 3, 4] 
WHERE form_id = 1;

-- 3. Configure subform metadata (optional)
UPDATE cbs_master_sub_forms 
SET metadata_attribute_ids = [1, 2] 
WHERE sub_form_id = 1;
```

### Usage

No changes to your submission payload are required. The metadata is injected automatically during processing:

```json
{
  "form_id": 2,
  "values": {
    "1001": "10010000001",
    "1002": "Entity"
  },
  "sub_forms": [
    {
      "sub_form_id": 32,
      "values": {
        "1003": "Private Entity"
      }
    }
  ]
}
```

The system will automatically add metadata attributes based on your form configuration.

## Exception Handling

The CBS system includes comprehensive exception handling with appropriate HTTP status codes for different types of errors.

### Error Types and Status Codes

- **400 Bad Request**: Configuration errors, payload mapping issues, table dependency problems
- **404 Not Found**: Forms, subforms, or attributes not found in database
- **409 Conflict**: Duplicate record violations
- **422 Unprocessable Entity**: Validation errors, missing required attributes, data type mismatches
- **500 Internal Server Error**: Database errors, insertion failures, unexpected errors

### Error Response Format

All errors follow a consistent JSON response format:

```json
{
  "error": {
    "type": "ValidationError",
    "message": "Form validation failed",
    "status_code": 422,
    "details": {
      "validation_errors": [
        "Field 'email' is required",
        "Field 'age' must be a number"
      ]
    }
  }
}
```

### Exception Classes

- `FormNotFoundException`: Form not found in database (404)
- `SubFormNotFoundException`: Subform not found in database (404)
- `ValidationError`: Form data validation failed (422)
- `RequiredAttributeMissingError`: Required attributes missing (422)
- `DataTypeMismatchError`: Data type doesn't match expected type (422)
- `DatabaseError`: General database operation failed (500)
- `InsertionError`: Record insertion failed (500)
- `ForeignKeyError`: Foreign key constraint violation (500)
- `MetadataConfigurationError`: Metadata configuration invalid (400)
- `PayloadMappingError`: Payload mapping failed (400)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here] 