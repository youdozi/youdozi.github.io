#!/usr/bin/env python3
"""Execute paired Ruby article probes in temporary build/bundle directories."""
from pathlib import Path
import argparse,json,os,re,shlex,subprocess,tempfile
KEYS=['2023-09-04-jekyll-install','2026-04-07-ruby-rbenv-jekyll-build-troubleshooting']
def extract(lang):
    text=Path(f'src/content/posts/{lang}/{KEYS[0]}.md').read_text()
    files=dict(re.findall(r'^### `([^`]+)`\n\n```ruby\n([\s\S]*?)\n```',text,re.M))
    assert set(files)=={'Gemfile','jekyll_probe.rb'}
    text=Path(f'src/content/posts/{lang}/{KEYS[1]}.md').read_text()
    blocks=re.findall(r'^```ruby\n([\s\S]*?)\n```',text,re.M)
    assert len(blocks)==1
    return {**files,'native_probe.rb':blocks[0]}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--install',action='store_true',help='Install the legacy fixture bundle into temporary storage');args=parser.parse_args()
    files=extract('en');assert files==extract('ko'),'Paired files differ'
    assert subprocess.check_output(['ruby','-e','print RUBY_VERSION'],text=True)=='3.2.2','This legacy reproduction requires Ruby3.2.2'
    with tempfile.TemporaryDirectory(prefix='ruby-article-') as directory:
        root=Path(directory)
        for name,code in files.items():(root/name).write_text(code+'\n')
        env={**os.environ,'BUNDLE_GEMFILE':str(root/'Gemfile'),'BUNDLE_USER_HOME':str(root/'bundler-home')}
        if args.install:
            env['BUNDLE_PATH']=str(root/'gems')
            command=['bundle','install','--jobs','4','--retry','2']
        else:command=['bundle','lock','--local']
        subprocess.run(command,env=env,check=True,timeout=240)
        run=subprocess.run(['bundle','exec','ruby',str(root/'jekyll_probe.rb')],env=env,check=True,capture_output=True,text=True,timeout=60)
        data=json.loads(run.stdout);assert data=={'ruby':'3.2.2','jekyll':'3.9.3','pages':2,'result':'passed'},data
        print('[ok] Declared bundle rendered two temporary pages, their heading and link.')
        print((root/'Gemfile.lock').read_text())
        probe_env=os.environ.copy();probe_env['CXX']='c++';probe_env['PROBE_CXXFLAGS']=''
        if os.uname().sysname=='Darwin':
            sdk=subprocess.check_output(['xcrun','--show-sdk-path'],text=True).strip();headers=str(Path(sdk)/'usr/include/c++/v1');assert Path(headers).is_dir()
            probe_env['PROBE_CXXFLAGS']=shlex.join(['-isysroot',sdk,'-isystem',headers])
        run=subprocess.run(['ruby',str(root/'native_probe.rb')],env=probe_env,check=True,capture_output=True,text=True,timeout=60)
        data=json.loads(run.stdout);assert data['output']=='42' and data['result']=='passed'
        print('[ok] Temporary C++17 compilation/execution:',json.dumps(data))
        for compiler in ['',str(root/'missing-compiler')]:
            result=subprocess.run(['ruby',str(root/'native_probe.rb')],env={**probe_env,'CXX':compiler},capture_output=True,text=True,timeout=30)
            assert result.returncode!=0,'Invalid compiler must fail'
        print('[ok] Empty and missing compiler commands fail. No Ruby/config/SDK installation changed.')
if __name__=='__main__':main()
