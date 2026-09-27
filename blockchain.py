import hashlib
import json
import time


class Block:
    DIFFICULTY = 4  # Hash must start with "0000" — Proof of Work

    def __init__(self, index, data, previous_hash):
        self.index         = index
        self.timestamp     = time.strftime("%Y-%m-%d %H:%M:%S")
        self.data          = data
        self.previous_hash = previous_hash
        self.nonce         = 0
        self.hash          = self.mine()

    def calculate_hash(self):
        content = json.dumps({
            "index":         self.index,
            "timestamp":     self.timestamp,
            "data":          self.data,
            "previous_hash": self.previous_hash,
            "nonce":         self.nonce
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def mine(self):
        """Proof of Work: find nonce so hash starts with DIFFICULTY zeros."""
        target = "0" * self.DIFFICULTY
        while True:
            h = self.calculate_hash()
            if h.startswith(target):
                return h
            self.nonce += 1

    def to_dict(self):
        return {
            "index":         self.index,
            "timestamp":     self.timestamp,
            "data":          self.data,
            "previous_hash": self.previous_hash,
            "nonce":         self.nonce,
            "hash":          self.hash
        }


class Blockchain:
    # Slab tariff: (max_units, rate_per_unit)
    SLABS = [
        (100, 3),
        (300, 5),
        (float('inf'), 7)
    ]

    def __init__(self):
        self.chain     = []
        self.consumers = {}
        self.history   = {}
        self._create_genesis_block()

    def calculate_bill(self, units):
        amount, remaining, prev = 0, units, 0
        breakdown = []
        for (limit, rate) in self.SLABS:
            in_slab = min(remaining, limit - prev)
            if in_slab <= 0:
                break
            cost = in_slab * rate
            amount += cost
            breakdown.append({"units": in_slab, "rate": rate, "cost": cost})
            remaining -= in_slab
            prev = limit
            if remaining <= 0:
                break
        return amount, breakdown

    def _create_genesis_block(self):
        self.chain.append(Block(0, {"message": "Genesis Block"}, "0"))

    def add_reading(self, consumer_id, name, address, units, month=""):
        units  = int(units)
        amount, breakdown = self.calculate_bill(units)
        month  = month or time.strftime("%B %Y")

        self.consumers[consumer_id] = {
            "name": name, "address": address,
            "units": units, "amount": amount,
            "breakdown": breakdown, "month": month,
            "paid": False, "paid_at": None
        }
        if consumer_id not in self.history:
            self.history[consumer_id] = []
        self.history[consumer_id].append(
            {"month": month, "units": units, "amount": amount, "paid": False}
        )

        block = Block(len(self.chain), {
            "type": "METER_READING", "consumer_id": consumer_id,
            "name": name, "address": address, "units": units,
            "amount_due": amount, "month": month, "breakdown": breakdown
        }, self.chain[-1].hash)
        self.chain.append(block)
        return block

    def pay_bill(self, consumer_id):
        if consumer_id not in self.consumers:
            return None, "Consumer not found"
        c = self.consumers[consumer_id]
        if c["paid"]:
            return None, "Bill already paid"
        c["paid"]    = True
        c["paid_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        if self.history.get(consumer_id):
            self.history[consumer_id][-1]["paid"] = True

        block = Block(len(self.chain), {
            "type": "PAYMENT", "consumer_id": consumer_id,
            "name": c["name"], "amount_paid": c["amount"],
            "month": c.get("month", ""), "paid_at": c["paid_at"]
        }, self.chain[-1].hash)
        self.chain.append(block)
        return block, "Payment successful"

    def is_chain_valid(self):
        target = "0" * Block.DIFFICULTY
        for i in range(1, len(self.chain)):
            cur, prv = self.chain[i], self.chain[i-1]
            if cur.hash != cur.calculate_hash():
                return False, i
            if cur.previous_hash != prv.hash:
                return False, i
            if not cur.hash.startswith(target):
                return False, i
        return True, -1

    def tamper_block(self, block_index, new_units):
        if block_index <= 0 or block_index >= len(self.chain):
            return False, "Invalid block index"
        self.chain[block_index].data["units"]      = new_units
        self.chain[block_index].data["amount_due"] = new_units * 3
        return True, f"Block #{block_index} secretly modified. Chain is now INVALID!"

    def get_bill(self, consumer_id):
        return self.consumers.get(consumer_id)

    def get_history(self, consumer_id):
        return self.history.get(consumer_id, [])

    def get_chain(self):
        return [b.to_dict() for b in self.chain]

    def get_stats(self):
        total   = len(self.consumers)
        paid    = sum(1 for c in self.consumers.values() if c["paid"])
        valid, _ = self.is_chain_valid()
        return {
            "total_blocks":    len(self.chain),
            "total_consumers": total,
            "paid":            paid,
            "unpaid":          total - paid,
            "revenue":         sum(c["amount"] for c in self.consumers.values() if c["paid"]),
            "pending":         sum(c["amount"] for c in self.consumers.values() if not c["paid"]),
            "is_valid":        valid,
            "consumer_data":   [
                {"id": cid, "name": c["name"], "units": c["units"],
                 "amount": c["amount"], "paid": c["paid"]}
                for cid, c in self.consumers.items()
            ]
        }