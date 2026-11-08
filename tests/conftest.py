import numpy as np
import pytest
from astropy.utils import iers
from astropy.time import Time
from navic_compare.rinex import Ephemeris
from navic_compare.orbits import MU,OMEGA

@pytest.fixture(autouse=True)
def offline_eop():
    iers.conf.auto_download=False
    with iers.earth_orientation_table.set(iers.IERS_B.open(iers.IERS_B_FILE)):
        yield

@pytest.fixture
def geo():
    time=Time('2020-01-01T00:00:00',scale='utc')
    values=[0.0]*28
    values[7]=(MU/OMEGA**2)**(1/6)
    values[8]=float(time.gps)%604800
    values[10]=OMEGA*values[8]
    values[18]=int(time.gps//604800)
    values[20]=2.4
    return Ephemeris('I10',time,time,values,[0,0,0])
