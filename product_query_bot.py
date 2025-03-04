from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd
import requests
GEMINI_API_KEY = "AIzaSyALByPM1OQZCVCUAEqS_UDBOhTzIg2WbYY"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"


app = Flask(__name__)
CORS(app)

# Load product data from CSV into a dictionary
df = pd.read_csv('products.csv')
product_dict = df.set_index('Product').to_dict(orient='index')

# Your Gemini API key (replace with your actual key)
  # Adjust as per actual API docs

def get_response_from_gemini(message_body, product_dict):
    """
    Use Gemini API to detect the product and generate a full response.
    Returns the generated response string.
    """
    headers = {
        "Content-Type": "application/json"
    }
    
    # Construct the prompt with product info and user message
    product_list = "\n".join([f"- {product}: {info['Price']} {info['Currency']} {info['Description']}" for product, info in product_dict.items()])
    prompt = f"""
    You are a helpful WhatsApp assistant for a store. The user has sent this message: "{message_body}".
    Your task is to:
    1. Identify the product name the user is asking about (if any).
    2. Generate a natural, friendly response based on the product details below.
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
        print(text_response, flush=True)
        # Adjust based on actual Gemini API response structure
        return text_response
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        return "Sorry, I couldn’t process your request right now. Please try again later."

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Get the incoming message from the request body
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
            
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided in request'}), 400
            
        message_body = data['message'].lower()
        
        # Get the full response from Gemini
        response_message = get_response_from_gemini(message_body, product_dict)

        print("response_message: ", response_message)
        
        # Return JSON response
        return jsonify({'response': response_message})
        
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({'error': 'Invalid request format'}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
