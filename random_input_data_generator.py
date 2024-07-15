import pymongo
import random
import time

# Constants
WAIT_TIME = 10

# Variables
url = "YOUR MONGODB URL"

# MongoDB Atlas connection string
connection_string = url

# Function to generate random data
def generate_random_data():
    data = {
        'Temperature': round(random.uniform(0, 35), 2),   # Temperature between 0°C and 35°C
        'pH': round(random.uniform(0, 14), 2),            # pH between 0 and 14
        'TDS': round(random.uniform(0, 1000), 2),         # TDS between 0 and 1000 ppm
        'EC': round(random.uniform(0, 2000), 2)           # EC between 0 and 2000 µS/cm
    }
    return data

# Function to connect to MongoDB Atlas and insert data
def push_data_to_mongodb(data):
    try:
        # Connect to MongoDB Atlas
        client = pymongo.MongoClient(connection_string)
        db = client.get_database("data-sensor")  # Replace with your database name
        collection = db.get_collection("data")  # Replace with your collection name

        # Insert data into MongoDB
        result = collection.insert_one(data)
        print(f"Data inserted successfully with ID: {result.inserted_id}")

    except Exception as e:
        print(f"Error inserting data: {e}")

    finally:
        client.close()  # Close the MongoDB connection

# Main function to push random data to MongoDB every 10 seconds
def main():
    while True:
        data = generate_random_data()
        push_data_to_mongodb(data)
        time.sleep(WAIT_TIME)  # Wait for 10 seconds before generating and pushing next data

if __name__ == "__main__":
    main()
