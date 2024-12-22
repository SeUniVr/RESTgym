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

#### Building or downloading Docker images
`python3 build.py`

#### Experiment execution
`python3 run.py`

#### Integrity check
`python3 run.py`

#### Processing raw results
`python3 process_results.py`