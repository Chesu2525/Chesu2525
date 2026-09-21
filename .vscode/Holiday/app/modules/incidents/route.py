from flask import Blueprint, jsonify, request

from .controller import IncidentController


incidents_bp = Blueprint("incidents", __name__)
incident_controller = IncidentController()

VALID_CATEGORIES = {"disease", "flood", "fire", "earthquake", "storm", "other"}
VALID_SEVERITIES = {"low", "medium", "high", "critical"}
VALID_STATUSES = {"reported", "verified", "responding", "resolved"}
REQUIRED_FIELDS = {
    "title",
    "description",
    "category",
    "severity",
    "latitude",
    "longitude",
}


def _validate_incident(payload):
    if not isinstance(payload, dict):
        return "Request body must be a JSON object."
    missing = REQUIRED_FIELDS - payload.keys()
    if missing:
        return f"Missing required fields: {', '.join(sorted(missing))}."
    if not isinstance(payload["title"], str) or not payload["title"].strip():
        return "title must be a non-empty string."
    if not isinstance(payload["description"], str) or not payload["description"].strip():
        return "description must be a non-empty string."
    if payload["category"] not in VALID_CATEGORIES:
        return "category is not supported."
    if payload["severity"] not in VALID_SEVERITIES:
        return "severity is not supported."
    for field, minimum, maximum in (
        ("latitude", -90, 90),
        ("longitude", -180, 180),
    ):
        value = payload[field]
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not minimum <= value <= maximum:
            return f"{field} must be a number between {minimum} and {maximum}."
    people_affected = payload.get("people_affected", 0)
    if not isinstance(people_affected, int) or isinstance(people_affected, bool) or people_affected < 0:
        return "people_affected must be a non-negative integer."
    return None


@incidents_bp.route("", methods=["GET"])
def list_incidents():
    status = request.args.get("status")
    severity = request.args.get("severity")
    if status and status not in VALID_STATUSES:
        return jsonify(error="status is not supported."), 400
    if severity and severity not in VALID_SEVERITIES:
        return jsonify(error="severity is not supported."), 400
    return jsonify(data=incident_controller.list_incidents(status, severity))


@incidents_bp.route("", methods=["POST"])
def create_incident():
    payload = request.get_json(silent=True)
    error = _validate_incident(payload)
    if error:
        return jsonify(error=error), 400
    return jsonify(data=incident_controller.create_incident(payload)), 201


@incidents_bp.route("/<int:incident_id>", methods=["GET"])
def get_incident(incident_id):
    incident = incident_controller.get_incident(incident_id)
    if not incident:
        return jsonify(error="Incident not found."), 404
    return jsonify(data=incident)


@incidents_bp.route("/<int:incident_id>/status", methods=["PATCH"])
def update_status(incident_id):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or payload.get("status") not in VALID_STATUSES:
        return jsonify(error="status must be one of the supported values."), 400
    incident = incident_controller.update_status(incident_id, payload["status"])
    if not incident:
        return jsonify(error="Incident not found."), 404
    return jsonify(data=incident)
