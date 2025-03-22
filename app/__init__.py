from flask import Flask
from app.config.environment import config
from app.services.search_service import init_search_service
from app.routes import main
from app.lib.interfaces.global_error import GlobalError
from app.lib.enums.http_status_code import HttpStatusCode
import nltk
def create_app(config_class=config):
    try:
        app = Flask(__name__)
        app.config.from_object(config_class)

        # Initialize FAISS index and other services
        init_search_service()

        # Register blueprints
        app.register_blueprint(main)

        nltk.download('punkt')
        nltk.download('wordnet')
        nltk.download('stopwords')
        nltk.download('punkt_tab')

        return app
    except Exception as e:
        if isinstance(e, GlobalError):
            return e
        return GlobalError(message="An unexpected error occurred", status_code=HttpStatusCode.INTERNAL_SERVER_ERROR.value, error=e).to_dict()
