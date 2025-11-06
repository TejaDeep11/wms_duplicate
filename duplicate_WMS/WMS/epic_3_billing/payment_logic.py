# In epic_3_billing/payment_logic.py

from utils.db_connector import execute_query, fetch_one
import datetime # Make sure this is imported

def process_cash_payment(booking_id, amount):
    """
    Logs a CASH payment collected by a driver.
    """
    # 1. Get the client_id associated with this booking
    client_query = "SELECT client_id FROM ServiceBookings WHERE booking_id = %s"
    client_result = fetch_one(client_query, (booking_id,))
    if not client_result:
        print(f"Error: Could not find client for booking_id {booking_id}")
        return False
    
    client_id = client_result['client_id']

    # 2. Create the payment record with a special transaction ID
    payment_query = """
        INSERT INTO Payments (booking_id, client_id, amount, payment_gateway_txn_id, status, payment_date)
        VALUES (%s, %s, %s, 'CASH_COLLECTED_BY_DRIVER', 'Succeeded', NOW())
    """
    payment_id = execute_query(payment_query, (booking_id, client_id, amount))

    if not payment_id:
        print(f"Error: Failed to insert cash payment for booking_id {booking_id}")
        return False

    # 3. Generate a receipt for the client's records
    receipt_query = """
        INSERT INTO Receipts (payment_id, receipt_number, generated_at, sent_to_email)
        VALUES (%s, %s, NOW(), (SELECT email FROM Users WHERE user_id = %s))
    """
    receipt_num = f"RCPT-{datetime.date.today().year}-{payment_id}"
    execute_query(receipt_query, (payment_id, receipt_num, client_id))
    
    print(f"Successfully logged cash payment {payment_id} for booking {booking_id}")
    return True