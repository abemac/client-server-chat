import subprocess
import os
subprocess.Popen(['python3','client.py','abraham'])
subprocess.Popen(['python3','client.py','bob'])
os.system('python3 server.py')
