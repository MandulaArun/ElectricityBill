from flask import Flask, render_template, request, jsonify
from blockchain import Blockchain

app = Flask(__name__)

# Single blockchain instance (lives as long as the server runs)
ledger = Blockchain()


# ─── Page Routes ──────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("index.html")


# ─── API Routes ───────────────────────────────────────────────

@app.route("/api/add_reading", methods=["POST"])
def add_reading():
    data = request.get_json()

    consumer_id = data.get("consumer_id", "").strip()
    name        = data.get("name", "").strip()
    address     = data.get("address", "").strip()
    units       = data.get("units", 0)
    month       = data.get("month", "").strip()

    if not consumer_id or not name or not address or not units:
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        units = int(units)
        if units <= 0:
            raise ValueError
    except ValueError:
        return jsonify({"success": False, "message": "Units must be a positive number"}), 400

    block = ledger.add_reading(consumer_id, name, address, units, month)

    return jsonify({
        "success": True,
        "message": f"Meter reading added. Bill generated: Rs.{block.data['amount_due']}",
        "block": {
            "index":     block.index,
            "hash":      block.hash,
            "timestamp": block.timestamp,
            "nonce":     block.nonce,                    # FIX: was missing
            "amount":    block.data["amount_due"],
            "breakdown": block.data.get("breakdown", []) # FIX: was missing
        }
    })


@app.route("/api/get_bill/<consumer_id>")
def get_bill(consumer_id):
    bill = ledger.get_bill(consumer_id)
    if not bill:
        return jsonify({"success": False, "message": "No bill found for this Consumer ID"}), 404

    return jsonify({"success": True, "bill": bill, "consumer_id": consumer_id})


@app.route("/api/pay_bill", methods=["POST"])
def pay_bill():
    data        = request.get_json()
    consumer_id = data.get("consumer_id", "").strip()

    if not consumer_id:
        return jsonify({"success": False, "message": "Consumer ID required"}), 400

    block, message = ledger.pay_bill(consumer_id)

    if block:
        return jsonify({
            "success": True,
            "message": message,
            "block": {
                "index":     block.index,
                "hash":      block.hash,
                "timestamp": block.timestamp,
                "nonce":     block.nonce             # FIX: was missing
            }
        })
    else:
        return jsonify({"success": False, "message": message}), 400


@app.route("/api/chain")
def get_chain():
    chain          = ledger.get_chain()
    is_valid, bad  = ledger.is_chain_valid()   # FIX: unpack tuple
    return jsonify({
        "chain":     chain,
        "length":    len(chain),
        "is_valid":  is_valid,
        "bad_index": bad,
        "consumers": len(ledger.consumers),
    })


# FIX: /api/stats was completely missing — dashboard calls this
@app.route("/api/stats")
def get_stats():
    stats          = ledger.get_stats()
    is_valid, bad  = ledger.is_chain_valid()   # FIX: unpack tuple
    stats["is_valid"]  = is_valid
    stats["bad_index"] = bad
    return jsonify(stats)


# FIX: /api/history/<id> was completely missing — Load History calls this
@app.route("/api/history/<consumer_id>")
def get_history(consumer_id):
    history = ledger.get_history(consumer_id)
    return jsonify({"success": True, "history": history, "consumer_id": consumer_id})


# FIX: /api/tamper was completely missing — Tamper Demo calls this
@app.route("/api/tamper", methods=["POST"])
def tamper():
    data        = request.get_json()
    block_index = data.get("block_index", 1)
    new_units   = data.get("new_units", 5)

    try:
        block_index = int(block_index)
        new_units   = int(new_units)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Invalid input"}), 400

    success, message = ledger.tamper_block(block_index, new_units)
    return jsonify({"success": success, "message": message})


@app.route("/api/validate")
def validate():
    is_valid, bad = ledger.is_chain_valid()    # FIX: unpack tuple
    return jsonify({
        "is_valid":  is_valid,
        "bad_index": bad,
        "message":   "Chain is valid — no tampering detected" if is_valid else "Chain is INVALID — tampering detected!"
    })


# ─── Run ──────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  Blockchain Electricity Billing System")
    print("  ======================================")
    print("  Open this in your browser:")
    print("  http://127.0.0.1:5000\n")
    app.run(debug=True)