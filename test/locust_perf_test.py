import configparser
import json

from locust import HttpUser, task

# performance tests
# run with 'locust -f test/locust_perf_test.py -u 5 -r 5 --headless -t 10s --host=http://localhost:5000'
# or to run only a single UserClass, add f.e. SmallPayloadToApi'
# 'locust -h' for detailed options


config = configparser.ConfigParser()
config.read("stack-output.ini")
sam_managed_api_url = config["DEFAULT"]["sam_managed_api_url"]
s3_event_api_url = config["DEFAULT"]["s3_event_api_url"]

with open("events/small.json") as file:
    small_payload = json.load(file)

with open("events/large.json") as file:
    large_payload = json.load(file)


class SmallPayload(HttpUser):
    @task
    def async_api(self):
        self.client.post(sam_managed_api_url + "/events-async", json=small_payload)

    @task
    def s3(self):
        self.client.post(s3_event_api_url + "/events-s3", json=small_payload)


class LargePayload(HttpUser):
    @task
    def async_api(self):
        self.client.post(sam_managed_api_url + "/events-async", json=large_payload)

    @task
    def s3(self):
        self.client.post(s3_event_api_url + "/events-s3", json=large_payload)
