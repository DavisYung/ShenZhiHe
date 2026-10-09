import json, os, re, sys, urllib.request, zipfile, io

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WHEELS = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\wheels"
TARGET = r"C:\Users\guomi\OneDrive\文件\deepseek-harness\default-workspace\f6chem\pylibs3"
os.makedirs(WHEELS, exist_ok=True)
os.makedirs(TARGET, exist_ok=True)

PKGS = ["rapidocr-onnxruntime", "pyclipper", "opencv-python", "Shapely",
        "PyYAML", "onnxruntime", "tqdm"]

PY = "cp312"
PLATS = ["win_amd64", "any"]


def fetch(pkg):
    url = "https://pypi.org/pypi/%s/json" % pkg
    return json.load(urllib.request.urlopen(url, timeout=60))


def pick(d):
    urls = d["urls"]
    # 1) cp312 win_amd64, 2) cp312 abi3 win_amd64, 3) py3-none-any, 4) py2.py3-none-any
    def score(u):
        f = u["filename"]
        if not f.endswith(".whl"):
            return -1
        if "win_amd64" in f:
            if PY + "-cp312" in f:
                return 100
            if "cp312-abi3" in f:
                return 90
            if "cp3" in f:
                return 70
            return 10
        if f.endswith("-none-any.whl"):
            if "py3-none-any" in f:
                return 60
            if "py2.py3-none-any" in f:
                return 50
            if "py2-none-any" in f:
                return 5
            return 40
        return -1

    best = max(urls, key=score)
    if score(best) < 0:
        raise RuntimeError("no wheel for %s" % d["info"]["name"])
    return best


def extract(path):
    with zipfile.ZipFile(path) as z:
        z.extractall(TARGET)


done = []
for p in PKGS:
    d = fetch(p)
    u = pick(d)
    fn = u["filename"]
    dst = os.path.join(WHEELS, fn)
    if not os.path.exists(dst):
        print("downloading", fn, u["size"], flush=True)
        req = urllib.request.Request(u["url"], headers={"User-Agent": "pip/24"})
        data = urllib.request.urlopen(req, timeout=300).read()
        with open(dst, "wb") as f:
            f.write(data)
    else:
        print("cached", fn, flush=True)
    extract(dst)
    done.append(fn)

# clean dist-info RECORD issues are fine for imports
print("OK installed:", ", ".join(done))
