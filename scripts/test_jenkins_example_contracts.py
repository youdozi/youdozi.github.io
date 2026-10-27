from pathlib import Path
import http.client
import re
import types
import unittest
from unittest.mock import Mock,patch
import urllib.error


class JenkinsArticleContracts(unittest.TestCase):
    def module(self):
        paired=[]
        for lang in ['en','ko']:
            text=Path(f'src/content/posts/{lang}/2023-09-28-jenkins-docker-install.md').read_text()
            blocks=re.findall(r'^### `jenkins_lab.py`\n\n```python\n([\s\S]*?)\n```',text,re.M)
            self.assertEqual(len(blocks),1);paired.append(blocks[0])
        self.assertEqual(*paired)
        module=types.ModuleType('article_jenkins_lab')
        exec(compile(paired[0],'article/jenkins_lab.py','exec'),module.__dict__)
        return module

    def test_transient_connections_retry_until_real_readiness_contract(self):
        module=self.module();lab=module.DockerLab();lab.image='test-digest';lab.home='test-home'
        lab.cli=Mock(side_effect=['container-id','127.0.0.1:49152'])
        response=Mock();response.status=200;response.headers={'X-Jenkins':'test-version'};response.read.return_value=b'Jenkins login'
        opened=Mock();opened.__enter__=Mock(return_value=response);opened.__exit__=Mock(return_value=False)
        errors=[ConnectionResetError('startup'),urllib.error.URLError('refused'),
                urllib.error.HTTPError('http://localhost',503,'starting',{},None),
                http.client.RemoteDisconnected('not ready'),opened]
        with patch.object(module.urllib.request,'urlopen',side_effect=errors) as get,patch.object(module.time,'sleep'):
            self.assertEqual(lab.start(),'{}-controller-0'.format(lab.prefix))
        self.assertEqual(get.call_count,5);self.assertEqual(lab.version,'test-version')
        self.assertEqual(len(lab.containers),1)

    def test_missing_header_times_out_and_programming_errors_are_not_retried(self):
        module=self.module();lab=module.DockerLab();lab.image='test';lab.home='test'
        lab.cli=Mock(side_effect=['id','127.0.0.1:49152'])
        response=Mock();response.status=200;response.headers={}
        opened=Mock();opened.__enter__=Mock(return_value=response);opened.__exit__=Mock(return_value=False)
        with patch.object(module.urllib.request,'urlopen',return_value=opened),patch.object(module.time,'monotonic',side_effect=[0,0,181]),patch.object(module.time,'sleep'):
            with self.assertRaisesRegex(RuntimeError,'not ready'):lab.start()
        lab.cli=Mock(side_effect=['id','127.0.0.1:49152'])
        with patch.object(module.urllib.request,'urlopen',side_effect=ValueError('bad request')):
            with self.assertRaisesRegex(ValueError,'bad request'):lab.start()
