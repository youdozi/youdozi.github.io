---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-11-27-droiddesk-android-linux-desktop",
  "routeSlug": "2026-11-27-droiddesk-android-linux-desktop",
  "kind": "post",
  "title": "DroidDesk के भीतर · Android फ़ोन पर Linux डेस्कटॉप कैसे चलता है?",
  "description": "अलग APK और Termux की इंस्टॉलेशन स्क्रिप्ट में प्रोग्राम चलाने और डेस्कटॉप दिखाने के तरीके अलग हैं। अपने फ़ोन पर पहला काम आज़माने से पहले इन्हें समझें।",
  "categories": [
    "tips"
  ],
  "tags": [
    "android",
    "linux",
    "termux"
  ],
  "sourcePath": "src/content/posts/en/2026-11-27-droiddesk-android-linux-desktop.md",
  "sourceSha256": "656b9e1b21a758a366d894876650b607e9bd2eadcb535e4a0565a68566807a1f",
  "draftSha256": "a52104cc3ef2cd9da708542b9d11c169874812319b2b8146a02e5b462e5e4e6b",
  "manifestPath": ".pipeline/technical-translations/batch-130/manifest.json",
  "manifestSha256": "155408f4218bb7fd2e43ec0f8dcb31522024a85ed96fb84e2f9768840357e28c",
  "publishedAt": "2026-11-27T06:13:21.434Z",
  "updatedAt": "2026-11-27T06:13:21.434Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 207,
    "approvedAt": "2026-11-27T06:13:21.434Z",
    "basis": "Explicit user request to publish the approved DroidDesk manuscript from item 129 in all nine languages (item 130)."
  }
}
---

क्या किसी पुराने Android फ़ोन से कीबोर्ड जोड़कर Linux के एडिटर और ब्राउज़र में काम किया जा सकता है? DroidDesk एक ओपन सोर्स प्रोजेक्ट है जो Android पर Linux डेस्कटॉप चलाता है। इंस्टॉल करने का तरीका चुनने से पहले एक फ़र्क़ समझना ज़रूरी है। अलग से मिलने वाला APK और Termux की इंस्टॉलेशन स्क्रिप्ट डेस्कटॉप चलाने के लिए अलग रास्ते अपनाते हैं।

यह लेख orailnoor/DroidDesk v1.3.1 के रिलीज़ नोट्स और सोर्स कोड पर आधारित है। इन्हें 2026-11-27 को देखा गया था। किसी असली फ़ोन पर APK इंस्टॉल करके या अलग-अलग ऐप का प्रदर्शन मापकर परीक्षण नहीं किया गया। [रिलीज़ नोट्स](https://github.com/orailnoor/DroidDesk/releases/tag/v1.3.1)

## APK और Termux स्क्रिप्ट में क्या फ़र्क़ है?

| इंस्टॉलेशन का तरीका | प्रोग्राम कहाँ चलता है | डेस्कटॉप कैसे दिखता है |
| --- | --- | --- |
| अलग APK, रूट ऐक्सेस के बिना | डिफ़ॉल्ट डेस्कटॉप ऐप के अपने Termux में चलता है। चाहें तो Debian इंस्टॉल करके PRoot से चला सकते हैं | ऐप में शामिल Termux:X11 |
| अलग APK, रूट ऐक्सेस के साथ | ARM64 वाला Ubuntu फ़ाइल सिस्टम chroot में चलता है | ऐप में शामिल Termux:X11 |
| Termux की इंस्टॉलेशन स्क्रिप्ट | अलग से इंस्टॉल किया गया Termux और डिस्ट्रीब्यूशन के पैकेज के लिए PRoot | अलग Termux:X11 ऐप या वैकल्पिक VNC |

![अलग APK अपने साथ आए Termux:X11 पर डेस्कटॉप दिखाता है। Termux स्क्रिप्ट इसके लिए अलग Termux:X11 ऐप या VNC का इस्तेमाल करती है।](/assets/diagrams/technical/hi-2026-11-27-droiddesk-android-linux-desktop.svg)

README के मुताबिक बिना रूट ऐक्सेस के APK में PRoot का इस्तेमाल नहीं होता। डिफ़ॉल्ट डेस्कटॉप के लिए यह सही है, क्योंकि वह सीधे Termux में चलता है। लेकिन v1.3.1 के LinuxRuntime में Debian इंस्टॉल करने का विकल्प और PRoot लॉन्चर भी है। इसलिए एक ही ऐप में डिफ़ॉल्ट डेस्कटॉप से चलाए गए प्रोग्राम और Debian में चलाए गए प्रोग्राम को अलग परिवेश मिल सकते हैं। [README](https://github.com/orailnoor/DroidDesk/blob/v1.3.1/README.md) · [LinuxRuntime](https://github.com/orailnoor/DroidDesk/blob/v1.3.1/app/android/app/src/main/kotlin/com/orailnoor/droiddesk/runtime/LinuxRuntime.kt) · [ChrootRuntime](https://github.com/orailnoor/DroidDesk/blob/v1.3.1/app/android/app/src/main/kotlin/com/orailnoor/droiddesk/runtime/ChrootRuntime.kt)

## अपने फ़ोन पर क्या इस्तेमाल कर सकते हैं?

शुरुआत किसी एक ऐसे प्रोग्राम से करें जिसकी आपको ज़रूरत है। प्रोजेक्ट ने Firefox, LibreOffice और VS Code जैसे उदाहरण दिए हैं। v1.3.1 के रिलीज़ नोट्स में इंस्टॉल करने या शुरू करने में आने वाली गड़बड़ियों के सुधार भी दर्ज हैं। इनमें Firefox के लिए ज़रूरी एक पैकेज और VS Code भी शामिल हैं। एडिटर का आइकन दिखने के बाद जाँचें कि रोज़ इस्तेमाल होने वाले एक्सटेंशन, इनपुट मेथड और फ़ाइल पाथ भी काम करते हैं या नहीं। [रिलीज़ नोट्स](https://github.com/orailnoor/DroidDesk/releases/tag/v1.3.1)

ग्राफ़िक्स का अनुभव भी डिवाइस के हिसाब से बदल सकता है। सोर्स में Adreno के लिए Turnip और Zink इस्तेमाल करने का रास्ता है, और llvmpipe से सॉफ़्टवेयर रेंडरिंग का भी। Blender जैसे ग्राफ़िक्स पर भारी दबाव डालने वाले ऐप के लिए देखें कि आपके फ़ोन पर ऐक्सेलरेशन काम कर रहा है या नहीं और असली प्रोजेक्ट पर काम कितना सहज है। अगर आप PRoot में सॉफ़्टवेयर बिल्ड करेंगे, तो ध्यान रखें कि बार-बार फ़ाइलें पढ़ने या लिखने वाले काम में अतिरिक्त समय लग सकता है। [PRoot की सीमाएँ](https://github.com/termux/proot-distro#limitations)

बाहरी मॉनिटर इस्तेमाल करने से पहले देखें कि फ़ोन USB-C से वीडियो आउटपुट देता है या नहीं। प्रोजेक्ट के दस्तावेज़ में बताए Raspberry Pi वाले सेटअप में Pi, Termux स्क्रिप्ट से मिलने वाला VNC सेशन लेकर उसे मॉनिटर पर दिखाता है। अलग APK में शामिल X11 डिस्प्ले का तरीका इससे अलग है। [मॉनिटर जोड़ने का तरीका](https://github.com/orailnoor/DroidDesk/blob/v1.3.1/README.md#for-monitor-output--optional-)

## पहली बार कौन-सा काम आज़माएँ?

अगर आपके पास ARM64 वाला Android डिवाइस है, तो प्रोजेक्ट के आधिकारिक रिलीज़ पेज पर APK देखें और पहले फ़ोन की स्क्रीन पर ही आज़माएँ। उदाहरण के लिए एडिटर में कुछ कोरियाई पाठ लिखें, फ़ाइल सेव करें, सेशन दोबारा खोलें और उसी फ़ाइल को लोड करें। अगर यह काम करता है तो कीबोर्ड और माउस या बाहरी मॉनिटर जोड़कर अपना रोज़मर्रा का काम करके देखें। DroidDesk की ख़ूबी यही है कि आप अपने मौजूदा फ़ोन पर आज़मा सकते हैं कि Linux के कौन-से औज़ार आपके काम आते हैं। दस्तावेज़ों के लिए पहले टाइप करना और सेव करना जाँचें, डेवलपमेंट के लिए ज़रूरी पैकेज और एक्सटेंशन देखें, और ग्राफ़िक्स के लिए ऐक्सेलरेशन और स्क्रीन की प्रतिक्रिया परखें। [Android बिल्ड सेटिंग](https://github.com/orailnoor/DroidDesk/blob/v1.3.1/app/android/app/build.gradle.kts)

[Mac पर Docker Desktop का डिस्क इस्तेमाल जाँचें](../2026-11-27-docker-desktop-mac-disk-space/)
