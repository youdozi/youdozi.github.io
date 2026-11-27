---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-10-27-jenkins-home-backup-restore",
  "routeSlug": "2026-10-27-jenkins-home-backup-restore",
  "kind": "post",
  "title": "Jenkins Home का बैकअप जाँचें: बंद कंट्रोलर को नए वॉल्यूम में बहाल करें",
  "description": "लैब कंट्रोलर बंद करें, master.key को आर्काइव से अलग रखें और बहाली के समय अलग से कॉपी करें। नए वॉल्यूम से Jenkins शुरू करके मार्कर और मूल शुरुआती पासवर्ड जाँचें।",
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
  "sourcePath": "src/content/posts/en/2026-10-27-jenkins-home-backup-restore.md",
  "sourceSha256": "f6fcbb37f82b9829ef3535f5fee0b0fdf0b7b0ebe4e8b4f96bb3f2ff104a59b4",
  "draftSha256": "3b68d7911d89b5010f3961ffb6d5aaf69ab3c56f82942675a8ebd35f999e44d4",
  "manifestPath": ".pipeline/technical-translations/batch-141/manifest.json",
  "manifestSha256": "edfaf1b1fc31bea15d90b136c5f93dbf615cbf995ac63c9126177915c9e13875",
  "publishedAt": "2026-11-27T11:07:35.795Z",
  "updatedAt": "2026-11-27T11:07:35.795Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 217,
    "approvedAt": "2026-11-27T11:07:35.795Z",
    "basis": "The owner authorized publication of the five Hindi editions in item 141. Translation and diagram review was performed by the translator."
  }
}
---

बैकअप की जाँच के लिए उसे नए वॉल्यूम में बहाल करें और उसी वॉल्यूम से Jenkins शुरू करें। केवल आर्काइव फ़ाइल मौजूद होने से यह पता नहीं चलता कि कंट्रोलर उसे इस्तेमाल कर सकता है।

इस प्रयोग में नया कंट्रोलर किसी और काम में नहीं लगा है। उसकी होम डायरेक्टरी कॉपी करने से पहले उसे बंद करते हैं और master.key को आर्काइव से अलग रखते हैं। फिर निजी आर्काइव को दूसरे नए वॉल्यूम में बहाल करते हैं, उसी इमेज डाइजेस्ट से कंट्रोलर शुरू करते हैं और मार्कर व मूल शुरुआती पासवर्ड जाँचते हैं। तुलना में किसी भी पासवर्ड का मान नहीं छपता। प्रयोग में प्रोडक्शन कंट्रोलर, चालू जॉब या प्लगइन माइग्रेशन शामिल नहीं है।

## कंट्रोलर बंद करने से बहाल कॉपी शुरू करने तक

![लैब कंट्रोलर बंद करें, उसका वॉल्यूम कॉपी करें और अलग वॉल्यूम में बहाली जाँचें](/assets/diagrams/technical/hi-2026-10-27-jenkins-home-backup-restore.svg)

[Jenkins की बैकअप गाइड](https://www.jenkins.io/doc/book/system-administration/backing-up/) बताती है कि बैकअप में क्या रखना है और बहाली कैसे जाँचनी है। इस उदाहरण में कॉपी करते समय कंट्रोलर फ़ाइलें न लिखे, इसलिए पहले उसे बंद किया जाता है। यह बाहरी डेटाबेस, एजेंट और डेटा लिखने वाली अन्य प्रक्रियाओं का समन्वित स्नैपशॉट नहीं है।

[कंट्रोलर दोबारा बनाने के प्रयोग](/en/posts/2023-09-28-jenkins-docker-install/) से पूरी `jenkins_lab.py` लें और उसके साथ यह दूसरी फ़ाइल सहेजें। इसके लिए Python3 और Linux कंटेनर चलाने वाला सक्रिय Docker इंजन चाहिए।

### `jenkins_restore.py`

```python
import json
import tempfile
from jenkins_lab import DockerLab

with DockerLab() as lab, \
        tempfile.TemporaryDirectory(prefix='jenkins-private-backup-') as backup, \
        tempfile.TemporaryDirectory(prefix='jenkins-private-key-') as keys:
    original = lab.start()
    password = lab.password(original)
    assert password, 'Missing initial password'
    lab.cli('exec', original, 'sh', '-c', 'printf restored > /var/jenkins_home/lab-marker')
    lab.cli('stop', '-t', '30', original)
    lab.cli('run', '--rm', '--user', '0:0', '--entrypoint', 'sh',
            '--mount', f'type=volume,source={lab.home},target=/source,readonly',
            '--mount', f'type=bind,source={backup},target=/backup',
            '--mount', f'type=bind,source={keys},target=/keys', lab.image,
            '-c', 'set -e; umask 077; tar -C /source --exclude=./secrets/master.key -czpf /backup/home.tgz .; cp -p /source/secrets/master.key /keys/master.key')
    members = lab.cli('run', '--rm', '--user', '0:0', '--entrypoint', 'tar',
                      '--mount', f'type=bind,source={backup},target=/backup,readonly', lab.image,
                      '-tzf', '/backup/home.tgz')
    assert './secrets/master.key' not in members.splitlines()
    restored_home = lab.volume()
    lab.cli('run', '--rm', '--user', '0:0', '--entrypoint', 'tar',
            '--mount', f'type=bind,source={backup},target=/backup,readonly',
            '--mount', f'type=volume,source={restored_home},target=/restore', lab.image,
            '-xzpf', '/backup/home.tgz', '-C', '/restore')
    lab.cli('run', '--rm', '--user', '0:0', '--entrypoint', 'cp',
            '--mount', f'type=bind,source={keys},target=/keys,readonly',
            '--mount', f'type=volume,source={restored_home},target=/restore', lab.image,
            '-p', '/keys/master.key', '/restore/secrets/master.key')
    restored = lab.start(restored_home)
    assert lab.marker(restored) == 'restored'
    assert lab.password(restored) == password
    print(json.dumps({'image': lab.image, 'jenkins': lab.version, 'sourceStopped': True,
                      'restoredToNewVolume': True, 'masterKeyExcluded': True, 'keyCopiedSeparately': True, 'markerRestored': True,
                      'passwordRestored': True, 'result': 'passed'}))
```

इसे चलाएँ।

```sh
python3 jenkins_restore.py
```

सहायक कंटेनर फ़ाइल कॉपी करने वाले टूल को एंट्रीपॉइंट बनाते हैं, इसलिए उनमें Jenkins की दूसरी प्रक्रिया शुरू नहीं होती। वे केवल कॉपी के दौरान मूल स्वामित्व और अनुमतियाँ बनाए रखने के लिए root के रूप में चलते हैं। आर्काइव की फ़ाइल सूची में master.key नहीं होनी चाहिए। Jenkins शुरू होने से पहले एक अलग सहायक कंटेनर उस कुंजी को बहाल करता है। स्रोत कंट्रोलर बंद होने के बाद उसका वॉल्यूम केवल पढ़ने के लिए माउंट होता है। बहाली के लिए प्रयोग एक अलग वॉल्यूम बनाता है और शुरुआत में चुना गया इमेज डाइजेस्ट ही इस्तेमाल करता है।

सफल परिणाम में `sourceStopped`, `restoredToNewVolume`, `markerRestored`, `passwordRestored`, `masterKeyExcluded`, `keyCopiedSeparately` और `result: passed` मिलते हैं। बहाल कंट्रोलर को `DockerLab.start` की HTTP readiness जाँच भी पास करनी होती है। शुरुआती पासवर्ड का मेल बताता है कि यह विशेष सीक्रेट सुरक्षित रहा। इससे उपयोगकर्ता प्रबंधन का पूरा सेटअप या हर क्रेडेंशियल प्लगइन नहीं जाँचा जाता।

## आर्काइव को कंट्रोलर के निजी डेटा की तरह सँभालें

यह बहाली का अस्थायी अभ्यास है। आर्काइव में `secrets/master.key` नहीं रहती। कुंजी अलग से कॉपी होती है और आर्काइव खोलने के बाद अपनी जगह रखी जाती है। कंट्रोलर के अन्य सीक्रेट आर्काइव में रहते हैं। दोनों अस्थायी डायरेक्टरियाँ निजी हैं और प्रयोग समाप्त होने पर हट जाती हैं। आर्काइव को CI आर्टिफ़ैक्ट के रूप में अपलोड या कमिट न करें। पूरी डायरेक्टरी एक साथ कॉपी करने के इस तरीके को प्रोडक्शन की बैकअप नीति न बनाएँ।

प्रोडक्शन के लिए [कंट्रोलर की कुंजी पर Jenkins के निर्देश](https://www.jenkins.io/doc/book/system-administration/backing-up/) कहते हैं कि `master.key` को नियमित बैकअप से अलग सँभालें। बैकअप प्रक्रिया अपनाने से पहले तय करें कि कुंजी कैसे वापस मिलेगी, आर्काइव कैसे एन्क्रिप्ट होगा, कितने समय तक रखा जाएगा, किसे पहुँच मिलेगी, दूसरी मशीन पर कहाँ रखा जाएगा और बाहरी सिस्टम की स्थिति कैसे बहाल होगी। इसी मशीन पर बना अस्थायी आर्काइव टिकाऊ भंडारण की ये गारंटियाँ नहीं देता।

प्रयोग समाप्त होने पर बहाल कंट्रोलर भी हट जाता है, इसलिए अभ्यास दोहराया जा सकता है। मार्कर, सीक्रेट और HTTP जाँच पास होने से हर जॉब, प्लगइन, क्रेडेंशियल या बाहरी इंटीग्रेशन की बहाली सिद्ध नहीं होती। वास्तविक सिस्टम के बहाली अभ्यास में उसके सामान्य काम का नमूना चलाएँ और सीक्रेट को डिक्रिप्ट करके जाँचें।
