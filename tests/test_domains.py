from scene_generator import load_domain_configs


def test_validate_domain_config():
    domain_configs = load_domain_configs()
    assert "salt_lake_city" in domain_configs
