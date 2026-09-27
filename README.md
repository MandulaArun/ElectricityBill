# Blockchain Electricity Billing System

A Flask-based electricity billing application that records meter readings and payments in a small proof-of-work blockchain.

## Features

- Slab-based electricity bill calculation
- Proof-of-work mining for meter readings and payments
- Consumer bill lookup and payment flow
- Billing history per consumer
- Live blockchain ledger viewer
- Chain validation and tamper-detection demonstration
- Dashboard with payment and consumption statistics
- Light and dark display themes

## Requirements

- Python 3.9 or newer
- Flask

Install Flask with:

```bash
pip install flask
```

## Run Locally

From the project directory, run:

```bash
python app.py
```

Open http://127.0.0.1:5000/ in a browser.

The application stores blockchain data in memory, so restarting the server resets the ledger.

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/` | Web application |
| POST | `/api/add_reading` | Add a meter reading and mine a block |
| GET | `/api/get_bill/<consumer_id>` | Get the current bill |
| POST | `/api/pay_bill` | Pay a consumer bill and mine a payment block |
| GET | `/api/history/<consumer_id>` | Get billing history |
| GET | `/api/stats` | Get dashboard statistics |
| GET | `/api/chain` | Get the complete blockchain |
| GET | `/api/validate` | Validate the blockchain |
| POST | `/api/tamper` | Demonstrate tamper detection |

## Project Structure

```text
app.py                 Flask application and API routes
blockchain.py          Block, mining, billing, and validation logic
templates/index.html   Frontend dashboard
ElectricityDApp/       Duplicate project copy retained from the original workspace
```

## Notes

This is an educational demonstration. It uses an in-memory ledger and Flask's development server; it is not intended for production billing or payment processing.