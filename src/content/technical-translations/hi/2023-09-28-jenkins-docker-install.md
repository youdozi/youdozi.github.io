---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2023-09-28-jenkins-docker-install",
  "routeSlug": "2023-09-28-jenkins-docker-install",
  "kind": "post",
  "title": "Docker में Jenkins: कंटेनर दोबारा बनाकर स्टार्टअप और डेटा की जाँच करें",
  "description": "इमेज के डाइजेस्ट से अस्थायी Jenkins कंट्रोलर चलाएँ। लूपबैक पर HTTP की तैयारी और उसी वॉल्यूम पर कंटेनर दोबारा बनने के बाद डेटा की जाँच करें। शुरुआती पासवर्ड लॉग में नहीं जाता।",
  "categories": [
    "jenkins"
  ],
  "tags": [
    "jenkins",
    "docker",
    "containers",
    "backup",
    "testing"
  ],
  "sourcePath": "src/content/posts/en/2023-09-28-jenkins-docker-install.md",
  "sourceSha256": "ed131abbe5537f6f1828891ac35483b44e96395c554a52b53f5c1ab6c4ff895e",
  "draftSha256": "6b6e490a8232744cc93007f238668e9c8393e52cde1ec828ee3f89fabc70b737",
  "manifestPath": ".pipeline/technical-translations/batch-144/manifest.json",
  "manifestSha256": "f2cdc48717558ad001e3a065a1fcd8bf668c42c267757c24843b091e441bad71",
  "publishedAt": "2026-11-27T12:46:07.279Z",
  "updatedAt": "2026-11-27T12:46:07.279Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 220,
    "approvedAt": "2026-11-27T12:46:07.279Z",
    "basis": "The owner authorized publication of the five Hindi editions in item 144. The translator reviewed the translations and diagrams."
  }
}
---

Jenkins की होम निर्देशिका के लिए नाम वाला वॉल्यूम लगाएँ, कंट्रोलर शुरू करें और उसका HTTP एंडपॉइंट जाँचें। फिर उसी वॉल्यूम के साथ कंटेनर दोबारा बनाएँ। सेटअप स्क्रीन खुलने से पता चलता है कि कंट्रोलर शुरू हो गया है। दूसरी बार शुरू करने पर जाँच सकते हैं कि कंटेनर बदलने के बाद होम निर्देशिका का डेटा बचा है या नहीं।

रोलिंग टैग बाद में किसी दूसरी इमेज को इंगित कर सकता है। प्रयोग के लिए एक बार इमेज का डाइजेस्ट निकालें और जनरेट हुआ शुरुआती पासवर्ड गोपनीय रखें। यह अस्थायी प्रयोग पासवर्ड छापे बिना तुलना का परिणाम बताता है।

## एक प्रयोग के लिए इमेज तय करें

![लूपबैक पर Jenkins शुरू करें और कंटेनर दोबारा बनाकर उसी वॉल्यूम के डेटा की जाँच करें](/assets/diagrams/technical/hi-2023-09-28-jenkins-docker-install.svg)

Python 3 और Linux कंटेनर चलाने वाले Docker इंजन का उपयोग करें। [Jenkins इमेज के निर्देश](https://github.com/jenkinsci/docker/blob/master/README.md) में `jenkins/jenkins` और उसकी होम निर्देशिका का विवरण है। यह प्रयोग `jenkins/jenkins:lts-jdk21` को पुल करता है और उसका रिपॉज़िटरी डाइजेस्ट निकालता है। उस रन का हर कंट्रोलर रोलिंग टैग को फिर से खोजे बिना उसी डाइजेस्ट का उपयोग करता है। रन दोहराने के लिए डाइजेस्ट और प्रतिक्रिया में मिला Jenkins संस्करण दर्ज करें। टैग किसी एक स्थायी रिलीज़ की पहचान नहीं है।

Docker में [पोर्ट प्रकाशित करने के नियम](https://docs.docker.com/engine/network/port-publishing/) तय करते हैं कि मैप किए गए पोर्ट तक कौन पहुँच सकता है। स्क्रिप्ट `127.0.0.1::8080` माँगती है ताकि Docker लूपबैक से जुड़ा होस्ट पोर्ट चुने। फिर स्क्रिप्ट लौटाई गई बाइंडिंग जाँचती है। यह एजेंट पोर्ट प्रकाशित नहीं करती और Docker सॉकेट भी माउंट नहीं करती। यह स्थानीय कंट्रोलर का प्रयोग है। Docker बिल्ड एजेंट और दूरस्थ HTTPS सेवा की स्थापना इसके दायरे से बाहर हैं।

## पूरा प्रयोग चलाएँ

यह पूरी फ़ाइल `jenkins_lab.py` के नाम से सहेजें। यह अपने वॉल्यूम और कंटेनर अलग-अलग अनूठे नामों से बनाती है। जाँच खत्म होने पर कॉन्टेक्स्ट मैनेजर प्रयोग के संसाधनों को हटा देता है, भले ही तैयारी या डेटा की जाँच विफल हो जाए। इस अस्थायी उदाहरण में प्रोडक्शन वॉल्यूम का इस्तेमाल न करें।

### `jenkins_lab.py`

```python
import http.client
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
import uuid


class DockerLab:
    def __init__(self):
        self.prefix = 'jenkins-proof-' + uuid.uuid4().hex[:12]
        self.containers, self.volumes = [], []

    def cli(self, *args):
        return subprocess.check_output(['docker', *args], text=True, stderr=subprocess.PIPE).strip()

    def volume(self):
        name = f'{self.prefix}-home-{len(self.volumes)}'
        existing = subprocess.run(['docker', 'volume', 'inspect', name], capture_output=True)
        if existing.returncode == 0:
            raise RuntimeError('Refusing an existing volume')
        self.cli('volume', 'create', name)
        self.volumes.append(name)
        return name

    def __enter__(self):
        self.cli('info')
        requested = os.environ.get('JENKINS_IMAGE', 'jenkins/jenkins:lts-jdk21')
        self.cli('pull', requested)
        self.image = self.cli('image', 'inspect', requested, '--format', '{{index .RepoDigests 0}}')
        if '@sha256:' not in self.image:
            raise RuntimeError('Expected a pulled repository digest')
        self.home = self.volume()
        return self

    def start(self, volume=None):
        name = f'{self.prefix}-controller-{len(self.containers)}'
        self.cli('run', '-d', '--name', name, '-p', '127.0.0.1::8080',
                 '--mount', f'type=volume,source={volume or self.home},target=/var/jenkins_home', self.image)
        self.containers.append(name)
        port = self.cli('port', name, '8080/tcp')
        if not port.startswith('127.0.0.1:'):
            raise RuntimeError('Expected a loopback binding')
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            try:
                with urllib.request.urlopen(f'http://{port}/login', timeout=5) as response:
                    self.version = response.headers.get('X-Jenkins')
                    if response.status == 200 and self.version and b'Jenkins' in response.read():
                        return name
            except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException):
                pass
            time.sleep(2)
        raise RuntimeError('Jenkins login was not ready within 180 seconds')

    def password(self, name):
        return self.cli('exec', name, 'cat', '/var/jenkins_home/secrets/initialAdminPassword')

    def marker(self, name):
        return self.cli('exec', name, 'cat', '/var/jenkins_home/lab-marker')

    def __exit__(self, *_):
        for name in reversed(self.containers):
            subprocess.run(['docker', 'rm', '-f', name], capture_output=True)
        for name in reversed(self.volumes):
            subprocess.run(['docker', 'volume', 'rm', name], capture_output=True)


if __name__ == '__main__':
    with DockerLab() as lab:
        first = lab.start()
        password = lab.password(first)
        assert password, 'Missing initial password'
        lab.cli('exec', first, 'sh', '-c', 'printf kept > /var/jenkins_home/lab-marker')
        lab.cli('rm', '-f', first)
        second = lab.start()
        assert lab.marker(second) == 'kept'
        assert lab.password(second) == password
        print(json.dumps({'image': lab.image, 'jenkins': lab.version, 'recreated': True,
                          'markerPersisted': True, 'passwordPersisted': True, 'result': 'passed'}))
```

Docker डेमन चल रहा हो तो यह कमांड चलाएँ।

```sh
python3 jenkins_lab.py
```

कंट्रोलर दोनों बार शुरू होने पर अधिकतम 180 सेकंड तक `/login` पर HTTP 200, `X-Jenkins` हेडर और प्रतिक्रिया के मुख्य भाग में `Jenkins` की प्रतीक्षा होती है। इस समय-सीमा के भीतर कनेक्शन रीसेट, अस्थायी HTTP त्रुटि या अधूरे HTTP हैंडशेक पर फिर प्रयास होता है। जाँच एक पहचान चिह्न लिखती है, शुरुआती पासवर्ड को बिना दिखाए पढ़ती है, पहला कंटेनर बदलती है और दोनों मान फिर जाँचती है। परिणाम में `recreated`, `markerPersisted`, `passwordPersisted` और `result: passed` मिलें तो ये चुनी हुई जाँचें सफल हुई हैं। JSON में डाइजेस्ट और वास्तविक Jenkins संस्करण भी दर्ज होते हैं, इसलिए इमेज पुल का काल्पनिक लॉग लिखने की ज़रूरत नहीं है।

प्रयोग Jenkins को अनलॉक नहीं करता, प्लगइन स्थापित नहीं करता, व्यवस्थापक खाता बनाने की प्रक्रिया पूरी नहीं करता और कोई जॉब नहीं चलाता। इसकी तैयारी की जाँच लॉगिन पन्ने के HTTP उत्तर तक सीमित है। यदि Mac पर Docker इंजन नहीं चल रहा है, तो पहले अपना चुना हुआ इंजन शुरू करें। अकेले Docker CLI से यह प्रयोग नहीं चल सकता।

## स्थापना और डेटा बने रहने की अलग जाँचें

इंटरैक्टिव स्थापना के लिए [आधिकारिक सेटअप विज़ार्ड](https://www.jenkins.io/doc/book/installing/docker/) के निर्देशों से व्यवस्थापक खाता बनाएँ। अपने कंट्रोलर में `/var/jenkins_home/secrets/initialAdminPassword` से शुरुआती पासवर्ड पढ़ें। उदाहरण का पासवर्ड इस्तेमाल न करें और पासवर्ड वाले कंट्रोलर लॉग प्रकाशित न करें। स्क्रिप्ट अंत में अपने संसाधन हटा देती है, इसलिए लगातार इस्तेमाल के लिए Jenkins स्थापित करने हेतु इसे न चलाएँ।

कंटेनर हटाने के बाद भी [नाम वाला Docker वॉल्यूम](https://docs.docker.com/engine/storage/volumes/) रह सकता है, लेकिन वॉल्यूम खोने पर उसका डेटा भी चला जाता है। बैकअप की जाँच के लिए [रुके हुए वॉल्यूम के बैकअप और पुनर्स्थापन का प्रयोग](/hi/posts/2026-10-27-jenkins-home-backup-restore/) इसी इमेज और दूसरे गंतव्य वॉल्यूम का उपयोग करता है। इस ब्लॉग की प्रकाशन प्रक्रिया [Astro में Draft PR का कार्यप्रवाह](/hi/posts/2026-04-07-jekyll-github-actions-content-pipeline/) में दी गई है। Jenkins का यह उदाहरण उस प्रक्रिया की जगह नहीं लेता।
