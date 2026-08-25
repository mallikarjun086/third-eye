import os
import sys
import tarfile
import urllib.request

def download_lfw_sample(target_dir):
    os.makedirs(target_dir, exist_ok=True)
    url = "http://vis-www.cs.umass.edu/lfw/lfw-a.tgz" # Public subset 'A' of LFW dataset
    tar_path = os.path.join(target_dir, "lfw-a.tgz")
    
    print(f"Downloading public face dataset subset from: {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response, open(tar_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print(f"Downloaded archive successfully ({len(data)} bytes). Extracting...")
        
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=target_dir)
        print("Extraction complete!")
        return True, len(data)
    except Exception as e:
        print(f"Download or extraction notice: {e}")
        return False, str(e)

if __name__ == "__main__":
    target = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "lfw"))
    download_lfw_sample(target)
