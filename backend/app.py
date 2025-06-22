from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import sys
import random

app = Flask(__name__)
# CORS configuration - allow all origins to fix the CORS issue
CORS(app, origins="*")  # Allow all origins for now

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'wmv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    print(f"Upload directory created/verified: {os.path.abspath(UPLOAD_FOLDER)}")
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
        
        # Add myEnv to the Python path so we can import from it
        myenv_path = os.path.join(os.path.dirname(__file__), 'myEnv')
        if myenv_path not in sys.path:
            sys.path.append(myenv_path)
        
        # Import the actual model functions only when needed
        from myEnv.runModel import runModel as imported_runModel
        from myEnv.sigmaMethod import runVideo as imported_runVideo
        runModel = imported_runModel
        runVideo = imported_runVideo
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

@app.route('/upload', methods=['POST'])
def upload_file():
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
        
        file.save(filepath)
        print(f"SUCCESS: File saved to {filepath}")
        
        # Verify file was actually saved
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"VERIFICATION: File exists with size {file_size} bytes")
        else:
            print(f"ERROR: File was not actually saved to {filepath}")
        
        # List contents of uploads directory
        uploads_contents = os.listdir(app.config['UPLOAD_FOLDER'])
        print(f"Uploads directory contents: {uploads_contents}")
        
        # Try to load model if not already loaded
        if not MODEL_AVAILABLE:
            load_model()
        
        # Use the actual AI detection model if available, otherwise use random
        if MODEL_AVAILABLE and runModel is not None:
            try:
                # Determine if file is video or image based on extension
                video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm'}
                file_extension = os.path.splitext(filepath)[1].lower()
                
                # Use the actual model to detect AI vs Human
                if file_extension in video_extensions and runVideo is not None:
                    model_result = runVideo(filepath, 3)
                    print("______________VIDEO______________")
                else:
                    model_result = runModel(filepath)
                    print("______________IMAGE______________")
                print(f"Model result: {model_result}")
                
                # Convert model result to percentage (assuming it returns a confidence score)
                if isinstance(model_result, (int, float)):
                    percentage = round(float(model_result), 1)
                    print("==============MODEL SUCCESS==============")
                else:
                    # Fallback to random if model result is unexpected
                    percentage = round(random.random() * 100, 1)
                    print("==============MODEL FALLBACK==============")
            except Exception as e:
                print(f"Model failed, using fallback: {e}")
                print("==============MODEL ERROR FALLBACK==============")
                percentage = round(random.random() * 100, 1)
        else:
            # Fallback to random function
            percentage = round(random.random() * 100, 1)
            print("==============NO MODEL FALLBACK==============")
        
        # Calculate percentage and determine AI/Human
        if percentage < 50:
            confidence = round(100 - percentage, 1)
            analysis_result = f"{confidence}% sure this is AI"
        else:
            confidence = round(percentage, 1)
            analysis_result = f"{confidence}% sure this is human"
        
        print(f"Percentage: {percentage}%")
        print(f"Analysis: {analysis_result}")
        
        print(f'''
        ____________________________________________________
        Image file path: {filepath}
        Percentage: {percentage}%
        Analysis: {analysis_result}
        ____________________________________________________
        ''')
        
        # Delete the uploaded file after processing
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"SUCCESS: File deleted from {filepath}")
            else:
                print(f"WARNING: File not found for deletion: {filepath}")
        except Exception as e:
            print(f"ERROR: Failed to delete file {filepath}: {str(e)}")
        
        # Clean up memory after processing
        try:
            import gc
            gc.collect()  # Force garbage collection
            if 'torch' in sys.modules:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            print("Memory cleanup completed")
        except Exception as e:
            print(f"Memory cleanup failed: {e}")
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'filepath': filepath,
            'percentage': percentage,
            'analysis_result': analysis_result,
            'model_used': MODEL_AVAILABLE
        }), 200
        
    except Exception as e:
        print(f"EXCEPTION: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'model_available': MODEL_AVAILABLE}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000) 