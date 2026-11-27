---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-11-20-ponytail-skill-guide",
  "routeSlug": "2026-11-20-ponytail-skill-guide",
  "kind": "post",
  "title": "Ponytail स्किल का उपयोग — Codex में छोटा सुधार करें और रिग्रेशन परीक्षण चलाएँ",
  "description": "Codex और Claude Code में Ponytail बुलाने का तरीका और Lite, Full व Ultra का अंतर जानें। Codex CLI के उदाहरण में मौजूदा फ़ंक्शन का फिर उपयोग करें और Node.js रिग्रेशन परीक्षण जाँचें।",
  "categories": [
    "ai"
  ],
  "tags": [
    "ponytail",
    "codex",
    "claude-code",
    "agent-skills",
    "refactoring",
    "nodejs"
  ],
  "sourcePath": "src/content/posts/en/2026-11-20-ponytail-skill-guide.md",
  "sourceSha256": "7b1777565ade628aa9381193123b7b19f84ba4c91e57779cba53f40b8b19b6de",
  "draftSha256": "45b690296926375da2f63f58bd3ea3b4128780c4f93e63c2a2f76ee845e0400b",
  "manifestPath": ".pipeline/technical-translations/batch-139/manifest.json",
  "manifestSha256": "0cc88a23412afe4afe8035992a38c4aa4c53a00a07184c1b7722f6376e8de0a4",
  "publishedAt": "2026-11-27T10:26:18.984Z",
  "updatedAt": "2026-11-27T10:26:18.984Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 215,
    "approvedAt": "2026-11-27T10:26:18.984Z",
    "basis": "The owner requested publication of these five Hindi editions in item 139. The translation and diagrams were self-reviewed against the Korean and English editions."
  }
}
---

**Ponytail एक स्किल है जो AI कोडिंग एजेंट को मौजूदा कोड का इस्तेमाल करके माँगा गया बदलाव पूरा करने में मदद करती है।** मान लें कि स्टॉक में एक इकाई होने पर भी लेबल में `1 items` आता है। पहले देखें कि प्रोजेक्ट में एकवचन और बहुवचन दिखाने का फ़ंक्शन पहले से है या नहीं। उसी से लेबल सुधारें और परीक्षण करें कि 0 और 2 की मात्रा पर व्यवहार पहले जैसा है।

## Codex और Claude Code में शुरुआत

यदि Codex में स्वतंत्र Ponytail स्किल पहले से स्थापित है तो चैट में `$ponytail-help` लिखकर नाम और मोड देखें। `$ponytail full` के बाद बदलने वाला व्यवहार, कायम रखने वाली शर्तें और जाँच कमांड लिखें। नीचे के अभ्यास में उपयोगकर्ता पथ `~/.agents/skills/ponytail/SKILL.md` पर स्थापित स्वतंत्र स्किल इस्तेमाल हुई। इस व्यवस्था में मोड मौजूदा बातचीत के लिए काम की प्राथमिकता तय करता है। `$ponytail off` से इसे बंद कर सकते हैं। [Codex स्किल दस्तावेज़](https://learn.chatgpt.com/docs/build-skills)

Ponytail प्रोजेक्ट एक प्लगइन भी वितरित करता है। Codex CLI के लिए शेल में नीचे के दो कमांड चलाएँ। फिर Codex खोलें और `/hooks` में जाँचें कि दोनों हुक क्या चलाते हैं। इन्हें इस्तेमाल करना हो तो समीक्षा के बाद भरोसेमंद चिह्नित करें और नई बातचीत शुरू करें। हुक चलाने वाले परिवेश के `PATH` में `node` चाहिए। [Ponytail स्थापना गाइड](https://github.com/DietrichGebert/ponytail/blob/main/INSTALL.md#codex)

```bash
codex plugin marketplace add DietrichGebert/ponytail
codex plugin add ponytail@ponytail
```

Claude Code के इनपुट में नीचे के कमांड एक-एक पंक्ति करके चलाएँ, फिर `/ponytail full` से मोड चुनें। इसके साथ `/ponytail-review` समीक्षा कमांड मिलता है। Codex प्लगइन में समीक्षा स्किल के नाम में प्लगइन का उपसर्ग दिखता है, जैसे `$ponytail:ponytail-review`। दोनों प्लगइन की स्थापना और हुक का व्यवहार सार्वजनिक दस्तावेज़ों पर आधारित है। [Claude Code स्थापना गाइड](https://github.com/DietrichGebert/ponytail/blob/main/INSTALL.md#claude-code) · [Ponytail कमांड सूची](https://github.com/DietrichGebert/ponytail#commands)

```text
/plugin marketplace add DietrichGebert/ponytail
/plugin install ponytail@ponytail
```

## Lite, Full या Ultra कब चुनें?

स्वतंत्र Codex स्किल में केवल `$ponytail` लिखने पर डिफ़ॉल्ट Full मोड लागू होता है।

| आह्वान | काम करने का तरीका | उदाहरण |
| --- | --- | --- |
| `$ponytail lite` | अनुरोध पूरा करता है और छोटा तरीका वास्तव में उपयोगी हो तो संक्षेप में बताता है। | टीम की सहमति वाला UI पाठ बदलना। |
| `$ponytail full` | कॉल करने वाला कोड और मौजूदा परीक्षण जाँचकर सबसे छोटे पूरे बदलाव से व्यवहार सुधारता है। पुष्ट परिणाम और बाकी जोखिम बताता है। | एकवचन का लेबल सुधारकर मौजूदा इनपुट भी जाँचना। |
| `$ponytail ultra` | अनुरोध पूरा करते समय ध्यान दिलाता है कि कहाँ काम का दायरा अनावश्यक रूप से बढ़ रहा है। | एक स्क्रीन की त्रुटि सुधारना और साझा UI के पुनर्निर्माण की ज़रूरत अलग से परखना। |

बदलाव छोटा रखने के लिए अनुरोध में **क्या बदलना है, क्या बनाए रखना है और जाँच कैसे होगी** लिखें। जिन व्यवहारों पर कॉल करने वाला कोड निर्भर है, जैसे अनुमति जाँच, इनपुट सत्यापन और डेटा सुरक्षा, उन्हें भी शामिल करें। स्किल एजेंट के काम करने का तरीका तय करती है। फ़ाइल लेखन और कमांड चलाने का दायरा एजेंट की अनुमतियों में तय होता है।

## अभ्यास — स्टॉक में एक इकाई हो तो `1 item` दिखाएँ

अभ्यास एक खाली रिपॉज़िटरी में Node.js 22.17.0 और Codex CLI 0.169.0 पर चला। शुरुआती स्थिति बनाने के लिए `stockLabel` में नीचे दी गई return पंक्ति रखें। `stock.test.mjs` का पहला परीक्षण पहले से था, दूसरा इस बदलाव के लिए जोड़ा गया।

```javascript
return `${count} items`;
```

**प्रॉम्प्ट का उदाहरण** `$ponytail full` stockLabel(1) के 1 items लौटाने की समस्या ठीक करो। 0 और 2 के लिए items बनाए रखो। मौजूदा formatCount का इस्तेमाल करो, stockLabel का रिग्रेशन परीक्षण जोड़ो और `node --test` चलाओ। इस अभ्यास रिपॉज़िटरी के बाहर कुछ मत बदलो और कमिट मत करो।

![अनुरोध मिलने पर stockLabel और formatCount देखें। मौजूदा formatCount इस्तेमाल करें, 0, 1 और 2 इकाइयों के लेबल जाँचें और परिणाम दर्ज करें।](/assets/diagrams/technical/hi-2026-11-20-ponytail-skill-guide.svg)

`stock.mjs` में केवल `stockLabel` का return एक्सप्रेशन बदला। यह मौजूदा `formatCount` को बुलाता है जो एकवचन और बहुवचन पहले से सँभालता है।

```javascript
export function formatCount(count, noun) {
  return `${count} ${count === 1 ? noun : noun + 's'}`;
}

export function stockLabel(count) {
  return formatCount(count, 'item');
}
```

`stock.test.mjs` में 0, 1 और 2 की मात्रा के लेबल जाँचें। दोनों फ़ाइलें एक ही निर्देशिका में रखकर `node --test` चलाएँ।

```javascript
import assert from 'node:assert/strict';
import test from 'node:test';
import { formatCount, stockLabel } from './stock.mjs';

test('formatCount handles singular and plural', () => {
  assert.equal(formatCount(1, 'item'), '1 item');
  assert.equal(formatCount(2, 'item'), '2 items');
});

test('stockLabel handles zero, one, and two items', () => {
  assert.equal(stockLabel(0), '0 items');
  assert.equal(stockLabel(1), '1 item');
  assert.equal(stockLabel(2), '2 items');
});
```

मूल कोड पर नया परीक्षण मात्रा 1 के लिए विफल हुआ। अपेक्षित लेबल `1 item` था, वास्तविक लेबल `1 items` था। सुधार के बाद यह आउटपुट मिला।

```text
ok 1 - formatCount handles singular and plural
ok 2 - stockLabel handles zero, one, and two items
# tests 2
# pass 2
# fail 0
```

यह अभ्यास दो परीक्षण और दो फ़ाइलों के बदलाव तक सीमित है। एजेंट का काम पूरा होने का संदेश मिलने पर वास्तविक `git diff` और परीक्षण के परिणाम मिलाएँ। इससे जाँच सकते हैं कि मौजूदा फ़ंक्शन इस्तेमाल हुआ और बदलाव अनुरोध के दायरे में रहा।

## बदलाव के बाद समीक्षा का दायरा तय करें

साथ की स्वतंत्र स्किल स्थापित हों तो नीचे के कमांड इस्तेमाल कर सकते हैं। कोड के किस हिस्से की समीक्षा चाहिए, यह बताने से निष्कर्षों की जाँच आसान होती है। [Ponytail कमांड सूची](https://github.com/DietrichGebert/ponytail#commands)

| आह्वान | कब इस्तेमाल करें |
| --- | --- |
| `$ponytail-review` | मौजूदा diff और संबंधित कोड की समीक्षा करता है। PR खोलने से पहले कॉल करने वाला कोड या छूटे हुए रिग्रेशन परीक्षण देखें। |
| `$ponytail-audit` | पूरी रिपॉज़िटरी को केवल पढ़कर संभावित समस्याएँ प्राथमिकता के क्रम में देता है। |
| `$ponytail-debt` | समीक्षा के लिए मौजूदा `shortcut:` और पुराने `ponytail:` कमेंट इकट्ठे करता है। |
| `$ponytail-gain` | प्रोजेक्ट की प्रकाशित बेंचमार्क रिपोर्ट दिखाता है। अपनी रिपॉज़िटरी में समय या लागत की बचत मापने के लिए अलग तुलनात्मक रन चाहिए। |
| `$ponytail-help` | स्थापित स्किल के मोड और उन्हें बुलाने का तरीका दिखाता है। |
