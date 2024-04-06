import os
import threading

threading._start_new_thread(os.system, (f'python -u "{os.getcwd()}/homeHub.py"',))