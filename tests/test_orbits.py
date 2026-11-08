import numpy as np
from astropy import units as u
from astropy.time import Time,TimeDelta
from astropy.coordinates import ITRS,TEME,CartesianRepresentation
from sgp4.api import Satrec
from navic_compare.orbits import broadcast_position,rtn_residual,MU,OMEGA
from navic_compare.timeframes import teme_to_ecef,system_time,utc_grid

def test_vallado_near_earth_reference():
    sat=Satrec.twoline2rv('1 00005U 58002B   00179.78495062  .00000023  00000-0  28098-4 0  4753',
                         '2 00005  34.2682 348.7242 1859667 331.7664  19.3264 10.82419157413667')
    for minutes,expected in [(0,[7022.46529266,-1400.08296755,0.03995155]),
                             (360,[-7154.03120202,-3783.17682504,-3536.19412294])]:
        error,p,v=sat.sgp4_tsince(minutes)
        assert error==0
        np.testing.assert_allclose(p,expected,rtol=0,atol=1e-7)

def test_vallado_deep_space_reference():
    sat=Satrec.twoline2rv('1 04632U 70093B   04031.91070959 -.00000084  00000-0  10000-3 0  9955',
                         '2 04632  11.4628 273.1101 1450506 207.6000 143.9350  1.20231981 44145')
    assert sat.method=='d'
    error,p,v=sat.sgp4_tsince(-5184)
    assert error==0
    np.testing.assert_allclose(p,[-29020.02587128,13819.84419063,-5713.33679183],rtol=0,atol=1e-7)

def test_circular_geo_stays_fixed(geo):
    t=geo.toe+TimeDelta(np.arange(0,86400,300),format='sec')
    expected=np.tile([(MU/OMEGA**2)**(1/3)/1000,0,0],(len(t),1))
    np.testing.assert_allclose(broadcast_position(geo,t),expected,rtol=0,atol=1e-8)

def test_geo_rtn_uses_inertial_velocity(geo):
    t=geo.toe+TimeDelta([0,30,60],format='sec')
    p=broadcast_position(geo,t)
    base=ITRS(CartesianRepresentation(p.T*u.km),obstime=t).transform_to(TEME(obstime=t)).cartesian.xyz.to_value(u.km).T
    radial=base/np.linalg.norm(base,axis=1,keepdims=True)
    out=rtn_residual(geo,t,base+radial*2)
    np.testing.assert_allclose(out,np.tile([2,0,0],(3,1)),atol=1e-7)
    np.testing.assert_allclose(np.linalg.norm(out,axis=1),2,atol=1e-7)

def test_frame_rotation_independent_gmst_and_poles():
    from astropy.utils import iers
    t=Time('2020-01-01T12:00:00',scale='utc')
    vector=np.array([20000.,30000.,10000.])
    centuries=((t.ut1.jd1-2451545)+t.ut1.jd2)/36525
    gmst=(67310.54841+(876600*3600+8640184.812866)*centuries+0.093104*centuries**2-6.2e-6*centuries**3)*np.pi/43200
    c,s=np.cos(gmst),np.sin(gmst)
    pef=np.array([[c,s,0],[-s,c,0],[0,0,1]])@vector
    xp,yp=iers.earth_orientation_table.get().pm_xy(t)
    xp,yp=xp.to_value(u.rad),yp.to_value(u.rad)
    # Vallado polar matrix; TEME implementation sets TIO locator s' to zero.
    cx,sx,cy,sy=np.cos(xp),np.sin(xp),np.cos(yp),np.sin(yp)
    polar=np.array([[cx,sx*sy,sx*cy],[0,cy,-sy],[-sx,cx*sy,cx*cy]])
    expected=polar@pef
    np.testing.assert_allclose(teme_to_ecef(vector,t),expected,atol=2e-5,rtol=0)

def test_system_offset_and_leap_grid():
    assert abs((system_time('2020-01-01T00:00:18').utc-Time('2020-01-01T00:00:00',scale='utc')).sec)<1e-8
    grid=utc_grid('2016-12-31',1)
    assert len(grid)==86401
    assert grid[-1].utc.isot=='2016-12-31T23:59:60.000'
    assert np.allclose(np.diff(grid.tai.jd)*86400,1,atol=5e-5)
