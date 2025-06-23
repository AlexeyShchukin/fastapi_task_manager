from locust import HttpUser, task, between



class SingleUserLoad(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        payload = {
            "username": "Alex",
            "password": "My_pass1"
        }
        response = self.client.post(
            "/api/v1/auth/login/",
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print("Login response:", response.status_code, response.text)

        if response.status_code != 200:
            raise Exception("Login failed")

        tokens = response.json()
        self.access_token = tokens["access_token"]
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    @task
    def get_tasks(self):
        self.client.get("/api/v1/tasks/", headers=self.headers)