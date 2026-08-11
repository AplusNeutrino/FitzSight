from dataclasses import dataclass, asdict
import pandas as pd
from scipy.stats import chi2_contingency
from fitzsight.data.scenarios import CRM_ROUTING_SCENARIO

@dataclass(frozen=True)
class CohortComparison:
    cohort:str; pre_n:int; post_n:int; pre_conversion:float; post_conversion:float
    absolute_change_pp:float; pre_response_median:float; post_response_median:float; conversion_p_value:float

def compare_pre_post(df, change_date, label):
    d=df.copy(); d["lead_created_at"]=pd.to_datetime(d.lead_created_at)
    pre=d[d.lead_created_at.dt.date < change_date]; post=d[d.lead_created_at.dt.date >= change_date]
    pr=float(pre.converted_ftd.mean()) if len(pre) else 0.; po=float(post.converted_ftd.mean()) if len(post) else 0.
    if len(pre) and len(post):
        tab=[[int(pre.converted_ftd.sum()), int(len(pre)-pre.converted_ftd.sum())],[int(post.converted_ftd.sum()),int(len(post)-post.converted_ftd.sum())]]
        p=float(chi2_contingency(tab, correction=False)[1])
    else: p=1.
    return CohortComparison(label,len(pre),len(post),pr,po,(po-pr)*100,float(pre.response_time_minutes.median()) if len(pre) else 0.,float(post.response_time_minutes.median()) if len(post) else 0.,p)

def investigate_crm_routing_change(df):
    s=CRM_ROUTING_SCENARIO
    affected=df[df.region.eq(s.region)&df.assigned_team.isin(s.affected_teams)]
    control=df[df.region.eq(s.region)&~df.assigned_team.isin(s.affected_teams)]
    a=compare_pre_post(affected,s.change_date,"Europe / Team A+B"); c=compare_pre_post(control,s.change_date,"Europe / control teams")
    return {"scenario":s.event_type,"change_date":s.change_date.isoformat(),"affected":asdict(a),"control":asdict(c),
            "diagnosis":{"affected_conversion_deteriorated":a.post_conversion<a.pre_conversion,
                         "affected_response_time_increased":a.post_response_median>a.pre_response_median,
                         "effect_stronger_than_control":a.absolute_change_pp<c.absolute_change_pp,
                         "statistically_significant_conversion_shift":a.conversion_p_value<.05}}
