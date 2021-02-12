import json
import os

from locust import HttpUser, task

# performance tests
# run with 'locust -f test/locust_perf_test.py -u 5 -r 5 --headless -t 10s --host=http://localhost:5000'
# or to run only a single UserClass, add f.e. SmallPayloadToApi'
# 'locust -h' for detailed options
# set AWS_PROFILE and/or AWS_REGION environment variables if they are not the default ones

os.system("bin/dump-stack-output.sh")
with open("stack-output.json") as file:
    stack_outputs = json.load(file)["Stacks"][0]["Outputs"]

sam_managed_api_url = [output["OutputValue"] for output in stack_outputs
                       if output["OutputKey"] == "SamManagedApiUrl"][0]
s3_event_api_url = [output["OutputValue"] for output in stack_outputs
                    if output["OutputKey"] == "S3EventApiUrl"][0]

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
