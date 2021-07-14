from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel


class SpatialGrid(BaseModel):
    xmin: float
    xmax: float
    xres: float
    ymin: float
    ymax: float
    yres: float


class DomainConfig(BaseModel):
    is_enabled: Optional[bool] = True
    receptor_grid: SpatialGrid
    footprint_grid: SpatialGrid
    stilt_config: Dict[str, Any]


def test_validate_domain_config():
    with open("domains.yaml") as f:
        domain_dict = yaml.safe_load(f)

    domain_configs = {k: DomainConfig(**v) for k, v in domain_dict.items()}

    for name, domain_config in domain_configs.items():
        assert name
        for grid in (domain_config.receptor_grid, domain_config.footprint_grid):
            assert grid.xmin >= -180
            assert grid.xmin <= 180
            assert grid.ymin > -90
            assert grid.ymax < 90
            assert grid.xres >= 0.0001
            assert grid.yres >= 0.0001

    assert "salt_lake_city" in domain_configs
