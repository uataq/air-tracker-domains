import os
import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Dict, Optional

import requests
import yaml
from loguru import logger
from pydantic import BaseModel, confloat

if TYPE_CHECKING:
    longitude_type = float
    latitude_type = float
    resolution_type = float
else:
    # Constrained types in pydantic currently raise an invalid type error from MyPy,
    # likely related to this issue:
    #   https://github.com/samuelcolvin/pydantic/issues/3080
    longitude_type = confloat(ge=-180, lt=180)
    latitude_type = confloat(gt=-90, lt=90)
    resolution_type = confloat(ge=0.001)


def from_to_by(start: float, stop: float, step: float, digits: int = 8) -> list[float]:
    """Sequence between start and stop (inclusive) by step, rounded to digits."""
    length = round((stop - start) / step)
    return [round(start + step * x, digits) for x in range(length + 1)]


class Point(BaseModel):
    x: longitude_type
    y: latitude_type


class Grid(BaseModel):
    xmin: longitude_type
    xmax: longitude_type
    xres: float
    ymin: latitude_type
    ymax: latitude_type
    yres: float

    def to_points(self) -> list[Point]:
        """Returns points placed on grid vertices."""
        xs = from_to_by(self.xmin, self.xmax, self.xres)
        ys = from_to_by(self.ymin, self.ymax, self.yres)
        return [Point(x=x, y=y) for x in xs for y in ys]


class MeteorologyModel(str, Enum):
    HRRR = "hrrr"
    HRRR_FORECAST = "hrrr_forecast"


class SimulationConfig(BaseModel):
    """Parameters passed to STILT/HYSPLIT.

    For parameter documentation, see:
        https://uataq.github.io/stilt/#/configuration

    Args:
        r_run_time (datetime): simulation start time
        r_lati (float): receptor latitude
        r_long (float): receptor longitude
        r_zagl (float): receptor height above ground in meters
        simulation_id (str): optionally set a unique identifier for the simulation!!!

        n_hours (int): simulation duration in hours
        xmn (float): footprint minimum longitude in -180:180
        xmx (float): footprint maximum longitude in -180:180
        xres (float): footprint longitude resolution
        ymn (float): footprint minimum latitude in -90:90
        ymx (float): footprint maximum latitude in -90:90
        yres (float): footprint latitude resolution
        time_integrate (bool): should footprints be summed across time; defaults true.
    """

    n_hours: int
    xmn: longitude_type
    xmx: longitude_type
    xres: resolution_type
    ymn: latitude_type
    ymx: latitude_type
    yres: resolution_type
    timeout: int = 60

    capemin: Optional[float] = None
    cmass: Optional[float] = None
    conage: Optional[float] = None
    cpack: Optional[float] = None
    dxf: Optional[float] = None
    dyf: Optional[float] = None
    dzf: Optional[float] = None
    efile: Optional[str] = None
    emisshrs: Optional[float] = None
    frhmax: Optional[float] = None
    frhs: Optional[float] = None
    frme: Optional[float] = None
    frmr: Optional[float] = None
    frts: Optional[float] = None
    frvs: Optional[float] = None
    hnf_plume: Optional[bool] = None
    horcoruverr: Optional[float] = None
    horcorzierr: Optional[float] = None
    hscale: Optional[float] = None
    ichem: Optional[float] = None
    idsp: Optional[float] = None
    initd: Optional[float] = None
    k10m: Optional[float] = None
    kagl: Optional[float] = None
    kbls: Optional[float] = None
    kblt: Optional[float] = None
    kdef: Optional[float] = None
    khinp: Optional[float] = None
    khmax: Optional[float] = None
    kmix0: Optional[float] = None
    kmixd: Optional[float] = None
    kmsl: Optional[float] = None
    kpuff: Optional[float] = None
    krand: Optional[float] = None
    krnd: Optional[float] = None
    kspl: Optional[float] = None
    kwet: Optional[float] = None
    kzmix: Optional[float] = None
    maxdim: Optional[float] = None
    maxpar: Optional[float] = None
    mgmin: Optional[float] = None
    n_met_min: Optional[float] = None
    ncycl: Optional[float] = None
    ndump: Optional[float] = None
    ninit: Optional[float] = None
    nstr: Optional[float] = None
    nturb: Optional[float] = None
    numpar: Optional[int] = None
    nver: Optional[float] = None
    outdt: Optional[float] = None
    outfrac: Optional[float] = None
    p10f: Optional[float] = None
    pinbc: Optional[str] = None
    pinpf: Optional[str] = None
    poutf: Optional[str] = None
    projection: Optional[str] = None
    qcycle: Optional[float] = None
    random: Optional[float] = None
    rhb: Optional[float] = None
    rht: Optional[float] = None
    rm_dat: Optional[bool] = None
    siguverr: Optional[float] = None
    sigzierr: Optional[float] = None
    simulation_id: Optional[str] = None
    smooth_factor: Optional[float] = None
    splitf: Optional[float] = None
    time_integrate: Optional[bool] = True
    tkerd: Optional[float] = None
    tkern: Optional[float] = None
    tlfrac: Optional[float] = None
    tluverr: Optional[float] = None
    tlzierr: Optional[float] = None
    tout: Optional[float] = None
    tratio: Optional[float] = None
    tvmix: Optional[float] = None
    varsiwant: Optional[str] = None
    veght: Optional[float] = None
    vscale: Optional[float] = None
    vscaleu: Optional[float] = None
    vscales: Optional[float] = None
    w_option: Optional[float] = None
    wbbh: Optional[float] = None
    wbwf: Optional[float] = None
    wbwr: Optional[float] = None
    wvert: Optional[bool] = None
    zicontroltf: Optional[float] = None
    ziscale: Optional[float] = None
    z_top: Optional[float] = None
    zcoruverr: Optional[float] = None


class GriddedScene(BaseModel):
    pixel_grid: Grid
    simulation_config: SimulationConfig
    meteorology_model: MeteorologyModel


class DomainConfig(GriddedScene):
    is_enabled: Optional[bool] = True


class CreateSceneDTO(BaseModel):
    pixel_points: list[Point]
    simulation_config: SimulationConfig
    meteorology_model: MeteorologyModel
    scene_id: Optional[uuid.UUID] = None
    time: Optional[datetime] = None


def load_domain_configs() -> Dict[str, DomainConfig]:
    with open("domains.yaml") as f:
        domain_dict = yaml.safe_load(f)
    return {k: DomainConfig(**v) for k, v in domain_dict.items()}


class CreateSceneException(Exception):
    """Raised when unable to create a scene."""


def main():
    SCENES_API_URL = os.getenv("SCENES_API_URL")
    assert SCENES_API_URL

    domain_configs = load_domain_configs()
    for domain_config in domain_configs.values():
        if not domain_config.is_enabled:
            logger.info(f"Skipping: DomainConfig{domain_config}")
            continue

        logger.info(f"Creating: DomainConfig{domain_config}")
        try:
            payload = CreateSceneDTO(
                pixel_points=domain_config.pixel_grid.to_points(),
                simulation_config=domain_config.simulation_config,
                meteorology_model=domain_config.meteorology_model,
            )

            response = requests.post(
                SCENES_API_URL, data=payload.json(exclude_defaults=True)
            )
            if not response.ok:
                raise CreateSceneException(response.content)
            logger.info(f"Successfully created: DomainConfig{domain_config}")
        except CreateSceneException as e:
            logger.exception(e)


if __name__ == "__main__":
    main()
