import copy
import gzip
import hashlib
import json
from datetime import date,datetime,timezone
from pathlib import Path
import pytest
from navic_compare.acquire import Archive,discover_current_files,acquire_current_nav,assess_current_records
from test_validity import rinex_text

def config():
    return {'broadcast_max_age_seconds':7200,'broadcast_window_basis':'test policy',
            'current_acquisition':{'directory':'https://example.test/{year}/{doy}/','minimum_usable_satellites':1}}

def test_directory_discovery_is_date_specific_and_rejects_external_links():
    names=['BRDC00WRD_R_20200010000_01D_MN.rnx.gz','BRDC00WRD_S_20200010000_01D_MN.rnx.gz',
           'BRDC00WRD_S_20193650000_01D_MN.rnx.gz','https://evil.test/BRDC00WRD_S_20200010000_01D_MN.rnx.gz',
           '../BRDC00WRD_S_20200010000_01D_MN.rnx.gz']
    html=''.join(f'<a href="{n}">file</a>' for n in names)
    assert discover_current_files(html,date(2020,1,1))==[names[1],names[0]]

def test_304_reuses_verified_body_and_keeps_receipt_time(tmp_path,monkeypatch):
    archive=Archive(tmp_path);responses=[];calls=[]
    class Response:
        def __init__(self,status,content=b'',headers=None):self.status_code=status;self.content=content;self.headers=headers or {}
        def raise_for_status(self):pass
    responses.extend([Response(200,b'orbit',{'ETag':'one','Last-Modified':'Wed, 01 Jan 2020 00:00:00 GMT'}),Response(304)])
    def get(url,**kwargs):calls.append(kwargs);return responses.pop(0)
    monkeypatch.setattr(archive.session,'get',get)
    first=archive.fetch('https://example.test/file','.rnx.gz');second=archive.fetch('https://example.test/file','.rnx.gz')
    assert first['retrieved_at']==second['retrieved_at'] and first['sha256']==second['sha256']
    assert second['http_status']==304 and second['not_modified']
    assert calls[1]['headers']=={'If-None-Match':'one','If-Modified-Since':'Wed, 01 Jan 2020 00:00:00 GMT'}
    Path(second['path']).write_bytes(b'tampered');responses.append(Response(304))
    with pytest.raises(ValueError,match='checksum'):archive.fetch('https://example.test/file','.rnx.gz')

def test_no_body_304_is_rejected(tmp_path,monkeypatch):
    archive=Archive(tmp_path)
    class Response:status_code=304
    monkeypatch.setattr(archive.session,'get',lambda *a,**k:Response())
    with pytest.raises(ValueError,match='no archived body'):archive.fetch('https://example.test/file','.json')

def test_current_selection_falls_back_from_invalid_product(tmp_path,monkeypatch,geo):
    source='BRDC00WRD_S_20200010000_01D_MN.rnx.gz';fallback='BRDC00WRD_R_20200010000_01D_MN.rnx.gz'
    class Response:
        status_code=200;headers={}
        def __init__(self,content):self.content=content
        def raise_for_status(self):pass
    def get(self,url,**kwargs):
        if url.endswith('/'):return Response(f'<a href="{source}">S</a><a href="{fallback}">R</a>'.encode())
        if url.endswith(source):return Response(gzip.compress(rinex_text(geo,prn='G01').encode()))
        return Response(gzip.compress(rinex_text(geo).encode()))
    monkeypatch.setattr('requests.Session.get',get)
    record,report=acquire_current_nav(config(),tmp_path,datetime(2020,1,1,1,tzinfo=timezone.utc))
    assert record['source'].endswith(fallback)
    assert report['freshness']['usable_satellites']==1
    assert report['attempts'][0]['accepted'] is False
    assert len(list((tmp_path/'acquisitions').glob('*.json')))==1

def test_recent_file_does_not_hide_stale_or_unhealthy_records(geo):
    now=datetime(2020,1,1,4,tzinfo=timezone.utc)
    stale=assess_current_records([geo],now,config())
    assert stale['usable_satellites']==0 and stale['satellites'][0]['flags']==['broadcast_gap']
    geo.values[21]=1
    unhealthy=assess_current_records([geo],datetime(2020,1,1,tzinfo=timezone.utc),config())
    assert unhealthy['usable_satellites']==0 and unhealthy['satellites'][0]['health']==1

def test_selection_prefers_fresher_records_over_filename_priority(tmp_path,monkeypatch,geo):
    source='BRDC00WRD_S_20200010000_01D_MN.rnx.gz';receiver='BRDC00WRD_R_20200010000_01D_MN.rnx.gz'
    newer=copy.deepcopy(geo);newer.values[8]+=3600
    class Response:
        status_code=200;headers={}
        def __init__(self,content):self.content=content
        def raise_for_status(self):pass
    def get(self,url,**kwargs):
        if url.endswith('/'):return Response(f'<a href="{source}">S</a><a href="{receiver}">R</a>'.encode())
        return Response(gzip.compress(rinex_text(newer if url.endswith(receiver) else geo).encode()))
    monkeypatch.setattr('requests.Session.get',get)
    record,report=acquire_current_nav(config(),tmp_path,datetime(2020,1,1,1,tzinfo=timezone.utc))
    assert record['source'].endswith(receiver)
    assert abs(report['freshness']['max_usable_toe_age_seconds'])<1e-6
