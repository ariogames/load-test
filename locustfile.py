import os
import json
import dotenv
import requests
import jinja2
from flask import request, jsonify, render_template
from locust import TaskSet, HttpLocust, events, web

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
my_loader = jinja2.ChoiceLoader([
    jinja2.FileSystemLoader(os.path.join(PROJECT_ROOT, 'templates')),
    web.app.jinja_loader,
])
web.app.jinja_loader = my_loader

dotenv.read_dotenv()
MASTER_IP_ADDR = os.environ.get('LOCUST_MASTER_IP_ADDR', None)
MASTER_WEB_PORT_ADDR = os.environ.get('LOCUST_MASTER_WEB_PORT_ADDR', '8089')


class Config:
    def __init__(self):
        if MASTER_IP_ADDR:
            print('Getting configuration from master...')
            master_config_url = 'http://{host}:{port}/config'.format(host=MASTER_IP_ADDR, port=MASTER_WEB_PORT_ADDR)
            try:
                rsp = requests.get(master_config_url).json()
                self.json_data = rsp['message']
                self.host = self.json_data['host']
                self.headers = dict(self.json_data['headers'])
                self.user_min_wait = self.json_data['min_wait']
                self.user_max_wait = self.json_data['max_wait']
                self.urls = self.json_data.get('urls', None)
                self.endpoints = self.json_data.get('endpoints', None)
            except KeyError:
                print('Configuration Error! You should post configuration to master first!!')
                exit(-1)

        else:
            self.host = os.environ.get('LOCUST_API_HOST', '')
            self.headers = json.loads(os.environ.get('LOCUST_API_HEADERS', '{}'))
            self.user_min_wait = int(os.environ.get('LOCUST_USER_MIN_WAIT', '100'))
            self.user_max_wait = int(os.environ.get('LOCUST_USER_MAX_WAIT', '200'))
            self.urls = os.environ.get('LOCUST_API_URLS', '').split(',')


config = Config()


def my_start_hatching_handler(*args, **kw):
    c = Config()

    MyTaskSet.tasks = get_task_callable(c)
    WebsiteUser.min_wait = c.user_min_wait
    WebsiteUser.max_wait = c.user_max_wait
    WebsiteUser.host = c.host


events.locust_start_hatching += my_start_hatching_handler


def get_task_callable(c):
    if c.urls:
        print("sending get requests against urls")
        return [get_urls_task_callable(c, url) for url in c.urls]
    elif c.endpoints:
        print("sending requests against endpoints")
        return [get_endpoints_task_callable(endpoint) for endpoint in c.endpoints]


def get_urls_task_callable(c, url):
    def f(l):
        l.client.get(url, headers=c.headers)

    return f


def get_endpoints_task_callable(endpoint):
    def f(l):
        if endpoint['method'].upper() == 'POST':
            l.client.post(endpoint['url'], data=json.dumps(endpoint['body']), headers=endpoint.get('headers', {}),
                          catch_response=True)
        elif endpoint['method'].upper() == 'GET':
            l.client.get(endpoint['url'], headers=endpoint.get('headers', {}))

    return f


class MyTaskSet(TaskSet):
    tasks = get_task_callable(config)


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
        print(data)
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


@web.app.route("/config/edit", methods=['GET'])
def edit_config():
    import pickle
    try:
        pkl_file = open('task_set.pkl', 'rb')
        data = pickle.load(pkl_file)
        pkl_file.close()
        return render_template('config_form.html', data=json.dumps(data))
    except FileNotFoundError:
        return render_template('config_form.html', data=json.dumps({}))
