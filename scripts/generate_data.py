from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from fitzsight.data.generator import write_csv_bundle
if __name__=="__main__":
    for n,p in write_csv_bundle(ROOT/"data/generated").items(): print(f"{n:18s} -> {p.relative_to(ROOT)}")
