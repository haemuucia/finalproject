import streamlit as st
import pandas as pd
import joblib
import time
import pymongo

# Constants
WAIT_TIME = 10

# Variables
url = "YOUR MONGODB URL"

# Settings
st.set_page_config(page_title="Water Quality App",
                   page_icon=":droplet:",
                   layout="wide",
                   initial_sidebar_state="auto")

# Inject Tailwind CSS
tailwind_cdn = """
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
"""
st.markdown(tailwind_cdn, unsafe_allow_html=True)

# Load model
model = joblib.load("water_quality_model.pkl")

# Predict Function
def predict(data):
  prediction = model.predict(data)
  quality = ["Bad", "Moderate", "Good"]
  return [quality[prediction] for prediction in prediction] 

# Status For Each Sensor
def temp_status(temp):
  if temp < 20:
    return "Cold"
  elif temp > 35:
    return "Hot"
  else:
    return "Normal"

def ph_status(ph):
  if ph < 6.5:
    return "Acidic"
  elif ph > 8.5:
    return "Alkaline"
  else:
    return "Normal"

def tds_status(tds):
  if tds < 300:
    return "Low"
  elif tds > 500:
    return "High"
  else:
    return "Normal"

def ec_status(ec):
  if ec < 1000:
    return "Low"
  elif ec > 2000:
    return "High"
  else:
    return "Normal"

# Database (MongoDB)
# Connect to MongoDB
def connect_to_mongodb():
  connection_string = url
  client = pymongo.MongoClient(connection_string)

  return client

# Function to fetch data from MongoDB
def fetch_data_from_mongodb(client):
  db = client.get_database("data-sensor")
  collection = db.get_collection("data")
  data = collection.find_one(sort=[('_id', pymongo.DESCENDING)], projection={'_id': False})
  return data

# Close MongoDB
def close_mongodb(client):
  client.close()

# HTML Components
def fragment_water_status_container(status, description):
  html_water_status_container = f'''
    <div class="w-full p-10 flex flex-col justify-center bg-white rounded-xl shadow-black shadow-2xl">
      <span class="text-5xl sm:text-6xl text-center mb-5">{status}</span>
      <span class="text-xl text-center">{description}</span>
    </div>
  '''
  return html_water_status_container

def fragment_data_container(title, temp, unit, category):
  html_sensor_container = f'''
    <div class="w-full px-10 py-5 flex flex-col justify-center bg-white rounded-xl shadow-black shadow-2xl">
      <span class="text-3xl text-center sm:text-left">{title}</span>
      <div class="w-full flex flex-col justify-center items-center">
        <div class="p-10 text-5xl sm:text-6xl text-center">{temp} {unit}</div>
        <span class="text-2xl text-center sm:text-left">{category}</span>
      </div>
    </div>
  '''
  return html_sensor_container

def fragment_body(temp, ph, tds, ec, status):
  html_body = f'''
    <div class="m-5 grid grid-cols-1 sm:grid-cols-2 gap-10">
      <div class="col-span-1 sm:col-span-2">{fragment_water_status_container(status, "Water quality is acceptable, there may be a moderate health concern for a very small number of people who are unusually sensitive to water pollution.")}</div>
      {fragment_data_container("Temperature", temp, "°C", temp_status(temp))}
      {fragment_data_container("pH", ph, "", ph_status(ph))}
      {fragment_data_container("TDS", tds, "ppm", tds_status(tds))}
      {fragment_data_container("EC", ec, "mS/cm", ec_status(ec))}
    </div>
  '''
  return html_body

# Body #
# Header
html_title_container = '''
  <div class="w-full py-5 flex flex-wrap sm:flex-rows items-center gap-2 text-black font-bold">
    <span class="text-4xl">Today's Water Quality</span>
    <span class="text-4xl hidden sm:block">-</span>
    <span class="text-2xl">Kota Bandung</span>
  </div>
'''
st.markdown(html_title_container, unsafe_allow_html=True)

# Content
placeholder = st.empty()

while True:
  # Get data from MongoDB
  client = connect_to_mongodb()
  data = fetch_data_from_mongodb(client)
  close_mongodb(client)

  # Convert data to DataFrame
  data = pd.DataFrame([data])
  
  # Rename columns
  data.rename(columns={'Temperature': 'Temperature (°C)', 'pH': 'pH', 'TDS': 'TDS (ppm)', 'EC': 'EC (µS/cm)'}, inplace=True)
  
  # Round data
  for key in data:
    data[key] = round(data[key], 1)
  
  temp = data['Temperature (°C)'][0]
  ph = data['pH'][0]
  tds = data['TDS (ppm)'][0]
  ec = data['EC (µS/cm)'][0]
  status = predict(data)[0]

  # Display data in Streamlit
  with placeholder.container():
    st.markdown(fragment_body(temp, ph, tds, ec, status), unsafe_allow_html=True)

  # wait for x seconds before fetching new data
  time.sleep(WAIT_TIME)