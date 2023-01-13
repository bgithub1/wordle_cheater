
import os, glob, sys
venv_name = sys.argv[1]
user = os.path.expanduser('~')
files = glob.glob(user+'/V*/' + venv_name +  '/bin/activate', recursive=True)
if len(files)>0:
   print(files[0])