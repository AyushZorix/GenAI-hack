import urllib.request
import json

url = "https://api.github.com/repos/AyushZorix/GenAI-hack/events"
req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0')
try:
    with urllib.request.urlopen(req) as res:
        events = json.loads(res.read().decode('utf-8'))
        for event in events:
            if event['type'] == 'PushEvent':
                print(f"PushEvent at {event['created_at']}")
                print(f"  Ref: {event['payload']['ref']}")
                print(f"  Before: {event['payload']['before']}")
                print(f"  Head: {event['payload']['head']}")
                for commit in event['payload']['commits']:
                    print(f"  Commit: {commit['sha']} - {commit['message']}")
                print("-" * 40)
except Exception as e:
    print(f"Failed to fetch events: {e}")
