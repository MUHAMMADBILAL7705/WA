from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import requests
from datetime import datetime
from collections import defaultdict
import gdown
import tempfile
import os
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GEMINI_API_KEY= "AIzaSyALByPM1OQZCVCUAEqS_UDBOhTzIg2WbYY"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# Google Drive file ID from the shared link
GDRIVE_FILE_ID = "1EQA-4txr1Qi6VFCsUlml4uP2SjVUrmmw"
GDRIVE_URL = f"https://drive.google.com/uc?id={GDRIVE_FILE_ID}"

app = Flask(__name__)
CORS(app)

# Initialize product dictionary
product_dict = {}

# Store conversation history: {contact_number: [(timestamp, role, message)]}
conversation_history = defaultdict(list)

def cleanup_temp_file(file_path, max_attempts=5, delay=1):
    """
    Attempt to clean up temporary file with retry logic for Windows
    """
    for attempt in range(max_attempts):
        try:
            if os.path.exists(file_path):
                os.close(os.open(file_path, os.O_RDONLY))  # Close any open handles
                os.unlink(file_path)
                logger.info("Temporary file cleaned up successfully")
            return True
        except Exception as e:
            if attempt < max_attempts - 1:
                logger.warning(f"Cleanup attempt {attempt + 1} failed, retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"Failed to clean up temporary file after {max_attempts} attempts: {str(e)}")
                return False

def load_product_data():
    """
    Load product data from Google Drive and update the product dictionary
    """
    global product_dict
    temp_file = None
    try:
        # Create a temporary file to store the CSV
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        temp_path = temp_file.name
        temp_file.close()  # Close the file handle immediately
        logger.info(f"Created temporary file: {temp_path}")
        
        # Download the file from Google Drive
        logger.info("Downloading file from Google Drive...")
        gdown.download(GDRIVE_URL, temp_path, quiet=False)
        
        # Read the CSV file into a pandas DataFrame with explicit parameters
        logger.info("Reading CSV file...")
        df = pd.read_csv(
            temp_path,
            encoding='utf-8',
            sep=',',
            on_bad_lines='skip',  # Skip problematic lines
            engine='python'  # More flexible CSV parser
        )
        
        logger.info(f"CSV columns found: {df.columns.tolist()}")
        
        if 'Product' not in df.columns:
            raise ValueError("Required column 'Product' not found in CSV")
        
        # Update the product dictionary
        product_dict = df.set_index('Product').to_dict(orient='index')
        logger.info(f"Successfully loaded {len(product_dict)} products")
        
        return True
        
    except Exception as e:
        logger.error(f"Error loading product data: {str(e)}")
        return False
        
    finally:
        # Clean up the temporary file
        if temp_path:
            cleanup_temp_file(temp_path)

def get_response_from_gemini(message_body, product_dict, contact_number):
    """
    Use Gemini API to detect the product and generate a full response.
    Returns the generated response string.
    """
    headers = {
        "Content-Type": "application/json"
    }
    
    # Get conversation history for this contact
    history = conversation_history[contact_number][-5:]  # Get last 5 messages
    conversation_context = "\n".join([
        f"{'User' if role == 'user' else 'Assistant'}: {msg}"
        for _, role, msg in history
    ])
    
    # Construct the prompt with conversation history, product info and user message
    product_list = "\n".join([f"- {product}: {info['Price']} {info['Currency']} {info['Description']}" for product, info in product_dict.items()])
    prompt = f"""
    You are a helpful WhatsApp assistant for a store.

    Previous conversation:
    {conversation_context}

    The user has sent this new message: "{message_body}".
    Your task is to:
    1. Consider the conversation history above for context.
    2. Identify the product name the user is asking about (if any).
    3. Generate a natural, friendly response based on the product details below.
    If no product is detected or the product isn't in the list, respond appropriately.

    Available products:
    {product_list}

    Return only the response text, nothing else.
    """
    
    payload = {
        "contents": [{
            "parts":  [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        text_response = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text").strip()
        
        # Store the conversation, keeping only last 5 messages
        current_time = datetime.now().isoformat()
        # Add new messages
        conversation_history[contact_number].append((current_time, 'user', message_body))
        conversation_history[contact_number].append((current_time, 'assistant', text_response))
        # Trim to keep only last 5 messages
        if len(conversation_history[contact_number]) > 5:
            conversation_history[contact_number] = conversation_history[contact_number][-5:]
        
        logger.info(f"Generated response: {text_response}")
        return text_response
    except Exception as e:
        logger.error(f"Error with Gemini API: {str(e)}")
        return "Sorry, I couldn't process your request right now. Please try again later."

@app.route('/update_data', methods=['GET'])
def update_data():
    """
    Endpoint to trigger data refresh from Google Drive
    """
    logger.info("Received request to update product data")
    success = load_product_data()
    if success:
        response = {'status': 'success', 'message': 'Product data updated successfully', 'product_count': len(product_dict)}
        logger.info(f"Data update successful. {len(product_dict)} products loaded.")
        return jsonify(response)
    else:
        error_msg = 'Failed to update product data'
        logger.error(error_msg)
        return jsonify({'status': 'error', 'message': error_msg}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Get the incoming message from the request body
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
            
        data = request.get_json()
        if not data or 'message' not in data or 'contact_number' not in data:
            return jsonify({'error': 'Message and contact number are required'}), 400
            
        message_body = data['message'].lower()
        contact_number = data['contact_number']
        
        # Get the full response from Gemini
        response_message = get_response_from_gemini(message_body, product_dict, contact_number)

        logger.info(f"Webhook response: {response_message}")
        
        # Return JSON response
        return jsonify({'response': response_message})
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({'error': 'Invalid request format'}), 400

# Load initial product data when the app starts
logger.info("Starting application, loading initial product data...")
load_product_data()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
