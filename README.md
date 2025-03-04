# Product Query WhatsApp Bot

A Flask-based API that answers product pricing queries using Google's Gemini AI model.

## Features

- CSV data processing for product information
- Natural language query processing using Gemini AI
- RESTful API endpoint for product queries
- Automatic response generation for product queries

## Installation

1. Clone this repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies (if you get permissions errors, use the --user flag):
```bash
# Regular installation
pip install -r requirements.txt

# If you get permissions errors, use:
pip install --user -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env  # On Windows: copy .env.example .env
```

2. Set up Google Gemini API:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create an API key
   - Update the `.env` file with your credentials

3. Update your `.env` file with:
   - GEMINI_API_KEY

## Running the Application

1. Make sure your virtual environment is activated
2. Start the Flask server:
```bash
python product_query_bot.py
```
3. The server will start on `http://localhost:5000`

## Using the API

1. Send POST requests to `/webhook` endpoint with JSON body:
```json
{
    "message": "What's the price of the laptop?"
}
```
2. The bot will respond with product details and pricing
3. If the product isn't found, it will let you know

## CSV Data Format

The application expects a CSV file named `products.csv` with the following columns:
- Product: Product name
- Price: Product price
- Currency: Price currency
- Description: Product description

## Troubleshooting

### Installation Issues

If you encounter permissions errors during package installation:
1. Try using the `--user` flag: `pip install --user -r requirements.txt`
2. Or run your command prompt/terminal as administrator
3. Make sure you're using the correct Python version (3.6+)

### Environment Issues

If the virtual environment isn't working:
1. Delete the `venv` folder
2. Create a new one with: `python -m venv venv`
3. Activate it and try installing again

## Notes

- The application uses Google's Gemini AI model for natural language understanding and response generation
- Queries can be written in natural language
- The bot maintains a friendly, helpful tone in responses