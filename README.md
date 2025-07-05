# Terms & Conditions Analyzer

A tool to analyze and simplify terms and conditions for users, focusing on privacy concerns and user rights.

## Features

- Analyze terms and conditions using OpenAI's GPT-4o
- Score T&Cs on a 1-10 scale
- Identify privacy concerns and red flags
- Simple REST API for integration

## Prerequisites

- Python 3.8+
- OpenAI API key
- Tavily API key (for web search functionality)

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd terms-and-conditions-bot
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

## Running the API

1. Start the Flask development server:
   ```bash
   python -m src.terms_analyzer.api.app
   ```

2. The API will be available at `http://localhost:5000`

## API Endpoints

- `GET /health` - Health check endpoint
- `POST /analyze` - Analyze terms and conditions
  
  Example request body:
  ```json
  {
    "app_name": "Example App",
    "terms_text": "Full text of terms and conditions...",
    "app_version": "1.0.0"
  }
  ```

## Testing

Run the test script to see a sample analysis:

```bash
python test_analysis.py
```

## Project Structure

```
.
├── src/
│   └── terms_analyzer/
│       ├── api/               # API endpoints
│       ├── models/            # Data models
│       ├── services/          # Business logic
│       └── utils/             # Utility functions
├── tests/                     # Integration tests
├── .env.example               # Example environment variables
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## License

MIT
