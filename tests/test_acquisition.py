import json
import pytest
from navic_compare.acquire import Archive

def test_immutable_archive_and_gp_poll_guard(tmp_path,monkeypatch):
    archive=Archive(tmp_path)
    class Response:
        status_code=200
        content=b'[{"test":"snapshot"}]'
        headers={'ETag':'a'}
        def raise_for_status(self): pass
    calls=[]
    def get(*args,**kwargs): calls.append(kwargs);return Response()
    monkeypatch.setattr(archive.session,'get',get)
    a=archive.fetch('https://example.test/gp','.json',gp=True)
    b=archive.fetch('https://example.test/gp','.json',gp=True)
    assert a['sha256']==b['sha256'] and b['cache_reused']
    assert len(calls)==1
    assert len(list((tmp_path/'raw').iterdir()))==1
    for p in (tmp_path/'cache').iterdir():
        state=json.loads(p.read_text());state['last_attempt']=0;p.write_text(json.dumps(state))
    archive.fetch('https://example.test/gp','.json',gp=True)
    assert calls[1]['headers']=={'If-None-Match':'a'}

def test_failed_poll_is_also_rate_limited(tmp_path,monkeypatch):
    import requests
    archive=Archive(tmp_path)
    def get(*a,**kw): raise requests.ConnectionError('offline')
    monkeypatch.setattr(archive.session,'get',get)
    with pytest.raises(requests.ConnectionError): archive.fetch('https://example.test/gp','.json',gp=True)
    with pytest.raises(ValueError,match='poll guard'): archive.fetch('https://example.test/gp','.json',gp=True)

def test_fallback_on_file_without_navic(tmp_path,monkeypatch,geo):
    from navic_compare.acquire import acquire
    from test_validity import rinex_text
    from datetime import date
    import gzip
    config={'sources':['https://example.test/no-i','https://example.test/valid'],
            'gp_url':'https://example.test/gp','eop_url':'https://example.test/eop','leaps_url':'https://example.test/leaps'}
    class Response:
        status_code=200
        headers={}
        def __init__(self,content): self.content=content
        def raise_for_status(self): pass
    def get(self,url,**kwargs):
        if url.endswith('no-i'): return Response(gzip.compress(rinex_text(geo,prn='G01').encode()))
        if url.endswith('valid'): return Response(gzip.compress(rinex_text(geo).encode()))
        return Response(b'[]')
    monkeypatch.setattr('requests.Session.get',get)
    monkeypatch.setattr('navic_compare.acquire.parse_gp',lambda p: [object()])
    result=acquire(date(2020,1,1),config,tmp_path)
    assert result['rinex']['source'].endswith('valid')
    assert result['acquisition_attempts'][0]['accepted'] is False
    assert result['acquisition_attempts'][1]['accepted'] is True
