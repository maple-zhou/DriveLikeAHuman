import os
import glob


files = glob.glob("log/*",recursive=True)

for f in files:
    os.remove(f)

files = glob.glob("results-db/*",recursive=True)

for f in files:
    os.remove(f)

files = glob.glob("results-video/*",recursive=True)

for f in files:
    os.remove(f)
    
