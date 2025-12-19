import common
import os
import sys
import math
import multiprocessing
import concurrent.futures



def clean_builds():
    print("Removing old images...")
    images = common.get_apis() + common.get_tools()
    for image in images:
        print(f" => {image}: ", end='')
        try:
            common.DOCKER_CLIENT.images.remove(image=common.DOCKER_PREFIX+image)
            print("Removed.")
        except:
            print("Image not found. Skipping.")

def build(image):
    try:
        common.DOCKER_CLIENT.images.get(common.DOCKER_PREFIX+image)
        print(f" => {image}: Already available in the local image registry.")
    except:
        sub_path = 'tools' if image in common.get_tools() else 'apis'
        path = f"{common.RESTGYM_BASE_DIR}/{sub_path}/{image}"
        print(f" => {image}: Building...")
        if os.path.exists(f"{path}/Dockerfile"):
            try:
                common.DOCKER_CLIENT.images.build(
                    path=f'{common.RESTGYM_BASE_DIR}',
                    dockerfile=f'{path}/Dockerfile',
                    tag=common.DOCKER_PREFIX+image,
                    rm=True,
                    forcerm=True
                )
                print(f" => {image}: Done.")
            except Exception as e: 
                print(f" => {image}: An error occurred during the build. Skipping.")
                print(f" => {image}: {e}")
        else:
            print(f" => {image}: Dockerfile not found. Skipping.")

def build_all():
    print("Building images...")
    images = common.get_apis() + common.get_tools()

    threads = math.floor(multiprocessing.cpu_count() * 0.9)

    with concurrent.futures.ThreadPoolExecutor(threads) as executor:
        for image in images:
            build(image)

# Main
if __name__ == "__main__":
    common.welcome()
    print("This is the build module. It can build Docker images for all APIs and tools, and clean them.")
    print("[1] Clean and build images")
    print("[2] Build images")
    print("[3] Clean images")
    choice = input("Your choice: ")
    if choice != '1' and choice != '2' and choice != '3':
        print("Invalid choice!")
        sys.exit(1)
    if choice == '1' or choice == '3':
        clean_builds()
    if choice == '1' or choice == '2':
        build_all()
    print("Completed.")
