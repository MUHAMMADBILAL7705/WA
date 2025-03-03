# Product Query WhatsApp Bot

A WhatsApp bot that answers product pricing queries using vector similarity search and natural language processing.

## Features

- CSV data processing for product information
- Vector similarity search using FAISS
- Natural language query processing
- WhatsApp integration via Twilio
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

2. Set up a Twilio account and get your credentials:
   - Go to [Twilio Console](https://www.twilio.com/console)
   - Get your Account SID and Auth Token
   - Set up WhatsApp Sandbox or Business Profile
   - Update the `.env` file with your credentials

3. Update your `.env` file with:
   - TWILIO_ACCOUNT_SID
   - TWILIO_AUTH_TOKEN
   - TWILIO_PHONE_NUMBER (WhatsApp number)

## Running the Application

1. Make sure your virtual environment is activated
2. Start the Flask server:
```bash
python product_query_bot.py
```
3. The server will start on `http://localhost:5000`

## Using with WhatsApp

1. Set up Twilio WhatsApp Sandbox:
   - Follow Twilio's instructions to join your sandbox
   - Configure your webhook URL to point to your server's `/webhook` endpoint
   
2. Send messages to your Twilio WhatsApp number:
   - Ask about products, e.g., "What's the price of the laptop?"
   - The bot will respond with product details and pricing
   - If the product isn't found, it will let you know

## CSV Data Format

The application expects a CSV file named `quotations.csv` with the following columns:
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

- The application uses semantic search, so queries don't need to match product names exactly
- The vector similarity threshold can be adjusted in the code for more or less strict matching
- The bot uses the all-MiniLM-L6-v2 model for sentence embeddings