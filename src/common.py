import docker
import os
import yaml



DOCKER_CLIENT = docker.from_env()
DOCKER_PREFIX = 'restgym-'
DB_FILENAME = 'results.db'
CODE_COVERAGE_PATH = '/code-coverage'
LOGS_PATH = '/logs'
RESTGYM_BASE_DIR_HOST = os.getenv('RESTGYM_BASE_DIR', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
RESTGYM_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


# Print welcome ASCII art
def welcome():
    print("    ____  _________________                    \n   / __ \\/ ____/ ___/_  __/___ ___  ______ ___ \n  / /_/ / __/  \\__ \\ / / / __ `/ / / / __ `__ \\\n / _, _/ /___ ___/ // / / /_/ / /_/ / / / / / /\n/_/ |_/_____//____//_/  \\__, /\\__, /_/ /_/ /_/ \n                       /____//____/            ")
    print("Welcome to the RESTgym experiment infrastructure.")

def check_enabled(t, wildcard):
    if t == 'api':
        config_file = f"{RESTGYM_BASE_DIR}/apis/{wildcard}/restgym-api-config.yml"
    elif t == 'tool':
        config_file = f"{RESTGYM_BASE_DIR}/tools/{wildcard}/restgym-tool-config.yml"
    else:
        return False

    with open(config_file, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
            return config['enabled']
        except yaml.YAMLError as exc:
            print(exc)
            return False

def get_apis():
    apis = os.listdir(f'{RESTGYM_BASE_DIR}/apis')
    try:
        apis.remove('.DS_Store')
    except ValueError:
        pass
    apis.remove('#api-template')
    apis[:] = [x for x in apis if check_enabled('api', x)]
    return apis

def get_tools():
    tools = os.listdir(f'{RESTGYM_BASE_DIR}/tools')
    try:
        tools.remove('.DS_Store')
    except ValueError:
        pass
    tools.remove('#tool-template')
    tools[:] = [x for x in tools if check_enabled('tool', x)]
    return tools