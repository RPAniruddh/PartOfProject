from flask import Flask, request, jsonify
import requests
import json
from transformers import TFAutoModelForCausalLM, AutoTokenizer
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# Load pre-trained language model and tokenizer
model = TFAutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-large")
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-large")

def weather(city):
    url = f"https://api.weatherapi.com/v1/current.json?key=3ae3dea5a8864fd6bf2140701230606&q={city}"
    r = requests.get(url)
    weather_data = json.loads(r.text)
    temperature = weather_data['current']['temp_c']
    return f"The Temperature of {city} is {temperature}"

def is_tourism_related(user_input):
    tourism_keywords = ['place', 'places', 'travel', 'visit', 'wellness', 'popular', 'destination', 'destinations', 'travelling', 'waterfall', 'malls', 'spiritual', 'tourism', 'vacation', 'trip', 'holiday', 'tour', 'hotel', 'resort', 'accommodation', 'restaurant', 'cuisine', 'attraction', 'sightseeing', 'landmark', 'monument', 'museum', 'beach', 'mountain', 'national park', 'adventure', 'outdoor', 'culture', 'tradition', 'festival', 'event', 'transportation', 'flight', 'cruise', 'visa', 'passport', 'currency', 'exchange rate', 'eco-tourism', 'sustainable travel', 'wildlife', 'safari', 'conservation', 'ecological reserves', 'scenic beauty', 'rural tourism', 'urban tourism', 'historical sites', 'archaeological sites', 'heritage tourism', 'backpacking', 'hiking', 'camping', 'trekking', 'cycling', 'adventure sports', 'wellness tourism', 'spa retreat', 'yoga retreat', 'health tourism', 'medical tourism', 'shopping', 'souvenirs', 'local crafts', 'gastronomy', 'food tourism', 'wine tourism', 'culinary tours', 'street food', 'nightlife', 'entertainment', 'theme parks', 'amusement parks', 'botanical gardens', 'zoos', 'aquariums', 'birdwatching', 'photography tourism', 'cultural exchange', 'homestays', 'volunteer tourism', 'educational tourism', 'language immersion', 'workation']

    user_input_lower = user_input.lower()

    # Use spaCy for NLP tasks
    import spacy
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(user_input_lower)

    for token in doc:
        if token.text in tourism_keywords:
            return True

    return False

@app.route('/api/chatbot', methods=['POST', 'GET'])
def chat():
    if request.method == 'GET':
        return 'Chatbot API is up and running.'

    if request.method == 'POST':
        data = request.get_json()
        user_input = data.get('message')

        if user_input.lower().startswith('weather'):
            try:
                city = user_input.split()[2]
                return jsonify({'response': weather(city)})
            except:
                return jsonify({'response': 'Please provide a city name after the word "weather".'})

        if user_input.lower() == 'q' or user_input.lower() == 'quit':
            return jsonify({'response': 'Goodbye!'})

        # Check if the user input is related to tourism
        elif is_tourism_related(user_input):
            # Tokenize input and generate response using the language model
            input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors='tf')
            response_output = model.generate(input_ids, max_length=150, do_sample=True, top_k=50, top_p=0.95, num_return_sequences=1)
            response_text = tokenizer.decode(response_output[0], skip_special_tokens=True)
            return jsonify({'response': response_text})

        else:
            return jsonify({'response': 'Sorry, I can only answer tourism-related questions.'})

    return jsonify({'error': 'Invalid request method'}), 405

if __name__ == '__main__':
    app.run(debug=True)