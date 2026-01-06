from flask import Flask, jsonify, send_from_directory, render_template, request, redirect, url_for, session
from woocommerce import API
import os

# Try importing Google Services with fallback
try:
    from dashboard_app.google_services import get_ga4_data, get_gsc_data
except ImportError:
    try:
        from google_services import get_ga4_data, get_gsc_data
    except ImportError:
        def get_ga4_data(): return {"active_users": "N/A", "total_users": "N/A", "status": "error"}
        def get_gsc_data(): return {"clicks": 0, "impressions": 0, "status": "error"}

app = Flask(__name__, static_folder='assets', static_url_path='/assets')
app.secret_key = 'omaya_secret_key_2024'  # Required for session

# Admin Credentials
ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'omaya2024')

# WooCommerce Configuration
# Default/Demo values (can be overridden by Environment Variables)
DEFAULT_WC_URL = "https://mahmoudbey-oc.com"
DEFAULT_WC_CK = "ck_08595738870196720131498e16f3930a08d0033c"
DEFAULT_WC_CS = "cs_883505c215286282e9b06292d348a7b686001004"

WC_URL = os.environ.get('WC_URL', DEFAULT_WC_URL)
WC_CK = os.environ.get('WC_CONSUMER_KEY', DEFAULT_WC_CK)
WC_CS = os.environ.get('WC_CONSUMER_SECRET', DEFAULT_WC_CS)

wcapi = API(
    url=WC_URL,
    consumer_key=WC_CK,
    consumer_secret=WC_CS,
    version="wc/v3",
    timeout=20
)

@app.route('/')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # Fetch recent orders for the dashboard
    try:
        response = wcapi.get("orders", params={"per_page": 5})
        recent_orders = response.json() if response.status_code == 200 else []
    except:
        recent_orders = []

    # Fetch Google Data
    ga4_data = get_ga4_data()
    gsc_data = get_gsc_data()

    return render_template('dashboard.html', recent_orders=recent_orders, ga4=ga4_data, gsc=gsc_data)

@app.route('/products')
def products():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        response = wcapi.get("products", params={"per_page": 20})
        products_data = response.json() if response.status_code == 200 else []
    except:
        products_data = []
        
    return render_template('products.html', products=products_data)

@app.route('/orders')
def orders():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
        
    try:
        response = wcapi.get("orders", params={"per_page": 20})
        orders_data = response.json() if response.status_code == 200 else []
    except:
        orders_data = []
        
    return render_template('orders.html', orders=orders_data)

@app.route('/customers')
def customers():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
        
    try:
        response = wcapi.get("customers", params={"per_page": 20})
        customers_data = response.json() if response.status_code == 200 else []
    except:
        customers_data = []
        
    return render_template('customers.html', customers=customers_data)

@app.route('/marketing')
def marketing():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
        
    try:
        response = wcapi.get("coupons", params={"per_page": 20})
        coupons_data = response.json() if response.status_code == 200 else []
    except:
        coupons_data = []
        
    return render_template('marketing.html', coupons=coupons_data)

@app.route('/reports')
def reports():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('reports.html')

@app.route('/settings')
def settings():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('settings.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = 'بيانات الدخول غير صحيحة'
            
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/<path:path>')
def serve_static(path):
    if path == 'favicon.ico': 
        return send_from_directory('.', path)
    return send_from_directory('.', path)

@app.route('/api/stats')
def get_stats():
    try:
        # Fetch Orders (Example Stat)
        orders_resp = wcapi.get("orders", params={"per_page": 1})
        orders_count = orders_resp.headers.get('X-WP-Total')
        
        # Fetch Products Count
        products_resp = wcapi.get("products", params={"per_page": 1})
        products_count = products_resp.headers.get('X-WP-Total')
        
        # Fetch Customers Count
        customers_resp = wcapi.get("customers", params={"per_page": 1})
        customers_count = customers_resp.headers.get('X-WP-Total')

        # Calculate Total Sales
        reports_resp = wcapi.get("reports/sales", params={"period": "year"})
        if reports_resp.status_code == 200:
            data = reports_resp.json()
            total_sales = data[0]['total_sales'] if data else 0
        else:
            total_sales = "Error"
        
        # Simplified for speed
        # total_sales = "N/A" # Reports API is often faster

        return jsonify({
            "orders": orders_count,
            "products": products_count,
            "customers": customers_count,
            "sales": total_sales
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Dashboard running at http://localhost:5000")
    app.run(debug=True, port=5000)
