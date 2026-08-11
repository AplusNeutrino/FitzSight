from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
from .scenarios import CRM_ROUTING_SCENARIO

REGIONS = ("Europe", "Asia", "Middle East", "Americas", "Oceania")
CHANNELS = ("Organic", "Paid Search", "Referral", "Affiliate", "Events")
TEAMS = ("Team A", "Team B", "Team C", "Team D", "Team E")

@dataclass(frozen=True)
class GeneratorConfig:
    seed: int = 20260811
    n_customers: int = 20_000
    n_salespeople: int = 50
    start_date: str = "2026-01-01"
    end_date: str = "2026-08-10"

def _dates(rng, n, start, end):
    days = (end.normalize() - start.normalize()).days
    return start + pd.to_timedelta(rng.integers(0, days + 1, n), unit="D") + pd.to_timedelta(rng.integers(0, 86400, n), unit="s")

def generate_salespeople(cfg, rng):
    ids = [f"SP{i:03d}" for i in range(1, cfg.n_salespeople + 1)]
    # Spread every team across regions so affected and control teams coexist in Europe.
    combinations = [(team, region) for region in REGIONS for team in TEAMS]
    repeated = [combinations[i % len(combinations)] for i in range(cfg.n_salespeople)]
    teams = np.array([x[0] for x in repeated])
    regions = np.array([x[1] for x in repeated])
    return pd.DataFrame({"salesperson_id": ids, "team_id": teams, "region": regions,
                         "tenure_months": rng.integers(2, 61, cfg.n_salespeople)})

def generate_customers(cfg, rng, sp):
    reg_dates = _dates(rng, cfg.n_customers, pd.Timestamp(cfg.start_date), pd.Timestamp(cfg.end_date))
    regions = rng.choice(REGIONS, cfg.n_customers, p=[.34,.20,.16,.20,.10])
    channels = rng.choice(CHANNELS, cfg.n_customers, p=[.28,.24,.18,.20,.10])
    assigned, teams = [], []
    for r in regions:
        pool = sp[sp.region == r]
        row = pool.iloc[int(rng.integers(0, len(pool)))] if len(pool) else sp.iloc[int(rng.integers(0, len(sp)))]
        assigned.append(row.salesperson_id); teams.append(row.team_id)
    value = rng.lognormal(7.3, .9, cfg.n_customers)
    seg = pd.cut(value, [-np.inf,900,1800,4000,np.inf], labels=["Low","Core","Growth","High Value"]).astype(str)
    return pd.DataFrame({"customer_id":[f"C{i:06d}" for i in range(1,cfg.n_customers+1)],
        "registration_date":reg_dates,"region":regions,"country":[f"{r} Market" for r in regions],
        "acquisition_channel":channels,"assigned_salesperson":assigned,"assigned_team":teams,
        "customer_segment_gt":seg})

def generate_sales_activity(cfg, rng, c):
    s = CRM_ROUTING_SCENARIO
    d = c[["customer_id","registration_date","region","assigned_salesperson","assigned_team","acquisition_channel"]].copy()
    d["lead_created_at"] = d.registration_date
    response = rng.lognormal(np.log(95), .55, len(d))
    affected = (d.region.eq(s.region) & d.assigned_team.isin(s.affected_teams) & (d.registration_date.dt.date >= s.change_date))
    response[affected.to_numpy()] *= s.response_time_multiplier
    d["response_time_minutes"] = np.round(response,1)
    bonus = d.acquisition_channel.map({"Organic":.03,"Paid Search":-.02,"Referral":.06,"Affiliate":-.01,"Events":.02}).to_numpy()
    penalty = np.clip((d.response_time_minutes.to_numpy()-90)/900, -.02,.18)
    p = np.clip(.24 + bonus - penalty, .04,.48)
    p[affected.to_numpy()] *= s.conversion_probability_multiplier
    d["converted_ftd"] = rng.random(len(d)) < p
    d["contacted"] = rng.random(len(d)) < np.clip(.93 - d.response_time_minutes.to_numpy()/1500,.65,.95)
    d["qualified"] = d.contacted & (rng.random(len(d)) < .58)
    d["affected_by_crm_change_gt"] = affected
    d["activity_id"] = [f"A{i:06d}" for i in range(1,len(d)+1)]
    return d[["activity_id","customer_id","lead_created_at","region","assigned_salesperson","assigned_team","acquisition_channel","response_time_minutes","contacted","qualified","converted_ftd","affected_by_crm_change_gt"]]

def generate_deposits(cfg, rng, c, a):
    j = c[["customer_id","registration_date","customer_segment_gt"]].merge(a[["customer_id","converted_ftd"]], on="customer_id")
    scale={"Low":250.,"Core":650.,"Growth":1500.,"High Value":5000.}; rows=[]; i=1
    for r in j[j.converted_ftd].itertuples(index=False):
        for _ in range(int(rng.integers(1,5))):
            ts=pd.Timestamp(r.registration_date)+pd.Timedelta(days=int(rng.integers(0,75)))
            if ts > pd.Timestamp(cfg.end_date)+pd.Timedelta(days=1): continue
            rows.append({"deposit_id":f"D{i:07d}","customer_id":r.customer_id,"timestamp":ts,
                         "amount":round(float(rng.lognormal(np.log(scale[str(r.customer_segment_gt)]),.55)),2),
                         "currency":"USD","method":rng.choice(["Card","Bank Transfer","E-wallet"],p=[.45,.35,.20]),"status":"completed"}); i+=1
    return pd.DataFrame(rows)

def generate_withdrawals(cfg, rng, c, dep):
    if dep.empty: return pd.DataFrame(columns=["withdrawal_id","customer_id","timestamp","amount","currency","status"])
    t=dep.groupby("customer_id",as_index=False).amount.sum(); rows=[]; i=1
    maxday=(pd.Timestamp(cfg.end_date)-pd.Timestamp(cfg.start_date)).days
    for r in t.itertuples(index=False):
        if rng.random()>.48: continue
        for _ in range(int(rng.integers(1,3))):
            rows.append({"withdrawal_id":f"W{i:07d}","customer_id":r.customer_id,
                "timestamp":pd.Timestamp(cfg.start_date)+pd.Timedelta(days=int(rng.integers(30,maxday+1))),
                "amount":round(float(r.amount*rng.uniform(.05,.35)),2),"currency":"USD","status":"completed"}); i+=1
    return pd.DataFrame(rows)

def generate_trades(cfg, rng, c, a):
    j=a[a.converted_ftd][["customer_id"]].merge(c[["customer_id","registration_date","customer_segment_gt"]],on="customer_id")
    scale={"Low":.8,"Core":1.5,"Growth":3.,"High Value":7.}; rows=[]; i=1
    for r in j.itertuples(index=False):
        for _ in range(int(rng.integers(1,12))):
            ts=pd.Timestamp(r.registration_date)+pd.Timedelta(days=int(rng.integers(1,100)))
            if ts > pd.Timestamp(cfg.end_date)+pd.Timedelta(days=1): continue
            v=float(rng.lognormal(np.log(scale[str(r.customer_segment_gt)]),.7))
            rows.append({"trade_id":f"T{i:08d}","customer_id":r.customer_id,"timestamp":ts,
                         "instrument_group":rng.choice(["FX","Index","Commodity","Crypto CFD"]),
                         "volume":round(v,4),"pnl_mock":round(float(rng.normal(0,75*v)),2)}); i+=1
    return pd.DataFrame(rows)

def generate_business_events():
    s=CRM_ROUTING_SCENARIO
    return pd.DataFrame([{"event_id":s.event_id,"date":pd.Timestamp(s.change_date),"event_type":s.event_type,"region":s.region,
      "affected_team":",".join(s.affected_teams),"description":s.description,"expected_effect":"response_time_up;ftd_conversion_down","ground_truth_tag":"root_cause"},
      {"event_id":"EVT_EU_CAMPAIGN_20260620","date":pd.Timestamp("2026-06-20"),"event_type":"MARKETING_CAMPAIGN","region":"Europe",
       "affected_team":"All","description":"Benign campaign increases lead volume.","expected_effect":"lead_volume_up","ground_truth_tag":"background_event"}])

def generate_all(cfg=None):
    cfg=cfg or GeneratorConfig(); rng=np.random.default_rng(cfg.seed)
    sp=generate_salespeople(cfg,rng); c=generate_customers(cfg,rng,sp); a=generate_sales_activity(cfg,rng,c)
    dep=generate_deposits(cfg,rng,c,a); wd=generate_withdrawals(cfg,rng,c,dep); tr=generate_trades(cfg,rng,c,a)
    return {"salespeople":sp,"customers":c,"sales_activity":a,"deposits":dep,"withdrawals":wd,"trades":tr,"business_events":generate_business_events()}

def write_csv_bundle(output_dir, cfg=None):
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True); paths={}
    for name,df in generate_all(cfg).items():
        path=out/f"{name}.csv"; df.to_csv(path,index=False); paths[name]=path
    return paths
