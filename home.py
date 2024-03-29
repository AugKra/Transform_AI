from flask import Flask, render_template, redirect, request, jsonify, url_for, session
from werkzeug.utils import secure_filename
from utils.ocr_test2 import extract_key_concepts, generate_lm_text, generate_quiz_data, set_up_authentication, process_uploaded_image

credentials_path = "/Users/august/Desktop/acquired-subset-407621-d657e5b55854.json"
set_up_authentication(credentials_path)

app = Flask(__name__)
app.secret_key = "your_secret_key"  

@app.route('/')
def hello_world():
    return render_template('home_ui.html')


@app.route('/plain_text', methods=['POST', 'GET'])
def plain_text():
    if request.method == 'GET':
        improved_text = session.get('improved_text', None)

        if improved_text is None:
            return redirect('/')

        detected_text = session.get('detected_text', None)

        return render_template('plain_text.html', detected_text=detected_text)

    result = handle_file_upload_and_processing(request, 'plain_text')

    if result is not None:
        return result

    return "Invalid action specified."


@app.route('/mind_map', methods=['POST', 'GET'])
def mind_map():
    if request.method == 'GET':
        improved_text = session.get('improved_text', None)

        if improved_text is None:
            return redirect('/')

        key_concepts = extract_key_concepts(improved_text)

        return render_template('mind_map.html', key_concepts=key_concepts)

    result = handle_file_upload_and_processing(request, 'mind_map')

    if result is not None:
        return result

    return "Invalid action specified."


@app.route('/quiz', methods=['POST', 'GET'])
def generate_quiz():
    if request.method == 'GET':
        improved_text = session.get('improved_text', None)

        if improved_text is None:
            return redirect('/')

        quiz_data = generate_quiz_data(improved_text)

        return render_template('quiz.html', quiz_data=quiz_data)

    result = handle_file_upload_and_processing(request, 'generate_quiz')

    if result is not None:
        return result

    return "Invalid action specified."


def handle_file_upload_and_processing(request, action):
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if action == 'plain_text':
        detected_text = process_uploaded_image(file)

        improved_text = generate_lm_text(detected_text)

        session['improved_text'] = improved_text
        session['detected_text'] = detected_text

        return redirect('/plain_text')

    elif action == 'mind_map':
        detected_text = process_uploaded_image(file)

        improved_text = generate_lm_text(detected_text)

        session['improved_text'] = improved_text
        session['detected_text'] = detected_text

        return redirect('/mind_map')

    elif action == 'generate_quiz':
        detected_text = process_uploaded_image(file)
        quiz_data = generate_quiz_data(detected_text)

        improved_text = generate_lm_text(detected_text)

        session['improved_text'] = improved_text

        return redirect('/quiz')

    return None


if __name__ == '__main__':
    app.run()
