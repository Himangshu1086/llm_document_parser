from flask import jsonify
import uuid

class GlobalResponse:
    """
    Custom global response class for standardizing API responses.
    """
    def __init__(self, data=None, message="Success", status_code=200, error=None):
        self.data = data
        self.message = message
        self.status_code = status_code
        self.error = str(error) if error else None
    def to_dict(self):
        """
        Convert response to dictionary format for JSON responses.
        """
        return jsonify({
            'trace_id': self.error.get('trace_id', "TraceId" + "@" + str(uuid.uuid4())) if self.error and isinstance(self.error, dict) else "TraceId" + "@" + str(uuid.uuid4()),
            'data': [self.data],
            'message': self.message,
            'status_code': self.status_code,
            'error': self.error
        })


