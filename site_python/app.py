import os
import cv2
import numpy as np
from flask import Flask, render_template, request, send_from_directory

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
PROCESSED_FOLDER = os.path.join('static', 'processed')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def apply_filter(image_path, filter_type):

    image = cv2.imread(image_path)
    original_filename = os.path.basename(image_path)
    
    # filtro
    if filter_type == 'gray':
        processed = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif filter_type == 'blur':
        processed = cv2.GaussianBlur(image, (15, 15), 0)
    elif filter_type == 'threshold':
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, processed = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    elif filter_type == 'erode':
        kernel = np.ones((5,5), np.uint8)
        processed = cv2.erode(image, kernel, iterations=1)
    elif filter_type == 'dilate':
        kernel = np.ones((5,5), np.uint8)
        processed = cv2.dilate(image, kernel, iterations=1)
    else:
        return None, None
    
    processed_filename = 'processed.png'
    processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)
    cv2.imwrite(processed_path, processed)
    
    return original_filename, processed_filename

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'Nenhum arquivo enviado', 400
        file = request.files['file']
        if file.filename == '':
            return 'Nenhum arquivo selecionado', 400
        
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        filter_type = request.form.get('filter')
        original_filename, processed_filename = apply_filter(filepath, filter_type)
        
        if original_filename and processed_filename:
            return render_template('results.html', original=original_filename, processed=processed_filename)
        else:
            return 'Filtro inválido', 400
    
    return render_template('index.html')

# Rota para as imagens carregadas (uploads)
@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Rota para as imagens processadas (processed)
@app.route('/static/processed/<filename>')
def processed_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
