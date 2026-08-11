import pandas as pd
from finsight.analytics.kpis import ftd_conversion_rate, net_deposits

def test_ftd_conversion_rate():
    assert ftd_conversion_rate(pd.DataFrame({"converted_ftd":[True,False,True,True]})) == .75

def test_net_deposits():
    d=pd.DataFrame({"status":["completed","completed"],"amount":[100.,50.]})
    w=pd.DataFrame({"status":["completed"],"amount":[40.]})
    assert net_deposits(d,w)==110.
