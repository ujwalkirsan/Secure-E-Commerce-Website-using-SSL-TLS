from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import secrets
import ssl
import socket
import datetime
import hashlib
import json

# Blockchain-related imports
from datetime import datetime

class Block:
    def __init__(self, index, timestamp, data, previous_hash=''):
        """
        Initialize a new block in the blockchain
        
        Args:
            index (int): Position of the block in the blockchain
            timestamp (str): Time of block creation
            data (dict): Custom data/transactions for the block
            previous_hash (str): Hash of the previous block
        """
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0  # Used for proof-of-work
        self.hash = self.calculate_hash()
        
    
    def calculate_hash(self):
        """
        Calculate SHA-256 hash of the block's contents
        
        Returns:
            str: SHA-256 hash of the block
        """
        # Convert block contents to a string for hashing
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True).encode()
        
        return hashlib.sha256(block_string).hexdigest()
    
    def mine_block(self, difficulty=4):
        """
        Perform proof-of-work mining
        
        Args:
            difficulty (int): Number of leading zeros required in hash
        """
        target = '0' * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

class BlockchainTransactionTracker:
    def __init__(self, blockchain_file='blockchain_transactions.json'):
        """
        Initialize blockchain transaction tracker
        
        Args:
            blockchain_file (str): File to store blockchain transactions
        """
        self.blockchain_file = blockchain_file
        self.chain = self.load_blockchain()
    
    def load_blockchain(self):
        """
        Load existing blockchain or create a new one
        
        Returns:
            list: Existing blockchain or new blockchain with genesis block
        """
        if os.path.exists(self.blockchain_file):
            try:
                with open(self.blockchain_file, 'r') as f:
                    saved_chain = json.load(f)
                    # Convert saved chain back to Block objects
                    return [Block(
                        block['index'], 
                        block['timestamp'], 
                        block['data'], 
                        block['previous_hash']
                    ) for block in saved_chain]
            except (json.JSONDecodeError, IOError):
                # If file is corrupted or unreadable, start a new blockchain
                return [self.create_genesis_block()]
        else:
            # Create a new blockchain with genesis block
            return [self.create_genesis_block()]
    
    def create_genesis_block(self):
        """
        Create the first block in the blockchain
        
        Returns:
            Block: Genesis block
        """
        return Block(0, str(datetime.now()), 
                     {"message": "E-Commerce Platform Genesis Block"})
    
    def add_transaction_block(self, transaction_data):
        """
        Add a new transaction block to the blockchain
        
        Args:
            transaction_data (dict): Transaction details to be recorded
        """
        # Get the latest block
        latest_block = self.chain[-1]
        
        # Create a new block
        new_block = Block(
            index=latest_block.index + 1,
            timestamp=str(datetime.now()),
            data=transaction_data,
            previous_hash=latest_block.hash
        )
        
        # Mine the block
        new_block.mine_block()
        
        # Add block to the chain
        self.chain.append(new_block)
        
        # Save blockchain
        self.save_blockchain()
    
    def save_blockchain(self):
        """
        Save the blockchain to a JSON file
        """
        try:
            # Convert blocks to a format that can be saved as JSON
            saveable_chain = [{
                'index': block.index,
                'timestamp': block.timestamp,
                'data': block.data,
                'previous_hash': block.previous_hash,
                'hash': block.hash,
                'nonce': block.nonce
            } for block in self.chain]
            
            with open(self.blockchain_file, 'w') as f:
                json.dump(saveable_chain, f, indent=2)
        except IOError as e:
            print(f"Error saving blockchain: {e}")
    
    def get_transaction_history(self):
        """
        Retrieve transaction history
        
        Returns:
            list: List of transaction blocks (excluding genesis block)
        """
        return [block for block in self.chain[1:]]

# Existing product data and other imports
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Sample product data
products = [
    {"id": 1, "name": "Laptop", "price": 100000, "description": "Powerful laptop with high performance"},
    {"id": 2, "name": "Smartphone", "price": 25000, "description": "Latest smartphone with advanced features"},
    {"id": 3, "name": "Headphones", "price": 8000, "description": "Noise cancelling premium headphones"},
    {"id": 4, "name": "Tablet", "price": 30000, "description": "Lightweight tablet for productivity"},
]

# Create global blockchain tracker
blockchain_tracker = BlockchainTransactionTracker()

# Existing routes
@app.route('/')
def index():
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in products if p["id"] == product_id), None)
    if product:
        return render_template('product.html', product=product)
    return redirect(url_for('index'))

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = next((p for p in products if p["id"] == product_id), None)
    if product:
        if 'cart' not in session:
            session['cart'] = []
        session['cart'].append(product)
        session.modified = True
        flash(f"{product['name']} added to cart!")
    return redirect(url_for('index'))

@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    total = sum(item['price'] for item in cart)
    return render_template('cart.html', cart=cart, total=total)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # Prepare transaction data
        cart = session.get('cart', [])
        total = sum(item['price'] for item in cart)
        
        # Prepare blockchain transaction data
        transaction_data = {
            "transaction_type": "purchase",
            "total_amount": total,
            "items": [item['name'] for item in cart],
            "timestamp": str(datetime.now()),
            "session_id": session.get('_id', 'unknown')
        }
        
        # Record transaction in blockchain
        blockchain_tracker.add_transaction_block(transaction_data)
        
        # Existing checkout logic
        session.pop('cart', None)
        flash("Thank you for your purchase!")
        return redirect(url_for('index'))
    
    return render_template('checkout.html')

@app.route('/transaction_history')
def transaction_history():
    """
    Display blockchain transaction history
    """
    transactions = blockchain_tracker.get_transaction_history()
    
    # Prepare transactions for template rendering
    transaction_list = [{
        'index': transaction.index,
        'timestamp': transaction.timestamp,
        'data': transaction.data,
        'hash': transaction.hash
    } for transaction in transactions]
    
    return render_template('transaction_history.html', transactions=transaction_list)

@app.route('/secure_info')
def secure_info():
    import socket
    import ssl
    import datetime

    # Gather comprehensive security information
    security_info = {
        "Current Timestamp": datetime.datetime.now().isoformat(),
        "Server Hostname": socket.gethostname(),
        "Server IP": socket.gethostbyname(socket.gethostname()),
        "Connection Details": {
            "Protocol Version": request.environ.get('SERVER_PROTOCOL', 'Unknown'),
            "SSL Cipher": request.environ.get('SSL_CIPHER', 'Unknown'),
            "SSL Protocol": request.environ.get('SSL_PROTOCOL', 'Unknown'),
            "Is Secure Connection": 'Yes' if request.is_secure else 'No',
        },
        "Client Information": {
            "Remote Address": request.remote_addr,
            "User Agent": request.user_agent.string,
        },
        "Security Flags": {
            "HTTPS Enforced": 'Yes' if request.is_secure else 'No',
            "Session Secure": 'Yes' if session.get('_secure', False) else 'No',
        }
    }

    # Generate HTML to display security information
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Secure Connection Information</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #2c3e50; border-bottom: 2px solid #3498db; }
            .security-section { background-color: #f4f4f4; padding: 15px; margin-bottom: 15px; border-radius: 5px; }
            .security-section h2 { color: #34495e; margin-bottom: 10px; }
            .security-item { margin-bottom: 10px; }
            .security-item strong { display: inline-block; width: 200px; color: #2980b9; }
            .secure { color: green; font-weight: bold; }
            .warning { color: orange; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🔒 Secure Connection Information</h1>
    """

    # Dynamic HTML generation
    for section, details in security_info.items():
        html += f"<div class='security-section'><h2>{section}</h2>"
        if isinstance(details, dict):
            for key, value in details.items():
                # Add color coding for security status
                if value == 'Yes':
                    html += f"<div class='security-item'><strong>{key}:</strong> <span class='secure'>{value}</span></div>"
                elif value == 'No':
                    html += f"<div class='security-item'><strong>{key}:</strong> <span class='warning'>{value}</span></div>"
                else:
                    html += f"<div class='security-item'><strong>{key}:</strong> {value}</div>"
        else:
            html += f"<div class='security-item'><strong>{section}:</strong> {details}</div>"
        html += "</div>"

    # Add return link and closing HTML
    html += """
        <div style="text-align: center; margin-top: 20px;">
            <a href="/" style="text-decoration: none; color: #3498db;">Return to Home</a>
        </div>
    </body>
    </html>
    """

    return html

if __name__ == '__main__':
    # First ensure we have certificates
    if not os.path.exists("cert.pem") or not os.path.exists("key.pem"):
        print("SSL certificates not found. Generating self-signed certificates...")
        from generate_cert import generate_self_signed_cert
        generate_self_signed_cert()
    
    # Configure SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    
    # Run Flask app with SSL/TLS
    print("Starting secure server at https://localhost:5000")
    app.run(host='0.0.0.0', port=5000, ssl_context=context, debug=True)