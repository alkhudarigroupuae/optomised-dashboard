# Omaya Dashboard Template

This is a Flask-based Dashboard Template designed to connect to any WooCommerce store.

## Features
- **WooCommerce Integration**: Connects to your store via REST API.
- **Analytics**: Supports Google Analytics 4 and Google Search Console.
- **Responsive Design**: Modern UI for managing your store.
- **Deployment Ready**: Configured for Render and Vercel.

## Configuration

To connect your own WordPress/WooCommerce store, set the following Environment Variables in your deployment platform (Render, Vercel, etc.) or a local `.env` file:

| Variable | Description | Default (Demo) |
|----------|-------------|----------------|
| `WC_URL` | Your WordPress Site URL | `https://mahmoudbey-oc.com` |
| `WC_CONSUMER_KEY` | WooCommerce Consumer Key | `ck_...` |
| `WC_CONSUMER_SECRET` | WooCommerce Consumer Secret | `cs_...` |
| `ADMIN_USER` | Dashboard Login Username | `admin` |
| `ADMIN_PASS` | Dashboard Login Password | `omaya2024` |

### How to get WooCommerce Keys:
1. Go to **WooCommerce > Settings > Advanced > REST API**.
2. Click **Add key**.
3. Give it a description (e.g., "Omaya Dashboard").
4. Set Permissions to **Read/Write**.
5. Copy the **Consumer Key** and **Consumer Secret**.

## Deployment

### Render
1. Create a new **Web Service**.
2. Connect your GitHub repository.
3. Add the Environment Variables listed above.
4. Deploy!

### Vercel
1. Import the project.
2. Add the Environment Variables in the Project Settings.
3. Deploy.

## Local Development
1. Clone the repo.
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python dashboard_app/app.py`
