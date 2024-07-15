import pandas as pd
import numpy as np
import random

# Generate dummy data
num_records = 5000
data = {
    'Temperature (°C)': np.random.uniform(0, 30, num_records),
    'pH': np.random.uniform(6, 8.5, num_records),
    'TDS (ppm)': np.random.uniform(100, 1000, num_records),
    'EC (µS/cm)': np.random.uniform(100, 2000, num_records)
}

df = pd.DataFrame(data)

# Assign quality labels based on some arbitrary rules
def classify_quality(row):
    if row['pH'] < 6.5 or row['pH'] > 8.5 or row['TDS (ppm)'] > 500:
        return 'bad'
    elif 6.5 <= row['pH'] <= 7.5 and row['TDS (ppm)'] <= 300:
        return 'good'
    else:
        return 'moderate'

df['Quality'] = df.apply(classify_quality, axis=1)

# Save to CSV
df.to_csv('water_quality_data.csv', index=False)
