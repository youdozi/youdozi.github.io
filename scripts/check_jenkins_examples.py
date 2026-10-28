from pathlib import Path
import subprocess,json,re,sys,tempfile,os
keys=['2023-09-28-jenkins-docker-install','2026-10-27-jenkins-home-backup-restore']
files={}
for key in keys:
    paired=[]
    for lang in ['en','ko']:
        source=Path(f'src/content/posts/{lang}/{key}.md').read_text()
        blocks=re.findall(r'^### `([^`]+)`\n\n```python\n([\s\S]*?)\n```',source,re.M)
        assert len(blocks)==1
        paired.append(dict(blocks))
    assert paired[0]==paired[1],'Paired complete files differ'
    files.update(paired[0])
assert set(files)=={'jenkins_lab.py','jenkins_restore.py'}
with tempfile.TemporaryDirectory(prefix='jenkins-article-') as directory:
    for name,code in files.items():Path(directory,name).write_text(code+'\n')
    env=os.environ.copy(); selected_image=None
    print(json.dumps({'requestedJenkinsImage':env.get('JENKINS_IMAGE','jenkins/jenkins:lts-jdk21')}),flush=True)
    for name in files:
        result=subprocess.run([sys.executable,str(Path(directory,name))],capture_output=True,text=True,timeout=600,env=env)
        if result.returncode:raise RuntimeError(f'{name} failed: {result.stderr}')
        report=json.loads(result.stdout)
        assert report['result']=='passed' and '@sha256:' in report['image']
        if selected_image is None:
            selected_image=report['image'];env['JENKINS_IMAGE']=selected_image
        assert report['image']==selected_image,'Both examples must use the same image digest'
        required=['recreated','markerPersisted','passwordPersisted'] if name=='jenkins_lab.py' else ['sourceStopped','restoredToNewVolume','markerRestored','passwordRestored','masterKeyExcluded','keyCopiedSeparately']
        assert all(report.get(field) is True for field in required)
        print(json.dumps({'example':name,**report}))
