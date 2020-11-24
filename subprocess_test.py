import  subprocess
import  shlex
command = "ls"
process = subprocess.Popen(command, stdout = subprocess.PIPE, cwd="/home/vivek/Documents/Johnnette_tech/gcs/Firmware", stderr=subprocess.PIPE, shell=True)
#process = subprocess.Popen(shlex.split(command), stdout = subprocess.PIPE, shell=False)
while process.poll() is None:
    output = process.stdout.readline()
    if output == '' and process.poll() is not None:
        break
    if output:
        print(output.strip())
error = process.stderr.read()
if error:
    print(error)
command = "ls"
process = subprocess.Popen(command, stdout = subprocess.PIPE, cwd="/home/vivek/Documents/Johnnette_tech/gcs/Firmware", stderr=subprocess.PIPE, shell=True)
while process.poll() is None:
    output = process.stdout.readline()
    if output == '' and process.poll() is not None:
        break
    if output:
        print(output.strip())
    #rc = process.poll()
error = process.stderr.read()
if error:
    print(error)
output = process.communicate()
