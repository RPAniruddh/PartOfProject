from flask import Flask, request, jsonify
import requests
import json
from hugchat import hugchat
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

chatbot = hugchat.ChatBot(cookie_path="cookies.json")
conversation_id = chatbot.new_conversation()
chatbot.change_conversation(conversation_id)

def weather(city):
    url = f"https://api.weatherapi.com/v1/current.json?key=3ae3dea5a8864fd6bf2140701230606&q={city}"
    r = requests.get(url)
    weather_data = json.loads(r.text)
    temperature = weather_data['current']['temp_c']
    return f"The Temperature of {city} is {temperature}"

def is_tourism_related(user_input):
    tourism_keywords = ['place', 'places' , 'travel', 'visit','wellness',
                        'popular', 'destination', 'destinations', 'travelling',
                        'waterfall', 'malls', 'spiritual', 'tourism', 'vacation',
                        'trip', 'holiday', 'tour', 'hotel', 'resort', 'accommodation', 
                        'restaurant', 'cuisine', 'attraction', 'sightseeing', 'landmark', 
                        'monument', 'museum', 'beach', 'mountain', 'national park', 'adventure', 
                        'outdoor', 'culture', 'tradition', 'festival', 'event', 'transportation',
                        'flight', 'cruise', 'visa', 'passport', 'currency', 'exchange rate', 'eco-tourism',
                        'sustainable travel', 'wildlife', 'safari', 'conservation', 'ecological reserves',
                        'scenic beauty', 'rural tourism', 'urban tourism', 'historical sites', 'archaeological sites',
                        'heritage tourism', 'backpacking', 'hiking', 'camping', 'trekking', 'cycling', 'adventure sports',
                        'wellness tourism', 'spa retreat', 'yoga retreat', 'health tourism', 'medical tourism', 'shopping',
                        'souvenirs', 'local crafts', 'gastronomy', 'food tourism', 'wine tourism', 'culinary tours', 'street food',
                        'nightlife', 'entertainment', 'theme parks', 'amusement parks', 'botanical gardens', 'zoos', 'aquariums', 'birdwatching',
                        'photography tourism', 'cultural exchange', 'homestays', 'volunteer tourism', 'educational tourism', 'language immersion', 
                        'workation']

    user_input_lower = user_input.lower()
    for keyword in tourism_keywords:
        if re.search(r'\b{}\b'.format(keyword), user_input_lower):
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

        elif user_input.lower() == 'c' or user_input.lower() == 'change':
            conversation_list = chatbot.get_conversation_list()
            return jsonify({'response': 'Choose a conversation to switch to:', 'conversations': conversation_list})

        elif user_input.lower() == 'n' or user_input.lower() == 'new':
            global conversation_id
            conversation_id = chatbot.new_conversation()
            chatbot.change_conversation(conversation_id)
            return jsonify({'response': 'Clean slate!'})

        # Check if the user input is related to tourism
        elif is_tourism_related(user_input):
            chatbot_response = chatbot.chat(user_input)
            #print(chatbot_response)
            return jsonify({'response': str(chatbot_response)})
        else:
            return jsonify({'response': 'Sorry, I can only answer tourism-related questions.'})

    return jsonify({'error': 'Invalid request method'}), 405

if __name__ == '__main__':
    app.run(debug=True)
