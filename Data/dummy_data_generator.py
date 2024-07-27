import pandas as pd
import numpy as np
import random

# Generate dummy data
num_records = 5000
data = {
    'Temperature (°C)': np.random.uniform(0, 50, num_records),
    'pH': np.random.uniform(6, 9, num_records),
    'TDS (ppm)': np.random.uniform(0, 1000, num_records),
    'EC (NTU)': np.random.uniform(0, 100, num_records)
}

df = pd.DataFrame(data)

# Assign quality labels based on some arbitrary rules
def classify_quality(row):
    if row['pH'] < 6.5 or row['pH'] > 8.5 or row['TDS (ppm)'] > 1000:
        return 'Unacceptable'
    elif 6.5 <= row['pH'] <= 7.5 and row['TDS (ppm)'] <= 300:
        return 'Excellent'
    elif 6.5 <= row['pH'] <= 7.5 and 300 < row['TDS (ppm)'] <= 500:
        return 'Good'
    elif 6.5 <= row['pH'] <= 7.5 and 500 < row['TDS (ppm)'] <= 800:
        return 'Moderate'
    else:
        return 'Poor'

df['Quality'] = df.apply(classify_quality, axis=1)

quality_descriptions = {
    'Unacceptable': 'Water is not suitable for consumption.',
    'Poor': 'Water is of poor quality and may require significant treatment.',
    'Moderate': 'Water is acceptable, but may have some impurities.',
    'Good': 'Water is suitable for consumption, but may require treatment.',
    'Excellent': 'Water is of exceptional quality.',
}

df['Quality Description'] = df['Quality'].map(quality_descriptions)
# Save to CSV
df.to_csv('water_quality_data.csv', index=False)
