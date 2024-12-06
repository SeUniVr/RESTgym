import common
import socket
import random
import threading
import time
import psutil
import sys
import os



# Check if a TCP port is free
def check_tcp_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return not s.connect_ex(('localhost', port)) == 0
    
# Get random free TCP port
def get_random_free_tcp_port():
    remaining_attempts = 1000
    while remaining_attempts > 0:
        candidate_port = random.randrange(10_000, 60_000)
        if check_tcp_port(candidate_port):
            return candidate_port
        remaining_attempts -= 1
    print("ERROR: could not find a free TCP port for the API.")
    sys.exit(1)

# Compute the remaining runs to execute
def compute_remaining_runs(desired_runs):
    remaining_runs = []
    apis = common.get_apis()
    tools = common.get_tools()
    for api in apis:
        for tool in tools:
            try:
                base_dir = f"./results/{api}/{tool}"
                subdirs = os.listdir(base_dir)
                count = 0
                for subdir in subdirs:
                    if os.path.exists(f"{base_dir}/{subdir}/completed.txt"):
                        count += 1
                while count < desired_runs:
                    remaining_runs.append({'api': api, 'tool': tool})
                    count += 1
            except:
                for _ in range(desired_runs):
                    remaining_runs.append({'api': api, 'tool': tool})
    return remaining_runs

# Verify Docker images have been built
def check_docker_images(remaining_runs):
    images = set()
    missing_images = []
    for remaining_run in remaining_runs:
        images.add(remaining_run['tool'])
        images.add(remaining_run['api'])
    for image in images:
        try:
            common.DOCKER_CLIENT.images.get(common.DOCKER_PREFIX+image)
        except:
            missing_images.append(image)
    return missing_images

# Filter out runs with missing images
def filter_runs_with_missing_images(remaining_runs, missing_images):
    filtered_remaining_runs = []
    for remaining_run in remaining_runs:
        if remaining_run['tool'] not in missing_images and remaining_run['api'] not in missing_images:
            filtered_remaining_runs.append(remaining_run)
    return filtered_remaining_runs

# Check if there are enough resources for another concurrent run
def check_resources():
    REQUIRED_RAM = 32 * 1024 * 1024 * 1024      # 32GB
    REQUIRED_CPUS = 14
    available_ram = getattr(psutil.virtual_memory(), 'available')
    available_cpus = (1 - (psutil.cpu_percent() / 100)) * psutil.cpu_count()
    return available_ram > REQUIRED_RAM and available_cpus > REQUIRED_CPUS

# Deeper check of resources (10 checks each second)
def deep_check_resources():
    for _ in range(10):
        if check_resources() == False:
            return False
        time.sleep(1)
    return True

# Execute an experiment run
def launch_run(api, tool, run_count, total_runs):

    attempts = 5
    successfully_completed = False

    while attempts > 0 and not successfully_completed:

        attempts -= 1
        error_occurred = False
        run = 'run-' + time.strftime('%Y%m%d-%H%M%S')
        results_path = f'./results/{api}/{tool}/{run}'
        ports = {'9090/tcp': get_random_free_tcp_port()}
        env = {
            'API': api,
            'TOOL': tool,
            'RUN': run,
            'PORT': ports['9090/tcp']
        }

        os.makedirs(results_path, exist_ok=True, mode=0o777)

        message = 'START' if attempts == 4 else 'RETRY'

        print(f" => [{message}] ({run_count}/{total_runs}) Running {tool} on {api} ({run}) with API on port {ports['9090/tcp']}.")
        with open(f'{results_path}/started.txt', 'a') as f:
            f.write(f'Run started on {time.ctime()}.\n')

        api_container_name = f'{api}_for_{tool}_{run}'
        tool_container_name = f'{tool}_for_{api}_{run}'

        # Verify Docker images have been built
        try:
            common.DOCKER_CLIENT.images.get(common.DOCKER_PREFIX+remaining_run['api'])
            common.DOCKER_CLIENT.images.get(common.DOCKER_PREFIX+remaining_run['tool'])
        except:
            print(f" => [ERROR] ({run_count}/{total_runs}) Execution failed for {remaining_run['tool']} on {remaining_run['api']}. Missing Docker image(s). Have you built them?")
            with open(f'{results_path}/errors.txt', 'a') as f:
                f.write(f"Docker image(s) not found for API ({remaining_run['api']}) or tool ({remaining_run['tool']}).\n\n")
            error_occurred = True

        # Start API
        if not error_occurred:
            try:
                api_container = common.DOCKER_CLIENT.containers.run(
                    image=f'{common.DOCKER_PREFIX}{api}',
                    name=api_container_name,
                    remove=True,
                    environment=env,
                    ports=ports,
                    volumes=[f'{os.getcwd()}/results/:/results/'],
                    mem_limit="16g",
                    nano_cpus=8_000_000_000,
                    user='root',
                    detach=True
                    )
            except Exception as e:
                with open(f'{results_path}/errors.txt', 'a') as f:
                    f.write(f"Could not start API ({api}) container.\n{e}\n\n")
                error_occurred = True
        
        # Wait 45 seconds for the API to start
        if not error_occurred:
            time.sleep(45)
        else:
            time.sleep(2)
        
        # Start tool
        if not error_occurred:
            try:
                tool_container = common.DOCKER_CLIENT.containers.run(
                    image=f'{common.DOCKER_PREFIX}{tool}',
                    name=tool_container_name,
                    remove=True,
                    environment=env,
                    privileged=True,
                    network_mode='host',
                    mem_limit="16gb",
                    nano_cpus=8_000_000_000,
                    detach=True
                    )
                time.sleep(1)
            except Exception as e:
                api_container.stop()
                with open(f'{results_path}/errors.txt', 'a') as f:
                    f.write(f"Could not start tool ({tool}) container.\n{e}\n\n")
                error_occurred = True


        # Perform a health check of containers each minute, for 60 times
        if not error_occurred:
            for minute in range(1, 61):
                time.sleep(60)
                try:
                    api_container.reload()
                    if api_container.status == 'exited':
                        raise Exception("Container exited")
                # If the container was removed or it exited
                except Exception as e:
                    print(f" => [ERROR] ({run_count}/{total_runs}) API container stopped.")
                    with open(f'{results_path}/errors.txt', 'a') as f:
                        f.write(f"API container not running at minute {minute}. Aborting.\n{e}\n\n")
                    try:
                        tool_container.stop()
                    except:
                        pass
                    error_occurred = True
                    break
                try:
                    tool_container.reload()
                    if tool_container.status == 'exited':
                        raise Exception("Container exited")
                # If the container was removed or it exited
                except Exception as e:
                    print(f" => [ERROR] ({run_count}/{total_runs}) Tool container stopped.")
                    with open(f'{results_path}/errors.txt', 'a') as f:
                        f.write(f"Tool container not running at minute {minute}. Aborting.\n{e}\n\n")
                    try:
                        api_container.stop()
                    except:
                        pass
                    error_occurred = True
                    break
        
        # Stop tool container
        if not error_occurred:
            try:
                tool_container.stop()
            except Exception as e:
                error_occurred = True
                with open(f'{results_path}/errors.txt', 'a') as f:
                    f.write(f'Could not stop tool ({tool}) container. It possibly crashed.\n{e}\n\n')
                try:
                    api_container.stop()
                except:
                    pass
        
        # Wait 5 seconds to let the API container store the database
        if not error_occurred:
            time.sleep(5)

        # Stop API container
        if not error_occurred:
            try:
                api_container.stop()
            except Exception as e:
                error_occurred = True
                with open(f'{results_path}/errors.txt', 'a') as f:
                    f.write(f'Could not stop API ({api}) container. It possibly crashed.\n{e}\n\n')

        # Final stages
        if not error_occurred:
            successfully_completed = True
            with open(f'{results_path}/completed.txt', 'a') as f:
                f.write(f'Run completed on {time.ctime()}.\n')
            print(f" => [-END-] ({run_count}/{total_runs}) Run of {tool} on {api} ({run}) completed.")
        else:
            time.sleep(2)
            if attempts == 0:
                print(f" => [ERROR] ({run_count}/{total_runs}) Run of {tool} on {api} ({run}) terminated with errors.")

# Main
if __name__ == "__main__":
    common.welcome()
    print("This is the run module. It will run up to 20 repetitions of the experiment for each tool and API.")
    try:
        desired_runs = int(input("How many runs? [1-20]: "))
    except:
        print("Please specify an whole number.")
        sys.exit(1)
    if desired_runs < 1 or desired_runs > 20:
        print("Please specify a number in the range 1-20.")
        sys.exit(1)
    
    remaining_runs = compute_remaining_runs(desired_runs)
    
    # Uncomment next line to launch a manual subset of runs
    #remaining_runs = [{'api': 'market', 'tool': 'restler'}]
    
    missing_images = check_docker_images(remaining_runs)
    if len(missing_images) > 0:
        filtered_remaining_runs = filter_runs_with_missing_images(remaining_runs, missing_images)
        print(f"Some Docker images required for the experiment have not been built. Skipping experiment runs that involve these images. Only {len(filtered_remaining_runs)} out of {len(remaining_runs)} runs can be launched.")
        remaining_runs = filtered_remaining_runs
    else:
        print(f"Runs planned for execution: {len(remaining_runs)}.")

    total_runs = len(remaining_runs)
    run_count = 0
    
    input("Press ENTER to start the execution of the experiment (or CTRL+C to cancel)...")

    while len(remaining_runs) > 0:

        run_count += 1

        # Pick random run
        remaining_run = remaining_runs.pop(random.randrange(len(remaining_runs)))

        # Stop until resources are available
        notify_no_resources = True
        while not deep_check_resources():
            if notify_no_resources:
                print(f" => [-WAIT] ({run_count}/{total_runs}) Waiting for system resources to be released.")
                notify_no_resources = False
            time.sleep(30)

        # Launch run in separate thread
        run_thread = threading.Thread(
            target=launch_run,
            args=(remaining_run['api'], remaining_run['tool'], run_count, total_runs)
            )
        run_thread.start()

        # If not last run, wait 60 seconds before launching next
        if len(remaining_runs) > 0:
            time.sleep(60)