# Contributing with a new API

This README provides instructions for adding a new API to RESTgym.

Since in RESTgym APIs run within a Docker container, you will need to package the API into a Docker image using a `Dockerfile`. This image should include all necessary dependencies for the API's execution, such as the Java Virtual Machine (JVM) if the API is written in Java, and any databases it requires. Additionally, the API container should incorporate all tools for metric collection. In this directory (i.e., `apis/#api-template/`), you will find the `Dockerfile` and other files used to build the Docker image for the SCS API. You can use these as a starting point for creating the Docker image for your own API.

## The API directory
Each API should be stored in a directory under `apis/`, and it is recommended that the directory name reflects the API's name. For example, the SCS API is located in the `apis/scs/` directory. **Keep this directory name in mind, as it will be used by RESTgym in scripts and other components. We will refer to this name as 'API slug' now on.**

The content of the API directory should be structured as follows:
- The executable or the source code of the API (in this case, we have the executable `scs-sut.jar`).
- The API configuration file for RESTgym, named `restgym-api-config.yml`. Currently, the only supported configuration is `enabled: true/false` to enable or disable the API in RESTgym.
- The `specifications/` directory, containing Swagger (2.0, preferably in YAML) or OpenAPI (3.0, preferably in JSON) specification for the API. The specification should be named as `aaa.yaml` and `aaa-openapi.json`, where `aaa` has to be replaced with the same slug used for the API directory name (the API slug).
- The `classes/` directory, containing the Java compiled classes for code coverage computation (only applicable to Java APIs).
- The `dictionaries/` directory containing dictionaries for tools, such as the LLM dictionary for DeepREST. Dictionaries for DeepREST can be generated with the script available in the DeepREST repository. If no dictionaries are provided to DeepREST, the LLM dictionary feature will not be utilized, which may negatively impact the tool's performance.
- The `database/` directory, containing SQL scripts to initialize the database of the API (only for APIs with a database).
- The `Dockerfile`, used to build the Docker image for the API. See the instructions in the next section.

## The Dockerfile
The `Dockerfile` is used to build the Docker image for the API. It contains commands to install the API along with its required dependencies and libraries. Additionally, it sets up the metric collection tools (such as JaCoCo and a MITM proxy) and ultimately runs both the API (on port 8080) and the metric collection tools.

As an example, we will refer to the `Dockerfile` contained in this directory. Refer to this example to create the `Dockerfile` for your API. If you need further assistance, please feel free to open an issue.

### Line 1: The starting image
In this case, our API image will be built on top of Ubuntu 22.04. However, you can use lighter images as long as they support the metric collection tools. Additionally, if your API is already available as a Docker image, you can start from that image and simply install the metric collection tools.

### Line 3: Environment variables definition
Use the command `ENV API=scs` to set an environment called `API` with the value equal to the API stub.

### Lines 5-7: Preparation of internal directories
Directories to contain the API files, the infrastructure files (metric collection tools and scripts), and the results are created. The `results/` directory in the image will be mapped to the `results/` directory of this repository on the host machine to store results persistently. This is done automatically by RESTgym.

### Lines 8-11: Installation of required packages
These lines install the required packages to run the API (e.g., the JDK in this case) and the MITM proxy, which is required for the collection of HTTP history for black-box metrics computation.

### Line 13: Copy of the API data into the image
This line copies all the API directory into the image at the location `/api/`.

### Line 14: Copy of the metric collection tools and scripts into the image
This line copies the provided scripts for metric collection into the Docker image.

### Lines 16-19: Container execution command
The last command of a `Dockerfile` starting with `CMD` says to Docker what command to execute when the container is launched.
- `mkdir -p /results/$API/$TOOL/$RUN` created the nested directories in the `results/` folder to store the results of a specific instance of the container.
- `sh /infrastructure/jacoco/collect-coverage-interval.sh` starts the code coverage collection script.
- `mitmdump -p 9090 --mode reverse:http://localhost:8080/ -s /infrastructure/mitmproxy/store-interactions.py` launched MITM proxy in reverse mode on port 9090 with a custom script to store HTTP interaction in a SQLite database.
- `java -javaagent:/infrastructure/jacoco/org.jacoco.agent-0.8.7-runtime.jar=includes=*,output=tcpserver,port=12345,address=* -Dfile.encoding=UTF-8 -jar /api/scs-sut.jar` finally executes the API instrumented by JaCoCo.