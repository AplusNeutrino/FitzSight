from finsight.data.generator import GeneratorConfig, generate_all
from finsight.analytics.baseline import investigate_crm_routing_change

def test_crm_routing_scenario_is_detectable():
    t=generate_all(GeneratorConfig())
    d=investigate_crm_routing_change(t["sales_activity"])["diagnosis"]
    assert d["affected_conversion_deteriorated"]
    assert d["affected_response_time_increased"]
    assert d["effect_stronger_than_control"]
    assert d["statistically_significant_conversion_shift"]
