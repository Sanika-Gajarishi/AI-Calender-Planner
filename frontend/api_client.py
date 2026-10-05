import requests

from config import API_BASE_URL


class APIClient:
    def __init__(self, token=None):
        self.token = token

    def _headers(self):
        headers = {
            "accept": "application/json",
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        return headers

    # -------------------------
    # AUTH
    # -------------------------

    def login(self, email, password):
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={
                "email": email,
                "password": password,
            },
            timeout=30,
        )

        response.raise_for_status()
        return response.json()

    def register(self, name, email, password):
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json={
                "name": name,
                "email": email,
                "password": password,
            },
            timeout=30,
        )

        response.raise_for_status()
        return response.json()

    # -------------------------
    # TASKS
    # -------------------------

    def get_tasks(self):
        response = requests.get(
            f"{API_BASE_URL}/tasks/",
            headers=self._headers(),
            timeout=30,
        )

        response.raise_for_status()
        return response.json()

    def create_task(self, task):
        response = requests.post(
            f"{API_BASE_URL}/tasks/",
            headers=self._headers(),
            json=task,
            timeout=30,
        )

        response.raise_for_status()
        return response.json()

    def update_task(self, task_id, task):
        response = requests.put(
            f"{API_BASE_URL}/tasks/{task_id}",
            headers=self._headers(),
            json=task,
            timeout=30,
        )

        response.raise_for_status()
        return response.json()

    def delete_task(self, task_id):
        response = requests.delete(
            f"{API_BASE_URL}/tasks/{task_id}",
            headers=self._headers(),
            timeout=30,
        )

        response.raise_for_status()
        return response.json()

    # -------------------------
    # AI TASK
    # -------------------------

    def create_ai_task(self, text):
        response = requests.post(
            f"{API_BASE_URL}/ai/create-task",
            headers=self._headers(),
            json={
                "text": text,
            },
            timeout=90,
        )

        response.raise_for_status()
        return response.json()

    # -------------------------
    # SCHEDULE
    # -------------------------

    def generate_schedule(
        self,
        start_date,
        number_of_days=7,
    ):
        response = requests.post(
            f"{API_BASE_URL}/schedule/generate",
            headers=self._headers(),
            params={
                "start_date": start_date,
                "number_of_days": number_of_days,
            },
            timeout=90,
        )

        response.raise_for_status()
        return response.json()

    def sync_schedule_to_google_calendar(
        self,
        start_date,
        number_of_days=7,
    ):
        response = requests.post(
            f"{API_BASE_URL}/schedule/sync-google",
            headers=self._headers(),
            params={
                "start_date": start_date,
                "number_of_days": number_of_days,
            },
            timeout=90,
        )

        response.raise_for_status()
        return response.json()