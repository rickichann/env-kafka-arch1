from datetime import datetime
from airflow import DAG 
from airflow.operators.python import PythonOperator
import json
import requests
import uuid
from uuid import UUID
from kafka import KafkaProducer
import time
import logging

default_args = {
    'owner':'devrichan',
    'start_date' : datetime(2023, 8, 3)
}


def extract_from_user_api_data():
    res = requests.get("https://randomuser.me/api/")
    res = res.json()
    return res['results'][0]
    
    

def transform_user_api_data(res):
    data = {}
    location = res['location']
    data['id'] = uuid.uuid4()
    data['first_name'] = res['name']['first']
    data['last_name'] = res['name']['last']
    data['gender'] = res['gender']
    data['address'] = f"{str(location['street']['number'])} {location['street']['name']}, " \
                      f"{location['city']}, {location['state']}, {location['country']}"
    data['post_code'] = location['postcode']
    data['email'] = res['email']
    data['username'] = res['login']['username']
    data['dob'] = res['dob']['date']
    data['registered_date'] = res['registered']['date']
    data['phone'] = res['phone']
    data['picture'] = res['picture']['medium']

    return data



def stream_user_api_data():
    res = transform_user_api_data(extract_from_user_api_data())

    def default_encoder(obj):
        if isinstance(obj, UUID):
            return str(obj)
        raise TypeError("Object of type {} is not JSON serializable".format(type(obj)))


    producer = KafkaProducer(bootstrap_servers=['broker:29092'], max_block_ms=5000)
    curr_time = time.time()

    
    while True:
        if time.time() > curr_time + 60:
            break
        try:
            producer.send('user_stream_data_created',json.dumps(res,default = default_encoder).encode('utf-8'))
            print("data sended")
        except Exception as e:
            logging.error(f'An error occured: {e}')
            continue



with DAG('user_stream',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dag:
    
    streaming_task = PythonOperator(
        task_id = 'extract_data_from_api',
        python_callable = stream_user_api_data
    )
    

# stream_user_api_data()
