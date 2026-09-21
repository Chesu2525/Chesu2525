from app.db.db import db
from .models import Incident


class IncidentController:
    def list_incidents(self, status=None, severity=None):
        query = Incident.query.order_by(Incident.created_at.desc())
        if status:
            query = query.filter_by(status=status)
        if severity:
            query = query.filter_by(severity=severity)
        return [incident.to_dict() for incident in query.all()]

    def create_incident(self, payload):
        incident = Incident(
            title=payload["title"].strip(),
            description=payload["description"].strip(),
            category=payload["category"],
            severity=payload["severity"],
            latitude=payload["latitude"],
            longitude=payload["longitude"],
            people_affected=payload.get("people_affected", 0),
        )
        db.session.add(incident)
        db.session.commit()
        return incident.to_dict()

    def get_incident(self, incident_id):
        incident = db.session.get(Incident, incident_id)
        return incident.to_dict() if incident else None

    def update_status(self, incident_id, status):
        incident = db.session.get(Incident, incident_id)
        if not incident:
            return None
        incident.status = status
        db.session.commit()
        return incident.to_dict()
