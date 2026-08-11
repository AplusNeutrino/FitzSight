from finsight.data.generator import GeneratorConfig, generate_all

def test_generator_is_deterministic():
    cfg=GeneratorConfig(seed=123,n_customers=1000,n_salespeople=20)
    a,b=generate_all(cfg),generate_all(cfg)
    assert a["customers"].equals(b["customers"])
    assert a["sales_activity"].equals(b["sales_activity"])

def test_customer_ids_unique():
    t=generate_all(GeneratorConfig(seed=123,n_customers=1000,n_salespeople=20))
    assert t["customers"].customer_id.is_unique
