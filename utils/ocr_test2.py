import os
import traceback
import openai
from werkzeug.utils import secure_filename
from google.cloud import vision_v1
from utils.secrets import API_KEY

API_KEY = 'API_KEY'

def set_up_authentication(credentials_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

def detect_text(image_path):
    client = vision_v1.ImageAnnotatorClient()

    with open(image_path, "rb") as image_file:
        content = image_file.read()

    image = vision_v1.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    if texts:
        # Print only the first detected text annotation
        print(f"Detected text: {texts[0].description}")
        return texts[0].description
    else:
        print("No text detected in the image.")
        return ""


def generate_lm_text(ocr_text):
    # Use OpenAI API to generate improved text
    prompt = f"Write a well formulated text based on the following unstructered text, originally handwritten and digitized through OCR. Use continuous prose without any bullet points or similar formatting. If interpretation is needed due to OCR errors, please provide the best approximation. Reply with only the transcribed text:\n\n{ocr_text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-1106",  # Use the desired chat model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=2000,
        n=1
    )
    improved_text = response['choices'][0]['message']['content'].strip()
    return improved_text


def process_uploaded_image(file):
    # Save the uploaded file
    file_path = "uploads/" + secure_filename(file.filename)
    file.save(file_path)

    # Call the OCR function from ocr_test2.py
    detected_text = detect_text(file_path)

    improved_text = generate_lm_text(detected_text)
    print("Improved Text:", improved_text)

    quiz_data = generate_quiz_data(improved_text)
    print("Generated Quiz Data:", quiz_data)

    return improved_text

def extract_key_concepts(improved_text):
    # Use OpenAI API to extract key concepts from improved_text
    prompt = f"Generate a concise list of key concepts for a mind map based on the following text. Present each concept on a separate line without using dashes, bullet points, or any additional characters. Use only one to three words per concept. Emphasize brevity and clarity.\n\n{improved_text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=40,
        n=1
    )
    key_concepts = response['choices'][0]['message']['content'].strip()
    print ("KEY CONCEPTS:", key_concepts)
    return key_concepts

def generate_quiz_data(improved_text):
    print("Generating quiz data...")
    quiz_data = []
    
    # Use OpenAI API to generate quiz questions and answers based on improved_text
    try:
        prompt = f"Generate a quiz question and answer based on the following text:\n\n{improved_text}\n\nQuestion 1:"
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",  # Choose the appropriate engine for quiz generation
            prompt=prompt,
            temperature=0.7,
            max_tokens=500,
            n=1
        )
        generated_data = response['choices'][0]['text'].strip()

        # Split the generated data into questions and answers
        qa_pairs = [pair.strip() for pair in generated_data.split('Answer') if pair.strip()]

        # Create a list of dictionaries with 'question' and 'answer'
        for i in range(0, len(qa_pairs), 2):
            question = qa_pairs[i]
            answer = qa_pairs[i + 1] if i + 1 < len(qa_pairs) else ''
            quiz_data.append({'question': question, 'answer': answer})

        print("QUIZ DATA:", quiz_data)
    except Exception as e:
        print("Error in OpenAI API call:", e)
        quiz_data = [{"question": "Error in generating quiz data", "answer": ""}]

    return quiz_data


