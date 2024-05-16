import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import pytz
import json

class GoogleClient:
    """
    A class for interacting with Google Calendar and Tasks APIs.
    """
    SCOPES = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/tasks"
    ]

    def __init__(self):
        self.creds = self.__auth()
        self.calendar_service = build("calendar", "v3", credentials=self.creds)
        self.tasks_service = build("tasks", "v1", credentials=self.creds)

    def __auth(self):
        """
        Private method to authenticate the Google API client.
        """
        creds = None

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", self.SCOPES)
                creds = flow.run_local_server(port=50567)
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return creds
    
    def refresh_token(self):
        """
        Method to refresh the access token.
        """
        if self.creds and self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

    # Google Calendar methods
    def list_calendars(self):
        try:
            results = self.calendar_service.calendarList().list().execute()
            items = results.get("items", [])
            if not items:
                return "No calendars found."
            calendar_summaries = [item['summary'] for item in items]
            return '\n'.join(calendar_summaries)
        except HttpError as err:
            return f"An error occurred: {err}"
        
    def get_day_events(self, calendar_id='primary', day=datetime.now(), timezone='America/Halifax'):
        """
        Retrieve events for the specified day and time range.
        """
        tz = pytz.timezone(timezone)
        day = tz.localize(datetime(day.year, day.month, day.day, 0, 0, 0, 0))
        start_of_day = day.isoformat()
        end_of_day = (day + timedelta(days=1, microseconds=-1)).isoformat()
        events_result = (
            self.calendar_service.events()
            .list(
                calendarId=calendar_id,
                timeMin=start_of_day,
                timeMax=end_of_day,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        return events
  
    def format_events_as_markdown(self, events):
        """
        Format the list of events as a markdown checklist, including the event's summary and description (if available).
        """
        if not events:
            print("No events found.")
            return []

        event_list = []
        for event in events:
            start_dt = datetime.fromisoformat(event["start"].get("dateTime", event["start"].get("date")).replace('Z', ''))
            end_dt = datetime.fromisoformat(event["end"].get("dateTime", event["end"].get("date")).replace('Z', ''))
            formatted_event = f"{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')} {event['summary']}"
            event_list.append(formatted_event)

        return [f"- {event}" for event in event_list]

    def get_calendar_day_events_as_markdown_checklist(self, calendar_id="primary", day=datetime.now(), timezone='America/Halifax'):
        """
        Main function to get events and format them as a markdown checklist.
        """
        events = self.get_day_events(calendar_id=calendar_id, day=day, timezone=timezone)
        return self.format_events_as_markdown(events)

    
    

    # Google Tasks methods
    def list_task_lists(self):
        """
        Lists the first 10 task lists.
        """
        try:
            results = self.tasks_service.tasklists().list().execute()
            items = results.get("items", [])

            if not items:
                print("No task lists found.")
            else:
                print("Task lists:")
                for item in items:
                    print(f"{item['title']}")
        except HttpError as err:
            print(err)

    def list_tasks(self, tasklist="@default", show_completed=False, show_hidden=False, max_results=100, due_min=None, due_max=None):
        """
        Lists tasks from the specified tasklist.
        https://developers.google.com/tasks/reference/rest/v1/tasks/list
        
        """
        try:
            # Refresh the token if needed
            self.refresh_token()
        except Exception as e:
            print(f"An error occurred while refreshing the token: {e}")
            return None
        
        try:
            results = self.tasks_service.tasks().list(
                tasklist=tasklist,
                showCompleted=show_completed,
                showHidden=show_hidden,
                maxResults=max_results,
                dueMin=due_min,
                dueMax=due_max
            ).execute()
            items = results.get("items", [])
            return items
        except HttpError as err:
            print(err)

    def get_current_tasks_as_markdown(self):
        """
        Returns a string containing current tasks in Markdown format.
        """
        now = datetime.now(pytz.utc)
        current_day = now.date()
        markdown_tasks = ""

        tasks = self.list_tasks()
        for task in tasks:
            if 'due' in task:
                due_datetime = datetime.strptime(task["due"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc)
                due_date = due_datetime.date()

                if due_date < current_day:
                    days_expired = (current_day - due_date).days - 1
                    if days_expired >= 14:
                        weeks_expired = days_expired // 7
                        status = f"{weeks_expired} weeks expired"
                    else:
                        status = f"{days_expired} days expired"

                    markdown_tasks += f"- [ ] **{task['title']}** ({status})\n"
                elif due_date == current_day:
                    markdown_tasks += f"- [ ] **{task['title']}** (Due today)\n"

        return markdown_tasks

    def find_and_complete_task(self, task_name, tasklist='@default'):
        tasks = self.list_tasks(tasklist)

        for task in tasks:
            if task['title'] == task_name:
                if task['status'] == 'completed':
                    print(f"Task '{task_name}' is already completed.")
                    return task
                else:
                    body = {
                        "id": task['id'],
                        "status": "completed",
                        "completed": datetime.utcnow().isoformat() + 'Z',
                    }

                    try:
                        updated_task = self.tasks_service.tasks().update(tasklist=tasklist, task=task['id'], body=body).execute()
                        print(f"Task '{task_name}' marked as completed.")
                        return updated_task
                    except Exception as e:
                        print(f"An error occurred: {e}")

    def add_task(self, task_name, completed=False, tasklist='@default', due_date=datetime.utcnow() + timedelta(days=1)):
        task_body = {
            'title': task_name,
            'due': due_date.isoformat() + 'Z',
            'status': 'completed' if completed else 'needsAction'
        }
        try:
            new_task = self.tasks_service.tasks().insert(tasklist=tasklist, body=task_body).execute()
            return new_task
        except Exception as e:
            print(f"An error occurred while creating the task: {e}")
            return None

if __name__ == "__main__":
    google_client = GoogleClient()
    
    # print(google_client.list_tasks()[0])
    