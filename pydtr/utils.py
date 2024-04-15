import numpy as np
import om.lib.geometry as geometry_functions


def get_corrected_lab_coordinates_in_reciprocal_units(
    fs: int,
    ss: int,
    pixel_maps: geometry_functions.TypePixelMaps,
    k: float,
    res: float,
    clen: float,
) -> tuple:
    data_shape = pixel_maps["x"].shape
    peak_index_in_slab = int(round(ss) * data_shape[1]) + int(round(fs))
    radius = (pixel_maps["radius"].flatten()[peak_index_in_slab] * k) / (res * clen)
    two_theta = np.arctan2(abs(radius), k)
    phi = pixel_maps["phi"].flatten()[peak_index_in_slab]
    x = k * np.sin(two_theta) * np.cos(phi)
    y = k * np.sin(two_theta) * np.sin(phi)
    z = k - k * np.cos(two_theta)

    return x, y, z


def rotate_in_x(x, y, z, angle):
    rotation_matrix = [
        [np.cos(angle), np.sin(angle), 0],
        [-1 * np.sin(angle), np.cos(angle), 0],
        [0, 0, 1],
    ]
    r = [x, y, z]
    return np.matmul(rotation_matrix, r)


def rotate_in_z(x, y, z, angle):
    rotation_matrix = [
        [1, 0, 0],
        [0, np.cos(angle), np.sin(angle)],
        [0, -1 * np.sin(angle), np.cos(angle)],
    ]
    r = [x, y, z]
    return np.matmul(rotation_matrix, r)
