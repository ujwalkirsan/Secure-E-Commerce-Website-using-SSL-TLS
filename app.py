# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import secrets
import ssl

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Sample product data
products = [
    {"id": 1, "name": "Laptop", "price": 999.99, "description": "Powerful laptop with high performance"},
    {"id": 2, "name": "Smartphone", "price": 599.99, "description": "Latest smartphone with advanced features"},
    {"id": 3, "name": "Headphones", "price": 199.99, "description": "Noise cancelling premium headphones"},
    {"id": 4, "name": "Tablet", "price": 399.99, "description": "Lightweight tablet for productivity"},
]

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
        # In a real app, here we would process payment securely
        session.pop('cart', None)
        flash("Thank you for your purchase!")
        return redirect(url_for('index'))
    return render_template('checkout.html')

@app.route('/secure_info')
def secure_info():
    # This route demonstrates that we're running on a secure connection
    return f"""
    <h1>Secure Connection Information</h1>
    <p>Protocol Version: {request.environ.get('SERVER_PROTOCOL', 'Unknown')}</p>
    <p>SSL Cipher: {request.environ.get('SSL_CIPHER', 'Unknown')}</p>
    <p>SSL Protocol: {request.environ.get('SSL_PROTOCOL', 'Unknown')}</p>
    <p>Is Secure: {'Yes' if request.is_secure else 'No'}</p>
    <p><a href="/">Return to Home</a></p>
    """

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
