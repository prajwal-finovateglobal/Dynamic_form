# CBS Submission System

A FastAPI-based submission processing system that handles form submissions with complex table relationships and foreign key mappings.

## Features

- **Dynamic Form Processing**: Handles submissions with multiple forms and subforms
- **Intelligent Table Mapping**: Maps form data to database tables with proper relationships
- **Foreign Key Management**: Automatically manages foreign key relationships between tables
- **Topological Insertion**: Inserts records in the correct order based on table dependencies
- **Attribute Mapping**: Converts attribute IDs to actual column names
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
│   └── ...
├── repositories/                 # Data access layer
│   ├── attribute.py
│   ├── base.py
│   └── ...
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
│   │   └── topo_sort.py        # Topological sorting
│   └── submission_service.py
├── utils/                        # Utilities
│   ├── insert_utils.py
│   └── logger.py
├── main.py                       # FastAPI application entry point
└── requirements.txt              # Python dependencies
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

### Payload Mapper
Converts submission payload into table-wise grouped records:
- Groups data by target tables
- Handles form and subform data
- Attaches FK target information
- Manages record merging for same tables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here] 