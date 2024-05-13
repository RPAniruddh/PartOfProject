import os
import random
from datetime import datetime, timedelta
import openai
import streamlit as st
from dotenv import load_dotenv
import re
import pandas as pd
import numpy as np

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')  # Replace with your actual API key

# Sample user-item ratings matrix (rows: users, columns: attractions)
# Replace this with your actual user-item ratings data
ratings = np.array([
    [5, 4, 0, 0],  # User 1 ratings (0 means not rated)
    [0, 0, 3, 4],  # User 2 ratings
    [0, 5, 0, 0],  # User 3 ratings
    [4, 0, 0, 5],  # User 4 ratings
    [0, 0, 4, 0]   # User 5 ratings
])

# Constants
EXAMPLE_DESTINATIONS = [
    'Ernakulam', 'Fort Kochi', 'Mattancherry', 'Cherai Beach']

def collaborative_filtering(ratings_matrix, user_id, num_recommendations=2):
    # Calculate similarities between the target user and all other users
    similarities = np.dot(ratings_matrix, ratings_matrix[user_id]) / (
        np.linalg.norm(ratings_matrix, axis=1) * np.linalg.norm(ratings_matrix[user_id])
    )

    # Sort users by similarity (in descending order) and exclude the target user
    similar_users = np.argsort(similarities)[::-1][1:]

    # Identify attractions not rated by the target user
    unrated_attractions = np.where(ratings_matrix[user_id] == 0)[0]

    # Calculate predicted ratings for unrated attractions based on similar users' ratings
    predicted_ratings = np.mean(ratings_matrix[similar_users][:, unrated_attractions], axis=0)

    # Get indices of top-rated attractions
    top_attraction_indices = np.argsort(predicted_ratings)[::-1][:num_recommendations]

    return top_attraction_indices

def generate_prompt(destination, arrival_to, arrival_date, arrival_time, departure_from,
                    departure_date, departure_time, additional_information, unique_locations, **kwargs):
    num_days = (departure_date - arrival_date).days + 1
    unique_locations_str = ', '.join(unique_locations)
    return f'''
Prepare a {num_days}-day trip schedule for {destination}, Here are the details:

* Arrival To: {arrival_to}
* Arrival Date: {arrival_date}
* Arrival Time: {arrival_time}

* Departure From: {departure_from}
* Departure Date: {departure_date}
* Departure Time: {departure_time}

* Additional Notes: {additional_information}

Unique locations to visit: {unique_locations_str}
'''.strip()

def extract_locations(text):
    locations = []
    visited_locations = set()
    for location, pois in LOCATIONS.items():
        if location.lower() in text.lower() and location.lower() not in visited_locations:
            locations.append(location)
            visited_locations.add(location.lower())
            for poi in pois:
                if poi.lower() in text.lower() and poi.lower() not in visited_locations:
                    locations.append(poi)
                    visited_locations.add(poi.lower())
    return locations

def collaborative_filtering_recommendations(user_id, num_recommendations=3):
    recommended_indices = collaborative_filtering(ratings, user_id, num_recommendations)
    return recommended_indices

def submit():
    # Generate the prompt
    unique_locations = extract_locations(st.session_state['output'])
    prompt = generate_prompt(unique_locations=unique_locations, **st.session_state)

    # Generate output
    output = openai.Completion.create(
        engine='text-davinci-003',  # Use an appropriate engine for prompt-based completion
        prompt=prompt,
        temperature=0.45,
        max_tokens=1024
    )

    # Store the generated itinerary
    st.session_state['output'] = output['choices'][0]['text']

    # Split the generated itinerary into individual days
    itinerary = st.session_state['output']
    days = re.split(r'Day \d+:', itinerary)

    num_days = (st.session_state['departure_date'] - st.session_state['arrival_date']).days + 1

    # Initialize visited locations list for each day
    visited_locations_per_day = []

    # Display itinerary for each day
    for i, day in enumerate(days[1:num_days+1], start=1):
        day_itinerary = day.strip()

        st.subheader(f'Day {i} Itinerary:')

        # Extract locations from the current day's itinerary
        day_locations = extract_locations(day_itinerary)

        # Geocode the locations (not shown here, replace with your geocoding logic)

        # Collaborative filtering recommendations
        user_id = 0  # Replace with the appropriate user ID
        recommendations = collaborative_filtering_recommendations(user_id)

        st.write("Recommended Attractions:")
        for idx in recommendations:
            st.write("Attraction", idx + 1)  # Add 1 to index to match 1-based indexing

        # Display the detailed itinerary for the current day
        st.write(day_itinerary)

# Initialization and Streamlit setup
if 'output' not in st.session_state:
    st.session_state['output'] = '--'

st.title('Trippr')
st.subheader('Let us plan your trip!')

# Streamlit form for user input
with st.form(key='trip_form'):
    # Form inputs for trip details
    # (not shown here, replace with your input fields)

    st.form_submit_button('Submit', on_click=submit)