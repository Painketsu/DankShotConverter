import sys, subprocess, requests, os, time, pickle, random
from pathlib import Path

path = sys.argv[1]
parent = Path(path).parents[0]
name = Path(path).stem
output = f"{parent}\{name}.ts"
print(f"Downloading to {output}...")

counter = 0
random_string = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=5)) # random string to support multiple script runs
temp_name = f"{parent}\\temp_{counter}_{random_string}.ts"
failed = []
with open(path) as pa:
    with open(temp_name, 'wb') as f:
        for line in pa:
            #time.sleep(random.uniform(0, 0.2)) # depending on site call limits this might be useful but haven't needed it yet
            segment_url = line
            try:
                response = requests.get(segment_url, timeout=5)
            except requests.exceptions.Timeout:
                print("Request timed out, retrying...")
                try:
                    response = requests.get(segment_url, timeout=5)
                except requests.exceptions.Timeout:
                    print(f"Request timed out, skipping {counter}.")
                    continue
            #print(response.status_code)
            if response.status_code != 200:
                print(f"Got {response.status_code} status from this segment, skipping it | {response.content}")
                failed.append(segment_url)
                continue
            counter+=1
            print(f"Downloading segment {counter}...")
            f.write(response.content)
            f.flush()
            os.fsync(f.fileno())
        if len(failed) > 0:
            with open(f"{Path(path).stem}_FailedSegments.log", "wb") as f:
                pickle.dump(failed, f)
print('Video saved to:', temp_name)
print(f'Converting {temp_name} to {output} ')
command = ["ffmpeg", "-i", temp_name, "-map", "0", "-c", "copy", output]
subprocess.call(command)
os.remove(temp_name)
try:
    os.startfile(output)
except:
    print("failed..!")
else:
    os.remove(path)
