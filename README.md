# RESTgym

A Flexible Infrastructure for Empirical Assessment of Automated REST API Testing Tools

---

RESTgym is an infrastructure designed for the empirical assessment of REST API testing tools, aimed at simplifying the validation of these tools and facilitating performance comparison with competitor state-of-the-art tools. It includes a collection of Docker images for 11 benchmark REST APIs, as well as Docker images for 6 state-of-the-art tools, that can be extended with supplementary APIs and tools.


### Features

- Automation of the execution of the experimental testing sessions for each tool across all APIs
- Support for multiple repetitions to account for non-deterministic behaviors of APIs and tools
- Collection of experimental data about effectiveness and efficiency (code coverage, operation coverage, fault detection, etc.).
- Parallel execution of experimental testing sessions to reduce execution time while monitoring the host machine's available resources to prevent saturation.
- Runtime health checks to verify that both the API and the testing tool containers stay alive during the testing sessions.
- Integrity checks on completed testing sessions and re-execution of any that are found to be corrupted
- Compilation of comprehensive reports for each experimental testing session, as well as a cumulative report summarizing all the testing sessions.

### Installation

Before installing RESTgym, ensure that your system has Python and Docker installed, as these are essential dependencies for RESTgym.

Initialize a Python virtual environment with:

```
python -m venv venv
```

Activate the virtual environment with:
```
source venv/bin/activate
```

Install the required Python libraries with:
```
pip install -r requirements.txt
```

### Configuration

Most configuration settings for RESTgym are prompted at runtime via the command line. However, some settings can be specified in YAML configuration files. 
Specifically, RESTgym includes a general configuration file named `restgym-config.yml`, located in the root directory. In this file, you can define two parameters: the minimum number of CPUs and the minimum amount of RAM required on your system before initiating a testing session. These values are utilized for parallelization and further test sessions are executed in parallel as long the specified resources are available. The RESTgym configuration file is in the following format:

```yaml
minimum_cpus: 4
minimum_ram_gb: 4
```

Additionally, each API and tool can be enabled through a configuration file located in their respective directories. Configuration files for APIs are named `restgym-api-config.yml`, while those for tools are named `restgym-tool-config.yml`.

The content is the following:

```yaml
enabled: true
```

Set `enabled` to `false` if you want to exclude and API or a tool from the experiment.

By default, only two tools (DeepREST and RESTler) and two APIs (Market and SCS) are enabled to facilitate low-resource consumption dry run of experiments.

### Usage

Please follow the steps below to conduct your experiment:

#### Building or downloading Docker images

`python3 build.py`

This script manages the building of Docker images for the APIs and testing tools. It builds local images (if available) and downloads our pre-built images from our repositories on Docker Hub ([https://hub.docker.com/u/restgym](https://hub.docker.com/u/restgym)).

#### Experiment execution

`python3 run.py`

This script orchestrates the execution of testing sessions for each testing tool across all APIs, allowing for multiple repetitions. The executions are parallelized to minimize overall execution time. Upon launch, the script prompts the user for the number of repetitions for each testing tool and API configuration, then executes the remaining sessions. For example, if a previous execution of the script was set to run 3 repetitions and the user relaunches the script specifying a total of 5 repetitions, the script will only execute the 2 remaining repetitions.

#### Integrity check

`python3 run.py`

This script check the integrity of the executed testing sessions. It ensures that metrics were consistently collected throughout the experiment, verifies that an adequate number of requests were recorded by the proxy, and confirms that coverage samples are always increasing (as coverage cannot decrease).

In the event of a corrupted execution, the user will be prompted to decide whether to delete the execution. If the user chooses to delete it, they should re-execute the removed session using the `run.py` script.

#### Processing raw results

`python3 process_results.py`

This script processes the raw data to extract measures of effectiveness and efficiency, generating a comprehensive report for each execution, along with a cumulative report that summarizes all executions.