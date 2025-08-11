# app.py
from flask import Flask, render_template, request, send_file, jsonify, url_for
import os
import uuid
import requests
import fitz  # PyMuPDF
from compare_pdfs import compare_and_annotate

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULT_FOLDER'] = 'results'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare_pdfs():
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({"error": "Missing files"}), 400

    file1, file2 = request.files['file1'], request.files['file2']
    if not file1.filename or not file2.filename:
        return jsonify({"error": "Empty files"}), 400

    path1 = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{file1.filename}")
    path2 = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{file2.filename}")
    file1.save(path1); file2.save(path2)

    temp_dir = os.path.join(app.config['RESULT_FOLDER'], 'temp')
    os.makedirs(temp_dir, exist_ok=True)

    output_path = os.path.join(app.config['RESULT_FOLDER'], f"comparison_{uuid.uuid4().hex}.pdf")

    try:
        compare_and_annotate(path1, path2, output_path, temp_dir)
        return jsonify({"result_url": url_for('get_result', filename=os.path.basename(output_path))})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(path1): os.remove(path1)
        if os.path.exists(path2): os.remove(path2)

@app.route('/results/<filename>')
def get_result(filename):
    return send_file(os.path.join(app.config['RESULT_FOLDER'], filename), as_attachment=False)

@app.route('/flatten-annotations', methods=['POST'])
def flatten_annotations():
    data = request.get_json()
    annotations = data.get('annotations', [])
    original_url = request.url_root.rstrip('/') + data['original_pdf_url']

    try:
        response = requests.get(original_url, stream=True)
        input_pdf = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{uuid.uuid4()}.pdf")
        with open(input_pdf, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
    except Exception as e:
        return {"error": f"Download failed: {str(e)}"}, 500

    output_pdf = os.path.join(app.config['RESULT_FOLDER'], f"annotated_{uuid.uuid4().hex}.pdf")
    doc = fitz.open(input_pdf)

    for ann in annotations:
        page_num = ann['page'] - 1
        if page_num >= len(doc): continue
        page = doc[page_num]
        rect = fitz.Rect(ann['x'], ann['y'], ann['x'] + ann['width'], ann['y'] + ann['height'])
        if ann['type'] == 'text':
            widget = page.add_text_annot(rect.tl, ann.get('text', ''))
            widget.set_flags(0)
            widget.update()
        elif ann['type'] == 'highlight':
            page.add_highlight_annot(rect)

    doc.save(output_pdf)
    doc.close()
    os.remove(input_pdf)
    return send_file(output_pdf, as_attachment=True, download_name="annotated_comparison.pdf")

if __name__ == '__main__':
    app.run(debug=True, port=5000)