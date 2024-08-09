import streamlit as st
import pandas as pd
import joblib
import time
import pymongo
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from collections import Counter


# Constants
WAIT_TIME = 10

# Variables
url = "mongodb+srv://ireneslebew:Akusayangayam12*@finalproject.hbgtqlm.mongodb.net/?retryWrites=true&w=majority&appName=finalproject"

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
model = joblib.load("waterquality_model.pkl")
# Load dataset
water = pd.read_csv('water_quality_data.csv')
temp = round(water['Temperature (°C)'][18], 1)  # round to 1 decimal place
ph = round(water['pH'][18], 1)

# Predict Function
def predict(data):
  prediction = model.predict(data)
  quality = ["Unacceptable", "Poor", "Moderate", "Good", "Excellent"]
  return [quality[prediction] for prediction in prediction] 

def get_description(status):
    if status == 'Unacceptable':
        return "Water is not suitable for consumption."
    elif status == 'Poor':
        return "Water is of poor quality and may require significant treatment."
    elif status == 'Moderate':
        return "Water is acceptable, but may have some impurities."
    elif status == 'Good':
        return "Water is suitable for consumption, but may require treatment."
    elif status == 'Excellent':
        return "Water is of exceptional quality."
    
# Status For Each Sensor
def temp_status(temp):
  if temp <= 0:
    return "Very cold"
  elif temp > 0 and temp < 16:
    return "Cold"
  elif temp >= 16 and temp < 27:
    return "Normal"
  elif temp >= 27 and temp < 35:
    return "Warm"
  else:
    return "Hot"

def ph_status(ph):
  if ph < 6.5:
    return "Acidic"
  elif ph > 8.5:
    return "Alkaline"
  else:
    return "Normal"

def tds_status(tds):
  if tds >= 0 and tds < 50:
    return "Very pure water"
  elif tds >= 50 and tds < 150:
    return "Excellent"
  elif tds >= 150 and tds < 300:
    return "Good"
  elif tds >= 300 and tds < 500:
    return "Fair"
  elif tds >= 500 and tds < 1000:
    return "Poor"
  else:
    return "Unacceptable"

def ec_status(ec):
  if ec >= 0 and ec < 1:
    return "Very clean"
  elif ec >= 1 and ec < 5:
    return "Slightly cloudy water"
  elif ec >= 5 and ec < 10:
    return "Moderately cloudy water"
  elif ec >= 10 and ec < 50:
    return "Noticeably cloudy water"
  elif ec >= 50 and ec < 100:
    return "Highly cloudy water"
  else:
    return "Extremely cloudy water"

# Possible Causes For Each Sensor Status
def temp_cause(temp):
  if temp <= 0:
    return ["High altitude locations", "Cold water inflow from another source", "Winter season"]
  elif temp > 0 and temp < 16:
    return ["Release of cold water from dams", "Seasonal or weather changes", "Cold water inflow from another source"]
  elif temp >= 27 and temp < 35:
    return ["Ambient air temperature", "Reduced water flow", "Lack of shade due to urban development"]
  elif temp >= 35:
    return ["High ambient temperature or seasonal changes", "Direct sunlight exposure or heat sources nearby", "Industrial discharge of hot water"]

def ph_cause(ph):
  if ph < 6.5:
    return ["Acid rain or runoff from acidic soils", "Industrial pollutants or chemical spills", "Natural sources like volcanic activities"]
  elif ph > 8.5:
    return ["Agricultural runoff (fertilizer, pesticides)", "Industrial waste containing alkaline substance", "Improper disposal of cleaning products (e.g. detergent, etc.)"]

def tds_cause(tds):
  if tds >= 150 and tds < 300:
    return ["Agricultural runoff (minimal)"]
  elif tds >= 300 and tds < 500:
    return ["Agricultural runoff", "Discharge from wastewater treatment plants", "Urban runoff (pollution)"]
  elif tds >= 500:
    return ["Industrial or agricultural runoff containing salts and minerals", "High levels of dissolved organic matter", "Contamination from sewage or wastewater discharge"]

def ec_cause(ec):
  if ec >= 1 and ec < 5:
    return ["Industrial discharge containing salts or conductive materials", "Agricultural runoff with fertilizers and chemicals", "High levels of dissolved ions from natural sources"]
  elif ec >= 5 and ec < 10:
    return ["Moderate mineral content", "Natural organic matter"]
  elif ec >= 10 and ec < 50:
    return ["Increased mineral content", "Agricultural runoff (moderate)"]
  elif ec >= 50 and ec < 100:
    return ["Urban runoff (moderate pollution)", "Industrial discharges", "Weather or seasonal changes"]
  elif ec >= 100:
    return ["Severe soil erosion", "Untreated wastewater", "Industrial accidents (chemical spills)"]

# Suggestions For Each Sensor Status
def temp_suggestion(temp):
  if temp > 0 and temp < 16:
    return [
      "Use a heater or adjust your HVAC system to maintain a more comfortable environment.",
      "Inspect windows and doors for drafts and seal any gaps.",
      "Monitor dam releases to minimize temperature fluctuations."
    ]
  elif temp >= 27 and temp < 35:
    return [
      "Organize tree-planting initiatives along riverbanks",
      "Encourage water conservation practices in the community.",
       "Monitor temperature level"
    ]
  elif temp >= 35:
    return ["Implement water flow regulations for industries",
            "Promote reforestation initiatives along riverbanks",
            "Implement heat mitigation strategies in urban areas"]

def ph_suggestion(ph):
  if ph < 6.5:
    return [
      "Use pH buffers to bring the pH level closer to neutral.",
      "Check for sources of contamination that may be lowering the pH, such as industrial waste or acidic substances.",
      "Apply neutralizing agents to correct the pH imbalance.",
      "Implement stricter regulations on industrial waste disposal"
    ]
  elif ph > 8.5:
    return [
      "Introduce acidic substances to neutralize excess alkalinity.",
      "Investigate any sources that may be causing alkalinity, such as alkaline runoff or chemical treatments.",
      "Use water filtration systems designed to handle alkaline conditions.",
      "Promote organic farming practices"
    ]

def tds_suggestion(tds):
  if tds >= 150 and tds < 300:
    return [
      "Implement storm drain filters to capture pollutants",
      "Promote responsible agricultural practices to minimize fertilizer and pesticide use"
    ]
  elif tds >= 300 and tds < 500:
    return [
      "Look for industrial or agricultural runoff that may be increasing TDS levels.",
      "Use advanced filtration systems to remove excess dissolved solids.",
      "Evaluate water treatment processes to ensure they are effectively managing TDS levels."
    ]
  elif tds >= 500:
    return ["Monitor mining activities",
            "Implement stricter regulations for industrial activities",
            "Invest in improved sewage treatment infrastructure"
            ]
  
def ec_suggestion(ec):
  if ec >= 1 and ec < 5:
    return [
      "Monitor EC levels",
      "Minimize pollution"
    ]
  elif ec >= 5 and ec < 10:
    return [
      "Monitor EC levels",
      "Promote responsible industrial practices"
    ]
  elif ec >= 10 and ec < 50:
    return ["Organize regular clean-up events along the riverbank",
            "Report suspected illegal dumping",
            "Improve urban runoff management and pollution control"
            ]
  elif ec >= 50 and ec < 100:
    return ["Implement coastal protection measures to minimize saltwater intrusion",
            "Promote responsible agricultural practices to minimize fertilizer and pesticide use",
            "Invest in improved sewage treatment infrastructure"]
  elif ec >= 100:
    return["Report any spills or suspicious activities",
           "Implement emergency response plan for industrial accidents",
           "Promote soil conservation techniques in agricultural areas",
           "Encourage proper wastewater management in livestock farms"]

# Database (MongoDB)
# Connect to MongoDB

# Load the MongoDB data
def connect_to_mongodb():
  connection_string = url
  client = pymongo.MongoClient(connection_string)
  return client

# Function to fetch data from MongoDB
def fetch_data_from_mongodb(client):
  db = client.get_database("waterqualitysensor")
  collection = db.get_collection("finalproject")
  data = collection.find_one(sort=[('_id', pymongo.DESCENDING)], projection={'_id': False, 'possible_causes': 0, 'possible_solutions': 0})
  return data
  
# Define the client
client = connect_to_mongodb()
def insert_into_button_collection():
  db = client.get_database("waterqualitysensor")
  button_collection = db.get_collection("button")
  return button_collection


# Close MongoDB
def close_mongodb(client):
  client.close()

## HTML Components
# Container for Body
def fragment_body(temp, ph, tds, ec, status):
  html_body = f'''
    <div class="m-5 grid grid-cols-1 sm:grid-cols-2 gap-5 sm:gap-10">
      <div class="col-span-1 sm:col-span-2">{fragment_water_status_container(status, get_description(status))}</div>
      {fragment_data_container("Temperature", temp, "°C", temp_status(temp))}
      {fragment_data_container("pH", ph, "", ph_status(ph))}
      {fragment_data_container("TDS", tds, "ppm", tds_status(tds))}
      {fragment_data_container("EC", ec, "NTU", ec_status(ec))}
      {fragment_possible_causes_container(temp, ph, tds, ec)}
      {fragment_suggestions_container(temp, ph, tds, ec)}
    </div>
  '''
  return html_body

# Container for Water Status
def fragment_water_status_container(status, description):
  html_water_status_container = f'''
    <div style="color: #1A3E7E; font-weight: bold;" class="w-full p-5 sm:p-10 flex flex-col justify-center bg-white rounded-xl shadow-black shadow-2xl">
      <span class="text-4xl sm:text-6xl text-center mb-5">{status}</span>
      <span class="text-md sm:text-xl text-center">{description}</span>
    </div>
  '''
  return html_water_status_container

# Container for Sensor Data
def fragment_data_container(title, value, unit, category):
  html_sensor_container = f'''
    <div style="color: #1A3E7E; font-weight: bold;" class="w-full p-5 sm:p-10 flex flex-col justify-center bg-white rounded-xl shadow-black shadow-2xl">
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
    f'{"".join([f"<li><span class=\"text-sm sm:text-2xl\">{cause}</span></li>" for cause in causes])}'
    f'</ul>'
    for key, causes in possible_causes.items() if causes
  ])
  
  html_possible_causes_container = f'''
    <div style="color: #1A3E7E;" class="w-full p-5 sm:p-10 flex flex-col bg-white rounded-xl shadow-black shadow-2xl">
      <span style="color: #1A3E7E; font-weight: bold;" class="text-3xl sm:text-4xl text-center mb-5">Possible Causes</span>
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
    <div style="color: #1A3E7E;" class="w-full p-5 sm:p-10 flex flex-col bg-white rounded-xl shadow-black shadow-2xl">
      <span style="color: #1A3E7E; font-weight: bold;" class="text-3xl sm:text-4xl text-center mb-5">Suggestions</span>
      {html_possible_suggestions if html_possible_suggestions else "<div class='flex-grow flex items-center justify-center text-xl text-gray-500'>No suggestions available</div>"}
    </div>
  '''
  return html_suggestion_container

## Header
html_title_container = '''
  <div class="w-full py-5 flex flex-wrap sm:flex-rows items-center gap-2 text-black font-bold">
    <span style="color: #1A3E7E; font-weight: bold;" class="text-4xl">Today's Water Quality</span>
    <span  style="color: #1A3E7E; font-weight: bold;" class="text-4xl hidden sm:block">-</span>
    <span style="color: #1A3E7E; font-weight: bold;" class="text-2xl">Kota Bandung</span>
  </div>
'''
st.markdown(html_title_container, unsafe_allow_html=True)

st.markdown("""
  <style>
      .stButton > button {
      background-color: #FFFFFF;
      color: #1A3E7E;
      font-weight: bold;
      padding: 10px 20px;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      margin-left: 5px;
      }
  </style>
  """, unsafe_allow_html=True)
st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    turn_on_button = st.button("Turn on Filtration")
with col2:
    turn_off_button = st.button("Turn off Filtration")

if turn_on_button:
    filtration = "on"
    button_collection = insert_into_button_collection()
    button_collection.insert_one({"filtration": filtration})
    st.write("Filtration turned on!")

if turn_off_button:
    filtration = "off"
    button_collection = insert_into_button_collection()
    button_collection.insert_one({"filtration": filtration})
    st.write("Filtration turned off!")

## Content
placeholder = st.empty()

while True:
  # Get data from MongoDB
  client = connect_to_mongodb()
  data = fetch_data_from_mongodb(client)
  db = client.get_database("waterqualitysensor")
  
  # Convert data to DataFrame
  data = pd.DataFrame([data])
  
  # Rename columns
  # data.rename(columns={'Temperature': 'Temperature (°C)', 'pH': 'pH', 'TDS': 'TDS (ppm)', 'EC': 'EC (NTU)'}, inplace=True)
  data.rename(columns={'Temperature (C)': 'Temperature (°C)', 'pH': 'pH', 'TDS (ppm)': 'TDS (ppm)', 'EC (NTU)': 'EC (NTU)'}, inplace=True)
  data = data[['Temperature (°C)', 'pH', 'TDS (ppm)', 'EC (NTU)']]  
  # Round data
  for key in data:
    data[key] = round(data[key], 1)

  tds = data['TDS (ppm)'][0]
  ec = data['EC (NTU)'][0]
  status = predict(data)[0]
  description = get_description(status)[0]

  # Render all the containers
  html_body = fragment_body(temp, ph, tds, ec, status)
  placeholder.markdown(html_body, unsafe_allow_html=True)

  close_mongodb(client)

  # wait for x seconds before fetching new data
  time.sleep(WAIT_TIME)
