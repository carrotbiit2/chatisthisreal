from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import sys
import random

app = Flask(__name__)
# CORS configuration - explicitly allow your Vercel domain
CORS(app, 
     origins=["https://chatisthisreal-zeta.vercel.app", "http://localhost:5173", "http://localhost:3000"],
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type"],
     supports_credentials=False)

# Configuration
# Use a more reliable upload directory for Render
if os.environ.get('RENDER'):
    # On Render, use /tmp for uploads (temporary storage)
    UPLOAD_FOLDER = '/tmp/uploads'
else:
    # Local development
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'wmv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    print(f"Upload directory created/verified: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"Upload directory exists: {os.path.exists(UPLOAD_FOLDER)}")
    print(f"Upload directory writable: {os.access(UPLOAD_FOLDER, os.W_OK)}")
except Exception as e:
    print(f"Error creating upload directory: {e}")

# Initialize model variables - will be loaded only when needed
MODEL_AVAILABLE = False
runModel = None
runVideo = None
model_loaded = False

def load_model():
    """Load the model from Render secret files to avoid memory issues"""
    global MODEL_AVAILABLE, runModel, runVideo, model_loaded
    
    if model_loaded:
        return MODEL_AVAILABLE
        
    try:
        print("Loading ML dependencies...")
        
        # Optimize PyTorch memory usage
        import torch
        torch.set_num_threads(1)  # Use only 1 thread to save memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()  # Clear GPU cache if available
        
        # Check if we're on Render (secret files are available)
        secret_files_dir = os.environ.get('RENDER_SECRET_FILES_DIR')
        if secret_files_dir:
            print(f"Running on Render, checking secret files at: {secret_files_dir}")
            model_file = os.path.join(secret_files_dir, 'image_classifier.pt')
            if os.path.exists(model_file):
                print(f"Found model file in secret files: {model_file}")
            else:
                print(f"Model file not found in secret files: {model_file}")
                return False
        else:
            # Local development - check local myEnv directory
            myenv_path = os.path.join(os.path.dirname(__file__), 'myEnv')
            model_file = os.path.join(myenv_path, 'image_classifier.pt')
            if not os.path.exists(model_file):
                print(f"Model file not found locally: {model_file}")
                return False
        
        # Add current directory and myEnv to the Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        myenv_path = os.path.join(current_dir, 'myEnv')
        
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        if myenv_path not in sys.path:
            sys.path.insert(0, myenv_path)
        
        print(f"Python path: {sys.path}")
        print(f"Current directory: {current_dir}")
        print(f"myEnv path: {myenv_path}")
        
        # Import the actual model functions only when needed
        try:
            # Try different import approaches
            try:
                from myEnv.runModel import runModel as imported_runModel
                print("Successfully imported runModel using myEnv.runModel")
            except ImportError:
                from runModel import runModel as imported_runModel
                print("Successfully imported runModel using direct import")
            
            runModel = imported_runModel
        except ImportError as e:
            print(f"Failed to import runModel: {e}")
            runModel = None
            
        try:
            # Try different import approaches
            try:
                from myEnv.sigmaMethod import runVideo as imported_runVideo
                print("Successfully imported runVideo using myEnv.sigmaMethod")
            except ImportError:
                from sigmaMethod import runVideo as imported_runVideo
                print("Successfully imported runVideo using direct import")
            
            runVideo = imported_runVideo
        except ImportError as e:
            print(f"Failed to import runVideo: {e}")
            runVideo = None
        
        MODEL_AVAILABLE = True
        model_loaded = True
        print("Model successfully loaded!")
        return True
    except ImportError as e:
        print(f"Warning: Could not import model files: {e}")
        return False
    except Exception as e:
        print(f"Error loading model: {e}")
        return False

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'https://chatisthisreal-zeta.vercel.app')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    print("=== UPLOAD REQUEST RECEIVED ===")
    print(f"Request files: {request.files}")
    print(f"Request form: {request.form}")
    
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            print("ERROR: No file in request.files")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        print(f"File object: {file}")
        print(f"File filename: {file.filename}")
        
        # Check if file was selected
        if file.filename == '':
            print("ERROR: Empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            print(f"ERROR: File type not allowed: {file.filename}")
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Save the file
        if file.filename is None:
            print("ERROR: Filename is None")
            return jsonify({'error': 'Invalid filename'}), 400
            
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        absolute_filepath = os.path.abspath(filepath)
        print(f"Attempting to save file to: {filepath}")
        print(f"Absolute filepath: {absolute_filepath}")
        print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
        print(f"Upload folder exists: {os.path.exists(app.config['UPLOAD_FOLDER'])}")
        print(f"Upload folder writable: {os.access(app.config['UPLOAD_FOLDER'], os.W_OK)}")
        
        # Check if file already exists
        if os.path.exists(filepath):
            print(f"WARNING: File already exists: {filepath}")
            # Optionally, you can rename the file to avoid conflicts
            base_name, extension = os.path.splitext(filename)
            counter = 1
            while os.path.exists(filepath):
                new_filename = f"{base_name}_{counter}{extension}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                counter += 1
            print(f"Using new filename: {os.path.basename(filepath)}")
        
        try:
            file.save(filepath)
            print(f"SUCCESS: File saved to {filepath}")
        except Exception as save_error:
            print(f"ERROR saving file: {save_error}")
            return jsonify({'error': f'Failed to save file: {save_error}'}), 500
        
        # Verify file was actually saved
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"VERIFICATION: File exists with size {file_size} bytes")
        else:
            print(f"ERROR: File was not actually saved to {filepath}")
            return jsonify({'error': 'File was not saved successfully'}), 500
        
        # List contents of uploads directory
        try:
            uploads_contents = os.listdir(app.config['UPLOAD_FOLDER'])
            print(f"Uploads directory contents: {uploads_contents}")
        except Exception as list_error:
            print(f"ERROR listing uploads directory: {list_error}")
        
        # For now, return a quick response without loading the model
        # This will prevent timeouts while we debug the model loading
        print("Returning quick response without model processing")
        
        # Calculate a simple random percentage for now
        percentage = round(random.random() * 100, 1)
        if percentage < 50:
            confidence = round(100 - percentage, 1)
            analysis_result = f"{confidence}% sure this is AI (demo mode)"
        else:
            confidence = round(percentage, 1)
            analysis_result = f"{confidence}% sure this is human (demo mode)"
        
        # Delete the uploaded file after processing
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"SUCCESS: File deleted from {filepath}")
            else:
                print(f"WARNING: File not found for deletion: {filepath}")
        except Exception as e:
            print(f"ERROR: Failed to delete file {filepath}: {str(e)}")
        
        response = jsonify({
            'message': 'File uploaded successfully (demo mode)',
            'filename': filename,
            'filepath': filepath,
            'percentage': percentage,
            'analysis_result': analysis_result,
            'model_used': False,
            'demo_mode': True
        })
        
        # Add CORS headers to the response
        response.headers.add('Access-Control-Allow-Origin', 'https://chatisthisreal-zeta.vercel.app')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        
        return response, 200
        
    except Exception as e:
        print(f"EXCEPTION: {str(e)}")
        response = jsonify({'error': str(e)})
        response.headers.add('Access-Control-Allow-Origin', 'https://chatisthisreal-zeta.vercel.app')
        return response, 500

@app.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({'message': 'Backend is working!', 'timestamp': '2024-01-01'}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'model_available': MODEL_AVAILABLE}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000) 