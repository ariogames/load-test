import os
import json
import dotenv
import requests
from flask import request, jsonify
from locust import TaskSet, HttpLocust, events, web

dotenv.read_dotenv()
MASTER_IP_ADDR = os.environ.get('LOCUST_MASTER_IP_ADDR', None)
MASTER_WEB_PORT_ADDR = os.environ.get('LOCUST_MASTER_WEB_PORT_ADDR', '8089')


class Config:
    def __init__(self):
        if MASTER_IP_ADDR:
            master_config_url = 'http://{host}:{port}/config'.format(host=MASTER_IP_ADDR, port=MASTER_WEB_PORT_ADDR)
            rsp = requests.get(master_config_url).json()
            self.json_data = rsp['message']
            self.host = self.json_data['host']
            self.headers = dict(self.json_data['headers'])
            self.user_min_wait = self.json_data['min_wait']
            self.user_max_wait = self.json_data['max_wait']
            self.urls = self.json_data['urls']
        else:
            self.host = os.environ.get('LOCUST_API_HOST')
            self.headers = json.loads(os.environ.get('LOCUST_API_HEADERS'))
            self.user_min_wait = int(os.environ.get('LOCUST_USER_MIN_WAIT'))
            self.user_max_wait = int(os.environ.get('LOCUST_USER_MAX_WAIT'))
            self.urls = os.environ.get('LOCUST_API_URLS').split(',')


config = Config()


def my_start_hatching_handler(*args, **kw):
    c = Config()
    MyTaskSet.tasks = [get_task_callable(url) for url in c.urls]


events.locust_start_hatching += my_start_hatching_handler


def get_task_callable(url):
    def f(l):
        l.client.get(url, headers=config.headers)

    return f


class MyTaskSet(TaskSet):
    tasks = [get_task_callable(url) for url in config.urls]


class WebsiteUser(HttpLocust):
    task_set = MyTaskSet
    min_wait = config.user_min_wait
    max_wait = config.user_max_wait
    host = config.host


@web.app.route("/config", methods=['GET', 'POST'])
def get_tasks():
    if request.method == 'POST':
        import pickle
        data = request.get_json()
        output = open('task_set.pkl', 'wb')
        pickle.dump(data, output)
        output.close()
        return jsonify({'message': 'ok'})
    else:
        import pickle
        try:
            pkl_file = open('task_set.pkl', 'rb')
            data = pickle.load(pkl_file)
            pkl_file.close()
            return jsonify({'message': data})
        except FileNotFoundError:
            return jsonify({'message': {}})
