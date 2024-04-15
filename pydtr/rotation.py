import sys
import h5py
import hdf5plugin
import numpy as np
from bblib.models import PF8Info, PF8
import matplotlib.pyplot as plt
import om.lib.geometry as geometry_functions
import matplotlib
matplotlib.use('Qt5Agg')
from os.path import basename, splitext
from scipy import constants
from PIL import Image
import tifffile as tif
import math
from matplotlib import cm
from utils import rotate_in_x, rotate_in_z, get_corrected_lab_coordinates_in_reciprocal_units
from settings import read, parse

config = settings.read(sys.argv[2])
info = settings.parse(config)

azimuth_of_the_tilt_axis = info["azimuth_of_the_tilt_axis_in_degrees"]*(np.pi/180)
tilt_angle = info["tilt_angle_in_degrees"]*np.pi/180
starting_angle = info["starting_angle_in_degrees"]*np.pi/180
space_stretching_factor = info["space_stretching_factor"]
intensity_factor = info["intensity_factor"]

PF8Config=PF8Info()


if sys.argv[1] == '-':
    stream = sys.stdin
else:
    stream = open(sys.argv[1], 'r')
reading_geometry = False
reading_chunks = False
reading_peaks = False
max_fs = -100500
max_ss = -100500


geometry_txt=[]
detector_shift_in_x = 0 
detector_shift_in_y = 0 

for line in stream:
    if reading_chunks:
        
        if line.startswith('End of peak list'):
            reading_peaks = False
        elif line.split(" //")[0]=='Event:':
            event_number = int(line.split(" //")[-1])
        elif line.split(" = ")[0]==info["detector_shift_in_x_entry"]:
            detector_shift_in_x = float(line.split(" = ")[-1])* res *1e-3
        elif line.split(" = ")[0]==info["detector_shift_in_y_entry"]:
            detector_shift_in_y= float(line.split(" = ")[-1])* res *1e-3

        elif line.startswith('  fs/px   ss/px (1/d)/nm^-1   Intensity  Panel'):
            reading_peaks = True
            PF8Config.set_geometry_from_file()
            PF8Config.update_pixel_maps(detector_shift_in_x, detector_shift_in_y)
            ## Update x pixel map and phi I think Crytsfel is in the other referential system
            PF8Config.pixel_maps["x"] *= -1
            PF8Config.pixel_maps["phi"] = np.arctan2(PF8Config.pixel_maps["y"], PF8Config.pixel_maps["x"])

        elif reading_peaks:
            fs, ss, dump, intensity = [float(i) for i in line.split()[:4]]
            if intensity>0:
                x_lab, y_lab, z_lab = get_corrected_lab_coordinates_in_reciprocal_units(int(fs), int(ss), PF8Config.pixel_maps, k, res, clen)
                x, y, z = rotate_in_z(x_lab, y_lab, z_lab, azimuth_of_the_tilt_axis)
                x, y, z = rotate_in_x(x, y, z, starting_angle + (event_number*tilt_angle))
                x, y, z = rotate_in_z(x, y, z, -1 *azimuth_of_the_tilt_axis)
                reciprocal_space[int(reciprocal_space_radius+space_stretching_factor*z), int(reciprocal_space_radius+space_stretching_factor*y),  int(reciprocal_space_radius+space_stretching_factor*x)] += intensity_factor*intensity
                reciprocal_space[int(reciprocal_space_radius-space_stretching_factor*z), int(reciprocal_space_radius-space_stretching_factor*y),  int(reciprocal_space_radius-space_stretching_factor*x)] += intensity_factor*intensity


    elif line.startswith('----- End geometry file -----'):
        reading_geometry = False
        PF8Config.geometry_txt=geometry_txt
        PF8Config.set_geometry_from_file()
        reciprocal_space_radius=int((max(PF8Config.get_detector_center())*k)/(res*clen))*space_stretching_factor
        reciprocal_space_dimension=2*reciprocal_space_radius
        reciprocal_space = np.zeros((reciprocal_space_dimension+1, reciprocal_space_dimension+1, reciprocal_space_dimension+1), dtype=np.int32)

    elif reading_geometry:
        geometry_txt.append(line)
        if line.split(' = ')[0]=="res":
            res=float(line.split(' = ')[-1])
        elif line.split(' = ')[0]=="clen":
            clen=float(line.split(' = ')[-1].split(";")[0])
        elif line.split(' = ')[0]=="photon_energy":
            beam_energy=int(line.split(' = ')[-1].split(";")[0])
            k = beam_energy / (1e9*constants.h * constants.c)
            print(k)
        elif line.split(' = ')[0]=="wavelength":
            wavelength = float(line.split(' = ')[-1].split(" ")[0])
            k = 1e-9/wavelength    

        try:
            par, val = line.split('=')
            if par.split('/')[-1].strip() == 'max_fs' and int(val) > max_fs:
                max_fs = int(val)
            elif par.split('/')[-1].strip() == 'max_ss' and int(val) > max_ss:
                max_ss = int(val)
        except ValueError:
            pass

    elif line.startswith('----- Begin geometry file -----'):
        reading_geometry = True
    elif line.startswith('----- Begin chunk -----'):
        reading_chunks = True

tif.imwrite(info["output_folder"]+"/"+splitext(basename(sys.argv[1]))[0]+'-merge.tif', reciprocal_space)
