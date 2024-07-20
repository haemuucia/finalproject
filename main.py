import streamlit as st
import pandas as pd
import joblib
import time
import pymongo

## Constants
WAIT_TIME = 10

## Variables
url = "YOUR_MONGO_URL"
databaseName = "testing"
collectionName = "test"

## App Settings
st.set_page_config(page_title="Water Quality App",
                   page_icon=":droplet:",
                   layout="wide",
                   initial_sidebar_state="auto")

## Inject Tailwind CSS
tailwind_cdn = """
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
"""
st.markdown(tailwind_cdn, unsafe_allow_html=True)

## Prediction With Model
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

# Possible Causes For Each Sensor Status
def temp_cause(temp):
  if temp < 20:
    return ["Cooler weather or seasonal changes", "Cold water inflow from another source", "Shaded area with minimal sunlight exposure"]
  elif temp > 35:
    return ["High ambient temperature or seasonal changes", "Direct sunlight exposure or heat sources nearby", "Industrial discharge of hot water"]

def ph_cause(ph):
  if ph < 6.5:
    return ["Acid rain or runoff from acidic soils", "Industrial pollutants or chemical spills", "Natural sources like volcanic activities"]
  elif ph > 8.5:
    return ["Runoff from alkaline souls or rocks", "Industrial waste containing alkaline substance", "Overuse of alkaline water treatments"]

def tds_cause(tds):
  if tds < 300:
    return ["Dilution by rainwater or freshwater sources", "Filtration or purification processes", "Low mineral content in the water source"]
  elif tds > 500:
    return ["Industrial or agricultural runoff containing salts and minerals", "High levels of dissolved organic matter", "Contamination from sewage or wastewater discharge"]
  
def ec_cause(ec):
  if ec < 1000:
    return ["Freshwater inflow diluting the mineral content", "Purification or desalination processes", "Naturally low mineral content in the water source"]
  elif ec > 2000:
    return ["Industrial discharge containing salts or conductive materials", "Agricultural runoff with fertilizers and chemicals", "High levels of dissolved ions from natural sources"]

# Suggestions For Each Sensor Status
def temp_suggestion(temp):
  if temp < 20:
    return [
      "Use a heater or adjust your HVAC system to maintain a more comfortable environment.",
      "Inspect windows and doors for drafts and seal any gaps.",
      "Reduce time spent in cold areas or use warm clothing if the temperature is consistently low."
    ]
  elif temp > 35:
    return [
      "Employ fans or air conditioning units to lower the temperature.",
      "Ensure that people in the area are drinking plenty of water to stay hydrated.",
      "Open windows or use ventilation systems to enhance air circulation and reduce heat buildup."
    ]

def ph_suggestion(ph):
  if ph < 6.5:
    return [
      "Use pH buffers to bring the pH level closer to neutral.",
      "Check for sources of contamination that may be lowering the pH, such as industrial waste or acidic substances.",
      "Apply neutralizing agents to correct the pH imbalance."
    ]
  elif ph > 8.5:
    return [
      "Use Acidic Additives: Introduce acidic substances to neutralize excess alkalinity.",
      "Monitor Nearby Sources: Investigate any sources that may be causing alkalinity, such as alkaline runoff or chemical treatments.",
      "Improve Filtration: Use water filtration systems designed to handle alkaline conditions."
    ]

def tds_suggestion(tds):
  if tds < 300:
    return [
      "Ensure that there is no dilution of minerals from sources like freshwater inflow or filtration systems.",
      "Verify that water purification or desalination systems are functioning correctly.",
      "Consider the possibility of naturally low mineral content in the water source."
    ]
  elif tds > 500:
    return [
      "Look for industrial or agricultural runoff that may be increasing TDS levels.",
      "Use advanced filtration systems to remove excess dissolved solids.",
      "Evaluate water treatment processes to ensure they are effectively managing TDS levels."
    ]
  
def ec_suggestion(ec):
  if ec < 1000:
    return [
      "Check if freshwater is diluting the mineral content in the water.",
      "Inspect purification or desalination processes that may be lowering EC.",
      "Consider whether the water source naturally has low mineral content."
    ]
  elif ec > 2000:
    return [
      "Investigate industrial activities that may be introducing salts or conductive materials.",
      "Look for runoff containing fertilizers and chemicals contributing to high EC.",
      "Evaluate if high levels of dissolved ions from natural sources are affecting the EC."
    ]

## Database (MongoDB)
# Connect to MongoDB
def connect_to_mongodb():
  connection_string = url
  client = pymongo.MongoClient(connection_string)

  return client

# Function to fetch data from MongoDB
def fetch_data_from_mongodb(client):
  db = client.get_database(databaseName)
  collection = db.get_collection(collectionName)
  data = collection.find_one(sort=[('_id', pymongo.DESCENDING)], projection={'_id': False})
  return data

# Close MongoDB
def close_mongodb(client):
  client.close()

## HTML Components
# Container for Body
def fragment_body(temp, ph, tds, ec, status):
  html_body = f'''
    <div class="m-5 grid grid-cols-1 sm:grid-cols-2 gap-5 sm:gap-10">
      <div class="col-span-1 sm:col-span-2">{fragment_water_status_container(status, "Water quality is acceptable, there may be a moderate health concern for a very small number of people who are unusually sensitive to water pollution.")}</div>
      {fragment_data_container("Temperature", temp, "°C", temp_status(temp))}
      {fragment_data_container("pH", ph, "", ph_status(ph))}
      {fragment_data_container("TDS", tds, "ppm", tds_status(tds))}
      {fragment_data_container("EC", ec, "mS/cm", ec_status(ec))}
      {fragment_possible_causes_container(temp, ph, tds, ec)}
      {fragment_suggestions_container(temp, ph, tds, ec)}
    </div>
  '''
  return html_body

# Container for Water Status
def fragment_water_status_container(status, description):
  html_water_status_container = f'''
    <div class="w-full p-5 sm:p-10 flex flex-col justify-center bg-white rounded-xl shadow-black shadow-2xl">
      <span class="text-4xl sm:text-6xl text-center mb-5">{status}</span>
      <span class="text-md sm:text-xl text-center">{description}</span>
    </div>
  '''
  return html_water_status_container

# Container for Sensor Data
def fragment_data_container(title, value, unit, category):
  html_sensor_container = f'''
    <div class="w-full p-5 sm:p-10 flex flex-col justify-center bg-white rounded-xl shadow-black shadow-2xl">
      <span class="text-3xl text-center sm:text-left">{title}</span>
      <div class="w-full flex flex-col justify-center items-center">
        <div class="p-5 sm:p-10 text-3xl sm:text-6xl text-center">{value} {unit}</div>
        <span class="text-xl sm:text-2xl text-center sm:text-left">{category}</span>
      </div>
    </div>
  '''
  return html_sensor_container

# Container for Possible Causes
def fragment_possible_causes_container(temp, ph, tds, ec):
  possible_causes = {
    "Temperature": temp_cause(temp),
    "pH": ph_cause(ph),
    "TDS": tds_cause(tds),
    "EC": ec_cause(ec)
  }

  html_possible_causes = "".join([
    f'<strong class="text-xl sm:text-2xl">{key}</strong>'
    f'<ul class="list-disc mb-5 sm:ml-5">'
    f'{"".join([f"<li><span class='text-sm sm:text-2xl'>{cause}</span></li>" for cause in causes])}'
    f'</ul>'
    for key, causes in possible_causes.items() if causes
  ])
  
  html_possible_causes_container = f'''
    <div class="w-full p-5 sm:p-10 flex flex-col bg-white rounded-xl shadow-black shadow-2xl">
      <span class="text-3xl sm:text-4xl text-center mb-5">Possible Causes</span>
      {html_possible_causes}
    </div>
  '''
  return html_possible_causes_container

# Container for Suggestion
def fragment_suggestions_container(temp, ph, tds, ec):
  possible_suggestions = {
    "Temperature": temp_suggestion(temp),
    "pH": ph_suggestion(ph),
    "TDS": tds_suggestion(tds),
    "EC": ec_suggestion(ec)
  }

  html_possible_suggestions = "".join([
    f'<strong class="text-xl sm:text-2xl">{key}</strong>'
    f'<ul class="list-disc mb-5 sm:ml-5">'
    f'{"".join([f"<li><span class='text-sm sm:text-2xl'>{suggestion}</span></li>" for suggestion in suggestions])}'
    f'</ul>'
    for key, suggestions in possible_suggestions.items() if suggestions
  ])
  
  html_suggestion_container = f'''
    <div class="w-full p-5 sm:p-10 flex flex-col bg-white rounded-xl shadow-black shadow-2xl">
      <span class="text-3xl sm:text-4xl text-center mb-5">Suggestions</span>
      {html_possible_suggestions if html_possible_suggestions else "<div class='flex-grow flex items-center justify-center text-xl text-gray-500'>No suggestions available</div>"}
    </div>
  '''
  return html_suggestion_container

## Header
html_title_container = '''
  <div class="w-full py-5 flex flex-wrap sm:flex-rows items-center gap-2 text-black font-bold">
    <span class="text-4xl">Today's Water Quality</span>
    <span class="text-4xl hidden sm:block">-</span>
    <span class="text-2xl">Kota Bandung</span>
  </div>
'''
st.markdown(html_title_container, unsafe_allow_html=True)

## Content
placeholder = st.empty()
while True:
  # Get data from MongoDB
  client = connect_to_mongodb()
  data = fetch_data_from_mongodb(client)
  close_mongodb(client)

  # Convert data to DataFrame
  data = pd.DataFrame([data])
  
  # Rename columns
  # data.rename(columns={'Temperature': 'Temperature (°C)', 'pH': 'pH', 'TDS': 'TDS (ppm)', 'EC': 'EC (µS/cm)'}, inplace=True)
  data.rename(columns={'temperature': 'Temperature (°C)', 'ph': 'pH', 'tds': 'TDS (ppm)', 'turbidity': 'EC (µS/cm)'}, inplace=True)
  
  data = data[['Temperature (°C)', 'pH', 'TDS (ppm)', 'EC (µS/cm)']]

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