# OMM LLM Backend

A Flask-based backend API for the OMM (Object Model Manager) LLM application that provides document management and conversational AI capabilities using OpenAI's Assistant API with vector storage and MongoDB persistence.

## Features

- **Document Upload & Management**: Upload files to OpenAI Vector Store for AI-powered document analysis
- **Conversational AI**: Ask questions about uploaded documents using OpenAI's Assistant API
- **Chat History**: Persistent conversation history stored in MongoDB
- **Document Tracking**: Keep track of all uploaded documents with metadata
- **CORS Support**: Cross-origin resource sharing enabled for web applications
- **Streaming Support**: Built-in streaming endpoint for real-time responses

## Tech Stack

- **Backend Framework**: Flask (Python)
- **AI Integration**: OpenAI API (Assistant & Vector Store)
- **Database**: MongoDB Atlas
- **Deployment**: Gunicorn (production-ready WSGI server)
- **CORS**: Flask-CORS for cross-origin requests

## Installation

### Prerequisites

- Python 3.7+
- OpenAI API Key
- MongoDB Atlas connection string

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd omm_backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

4. Run the application:
```bash
# Development
python app.py

# Production
gunicorn app:app --timeout 90
```

## API Endpoints

### 1. Upload Document
**POST** `/api/upload`

Upload a file to the OpenAI Vector Store for document analysis.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (FormData)

**Response:**
```json
{
  "message": "File uploaded successfully",
  "file_name": "document.pdf",
  "file_id": "file_xyz123"
}
```

### 2. Ask Question
**POST** `/api/ask`

Ask a question about the uploaded documents using the AI assistant.

**Request:**
```json
{
  "question": "What is the main topic of the uploaded document?"
}
```

**Response:**
```json
{
  "text": "The main topic is...",
  "sourceSnippet": "Generated using OpenAI Assistant"
}
```

### 3. Stream Response
**POST** `/api/ask_stream`

Get streaming responses from the API (demo endpoint).

**Response:**
- Content-Type: text/plain
- Streaming text response

### 4. Get Document List
**GET** `/get_document_list`

Retrieve a list of all uploaded documents.

**Response:**
```json
{
  "documents": [
    {
      "file_id": "file_xyz123",
      "name": "document.pdf"
    }
  ]
}
```

### 5. Get Conversation History
**GET** `/gethistorical`

Retrieve the complete conversation history.

**Response:**
```json
{
  "history": [
    {
      "question": "What is...?",
      "answer": "The answer is..."
    }
  ]
}
```

## Configuration

### OpenAI Configuration
The application uses pre-configured OpenAI resources:
- **Vector Store ID**: `vs_6824f56c052081919f25de6844131737`
- **Assistant ID**: `asst_lY2FkYc4pSomJSDF0H8lLCFN`

### MongoDB Configuration
- **Database**: `omm`
- **Collections**:
  - `document`: Stores uploaded file metadata
  - `conversation_history`: Stores Q&A pairs

## Error Handling

The API includes comprehensive error handling for:
- File upload failures
- OpenAI API errors
- MongoDB connection issues
- Request validation errors

All errors return appropriate HTTP status codes with descriptive error messages.

## Deployment

### Heroku Deployment
The application is configured for Heroku deployment with:
- `Procfile`: Specifies the web process command
- `requirements.txt`: Lists all Python dependencies
- Environment variables for sensitive data

### Environment Variables
Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key

## Development

### Local Development
```bash
python app.py
```
The application will run on `http://localhost:5000` with debug mode enabled.

### Dependencies
- `flask`: Web framework
- `gunicorn`: WSGI HTTP Server
- `openai`: OpenAI API client
- `flask-cors`: CORS support
- `pymongo`: MongoDB driver

## Security Considerations

- API keys are stored as environment variables
- MongoDB connection uses TLS encryption
- CORS is enabled for cross-origin requests
- File uploads are temporarily stored and processed securely

## License

This project is licensed under the BSD 3-Clause License. See the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions, please create an issue in the repository or contact the maintainer.

---

**Copyright (c) 2025, Nakul Shahdadpuri**
