from pathlib import Path
import json, sys, pandas as pd
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from finsight.data.generator import write_csv_bundle
from finsight.analytics.baseline import investigate_crm_routing_change
if __name__=="__main__":
    p=ROOT/"data/generated/sales_activity.csv"
    if not p.exists(): write_csv_bundle(ROOT/"data/generated")
    df=pd.read_csv(p,parse_dates=["lead_created_at"])
    print(json.dumps(investigate_crm_routing_change(df),indent=2,ensure_ascii=False))
