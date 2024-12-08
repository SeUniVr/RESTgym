import multiprocessing
import psutil
import math
import docker
import os



DOCKER_CLIENT = docker.from_env()
DOCKER_PREFIX = "restgym-"
DB_FILENAME = 'results.db'
CODE_COVERAGE_PATH = '/code-coverage'


# Print welcoe ASCII art
def welcome():
    print("    ____  _________________                    \n   / __ \\/ ____/ ___/_  __/___ ___  ______ ___ \n  / /_/ / __/  \\__ \\ / / / __ `/ / / / __ `__ \\\n / _, _/ /___ ___/ // / / /_/ / /_/ / / / / / /\n/_/ |_/_____//____//_/  \\__, /\\__, /_/ /_/ /_/ \n                       /____//____/            ")
    print("Welcome to the RESTgym experiment infrastructure.")

def get_apis():
    apis = os.listdir('./apis')
    apis.remove('#api-template')
    return apis

def get_tools():
    tools = os.listdir('./tools')
    tools.remove('#tool-template')
    return tools