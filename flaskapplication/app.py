from flask import Flask, render_template, request, jsonify
from NewDatabase import Database

import razorpay
import hmac
import hashlib

from decimal import Decimal

class ParkingApp:
    def __init__(self):
        # Initialize Flask
        self.app = Flask(__name__)
        self.app.jinja_env.globals['zip'] = zip
        # Set up routes
        self.setup_routes()

    def setup_routes(self):
        # Home route
        @self.app.route('/')
        def home(): 
            bills = Database().fetchAllBills()
            return render_template('index.html', bills=bills)
        
        @self.app.route("/create_order/<int:bill_id>")
        def create_payment_order(bill_id):

            client = razorpay.Client(auth=("rzp_test_RhyiBK22nSr7DA", "31RnGGhvP3TRgZQGp7eoJuRe"))

            array = Database().fetchBillsfromID(bill_id)
            
            amount = array[2]
            
            if amount < 1:
                amount = 1
            
            if isinstance(amount, Decimal):
                amount = int(amount)

            amount = amount * 100

            order = client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": 1
            })  

            return jsonify({
                "order_id": order["id"],
                "amount": amount,
                "key_id": "rzp_test_RhyiBK22nSr7DA"
            })


            
        # -------------------------------
        # 2️⃣ VALIDATE PAYMENT SIGNATURE  
        # -------------------------------
        def verify_signature(order_id, payment_id, signature):
            generated_signature = hmac.new(
                bytes("31RnGGhvP3TRgZQGp7eoJuRe", "utf-8"),
                bytes(order_id + "|" + payment_id, "utf-8"),
                hashlib.sha256
            ).hexdigest()

            return generated_signature == signature


        # -------------------------------
        # 3️⃣ PAYMENT SUCCESS CALLBACK
        # -------------------------------
        @self.app.route("/payment_success", methods=["POST"])
        def payment_success():

            order_id = request.form.get("razorpay_order_id")
            payment_id = request.form.get("razorpay_payment_id")
            signature = request.form.get("razorpay_signature")
            bill_id = request.form.get("bill_id")

            if verify_signature(order_id, payment_id, signature):
                # TODO: Update your database payment table here
                print("Payment Verified:", payment_id)
                Database().updatebillpayment(bill_id)
                return jsonify({"status": "success", "payment_id": payment_id})

            else:
                return jsonify({"status": "failed", "message": "Invalid signature"})
            # return f"Details for Bill ID: {bill_id}"




    def run(self):
        # Run Flask app
        self.app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)


if __name__ == '__main__':
    app = ParkingApp()
    app.run()
#     bills = [
#                 {"plate": "MH15GR9755", "in_time": "03:30 AM", "out_time": "04:00 AM", "amount": 50},
#                 {"plate": "MH15FZ7455", "in_time": "03:30 AM", "out_time": "04:00 AM", "amount": 50},
#                 {"plate": "MH15AB1234", "in_time": "02:00 AM", "out_time": "03:15 AM", "amount": 40}
#             ]
#     app_instance = ParkingApp(bills)
#     app_instance.run()
