from app import create_app
from app.config.environment import config, EnvironmentVariables
app = create_app()


if __name__ == '__main__':
    '''TODO: Remove debug=False when ready to deploy and host on a cloud service'''
    app.run(host=config[EnvironmentVariables.FLASK_HOST.value], port=config[EnvironmentVariables.FLASK_PORT.value], debug=False)