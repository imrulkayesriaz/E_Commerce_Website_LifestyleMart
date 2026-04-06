import os
import requests
import uuid
from flask import url_for
from dotenv import load_dotenv

load_dotenv()

class SSLCommerzGateway:
    def __init__(self):
        self.store_id = os.getenv('SSLCOMMERZ_STORE_ID', 'test_store_id')
        self.store_pass = os.getenv('SSLCOMMERZ_STORE_PASS', 'test_store_pass')
        self.is_sandbox = os.getenv('SSLCOMMERZ_IS_SANDBOX', 'True').lower() == 'true'
        self.simulate = os.getenv('SSLCOMMERZ_SIMULATE', 'True').lower() == 'true'
        
        if self.is_sandbox:
            self.base_url = "https://sandbox.sslcommerz.com"
        else:
            self.base_url = "https://securepay.sslcommerz.com"
            
    def initiate_payment(self, order, user, host_url):
        """
        Initiates a payment session with SSLCommerz.
        If SIMULATE is True, it returns a local mock URL.
        """
        if self.simulate:
            # Simulate a successful session initiation by returning a mock URL
            return f"{host_url}/payment/simulate/{order.order_number}"

        payload = {
            'store_id': self.store_id,
            'store_passwd': self.store_pass,
            'total_amount': order.total_amount,
            'currency': 'BDT',
            'tran_id': order.order_number,
            'success_url': f"{host_url}/payment/success",
            'fail_url': f"{host_url}/payment/fail",
            'cancel_url': f"{host_url}/payment/cancel",
            'ipn_url': f"{host_url}/payment/ipn",
            'cus_name': user.name,
            'cus_email': user.email,
            'cus_add1': user.address or 'Dhaka',
            'cus_city': 'Dhaka',
            'cus_country': 'Bangladesh',
            'cus_phone': user.phone or '01711000000',
            'shipping_method': 'Courier',
            'num_of_item': len(order.order_items),
            'product_name': f"Order {order.order_number}",
            'product_category': 'eCommerce',
            'product_profile': 'general'
        }

        try:
            response = requests.post(
                f"{self.base_url}/gwprocess/v4/api.php", 
                data=payload,
                timeout=10
            )
            response_data = response.json()
            
            if response_data.get('status') == 'SUCCESS':
                return response_data.get('GatewayPageURL')
            else:
                print(f"SSLCommerz Error: {response_data.get('failedreason')}")
                return None
        except Exception as e:
            print(f"Error connecting to SSLCommerz: {str(e)}")
            return None

    def validate_payment(self, val_id):
        """
        Validates the payment using the val_id provided in the callback.
        """
        if self.simulate:
            return True

        params = {
            'val_id': val_id,
            'store_id': self.store_id,
            'store_passwd': self.store_pass,
            'format': 'json'
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/validator/api/validationserverphp.php",
                params=params,
                timeout=10
            )
            result = response.json()
            return result.get('status') in ['VALID', 'VALIDATED']
        except Exception as e:
            print(f"Error validating payment: {str(e)}")
            return False
