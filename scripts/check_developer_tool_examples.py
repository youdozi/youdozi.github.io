#!/usr/bin/env python3
"""Execute the paired developer-tool examples using only local disposable fixtures."""
from pathlib import Path
import http.client
import json
import re
import runpy
import selectors
import subprocess
import sys
import tempfile
import threading
from xml.etree import ElementTree as ET

POSTS = Path('src/content/posts')
HTTP = '2021-07-20-http-status-test'
DRAW = '2021-07-23-app-diagrams.net'
SEARCH = '2021-08-06-search-github'


def paired(key, language):
    editions=[]
    for locale in ['en','ko']:
        text=(POSTS/locale/(key+'.md')).read_text()
        editions.append(re.findall(r'^```'+re.escape(language)+r'\n([\s\S]*?)^```[ \t]*$',text,re.M))
    assert editions[0] and editions[0]==editions[1], f'Paired {language} examples differ: {key}'
    return editions[0]


def request(port, path):
    connection=http.client.HTTPConnection('127.0.0.1',port,timeout=3)
    try:
        connection.request('GET',path)
        response=connection.getresponse()
        return response.status, dict(response.getheaders()), response.read()
    finally:
        connection.close()


def check_http(tmp):
    code=paired(HTTP,'python');assert len(code)==1
    file=tmp/'status_server.py';file.write_text(code[0])
    module=runpy.run_path(str(file))
    server=module['make_server'](0)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    cases=0
    try:
        for expected in [200,201,204,400,404,429,500,503]:
            status,headers,body=request(server.server_port,f'/status/{expected}')
            assert status==expected
            if expected==204:
                assert body==b'' and 'Content-Length' not in headers and 'Content-Type' not in headers
            else:
                assert headers['Content-Type']=='application/json; charset=utf-8'
                assert int(headers['Content-Length'])==len(body)
                assert json.loads(body)=={'status':expected}
            cases+=1
        for path in ['/status/999','/status/bad','/other','/status/0200']:
            status,_,body=request(server.server_port,path)
            assert status==404 and json.loads(body)=={'status':404};cases+=1
        status,headers,body=request(server.server_port,'/html/200')
        assert status==200 and headers['Content-Type']=='text/html; charset=utf-8'
        assert int(headers['Content-Length'])==len(body)
        try:json.loads(body)
        except json.JSONDecodeError:pass
        else:raise AssertionError('HTML fixture unexpectedly parsed as JSON')
        cases+=1
        status,_,body=request(server.server_port,'/status/200?ignored=1')
        assert status==200 and json.loads(body)=={'status':200};cases+=1
    finally:
        server.shutdown();thread.join(timeout=3);server.server_close()
    for port in ['-1','65536','not-a-number']:
        result=subprocess.run([sys.executable,str(file),'--port',port],capture_output=True,text=True,timeout=5)
        assert result.returncode==2 and result.stderr
    process=subprocess.Popen([sys.executable,str(file),'--port','0'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout,selectors.EVENT_READ)
            assert selector.select(timeout=5),'CLI server did not report its actual port'
        url=process.stdout.readline().strip()
        assert re.fullmatch(r'http://127\.0\.0\.1:[0-9]+',url),url
        port=int(url.rsplit(':',1)[1]);assert port>0
        assert request(port,'/status/200')[0]==200;cases+=1
    finally:
        process.terminate();process.communicate(timeout=5)
    return {'httpResponseCases':cases,'invalidPortCLICases':3}


def check_drawio():
    blocks=paired(DRAW,'xml');assert len(blocks)==1
    tree=ET.fromstring(blocks[0]);assert tree.tag=='mxfile'
    cells=tree.findall('./diagram/mxGraphModel/root/mxCell')
    by_id={cell.attrib['id']:cell for cell in cells};assert len(by_id)==len(cells)
    vertices={key:cell for key,cell in by_id.items() if cell.get('vertex')=='1'}
    assert {key:cell.get('value') for key,cell in vertices.items()}=={'request':'Request','validate':'Validate','response':'Response'}
    edges=[cell for cell in cells if cell.get('edge')=='1']
    assert {(cell.get('source'),cell.get('target')) for cell in edges}=={('request','validate'),('validate','response')}
    for cell in cells:
        if cell.get('parent') is not None:assert cell.get('parent') in by_id
    for cell in vertices.values():
        geometry=cell.find('mxGeometry');assert geometry is not None
        assert float(geometry.get('width'))>0 and float(geometry.get('height'))>0
    for cell in edges:
        assert cell.get('source') in vertices and cell.get('target') in vertices
        assert cell.find('mxGeometry').get('relative')=='1'
    again=ET.fromstring(ET.tostring(tree))
    assert len(again.findall('.//mxCell'))==len(cells)
    flows=json.loads(Path('content/diagrams/workflows.json').read_text())['diagrams']
    flow=next(i for i in flows if i['key']==DRAW)
    assert [s['en'][0] for s in flow['steps']]==['Request','Validate','Response']
    return {'drawioVertices':3,'drawioDirectedEdges':2,'editorUIOrExportExecuted':False}


def check_search(tmp):
    blocks=paired(SEARCH,'sh');assert len(blocks)==1
    paired(SEARCH,'text')
    script=tmp/'search.sh';script.write_text(blocks[0])
    subprocess.run(['sh','-n',str(script)],check=True)
    result=subprocess.run(['sh',str(script)],cwd=tmp,capture_output=True,text=True,timeout=10,check=True)
    expected='src/WebClient.java:1:interface WebClient {}'
    assert result.stdout.strip()==expected,result.stdout
    repo=tmp/'demo-search'
    def grep(pattern,*paths):
        return subprocess.run(['git','-c','color.ui=false','grep','-n','-F',pattern,'--',*paths],cwd=repo,capture_output=True,text=True,timeout=5)
    broad=grep('interface WebClient');assert broad.returncode==0 and len(broad.stdout.splitlines())==2
    (repo/'src/Other.java').write_text('class Other { String s = "StreamXof("; }\n')
    subprocess.run(['git','add','src/Other.java'],cwd=repo,check=True)
    literal=grep('Stream.of(','src');assert literal.returncode==1 and not literal.stdout
    (repo/'src/Match.java').write_text('class Match { String s = "Stream.of("; }\n')
    subprocess.run(['git','add','src/Match.java'],cwd=repo,check=True)
    literal=grep('Stream.of(','src');assert literal.returncode==0 and 'src/Match.java:1:' in literal.stdout and 'Other.java' not in literal.stdout
    before=(repo/'src/WebClient.java').read_bytes()
    again=subprocess.run(['sh',str(script)],cwd=tmp,capture_output=True,text=True,timeout=5)
    assert again.returncode!=0 and (repo/'src/WebClient.java').read_bytes()==before
    return {'localGitSearchCases':5,'liveHostedSearchExecuted':False}


def main():
    with tempfile.TemporaryDirectory(prefix='youdozi-tools-') as directory:
        tmp=Path(directory)
        result={**check_http(tmp),**check_drawio(),**check_search(tmp)}
    print('[ok] Paired developer-tool snippets extracted and exercised: '+json.dumps(result))


if __name__=='__main__':main()
