import yaml
from pathlib import Path
import sys


def read(path: str):
    path = Path(path)
    config = path.read_text()
    config = yaml.safe_load(config)
    return config


def parse(config: dict):

    return {
        "output_folder": config["output_folder"],
        "azimuth_of_the_tilt_axis_in_degrees": config[
            "azimuth_of_the_tilt_axis_in_degrees"
        ],
        "tilt_angle_in_degrees": config["tilt_angle_in_degrees"],
        "starting_angle_in_degrees": config["starting_angle_in_degrees"],
        "space_stretching_factor": config["space_stretching_factor"],
        "intensity_factor": config["intensity_factor"],
        "detector_shift_in_x_entry": config["detector_shift_in_x_entry"],
        "detector_shift_in_y_entry": config["detector_shift_in_y_entry"],
    }
