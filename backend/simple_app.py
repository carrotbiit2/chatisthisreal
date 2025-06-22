from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)

# Simple CORS configuration
CORS(app, origins=["https://chatisthisreal-zeta.vercel.app"])

@app.route('/')
def hello():
    return jsonify({'message': 'Hello from simple Flask!'})

@app.route('/test')
def test():
    return jsonify({'message': 'Test endpoint working!'})

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'https://chatisthisreal-zeta.vercel.app')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Just return success without saving
        response = jsonify({
            'message': 'File received successfully!',
            'filename': file.filename,
            'size': len(file.read()),
            'demo_mode': True,
            'percentage': 75.5,
            'analysis_result': '75.5% sure this is human (demo mode)'
        })
        
        response.headers.add('Access-Control-Allow-Origin', 'https://chatisthisreal-zeta.vercel.app')
        return response
        
    except Exception as e:
        response = jsonify({'error': str(e)})
        response.headers.add('Access-Control-Allow-Origin', 'https://chatisthisreal-zeta.vercel.app')
        return response, 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 