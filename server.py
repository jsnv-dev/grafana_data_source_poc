from flask import Flask, jsonify, request
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # Convert headers to dict and log them
    headers_dict = dict(request.headers)
    logger.info(json.dumps({
        "headers": headers_dict,
        "method": request.method,
        "path": f"/{path}" if path else "/"
    }, indent=2))

    return jsonify({
        "SSRF POC": "success",
        "path": f"/{path}" if path else "/"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
