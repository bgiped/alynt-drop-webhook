"""
Vercel-compatible webhook handler for eBay notifications
"""
from flask import Flask, request, jsonify
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/api/webhook/ebay', methods=['POST'])
def handle_ebay_notification():
    """Handle incoming eBay platform notifications"""
    try:
        # Get notification data
        data = request.get_json()
        headers = dict(request.headers)
        
        logger.info(f"Received eBay notification: {data}")
        
        # Process notification based on type
        notification_type = data.get('eventType', '')
        
        if notification_type == 'ItemSold':
            return handle_item_sold(data)
        elif notification_type == 'OrderPaid':
            return handle_order_paid(data)
        elif notification_type == 'ShippingLabelRequested':
            return handle_shipping_request(data)
        else:
            logger.info(f"Unhandled notification type: {notification_type}")
            return jsonify({"status": "received"}), 200
            
    except Exception as e:
        logger.error(f"Error handling eBay notification: {e}")
        return jsonify({"error": "Processing failed"}), 500

def handle_item_sold(data: Dict[str, Any]) -> tuple:
    """Handle ItemSold notification - trigger CJ order"""
    try:
        # Extract order details
        item_id = data.get('itemId')
        buyer_info = data.get('buyer', {})
        quantity = data.get('quantity', 1)
        price = data.get('price', 0)
        
        logger.info(f"🎉 SALE! Item: {item_id}, Qty: {quantity}, Price: ${price}")
        
        # TODO: Place CJ order automatically
        # This would integrate with your CJ API
        
        return jsonify({
            "status": "processed",
            "action": "sale_recorded",
            "message": f"Sale processed: ${price}",
            "next_step": "place_cj_order"
        }), 200
        
    except Exception as e:
        logger.error(f"Error handling ItemSold: {e}")
        return jsonify({"error": str(e)}), 500

def handle_order_paid(data: Dict[str, Any]) -> tuple:
    """Handle OrderPaid notification"""
    try:
        order_id = data.get('orderId')
        payment_status = data.get('paymentStatus')
        
        logger.info(f"💰 Payment confirmed: {order_id}")
        
        return jsonify({
            "status": "processed",
            "action": "payment_confirmed"
        }), 200
        
    except Exception as e:
        logger.error(f"Error handling OrderPaid: {e}")
        return jsonify({"error": str(e)}), 500

def handle_shipping_request(data: Dict[str, Any]) -> tuple:
    """Handle shipping label request"""
    try:
        order_id = data.get('orderId')
        
        logger.info(f"📦 Shipping requested: {order_id}")
        
        return jsonify({
            "status": "processed",
            "action": "tracking_provided"
        }), 200
        
    except Exception as e:
        logger.error(f"Error handling shipping request: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "alynt-drop-webhook",
        "version": "1.0.0"
    }), 200

@app.route('/', methods=['GET'])
def home():
    """Home page"""
    return jsonify({
        "message": "Alynt Drop eBay Webhook Service",
        "endpoints": {
            "webhook": "/api/webhook/ebay",
            "health": "/api/health"
        }
    }), 200

# For Vercel
if __name__ == "__main__":
    app.run(debug=True)