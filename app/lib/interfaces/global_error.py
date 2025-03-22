import uuid
from flask import jsonify

class GlobalError(Exception):
    """
    Custom global error class for handling application-wide exceptions.
    """
    def __init__(self, message="An unexpected error occurred", status_code=500, error=None):
        self.message = message
        self.status_code = status_code
        self.error = str(error) if error else None
        super().__init__(self.message, self.status_code)

    def to_dict(self):
        """
        Convert error to dictionary format for JSON responses.
        """
        return jsonify({
            'trace_id': "TraceId" + "@" + str(uuid.uuid4()),
            'error': self.message,
            'status_code': self.status_code,
            'root_error': self.error
        })
