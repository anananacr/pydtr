# pydtr

Diffraction tomography reconstruction using peaks list in a CrystFEL stream file.
It generates the reciprocal space in 3D from a rotational tilt series dataset.

### Reference:
- White, T. A. (2009). Structure Solution Using Precession Electron Diffraction and Diffraction Tomography. https://doi.org/10.17863/CAM.61012 
- https://git.bitwiz.me.uk/dtr.git/

### Dependencies:
- Python 3.10.5
- requirements.txt

### Usage
Set experiment parameters in config.yaml


python rotation.py /path/to/stream/file/*.stream config.yaml

### Author:
Ana Carolina Rodrigues (2024 - )
Contact: sc.anarodrigues@gmail.com
