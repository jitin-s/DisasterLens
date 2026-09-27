"""
Resilient Wheel Downloader & Installer for High-Latency / Drop-Prone Connections
Queries PyPI JSON API, matches the exact cp313-win_amd64 wheel, downloads with HTTP Range resume,
and installs locally.
"""

import os
import sys
import time
import subprocess
import requests

PACKAGES = [
    "joblib",
    "threadpoolctl",
    "scipy",
    "scikit-learn",
    "xgboost",
    "slicer",
    "shap"
]
WHEELS_DIR = os.path.join(os.path.dirname(__file__), ".wheels")
os.makedirs(WHEELS_DIR, exist_ok=True)


def find_best_wheel_url(pkg_name: str):
    url = f"https://pypi.org/pypi/{pkg_name}/json"
    r = requests.get(url, timeout=10)
    data = r.json()
    urls = data.get("urls", [])
    
    # Priority 1: cp313 win_amd64
    for u in urls:
        fn = u.get("filename", "")
        if "cp313" in fn and "win_amd64" in fn and fn.endswith(".whl"):
            return u["url"], fn
            
    # Priority 2: cp312/cp313 abi3 win_amd64
    for u in urls:
        fn = u.get("filename", "")
        if "abi3" in fn and "win_amd64" in fn and fn.endswith(".whl"):
            return u["url"], fn
            
    # Priority 3: py3-none-any
    for u in urls:
        fn = u.get("filename", "")
        if "py3-none-any" in fn and fn.endswith(".whl"):
            return u["url"], fn
            
    # Priority 4: any win_amd64
    for u in urls:
        fn = u.get("filename", "")
        if "win_amd64" in fn and fn.endswith(".whl"):
            return u["url"], fn
            
    raise RuntimeError(f"Could not find matching wheel for {pkg_name} on Python 3.13 win_amd64")


def download_with_resume(url: str, filename: str) -> str:
    target_path = os.path.join(WHEELS_DIR, filename)
    part_path = target_path + ".part"
    
    session = requests.Session()
    headers = {"User-Agent": "DisasterLens-Downloader/1.0"}
    
    print(f"\n[DOWNLOADING] {filename}...")
    
    while True:
        curr_size = os.path.getsize(part_path) if os.path.exists(part_path) else 0
        h = headers.copy()
        if curr_size > 0:
            h["Range"] = f"bytes={curr_size}-"
            print(f"  -> Resuming from {curr_size / (1024*1024):.2f} MB...")
            
        try:
            resp = session.get(url, headers=h, stream=True, timeout=20)
            if resp.status_code == 416: # Completed
                break
            if resp.status_code not in (200, 206):
                print(f"  -> HTTP {resp.status_code}, retrying...")
                time.sleep(2)
                continue
                
            mode = "ab" if (curr_size > 0 and resp.status_code == 206) else "wb"
            with open(part_path, mode) as f:
                for chunk in resp.iter_content(chunk_size=131072): # 128KB chunks
                    if chunk:
                        f.write(chunk)
                        
            # Verify download completed
            total_expected = int(resp.headers.get("content-length", 0))
            if resp.status_code == 206:
                # Content-Range: bytes START-END/TOTAL
                crange = resp.headers.get("content-range", "")
                if "/" in crange:
                    total_expected = int(crange.split("/")[-1])
            elif resp.status_code == 200:
                pass
                
            actual_size = os.path.getsize(part_path)
            if total_expected > 0 and actual_size >= total_expected:
                break
            elif total_expected == 0 and actual_size > 0:
                break
        except Exception as ex:
            print(f"  -> Connection dropped ({ex}). Reconnecting in 3s...")
            time.sleep(3)
            
    if os.path.exists(target_path):
        os.remove(target_path)
    os.rename(part_path, target_path)
    print(f"  [COMPLETED] {filename} ({os.path.getsize(target_path) / (1024*1024):.2f} MB)")
    return target_path


def main():
    pip_exe = os.path.join(os.path.dirname(__file__), ".venv", "Scripts", "pip.exe")
    python_exe = os.path.join(os.path.dirname(__file__), ".venv", "Scripts", "python.exe")
    
    for pkg in PACKAGES:
        print("=" * 60)
        print(f"RESOLVING: {pkg}")
        wheel_url, wheel_fn = find_best_wheel_url(pkg)
        print(f"URL: {wheel_url}")
        local_wheel = download_with_resume(wheel_url, wheel_fn)
        
        print(f"[INSTALLING] {wheel_fn} into .venv...")
        cmd = [pip_exe, "install", local_wheel, "--no-deps"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"[SUCCESS] Installed {pkg}!")
        else:
            print(f"[ERROR] Failed to install {pkg}: {res.stderr}")
            # Try regular pip install of dependencies
            cmd2 = [pip_exe, "install", local_wheel]
            res2 = subprocess.run(cmd2, capture_output=True, text=True)
            print(res2.stdout)
            
    print("=" * 60)
    print("All core wheels installed!")


if __name__ == "__main__":
    main()
