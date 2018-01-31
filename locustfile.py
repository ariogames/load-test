import os
import json
import dotenv

from locust import TaskSet, HttpLocust

dotenv.read_dotenv()
API_HOST = os.environ.get('LOCUST_API_HOST')
api_urls = os.environ.get('LOCUST_API_URLS').split(',')
api_headers = json.loads(os.environ.get('LOCUST_API_HEADERS'))
user_min_wait = int(os.environ.get('LOCUST_USER_MIN_WAIT'))
user_max_wait = int(os.environ.get('LOCUST_USER_MAX_WAIT'))


def get_task_callable(url):
    def f(l):
        l.client.get(url, headers=api_headers)

    return f


class MyTaskSet(TaskSet):
    tasks = [get_task_callable(API_HOST + url) for url in api_urls]


class WebsiteUser(HttpLocust):
    task_set = MyTaskSet
    min_wait = user_min_wait
    max_wait = user_max_wait
