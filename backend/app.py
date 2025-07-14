import hashlib
import uuid
from bson import ObjectId
from flask import Flask, abort, request, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
import traceback
import os
import requests
import boto3
from botocore.client import Config
import csv

app = Flask(__name__)
CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app, origins=["http://localhost:3000"])

# MongoDB setup (use your own credentials or environment variables)
MONGO_URI = 'mongodb+srv://user:password@cluster1.ullp5.mongodb.net/nts-company?retryWrites=true&w=majority'
client = MongoClient(MONGO_URI)
db = client['nts-company']
phones_collection = db['phones']
brands_collection = db['brands']
user_collection = db['users']
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB

# --- Telegram Bot Integration ---
# Replace with your actual Telegram Bot Token
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'

# --- Payment Gateway (Example with Tinkoff) ---
# Replace with your actual Tinkoff Terminal Key and Password
TINKOFF_TERMINAL_KEY = '1744526728600'
TINKOFF_PASSWORD = 'cmdBVuRK7rhZQB3C'
TINKOFF_INIT_URL = "https://securepay.tinkoff.ru/v2/Init"

# --- Product Data Import from CSV ---
PRODUCTS_CSV_FILE = 'products.csv'

def load_products_from_csv(filename):
    """Loads product data from a CSV file."""
    products = {}
    try:
        with open(filename, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Assuming CSV columns are 'product_id', 'name', 'price', 'description'
                product_id = row.get('product_id')
                if product_id:
                    products[product_id] = {
                        'name': row.get('name', 'Unknown Product'),
                        'price': float(row.get('price', 0)),
                        'description': row.get('description', '')
                    }
        print(f"Loaded {len(products)} products from {filename}")
    except FileNotFoundError:
        print(f"Error: CSV file '{filename}' not found.")
    except Exception as e:
        print(f"Error loading CSV: {e}")
    return products

# Load products on startup
PRODUCTS_DATA = load_products_from_csv(PRODUCTS_CSV_FILE)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

# Setup R2 client
r2 = boto3.client(
    's3',
    endpoint_url='', # Replace with your Cloudflare R2 endpoint URL
    aws_access_key_id='', # Replace with your Cloudflare R2 Access Key ID
    aws_secret_access_key='', # Replace with your Cloudflare R2 Secret Access Key
    config=Config(signature_version='s3v4'),
    region_name='auto'
)

def upload_file_to_r2(file, filename, bucket='sigminer'): # Replace 'sigminer' with your R2 bucket name
    r2.upload_fileobj(file, bucket, filename, ExtraArgs={'ACL': 'public-read'})
    # Replace with your R2 public access URL format
    return f'https://static.sigslot.com/{filename}'

@app.route('/upload-to-cloudflare', methods=['POST'])
def upload_to_r2_route():
    try:
        file = request.files['file']
        filename = file.filename

        url = upload_file_to_r2(file, filename)

        return jsonify({'url': url})
    except Exception as e:
        print("Upload to R2 failed:", e)
        return jsonify({'error': str(e)}), 500

@app.route('/phones', methods=['POST'])
def add_phone():
    try:
        def safe_float(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0

        data = {
            "name": request.form.get("name"),
            "brand": request.form.get("brand"),
            "model": request.form.get("model"),
            "memory": request.form.getlist("memory"),
            "colors": request.form.getlist("colors"),
            "description": request.form.get("description"),
            "price": safe_float(request.form.get("price")),
            "discounted_price": safe_float(request.form.get("discounted_price")),
            "video": request.form.get("video"),
            "photos": request.form.getlist("photos")
        }

        result = phones_collection.insert_one(data)
        return jsonify({"message": "Phone saved", "id": str(result.inserted_id)}), 201

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/phones/<string:phone_id>', methods=['PUT'])
def update_phone(phone_id):
    try:
        def safe_float(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0

        phone = phones_collection.find_one({"_id": ObjectId(phone_id)})
        if not phone:
            return jsonify({"error": "Phone not found"}), 404

        updated_data = {
            "name": request.form.get("name"),
            "brand": request.form.get("brand"),
            "model": request.form.get("model"),
            "memory": request.form.getlist("memory"),
            "colors": request.form.getlist("colors"),
            "description": request.form.get("description"),
            "price": safe_float(request.form.get("price")),
            "discounted_price": safe_float(request.form.get("discounted_price")),
        }

        video_url = request.form.get("video")
        if video_url:
            updated_data["video"] = video_url

        photo_urls = request.form.getlist("photos")
        if photo_urls:
            updated_data["photos"] = photo_urls

        phones_collection.update_one(
            {"_id": ObjectId(phone_id)},
            {"$set": updated_data}
        )

        return jsonify({"message": "Phone updated successfully"}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/phones', methods=['GET'])
def get_phones():
    try:
        platform = request.args.get('platform', '').lower()
        query = {}

        if platform == 'ios':
            query['brand'] = {'$regex': '^apple$', '$options': 'i'}
        elif platform == 'android':
            query['brand'] = {'$not': {'$regex': '^apple$', '$options': 'i'}}

        phones = []
        for phone in phones_collection.find(query):
            phones.append({
                "id": str(phone.get("_id")),
                "name": phone.get("name"),
                "brand": phone.get("brand"),
                "model": phone.get("model"),
                "memory": phone.get("memory"),
                "colors": phone.get("colors"),
                "description": phone.get("description"),
                "price": phone.get("price"),
                "discounted_price": phone.get("discounted_price"),
                "video": phone.get("video"),
                "photos": phone.get("photos"),
            })
        return jsonify(phones), 200
    except Exception as e:
        print("Error:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/phones/<string:phone_id>', methods=['GET'])
def get_phone_by_id(phone_id):
    try:
        phone = phones_collection.find_one({"_id": ObjectId(phone_id)})
        if not phone:
            return abort(404, description="Phone not found")
        phone["_id"] = str(phone["_id"])  # Convert ObjectId to string
        return jsonify(phone)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/brands', methods=['GET'])
def get_brands():
    brands = list(brands_collection.find({}, {'_id': 0}))  # exclude _id if not needed
    print(f"🚀 ~ brands:", brands)
    return jsonify(brands)

def generate_tinkoff_token(payload: dict, password: str) -> str:
    """Generates the Tinkoff API token."""
    # Only include core fields, exclude nested ones (like Receipt, DATA, Token)
    core_fields = {k: v for k, v in payload.items() if isinstance(v, (str, int)) and k != "Token"}

    # Add password at the end
    core_fields["Password"] = password

    # Sort by key
    sorted_items = sorted(core_fields.items())

    # Concatenate only values (without keys!)
    values_string = ''.join(str(v) for k, v in sorted_items)

    # SHA256 hash
    return hashlib.sha256(values_string.encode('utf-8')).hexdigest()

@app.route('/create-payment', methods=['POST'])
def create_payment():
    """Creates a payment session with Tinkoff and returns the payment URL."""
    data = request.json

    amount = int(float(data.get('amount')) * 100)
    description = data.get('description')
    order_id = str(uuid.uuid4())

    payload = {
        "TerminalKey": TINKOFF_TERMINAL_KEY,
        "Amount": amount,
        "OrderId": order_id,
        "Description": description,
        # You can add more fields like CustomerKey, NotificationURL, SuccessURL, FailURL
        # "NotificationURL": "YOUR_NOTIFICATION_URL", # URL for receiving payment status updates
        # "SuccessURL": "YOUR_SUCCESS_URL", # URL to redirect the user after successful payment
        # "FailURL": "YOUR_FAIL_URL", # URL to redirect the user after failed payment
    }

    # Add Token
    payload["Token"] = generate_tinkoff_token(payload, TINKOFF_PASSWORD)

    try:
        response = requests.post(TINKOFF_INIT_URL, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes
        tinkoff_response = response.json()

        if tinkoff_response.get('Success'):
            return jsonify({
                "payment_url": tinkoff_response.get('PaymentURL'),
                "payment_id": tinkoff_response.get('PaymentId'),
                "order_id": tinkoff_response.get('OrderId')
            }), 200
        else:
            error_message = tinkoff_response.get('Details', 'Unknown error from Tinkoff')
            return jsonify({"error": "Payment initialization failed", "details": error_message}), 400

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Tinkoff API: {e}")
        return jsonify({"error": "Failed to connect to payment gateway"}), 500
    except Exception as e:
        print(f"An unexpected error occurred during payment creation: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    data = request.json
    telegram_id = data.get("telegram_id")
    product_id = data.get("product_id")
    memory = data.get("memory")
    color = data.get("color")
    # Assuming quantity is 1 when adding to cart initially
    quantity = 1

    if not all([telegram_id, product_id, memory, color]):
        return jsonify({"error": "Missing fields"}), 400

    # Find the product details from the loaded CSV data
    product_info = PRODUCTS_DATA.get(product_id)
    if not product_info:
        # If not found in CSV, try to find in MongoDB (for phones)
        try:
            phone = phones_collection.find_one({"_id": ObjectId(product_id)})
            if phone:
                 product_info = {
                    'name': phone.get('name'),
                    'price': phone.get('price', 0),
                    'description': phone.get('description', '')
                 }
            else:
                 return jsonify({"error": "Product not found"}), 404
        except Exception:
             return jsonify({"error": "Product not found"}), 404


    user_collection.update_one(
        {"telegram_id": telegram_id},
        {"$addToSet": {
            "cart": {
                "productId": product_id,
                "name": product_info.get('name'),
                "price": product_info.get('price'),
                "memory": memory,
                "color": color,
                "quantity": quantity # Add quantity field
            }
        }},
        upsert=True # Create user if not exists
    )

    return jsonify({"message": "Item added to cart"}), 200

@app.route('/cart/<int:telegram_id>', methods=['GET'])
def get_cart(telegram_id):
    """Retrieves the user's cart."""
    user = user_collection.find_one({"telegram_id": telegram_id})
    if user:
        # Ensure cart is a list, default to empty list if not exists or is not a list
        cart = user.get("cart", [])
        if not isinstance(cart, list):
            cart = []
        return jsonify({"cart": cart}), 200
    else:
        return jsonify({"cart": []}), 200 # Return empty cart for new users

@app.route('/cart/update-quantity', methods=['POST'])
def update_quantity():
    data = request.json
    telegram_id = data.get('telegram_id')
    product_id = data.get('product_id')
    # memory = data.get('memory') # Include memory and color to uniquely identify item in cart
    # color = data.get('color')
    quantity = data.get('quantity')

    # Note: For updating quantity, you might need to identify the item more specifically
    # if a user can have the same product with different memory/color options in the cart.
    # The current implementation updates the first match of productId.
    # A more robust approach might involve a unique cart item ID or matching on productId, memory, and color.

    if not all([telegram_id, product_id]) or not isinstance(quantity, int) or quantity < 0:
        return jsonify({"error": "Invalid data"}), 400

    # Remove item if quantity is 0
    if quantity == 0:
        user_collection.update_one(
            {"telegram_id": telegram_id},
            {"$pull": {"cart": {"productId": product_id}}}
        )
        return jsonify({"message": "Item removed from cart"}), 200
    else:
        user_collection.update_one(
            {"telegram_id": telegram_id, "cart.productId": product_id},
            {"$set": {"cart.$.quantity": quantity}}
        )
        return jsonify({"message": "Quantity updated"}), 200

@app.route('/cart/remove-item', methods=['POST'])
def remove_item():
    data = request.json
    telegram_id = data.get('telegram_id')
    product_id = data.get('product_id')
    # memory = data.get('memory') # Include memory and color for specific removal
    # color = data.get('color')

    if not all([telegram_id, product_id]):
        return jsonify({"error": "Missing fields"}), 400

    user_collection.update_one(
        {"telegram_id": telegram_id},
        # For specific removal based on memory and color:
        # {"$pull": {"cart": {"productId": product_id, "memory": memory, "color": color}}}
        # For removal based on product_id only (removes all items with this product_id):
        {"$pull": {"cart": {"productId": product_id}}}
    )
    return jsonify({"message": "Item removed"}), 200

@app.route('/register-user', methods=['POST'])
def register_user():
    data = request.json
    telegram_id = data.get("telegram_id")
    username = data.get("username")

    if not telegram_id:
        return jsonify({"error": "Missing telegram_id"}), 400

    # Try to find the user first
    user = user_collection.find_one({"telegram_id": telegram_id})

    if not user:
        # If user doesn't exist, insert them
        user_collection.insert_one({
            "telegram_id": telegram_id,
            "username": username,
            "cart": []
        })
        user = user_collection.find_one({"telegram_id": telegram_id})

    # Return the user info (excluding _id for frontend safety)
    user["_id"] = str(user["_id"])
    return jsonify(user), 200

# --- New routes for Telegram payment integration ---

@app.route('/telegram/get-products', methods=['GET'])
def telegram_get_products():
    """Returns the list of products from the CSV for Telegram bot."""
    # Convert PRODUCTS_DATA dictionary to a list of product objects
    products_list = [{"product_id": pid, **data} for pid, data in PRODUCTS_DATA.items()]
    # You might want to include phones from MongoDB as well, depending on your use case
    # For simplicity, this example only uses CSV data.

    return jsonify(products_list), 200

@app.route('/telegram/create-telegram-invoice', methods=['POST'])
def create_telegram_invoice():
    """Creates a Telegram Payments invoice for a list of products."""
    data = request.json
    telegram_chat_id = data.get("chat_id")
    products_in_cart = data.get("products") # List of product objects from the user's cart

    if not telegram_chat_id or not products_in_cart:
        return jsonify({"error": "Missing chat_id or products"}), 400

    # Prepare invoice items
    invoice_items = []
    total_amount = 0

    for item in products_in_cart:
        product_id = item.get('productId')
        quantity = item.get('quantity', 1)
        price = item.get('price', 0) # Use price from the cart item
        name = item.get('name', 'Unknown Product')

        if not product_id or quantity <= 0:
            continue # Skip invalid items

        # Telegram expects amount in the smallest unit (cents for USD, kopecks for RUB)
        # Assuming price is in the main currency unit (e.g., RUB)
        amount_in_smallest_unit = int(price * quantity * 100)
        total_amount += amount_in_smallest_unit

        invoice_items.append({
            "label": f"{name} ({item.get('memory', '')}, {item.get('color', '')}) x {quantity}",
            "amount": amount_in_smallest_unit
        })

    if not invoice_items:
        return jsonify({"error": "No valid items in the cart"}), 400

    # Create a unique payload for this invoice
    payload = {
        "chat_id": telegram_chat_id,
        "title": "Ваш заказ",
        "description": "Оплата товаров из корзины",
        "payload": str(uuid.uuid4()), # Unique identifier for the payment
        "provider_token": "YOUR_TELEGRAM_PAYMENTS_PROVIDER_TOKEN", # **Replace with your Telegram Payments Provider Token**
        "currency": "RUB", # Replace with your currency code
        "prices": invoice_items,
        "need_name": True, # Request user's name
        "need_shipping_address": True, # Request shipping address
        "send_email_to_provider": True, # Send user's email to provider
        "send_phone_number_to_provider": True # Send user's phone number to provider
        # Add other optional fields as needed (e.g., photo_url, is_flexible)
    }

    try:
        # Send the request to Telegram Bot API to create the invoice
        telegram_response = requests.post(f'{TELEGRAM_API_URL}/sendInvoice', json=payload)
        telegram_response.raise_for_status() # Raise an exception for bad status codes
        telegram_data = telegram_response.json()

        if telegram_data.get('ok'):
            # The response for sendInvoice doesn't contain a direct payment URL
            # Instead, the Telegram bot sends a message with the invoice.
            # The user clicks a button in the message to pay.
            # The successful response indicates the message was sent successfully.
            return jsonify({"message": "Telegram invoice sent successfully"}), 200
        else:
            error_message = telegram_data.get('description', 'Unknown error from Telegram')
            return jsonify({"error": "Failed to send Telegram invoice", "details": error_message}), 400

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Telegram API: {e}")
        return jsonify({"error": "Failed to send Telegram invoice"}), 500
    except Exception as e:
        print(f"An unexpected error occurred during Telegram invoice creation: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

@app.route('/telegram/webhook', methods=['POST'])
def telegram_webhook():
    """Handles updates from the Telegram Bot API (e.g., pre-checkout queries, successful payments)."""
    update = request.json
    print("Received Telegram update:", update) # Log the incoming update

    # Handle pre-checkout queries (when user clicks "Pay" button)
    if 'pre_checkout_query' in update:
        query = update['pre_checkout_query']
        query_id = query['id']
        # You can perform final checks here (e.g., check stock availability)

        # Respond to the pre-checkout query
        # If everything is okay:
        answer_payload = {
            "pre_checkout_query_id": query_id,
            "ok": True
        }
        # If there is an error:
        # answer_payload = {
        #     "pre_checkout_query_id": query_id,
        #     "ok": False,
        #     "error_message": "Sorry, this item is out of stock."
        # }

        try:
            response = requests.post(f'{TELEGRAM_API_URL}/answerPreCheckoutQuery', json=answer_payload)
            response.raise_for_status()
            print("Answered pre-checkout query:", response.json())
        except requests.exceptions.RequestException as e:
            print(f"Error answering pre-checkout query: {e}")

    # Handle successful payment updates
    if 'message' in update and 'successful_payment' in update['message']:
        successful_payment = update['message']['successful_payment']
        chat_id = update['message']['chat']['id']
        invoice_payload = successful_payment.get('invoice_payload') # The unique payload you sent in sendInvoice
        currency = successful_payment.get('currency')
        total_amount = successful_payment.get('total_amount')
        provider_payment_charge_id = successful_payment.get('provider_payment_charge_id')

        print(f"Successful payment received! Chat ID: {chat_id}, Payload: {invoice_payload}, Amount: {total_amount} {currency}, Provider Charge ID: {provider_payment_charge_id}")

        # Here you should:
        # 1. Process the order based on the `invoice_payload`.
        #    - Find the user's cart associated with this payload.
        #    - Mark the order as paid in your database.
        #    - Clear the user's cart.
        # 2. Notify the user about the successful payment (optional, but good practice).
        #    You can use the `sendMessage` method of the Telegram Bot API.

        # Example: Clear the user's cart (assuming invoice_payload is linked to a user/cart)
        # This is a simplified example. You would need a way to link the payload to the user.
        # Maybe store the payload in the user's document when creating the invoice.
        # user_collection.update_one({"telegram_id": chat_id}, {"$set": {"cart": []}})
        # print(f"Cart cleared for user {chat_id}")

        # Example: Send a thank you message
        try:
            thank_you_message_payload = {
                "chat_id": chat_id,
                "text": "Спасибо за ваш заказ! Мы получили вашу оплату."
            }
            requests.post(f'{TELEGRAM_API_URL}/sendMessage', json=thank_you_message_payload)
        except requests.exceptions.RequestException as e:
            print(f"Error sending thank you message: {e}")


    # Return a 200 OK response to acknowledge the update
    return jsonify({"status": "ok"}), 200

@app.route('/products', methods=['GET'])
def get_products():
    """Returns the list of products from the CSV."""
    # Convert PRODUCTS_DATA dictionary to a list of product objects
    products_list = [{"product_id": pid, **data} for pid, data in PRODUCTS_DATA.items()]
    return jsonify(products_list), 200

@app.route('/products/<string:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    """Returns a single product by ID from the CSV."""
    product = PRODUCTS_DATA.get(product_id)
    if product:
        return jsonify({"product_id": product_id, **product}), 200
    else:
        return jsonify({"error": "Product not found"}), 404


if __name__ == '__main__':
    # Ensure the uploads directory exists
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(host='0.0.0.0', port=5000, debug=True) # Set debug=True for development