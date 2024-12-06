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
    #print(" ____              _____ _____ _____ _____ \n|    \\ ___ ___ ___| __  |   __|   __|_   _|\n|  |  | -_| -_| . |    -|   __|__   | | |  \n|____/|___|___|  _|__|__|_____|_____| |_|  \n              |_|                          ")
    print("Welcome to the RESTgym experiment infrastructure.")

def get_apis():
    return os.listdir('./apis')

def get_tools():
    return os.listdir('./tools')