import time
import logging
import requests

logger = logging.getLogger(__name__)

class PaymentProcessor:
    def __init__(self, gateway_url, timeout=30):
        self.gateway_url = gateway_url
        self.timeout = timeout
        self.max_retries = 3

    def process_payment(self, transaction_id, amount, currency='USD'):
        logger.info(f'Processing payment {transaction_id}: {amount} {currency}')
        retries = 0
        while retries < self.max_retries:
            try:
                response = self._send_to_gateway(transaction_id, amount, currency)
                if response.get('status') == 'success':
                    logger.info(f'Payment {transaction_id} processed successfully')
                    return response
                else:
                    logger.warning(f'Payment {transaction_id} failed: {response.get("error")}')
                    retries += 1
            except requests.exceptions.Timeout:
                logger.error(f'Timeout on payment {transaction_id}, retry {retries + 1}/{self.max_retries}')
                retries += 1
                time.sleep(2 ** retries)
            except requests.exceptions.ConnectionError as e:
                logger.error(f'Connection error on payment {transaction_id}: {e}')
                retries += 1
                time.sleep(2 ** retries)

        logger.critical(f'Payment {transaction_id} failed after {self.max_retries} retries')
        return {'status': 'failed', 'transaction_id': transaction_id}

    def _send_to_gateway(self, transaction_id, amount, currency):
        payload = {
            'transaction_id': transaction_id,
            'amount': amount,
            'currency': currency
        }
        response = requests.post(
            self.gateway_url,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    processor = PaymentProcessor('https://api.paymentgateway.com/v1/process')
    result = processor.process_payment('TXN-001', 150.00, 'USD')
    print(result)