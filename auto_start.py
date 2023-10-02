import subprocess
import time

while True:
    try:
        # Attempt to start main.py
        process = subprocess.Popen(['python', 'main.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait for the process to finish
        stdout, stderr = process.communicate()

        # Check the return code of the process
        return_code = process.returncode

        if return_code == 0:
            print("main.py executed successfully.")
        else:
            print(f"main.py exited with an error. Return code: {return_code}")
            print("Stdout:")
            print(stdout.decode('utf-8'))
            print("Stderr:")
            print(stderr.decode('utf-8'))

    except Exception as e:
        print(f"An exception occurred: {e}")

    # Wait for a while before restarting the script
    time.sleep(10)  # Adjust the sleep duration as needed
