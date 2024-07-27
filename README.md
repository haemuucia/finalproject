# Water Quality Monitoring System

A comprehensive water quality monitoring system that measures temperature, pH, Total Dissolved Solids (TDS), and Electrical Conductivity (EC). The system provides possible causes and suggestions based on the sensor readings to help maintain optimal water quality.

## Acknowledgements

This project was developed as a final project for completing Samsung Innovation Campus Batch 5. We extend our gratitude to the Samsung Innovation Campus for providing the opportunity and resources to undertake this project.

## Description

This project is designed to monitor the quality of water by measuring key parameters such as temperature, pH, TDS, and EC. Then we build a model with Random Forest to determine how is the overall water quality. Based on these readings, the system can provide potential causes for abnormal values and suggest corrective actions to maintain water quality.

## Technologies Used

- ESP32
- C
- Python
- Jupyter Notebook
- MongoDB
- Streamlit
- HTML/CSS

## Features

- Measure water temperature, pH, TDS, and EC.
- Display the overall water quality based on trained model.
- Display all of the sensor data.
- Display possible causes for abnormal readings.
- Provide actionable suggestions to address issues.
- Control filtration system.
- Responsive user interface built with Tailwind CSS.

## File Structure

- **[water_quality_data.csv](water_quality_data.csv)**  
  Dataset used for training the machine learning model. It includes water quality parameters such as temperature, pH, TDS, and EC, along with labels indicating water quality levels.

- **[water_quality_ml_model.ipynb](water_quality_ml_model.ipynb)**  
  Jupyter notebook for training the machine learning model and saving the trained model.

- **[waterquality_model.pkl](waterquality_model.pkl)**  
  The trained machine learning model file.

- **esp32/[esp32.ino](esp32/esp32.ino)**  
  Code for the ESP32 microcontroller. This file reads sensor data and communicates with the server via the MongoDB API.

- **[main.py](main.py)**  
  Main file for the Streamlit web application. It sets up the web interface, fetches and displays sensor data, provides possible causes and suggestions based on the readings, and controls filtration.

## How To Use

1. Clone Repository
   ```bash
   git clone https://github.com/haemuucia/finalproject
   cd finalproject
   ```

3. Install Dependencies
   ```bash
   pip install -r requirements.txt
   ```

5. Run Application
   ```bash
   streamlit run main.py 
   ```
   
