# Air Tracker domain registry

This repository is home to [`domains.yaml`](domains.yaml), which configures the STILT simulations used to generate and cache footprints for real-time consumption using forecast meteorology.

## Domain schema

A domain definition looks like

```yaml
salt_lake_city:
  is_enabled: true
  pixel_grid:
    xmin: -112.1
    xmax: -111.75
    xres: 0.01
    ymin: 40.4
    ymax: 40.9
    yres: 0.01
  simulation_config:
    n_hours: -4
    numpar: 200
    xmn: -112.5
    xmx: -111.5
    xres: 0.002
    ymn: 40.1
    ymx: 41.2
    yres: 0.002
  meteorology_model: 'hrrr_forecast'
```

This configures a `salt_lake_city` domain, where receptors placed on the vertices of `pixel_grid` (inclusive of boundaries) are used to generate STILT footprints using settings in `simulation_config` which are passed as named parameters to STILT.

<p align="center">
<img src="docs/stilt-example-domain.png" height=700></img>
</p>

For our example domain definition, the `pixel_grid` defines the black circles and the footprint grid defined in `simulation_config` is represented by the yellow area.

### Modifying the domain definitions

Open [`domains.yaml`](domains.yaml) and make your edits. You'll need to submit a pull request to validate the configuration before changes will be detected by the STILT simulation service.

## Deployment

Set these environment variables:

```bash
export PROJECT=air-tracker-edf
export ENVIRONMENT=dev
export SCENES_API_URL=http://api.air-tracker-dev.svc.cluster.local/scenes
# Optional:
export LOGURU_LEVEL=INFO
```

Then run the deploy script:

```bash
./deploy.sh
```

Or, as a one-liner:

```bash
PROJECT=air-tracker-edf ENVIRONMENT=dev SCENES_API_URL=http://api.air-tracker-dev.svc.cluster.local/scenes ./deploy.sh
```

## Local development

Install python dependencies to a virtual environment using [Poetry](https://python-poetry.org):

```bash
poetry install
```

Then run the tests with `pytest`:

```bash
pytest
```
