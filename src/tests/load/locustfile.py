from locust import HttpUser, task, between

from threading import Lock

token_lock = Lock()
shared_token = None

class SingleUserLoad(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        global shared_token
        with token_lock:
            if shared_token is None:
                payload = {
                    "username": "Alex",
                    "password": "My_pass1"
                }
                response = self.client.post(
                    "/api/v1/auth/login/",
                    data=payload,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                if response.status_code != 200:
                    raise Exception("Login failed")
                tokens = response.json()
                shared_token = tokens["access_token"]

        self.headers = {"Authorization": f"Bearer {shared_token}"}


    @task
    def get_tasks(self):
        self.client.get("/api/v1/tasks/", headers=self.headers)