# Contributing with a new tool

This README provides instructions for adding a new tool to RESTgym.

Since in RESTgym tools run within a Docker container, you will need to package the tool into a Docker image using a `Dockerfile`. This image should include all necessary dependencies for the tool's execution and, if required, a script that launches the tool with the proper configuration. The tool should execute indefinitely, so, if this is not the default behavior of the tool, we recommend to run the tool within a while true loop (more details about this below). In this directory (i.e., `tools/#tool-template/`), you will find the `Dockerfile` and other files used to build the Docker image for RestTestGen. You can use these as a starting point for creating the Docker image for your own tool.

## The tool directory
Each tool should be stored in a directory under `tools/`, and it is recommended that the directory name reflects the tool's name. For example, RestTestGen is located in the `tools/resttestgen/` directory. **Keep this directory name in mind, as it will be used by RESTgym in scripts and other components. We will refer to this name as 'Tool slug' now on.**

The content of the tool directory should be structured as follows:
- The executable or the source code of the tool (in this case, we have the executable `resttestgen.jar`).
- The configuration file for the tool, if required (for example, the `rtg-config.yml` is used to configure RestTestGen).
- A configuration scripts that adjusts the configuration for the tool according to the API being tested, setting the path to the API specification and the port on which the API is reachable. In this example, we use the `config.sh` script. The API being tested and the port being used are taken from the environment variables `API` and `PORT`, respectively.
- The tool configuration file for RESTgym, named `restgym-tool-config.yml`. Currently, the only supported configuration is `enabled: true/false` to enable or disable the tool in RESTgym.
- The `Dockerfile`, used to build the Docker image for the tool. See the instructions in the next section.

## The Dockerfile
The `Dockerfile` is used to build the Docker image for the tool. It contains commands to install the tool along with its required dependencies and libraries. 

As an example, we will refer to the `Dockerfile` contained in this directory. Refer to this example to create the `Dockerfile` for your tool. If you need further assistance, please feel free to open an issue.

### Line 1: The starting image
In this case, our tool image will be built on top of Ubuntu 22.04. However, you can use lighter images. Additionally, if your tool is already available as a Docker image, you can start from that image and simply include the configuration scripts, if required.

### Line 3: Preparation of internal directories
Directories to contain the tool files in the image

### Lines 4-6: Installation of required packages
These lines install the required packages to run the tool (e.g., the JDK in this case).

### Line 8: Copy of the tool data into the image
This line copies all the tool directory into the image at the location `/tool/`.

### Line 9: Copy of the API specifications into the image
This line copies the API specification for all APIs into the Docker image.

### Lines 11-13: Container execution command
The last command of a `Dockerfile` starting with `CMD` instructs Docker with what command to execute when the container is launched.
- `sh /tool/config.sh` dynamically configures the tool for the current testing session, by providing the correct API specification of the API under test and the port on which the API is reachable.
- `cd /tool` changes the working directory to the tool's directory.
- `while true; do java -jar resttestgen.jar; done` launches RestTestGen indefinitely. Since the `java` command is encapsulated into a while true loop, if the tool execution terminates, the tool is re-launched indefinitely. RESTgym will take care of killing the container when the testing time budget has ended.

## Environment variables

The tool should be configurable via the following environment variables:
- `HOST`: the hostname or IP address of the machine in which the API is running [**mandatory**].
- `PORT`: the TCP port to which the API is listening [**mandatory**].
- `TIME_BUDGET`: the time budget <u>in minutes</u> of the testing session being executed. We recommend the tool to run indefinitely in the container using a while true loop. This variable is only useful if the tool's strategy depends on the time budget, such that the tool is configured to maximize its effectiveness given the time budget. [**optional**]

If the tool does not support host and port overriding, but uses the server documented in the specification, we suggest to write an entrypoint script to overwrite the server in the specification with `http://$HOST:$PORT/`.
