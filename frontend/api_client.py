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

    

    def get_google_calendar_status(self):
        response = requests.get(
            f"{API_BASE_URL}/calendar/status",
            headers=self._headers(),
            timeout=30,
        )

        response.raise_for_status()
        return response.json()

    def connect_google_calendar(self):
        response = requests.post(
            f"{API_BASE_URL}/calendar/connect",
            headers=self._headers(),
            timeout=90,
        )

        response.raise_for_status()
        return response.json()

    def get_google_calendar_events(self, days=7):
        response = requests.get(
            f"{API_BASE_URL}/calendar/events",
            headers=self._headers(),
            params={
                "days": days,
            },
            timeout=90,
        )

        response.raise_for_status()
        return response.json()


    def chat_with_agent(self, message):
        response = requests.post(
            f"{API_BASE_URL}/agent/chat",
            headers=self._headers(),
            params={
                "message": message,
            },
            timeout=120,
        )

        response.raise_for_status()
        return response.json()