# WhatsApp Assistant with Product Catalog

A Flask-based WhatsApp assistant that uses Gemini API to handle product inquiries.

## Docker Setup

### Prerequisites
- Docker
- Docker Compose

### Running the Application

1. Build and start the containers:
```bash
docker-compose up --build
```

2. The application will be available at:
- Local: http://localhost:5000

### API Endpoints

- `POST /webhook`: Receive WhatsApp messages
  - Required JSON body:
    ```json
    {
        "message": "your message here",
        "contact_number": "user's contact number"
    }
    ```

- `GET /update_data`: Trigger product data refresh from Google Drive

### Development

To make changes during development:
1. The code is mounted as a volume, so changes will reflect immediately
2. The server will automatically restart when files change

### Stopping the Application

```bash
docker-compose down
```

## Environment Variables

The following environment variables are configured in docker-compose.yml:
- `FLASK_ENV`: Set to 'development' by default
- `GEMINI_API_KEY`: API key for Gemini AI service