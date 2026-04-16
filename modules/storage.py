import json
import os
from datetime import datetime


class AlertStorage:
    def __init__(self, filepath="data/alerts.json"):
        self.filepath = filepath
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.filepath):
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w') as f:
                json.dump([], f)

    def save_alert(self, data):
        alerts = self.load_alerts()
        alert = {
            "time": data.get("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "type": data.get("type", "intrusion"),
            "label": data.get("label", "unknown"),
            "image": data.get("image", "")
        }
        alerts.append(alert)
        
        with open(self.filepath, 'w') as f:
            json.dump(alerts, f, indent=2)

    def load_alerts(self):
        self._ensure_file()
        with open(self.filepath, 'r') as f:
            return json.load(f)

    def clear_alerts(self):
        with open(self.filepath, 'w') as f:
            json.dump([], f)


if __name__ == "__main__":
    storage = AlertStorage()
    
    storage.save_alert({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "intrusion",
        "label": "person",
        "image": "data/img_001.jpg"
    })
    
    print("Alerts saved:")
    alerts = storage.load_alerts()
    for alert in alerts:
        print(f"  - {alert}")
    
    storage.clear_alerts()
    print("\nAlerts cleared.")
