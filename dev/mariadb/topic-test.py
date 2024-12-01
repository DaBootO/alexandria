from quixstreams import Application
import json
from faker import Faker
import uuid
import time
import random

faker = Faker()
app = Application(broker_address="localhost:9094")

def main():
    while True:
        generate_data()

def generate_data():
    # Sample data to send
    data = [
        {'user_id': random.randint(1,10000), 'name': faker.name(), 'email': faker.email()},
        {'user_id': random.randint(1,10000), 'name': faker.name(), 'email': faker.email()},
        {'user_id': random.randint(1,10000), 'name': faker.name(), 'email': faker.email()},
        {'user_id': random.randint(1,10000), 'name': faker.name(), 'email': faker.email()},
        {'user_id': random.randint(1,10000), 'name': faker.name(), 'email': faker.email()}
    ]
    with app.get_producer() as producer:
        # iterate over the data from the hardcoded dataset
        # topic_name = str(uuid.uuid4())
        topic_name = str("XYZ")
        for row in data:
            json_data = json.dumps(row) # convert the row to JSON
            print(json_data)

            # publish the data to the topic
            producer.produce(
                topic=topic_name,
                value=json_data,
            )

        print("All rows published")
        time.sleep(2)

if __name__ == "__main__":
    main()
