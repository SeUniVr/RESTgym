# RESTgym

A flexible infrastructure for empirical assessment of automated REST API black-box testing tools

---

RESTgym is an infrastructure designed for the empirical assessment of REST API testing tools, aimed at simplifying the validation of these tools and facilitating performance comparison with competitor state-of-the-art tools. It includes a collection of Docker images for 11 benchmark REST APIs, as well as Docker images for 6 state-of-the-art tools, that can be extended with supplementary APIs and tools.


### Features

- Automation of the execution of the experimental testing sessions for each tool across all APIs
- Support for multiple repetitions to account for non-deterministic behaviors of APIs and tools
- Collection of experimental data about effectiveness and efficiency (code coverage, operation coverage, fault detection, etc.).
- Parallel execution of experimental testing sessions to reduce execution time while monitoring the host machine's available resources to prevent saturation.
- Runtime health checks to verify that both the API and the testing tool containers stay alive during the testing sessions.
- Integrity checks on completed testing sessions and re-execution of any that are found to be corrupted.
- Compilation of comprehensive reports for each experimental testing session, as well as a cumulative report summarizing all the testing sessions.

### Included tools and APIs

#### Tools (in alphabetic order)
- ARAT-RL
- DeepREST
- MoREST
- RESTler
- RestTestGen
- Schemathesis

#### APIs (in alphabetic order)
- Blog
- Features Service
- Genome Nexus
- LangaugeTool
- Market
- NCS
- Person Controller
- Project Tracking System
- REST Countries
- SCS
- User Management

### Changelog

#### Version 2.0.1
- Added `TIME_BUDGET` (in minutes) and `HOST` env variables support for future use.
- Fixed build script that in some cases provided wrong path to Docker build context.

#### Version 2.0.0
- Full Docker support: now also RESTgym itself executes within a Docker container, without requiring Python and dependencies to be installed in the host machine or in a Python virtual environment. **Docker is now the only requirement.**
- Testing time budget can now be configured via the configuration file.
- stdout and stderr of API and tool containers are now stored to log files.
- Only runs that have passed the verification are now used in the analysis.
- Added progress bar in long-executing scripts.
- Improved clarity of messages.
- Fixed file permission issues that prevented the RESTgym to access some of the results in the `results/` folder.
- Fixed a crash caused by the presence of `.DS_Store` files (macOS system files).

### Requirements
- Linux or macOS operating systems. RESTgym has been tested on Ubuntu 22.04, Ubuntu 24.04, and macOS 26.1.
- Docker.

### Configuration

Most configuration settings for RESTgym are prompted at runtime via the command line. However, some global settings can be specified in YAML configuration files. 
Specifically, RESTgym includes a general configuration file named `restgym-config.yml`, located in the root directory.

In this file, you can define three parameters:
- the minimum number of CPUs and the minimum amount of RAM required on your system before initiating a testing session. These values are utilized for parallelization and further test sessions are executed in parallel as long the specified resources are available (default: 4 CPUs and 4 GB of RAM).
- The time budget for each testing sessions in minutes (default: 60 minutes).

The RESTgym configuration file is in the following format:

```yaml
minimum_cpus: 4
minimum_ram_gb: 4
time_budget_mins: 60
```

Additionally, each API and tool can be enabled through a configuration file located in their respective directories. Configuration files for APIs are named `restgym-api-config.yml`, while those for tools are named `restgym-tool-config.yml`.

The content is the following:

```yaml
enabled: true
```

Set `enabled` to `false` if you want to exclude and API or a tool from the experiment.

By default, only two tools (DeepREST and RESTler) and two APIs (Market and SCS) are enabled to facilitate low-resource consumption dry run of experiments.

### Usage

Make the RESTgym shell script executable with:

```
sudo chmod +x restgym.sh
```

Please follow the steps below to conduct your experiment:

#### 1. Building or downloading Docker images

```
./restgym.sh b
```

Also `./restgym.sh build-images`. Former, now deprecated, `build.py`.

This script manages the building of Docker images for the APIs and testing tools. It builds local images (if available) and downloads our pre-built images from our repositories on Docker Hub ([https://hub.docker.com/u/restgym](https://hub.docker.com/u/restgym)).

**Output:** Docker images of enabled tools and APIs are build in the host system.

#### 2. Experiment execution

```
./restgym.sh l
```

Also `./restgym.sh launch-experiment`. Former, now deprecated, `run.py`.

This script orchestrates the execution of testing sessions for each testing tool across all APIs, allowing for multiple repetitions. The executions are parallelized to minimize overall execution time. Upon launch, the script prompts the user for the number of repetitions for each testing tool and API configuration, then executes the remaining sessions. For example, if a previous execution of the script was set to run 3 repetitions and the user relaunches the script specifying a total of 5 repetitions, the script will only execute the 2 remaining repetitions.

**Output:** Experimental testing sessions are executed in containers and results are stored in the `results/` folder.

#### 3. Integrity verification of experiment raw data

```
./restgym.sh v
```

Also `./restgym.sh verify-data`. Former, now deprecated, `check.py`.

This script check the integrity of the executed testing sessions. It ensures that metrics were consistently collected throughout the experiment, verifies that an adequate number of requests were recorded by the proxy, and confirms that coverage samples are always increasing (as coverage cannot decrease).

In the event of a corrupted execution, the user will be prompted to decide whether to delete the execution. If the user chooses to delete it, they should re-execute the removed session using the `run.py` script.

#### 4. Analyze raw data and extract cumulative results

```
./restgym.sh a
```

Also `./restgym.sh analyze-data`. Former, now deprecated, `process_results.py`.

This script processes the raw data to extract measures of effectiveness and efficiency, generating a comprehensive report for each execution, along with a cumulative report that summarizes all executions.

**Output:** Comprehensive results are generated for each experimental testing session based on raw data and are saved in a JSON file located in the appropriate sub-folder within the `results/` directory. Additionally, a cumulative summary of all experimental execution results is stored in CSV format in the main `results/` folder.

#### Force stop

To force the stop and remove all the running containers related to RESTgym, please run: `./restgym.sh s` or `./restgym.sh stop`

#### Remove

To remove the RESTgym Docker image from the host machine, please run `./restgym.sh r` or `./restgym.sh remove`

### Extending RESTgym with your testing tool or API

As an extensible framework, users of RESTgym can contribute with their on testing tool(s) or API(s). If you wish to add your tool or API, please refer to the READMEs in the two directories `apis/#api-template` and `tools/#tool-template`.