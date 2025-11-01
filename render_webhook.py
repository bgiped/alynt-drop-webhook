"""
Production webhook for eBay compliance - works with Render.com
"""
from flask import Flask, request, Response
import os
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This MUST match what you put in eBay console
VERIFICATION_TOKEN = "alynt-drop-webhook-token-2025"

@app.route('/')
def health():
    return {"status": "Alynt Drop Webhook Active", "timestamp": datetime.utcnow().isoformat()}

@app.route('/webhooks/marketplace-account-deletion', methods=['GET', 'POST'])
def marketplace_deletion():
    if request.method == 'GET':
        # eBay verification challenge
        challenge = request.args.get('challenge_code')
        token = request.args.get('verification_token')
        
        logger.info(f"Verification request - Token: {token}, Challenge: {challenge}")
        
        if token == VERIFICATION_TOKEN and challenge:
            logger.info("✅ Verification successful")
            return Response(challenge, mimetype='text/plain')
        else:
            logger.error("❌ Verification failed")
            return Response("Verification failed", status=400, mimetype='text/plain')
    
    # Handle actual notifications
    try:
        data = request.get_json() or {}
        logger.info(f"Marketplace notification: {data}")
        return {"status": "received", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"error": str(e)}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)