# Terms & Conditions Analyzer

A comprehensive tool to track, analyze, and simplify terms and conditions for various online services, with a focus on privacy concerns and user rights.

## Features

- **Multi-service Tracking**: Monitor terms and conditions for multiple services in one place
- **Automated Analysis**: Leverage OpenAI's GPT-4o for intelligent analysis of legal documents
- **Version Control**: Track changes to terms and conditions over time
- **Structured Data**: Store and query analysis results in a structured format
- **Modular Architecture**: Built with MCP (Model-Controller-Presenter) architecture for extensibility
- **REST API**: Simple integration with other services

## Prerequisites

- Python 3.10+
- SQLite (included) or PostgreSQL
- OpenAI API key
- Tavily API key (for web search functionality)

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd terms-and-conditions-bot
   ```

2. **Set up the environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   Copy `.env.example` to `.env` and update with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   DATABASE_URL=sqlite:///./terms_analyzer.db
   ```

4. **Initialize the database**:
   ```bash
   python scripts/init_db.py
   ```

## Usage

### Managing Services and Documents

Use the `manage_terms.py` script to interact with the system:

```bash
# List all services
python scripts/manage_terms.py list

# Add a new service
python scripts/manage_terms.py add "service_name" --display-name "Display Name" --website "https://example.com"

# Add a document to a service
python scripts/manage_terms.py add-doc "service_name" terms_of_service "https://example.com/terms" --file terms.txt

# Update document content
python scripts/manage_terms.py update-doc 1 --file updated_terms.txt --version "2.0.0"

# Analyze a document
python scripts/manage_terms.py analyze 1 --type full_analysis

# Check service status
python scripts/manage_terms.py status 1
```

### Running the API

Start the FastAPI development server:

```bash
uvicorn terms_analyzer.api.app:app --reload
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## Project Structure

```
.
├── src/
│   └── terms_analyzer/
│       ├── api/               # FastAPI application and endpoints
│       ├── chains/            # LangChain processing pipelines
│       ├── models/            # Database models and schemas
│       ├── retrievers/        # Document retrieval components
│       ├── tools/             # Custom LangChain tools
│       ├── utils/             # Utility functions
│       └── vector_store/      # Vector database integration
├── scripts/                   # Management and utility scripts
│   ├── init_db.py            # Database initialization
│   └── manage_terms.py       # CLI for managing terms
├── tests/                     # Integration tests
├── .env.example              # Example environment variables
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Database Schema

The system uses SQLAlchemy ORM with the following main tables:

- **services**: Tracked online services
- **categories**: Service categories (e.g., Social Media, Cloud Storage)
- **documents**: Versioned terms and conditions documents
- **analyses**: Analysis results of documents

## API Documentation

### Endpoints

- `GET /api/v1/services`: List all services
- `POST /api/v1/services`: Add a new service
- `GET /api/v1/services/{service_id}`: Get service details
- `POST /api/v1/documents`: Add a document
- `POST /api/v1/analyze/{document_id}`: Analyze a document
- `GET /api/v1/analyses/{analysis_id}`: Get analysis results

## Testing

Run the test suite:

```bash
pytest tests/
```

## License

MIT
