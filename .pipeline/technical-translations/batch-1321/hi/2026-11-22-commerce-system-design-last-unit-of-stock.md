---
{
  "state": "draft",
  "language": "hi",
  "translationKey": "2026-11-22-commerce-system-design-last-unit-of-stock",
  "title": "ई-कॉमर्स सिस्टम में आखिरी इकाई कौन खरीद सकता है?",
  "description": "एक ही इकाई के लिए दो ऑर्डर आने पर SKU का आरक्षण, भुगतान का मिलान और आरक्षण छूटने के बाद रिफ़ंड माँगने की प्रक्रिया समझें।",
  "sourcePath": "src/content/posts/en/2026-11-22-commerce-system-design-last-unit-of-stock.md",
  "sourceSha256": "63b33b1222e2cc6c885b4f2d63fb1a3f2727041b8710e7bf8ed7b335b6f8b9d6"
}
---

**जब दो ग्राहक आखिरी इकाई खरीदने की कोशिश करें, तो उसे एक ही ऑर्डर के लिए आरक्षित किया जा सकना चाहिए।** स्टॉक आरक्षित करने के बाद भुगतान प्रदाता का जवाब खो जाए तो भुगतान की पुष्टि तक ऑर्डर लंबित रहता है। आरक्षण छोड़ने के बाद भुगतान की पुष्टि हो तो ऑर्डर रद्द ही रहता है और रिफ़ंड का अनुरोध किया जाता है। एक खरीद को शुरू से अंत तक देखने से समझ आता है कि कैटलॉग, स्टॉक, ऑर्डर और भुगतान में से कौन किस डेटा का ज़िम्मेदार है।

इस उदाहरण में एक विक्रेता अपना भौतिक सामान बेचता है, हर ऑर्डर का भुगतान एक बार कोरियाई वॉन (KRW) में लेता है और एक ही गोदाम से भेजता है। रद्दीकरण और रिफ़ंड की चर्चा अनिश्चित या देर से मिले भुगतान परिणाम तक सीमित है। कई विक्रेताओं का निपटारा, आंशिक शिपमेंट और वापसी अलग डिज़ाइन के विषय हैं।

## पेज पर दिखता स्टॉक और ऑर्डर के लिए आरक्षित स्टॉक

**उत्पाद** कैटलॉग की वह प्रविष्टि है जिसे ग्राहक देखता है। **SKU** वह इकाई है जिसके हिसाब से ऑर्डर और स्टॉक दर्ज होते हैं। एक ही कीबोर्ड के सफ़ेद और काले विकल्पों के SKU अलग हैं। उत्पाद पेज पर उस समय की उपलब्धता दिखती है जब स्टॉक पढ़ा गया था। स्टॉक मॉड्यूल जवाब न दे तो भी उत्पाद दिखाएँ और मात्रा की जगह “स्टॉक की जाँच हो रही है” लिखें। इस डिज़ाइन में कार्ट में डालने से स्टॉक आरक्षित नहीं होता।

| ज़िम्मेदारी | किस डेटा में बदलाव कर सकता है | उदाहरण |
| --- | --- | --- |
| कैटलॉग और कीमत | उत्पाद, SKU, बिक्री की स्थिति, मौजूदा प्रति इकाई कीमत | काले कीबोर्ड `KB-BLK` की कीमत बदलना |
| स्टॉक | गोदामवार वास्तविक स्टॉक, आरक्षण और शिपमेंट का आवंटन | किसी ऑर्डर के लिए एक `KB-BLK` आरक्षित करना |
| ऑर्डर | खरीदार, खरीद के समय की ऑर्डर लाइनें और रकम, ऑर्डर की स्थिति | ऑर्डर `O-42` में मात्रा, इकाई कीमत, आवंटित छूट और शिपिंग शुल्क सहेजना |
| भुगतान | भुगतान प्रयास, प्रदाता की लेनदेन ID, भुगतान और रिफ़ंड की स्थिति | प्रयास `P-1` के लिए प्रदाता के परिणाम का मिलान |
| शिपमेंट | माल भेजने के अनुरोध और उनकी प्रगति | भुगतान और स्टॉक आवंटन के बाद गोदाम से सामान चुनना |

भुगतान से ठीक पहले सर्वर जाँचता है कि आइटम अब भी बिक्री पर है और उसकी कीमत क्या है। खरीदार की पहचान प्रमाणित सेशन से होती है। सर्वर अपने मूल्य, छूट और शिपिंग नियमों से रकम निकालता है। यदि कार्ट में डालते समय काले कीबोर्ड की कीमत 39,000 वॉन थी और अब 42,000 वॉन है, तो नई कीमत दिखाकर ग्राहक की सहमति फिर लें। ऑर्डर बनाते समय सर्वर जाँचता है कि लागू कीमत का संस्करण वही है जिसे ग्राहक ने स्वीकार किया था। SKU, विकल्प का नाम, मात्रा, इकाई कीमत, छूट, शिपिंग शुल्क और मुद्रा ऑर्डर में सहेजें। नई कीमत 42,000 वॉन में 2,000 वॉन की छूट और 3,000 वॉन शिपिंग जोड़ने पर प्रदाता को 43,000 वॉन का अनुरोध जाएगा। अगले दिन उत्पाद का नाम या कीमत बदलने पर भी स्वीकृत ऑर्डर की रकम वही दिखनी चाहिए। [Spring Boot में उत्पाद खोजने के उदाहरण (अंग्रेज़ी)](/en/posts/2026-11-22-spring-boot-4-2-restclient-migration/) में पेज दिखाने से आगे बढ़कर ऑर्डर लेते समय ये जाँचें जुड़ती हैं।

## एक ट्रांज़ैक्शन में क्या रखें?

कैटलॉग, स्टॉक, ऑर्डर और भुगतान रिकॉर्ड के लिए **एक ही एप्लिकेशन में अलग मॉड्यूल** से शुरुआत करें। सबका डेटाबेस एक है और हर मॉड्यूल अपनी तालिकाओं में बदलाव के नियम संभालता है। इससे ऑर्डर और आरक्षण एक स्थानीय ट्रांज़ैक्शन में कमिट हो सकते हैं। बाहरी भुगतान प्रदाता को उसके बाद कॉल करें।

1. **ऑर्डर बनाएँ और स्टॉक आरक्षित करें।** खरीदार और ऑर्डर अनुरोध कुंजी से दोहराए गए अनुरोध पहचानें। एक ही कुंजी के साथ अलग डेटा आए तो उसे टकराव मानें। स्टॉक मॉड्यूल SKU की पंक्ति लॉक करके या शर्त वाला अपडेट चलाकर उपलब्ध मात्रा जाँचता है और आरक्षण करता है। कई SKU हों तो सभी मिलने पर ही ऑर्डर लाइनें, आरक्षण और भुगतान प्रयास साथ सहेजें। एक भी आइटम कम हो तो पूरा ट्रांज़ैक्शन रोलबैक करें और स्टॉक की कमी की सूचना दें। भुगतान अनुरोध फिर शुरू करने के लिए ज़रूरी काम भी उसी स्थानीय कमिट में दर्ज करें।
2. **भुगतान प्रदाता को कॉल करें।** सहेजे गए भुगतान प्रयास की ID से जुड़ी प्रदाता की इडेम्पोटेंसी कुंजी के साथ अनुरोध भेजें। कॉल के तुरंत बाद सर्वर बंद हो जाए तो रिकॉर्ड खोजकर उसी प्रयास का मिलान संभव होना चाहिए। जवाब खो जाए तो प्रदाता से मौजूदा लेनदेन की स्थिति पूछें। अनुरोध तभी दोबारा भेजें जब समान कुंजी और समान इनपुट के लिए प्रदाता की गारंटी लागू हो। परिणाम अनिश्चित रहते हुए नया प्रयास न बनाएँ। [Stripe में इडेम्पोटेंट अनुरोध](https://docs.stripe.com/api/idempotent_requests)
3. **परिणाम लागू करें।** वेबहुक का हस्ताक्षर सत्यापित करके इवेंट दर्ज करें या सर्वर से प्रदाता के लेनदेन की स्थिति पूछें। ऑर्डर, भुगतान प्रयास, व्यापारी खाता, रकम और मुद्रा का मिलान करें। ऑर्डर और आरक्षण लॉक करके उनकी मौजूदा स्थितियाँ पढ़ें। भुगतान की स्थिति, स्टॉक का बदलाव और अगला काम एक ट्रांज़ैक्शन में सहेजें। माल भेजने या रिफ़ंड देने का अनुरोध उसी कमिट में आउटबॉक्स में लिखें। [Stripe में वेबहुक डिलीवरी के नियम](https://docs.stripe.com/webhooks#event-delivery-behaviors) · [AWS का ट्रांज़ैक्शनल आउटबॉक्स पैटर्न](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)

यहाँ **उपलब्ध स्टॉक = वास्तविक स्टॉक − सक्रिय आरक्षण − शिपमेंट के लिए आवंटित मात्रा** है। भुगतान की पुष्टि पर आरक्षित मात्रा घटाएँ और उतनी ही मात्रा शिपमेंट के आवंटन में जोड़ें। माल भेजते समय वास्तविक और आवंटित दोनों मात्राएँ घटाएँ। आखिरी इकाई के लिए एक साथ दो ऑर्डर आएँ तो पहला आरक्षण कमिट होने के बाद दूसरे ऑर्डर को उपलब्ध मात्रा शून्य दिखनी चाहिए। वास्तविक डेटाबेस में ट्रांज़ैक्शन एक साथ चलाकर यह नियम जाँचें।

## भुगतान अनिश्चित हो या उसकी पुष्टि देर से आए

![सत्यापित भुगतान परिणाम और ऑर्डर की स्थिति पढ़ें। अनिश्चित परिणाम पर आरक्षण बनाए रखें। बिना शुल्क लेनदेन बंद होने की पुष्टि पर उसे छोड़ें। भुगतान सफल हो तो स्टॉक आरक्षित होने पर शिपमेंट और पहले ही छोड़े जाने पर रिफ़ंड माँगें। वही परिणाम फिर लागू करने से काम दोबारा नहीं बनता।](2026-11-22-commerce-system-design-last-unit-of-stock.svg)

चित्र स्टॉक आरक्षित होने के बाद भुगतान परिणाम लागू करने का क्रम दिखाता है। सहेजी गई भुगतान स्थिति पहले से `PAID` या `REFUND_PENDING` हो तो कोड वही स्थिति रखता है और आगे कोई काम नहीं जोड़ता।

ऑर्डर, भुगतान और आरक्षण की अलग-अलग स्थितियाँ हैं। दुकान का पेज उन्हें मिलाकर ग्राहक को समझ आने वाला संदेश दिखाता है। उदाहरण के लिए, प्रदाता के जवाब में देरी हो तो ऑर्डर `PENDING_PAYMENT`, भुगतान `UNKNOWN` और आरक्षण `HELD` रहता है। ग्राहक को “भुगतान की पुष्टि हो रही है” दिखाएँ और उसी ऑर्डर की स्थिति फिर देखने दें।

| परिस्थिति | सहेजी जाने वाली स्थिति और अगला काम |
| --- | --- |
| भुगतान की पुष्टि, स्टॉक आरक्षित | ऑर्डर `CONFIRMED`, भुगतान `PAID`, स्टॉक `ALLOCATED`। शिपमेंट अनुरोध दर्ज करें |
| जवाब खो गया या प्रदाता अभी प्रक्रिया में है | ऑर्डर `PENDING_PAYMENT`, भुगतान `UNKNOWN`, स्टॉक `HELD`। मौजूदा भुगतान फिर जाँचें |
| बिना शुल्क लेनदेन बंद होने की पुष्टि | ऑर्डर `CANCELLED`, भुगतान `CLOSED_UNPAID`, आरक्षण `RELEASED` |
| अपवाद के तौर पर आरक्षण छोड़ने के बाद भुगतान की पुष्टि | ऑर्डर `CANCELLED`, भुगतान `REFUND_PENDING`, आरक्षण `RELEASED`। रिफ़ंड अनुरोध दर्ज करें |

आरक्षण की अवधि बीत जाए और भुगतान अनिश्चित हो तो पहले प्रदाता से स्थिति पूछें। जाँच बार-बार विफल हो तो मामला लंबित दर्ज करें ताकि ऑपरेटर लेनदेन खोजकर मिलान कर सके। अपवाद के तौर पर आरक्षण पहले छोड़ दिया गया हो और भुगतान की पुष्टि बाद में आए तो इस उदाहरण में स्टॉक फिर आरक्षित करने की जगह रिफ़ंड माँगते हैं। प्रदाता की पुष्टि के बाद ही रिफ़ंड सफल दर्ज करें। आरक्षण कितनी देर रखना है और अपवाद की मंज़ूरी कौन देगा, यह स्टॉक की बिक्री की गति और प्रदाता के अनुबंध के अनुसार तय करें।

वेबहुक इवेंट ID से दोहराई गई डिलीवरी पहचानें। अलग इवेंट ID से एक ही भुगतान की सूचना मिले तब भी शिपमेंट अनुरोध एक बार ही दर्ज होना चाहिए। उदाहरण के लिए, शिपमेंट आउटबॉक्स में `order_id` और काम के प्रकार की जोड़ी पर अद्वितीय बाधा रखें। रिफ़ंड आउटबॉक्स में `payment_attempt_id` और काम के प्रकार पर यही नियम रखें। आउटबॉक्स दोबारा संदेश भेज सकता है, इसलिए शिपमेंट और रिफ़ंड वर्कर भी उसी काम की ID से दोहरा निष्पादन रोकें। प्रदाता को रिफ़ंड अनुरोध फिर भेजते समय उसकी समर्थित रिफ़ंड-विशिष्ट इडेम्पोटेंसी कुंजी इस्तेमाल करें। पुरानी “प्रक्रिया जारी है” सूचना किसी पुष्ट भुगतान की स्थिति पीछे न ले जाए। ID या रकम बेमेल हो या परिणाम पुष्ट इतिहास से टकराए तो उसे अपने आप लागू करने की जगह मिलान सूची में डालें। [Stripe में डुप्लिकेट वेबहुक सँभालना](https://docs.stripe.com/webhooks#handle-duplicate-events) · [AWS का ट्रांज़ैक्शनल आउटबॉक्स पैटर्न](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)

## Java में भुगतान की स्थिति बदलने की जाँच

नीचे का कोड `CheckoutPolicy.java` में सहेजें और `java CheckoutPolicy.java` चलाएँ। इनपुट ऑर्डर से जुड़े **एक भुगतान प्रयास का सर्वर पर सत्यापित परिणाम** है। `CLOSED_UNPAID` का अर्थ है कि बिना शुल्क लेनदेन समाप्त होने की पुष्टि हो गई है। केवल अस्वीकृति संदेश काफ़ी नहीं है। कोड मानता है कि ऑर्डर और आरक्षण की स्थितियाँ मेल खाती हैं। भुगतान के लिए लंबित ऑर्डर का आरक्षण कायम है और रद्द ऑर्डर का आरक्षण छूट चुका है। कॉल करने वाला ID और रकम जाँचता है और विरोधी परिणामों का मिलान करता है। कोड अगली स्थिति और दर्ज किया जाने वाला काम लौटाता है।

```java
public class CheckoutPolicy {
    enum Order { PENDING_PAYMENT, CONFIRMED, CANCELLED }
    enum Payment { PENDING, UNKNOWN, PAID, CLOSED_UNPAID, REFUND_PENDING }
    enum Reservation { HELD, ALLOCATED, RELEASED }
    enum Result { UNRESOLVED, CLOSED_UNPAID, PAID }
    enum Effect { NONE, REQUEST_FULFILLMENT, REQUEST_REFUND }

    record State(Order order, Payment payment, Reservation reservation) {}
    record Decision(State state, Effect effect) {}

    static Decision apply(State current, Result result) {
        if (current.payment() == Payment.PAID
                || current.payment() == Payment.REFUND_PENDING) {
            return new Decision(current, Effect.NONE);
        }

        if (current.order() == Order.CANCELLED) {
            return switch (result) {
                case PAID -> new Decision(
                    new State(Order.CANCELLED, Payment.REFUND_PENDING, Reservation.RELEASED),
                    Effect.REQUEST_REFUND);
                case CLOSED_UNPAID -> new Decision(
                    new State(Order.CANCELLED, Payment.CLOSED_UNPAID, Reservation.RELEASED),
                    Effect.NONE);
                case UNRESOLVED -> new Decision(current, Effect.NONE);
            };
        }

        return switch (result) {
            case PAID -> new Decision(
                new State(Order.CONFIRMED, Payment.PAID, Reservation.ALLOCATED),
                Effect.REQUEST_FULFILLMENT);
            case CLOSED_UNPAID -> new Decision(
                new State(Order.CANCELLED, Payment.CLOSED_UNPAID, Reservation.RELEASED),
                Effect.NONE);
            case UNRESOLVED -> new Decision(
                new State(Order.PENDING_PAYMENT, Payment.UNKNOWN, Reservation.HELD),
                Effect.NONE);
        };
    }

    static void check(String label, Decision expected, Decision actual) {
        if (!expected.equals(actual)) {
            throw new AssertionError(label + ": " + actual);
        }
        System.out.println("PASS " + label);
    }

    public static void main(String[] args) {
        State held = new State(Order.PENDING_PAYMENT, Payment.PENDING, Reservation.HELD);
        State unknown = new State(Order.PENDING_PAYMENT, Payment.UNKNOWN, Reservation.HELD);
        State paid = new State(Order.CONFIRMED, Payment.PAID, Reservation.ALLOCATED);
        State closed = new State(
            Order.CANCELLED, Payment.CLOSED_UNPAID, Reservation.RELEASED);
        State released = new State(Order.CANCELLED, Payment.UNKNOWN, Reservation.RELEASED);
        State refundPending = new State(
            Order.CANCELLED, Payment.REFUND_PENDING, Reservation.RELEASED);

        check("unresolved retains hold", new Decision(unknown, Effect.NONE),
            apply(held, Result.UNRESOLVED));
        check("paid allocates stock", new Decision(paid, Effect.REQUEST_FULFILLMENT),
            apply(unknown, Result.PAID));
        check("duplicate paid has no effect", new Decision(paid, Effect.NONE),
            apply(paid, Result.PAID));
        check("old unresolved does not reopen payment", new Decision(paid, Effect.NONE),
            apply(paid, Result.UNRESOLVED));
        check("closed unpaid releases hold", new Decision(closed, Effect.NONE),
            apply(unknown, Result.CLOSED_UNPAID));
        check("late paid requests refund", new Decision(refundPending, Effect.REQUEST_REFUND),
            apply(released, Result.PAID));
        check("duplicate late paid has no effect", new Decision(refundPending, Effect.NONE),
            apply(refundPending, Result.PAID));
    }
}
```

JDK 21.0.1 में नीचे की सात जाँचें चलीं। भुगतान की पुष्टि दोबारा लागू करने से कोई अतिरिक्त काम नहीं बना। आरक्षण छोड़ने के बाद भुगतान की पुष्टि पर शिपमेंट के बजाय रिफ़ंड अनुरोध मिला।

```text
PASS unresolved retains hold
PASS paid allocates stock
PASS duplicate paid has no effect
PASS old unresolved does not reopen payment
PASS closed unpaid releases hold
PASS late paid requests refund
PASS duplicate late paid has no effect
```

वास्तविक कार्यान्वयन में दो तरह की होड़ अलग से जाँचें। दो ऑर्डर एक साथ आखिरी इकाई आरक्षित करें तो एक ही सफल होना चाहिए। एक ही ऑर्डर के लिए आरक्षण की अवधि समाप्त होने और भुगतान की पुष्टि की कार्रवाई साथ चले तो केवल एक परिणाम दर्ज हो सकता है। आरक्षण कायम हो तो शिपमेंट और छूट चुका हो तो रिफ़ंड। Java के इस क्रमिक उदाहरण के बाद डेटाबेस की होड़, प्रदाता के साथ एकीकरण और प्रोडक्शन भुगतान अलग से सत्यापित करने होंगे।

गोदामों की संख्या बढ़े या स्टॉक को स्वतंत्र रूप से डिप्लॉय या स्केल करने की ज़रूरत सामने आए तो स्टॉक की अलग सेवा पर विचार करें। तब ऑर्डर और स्टॉक डेटाबेस एक स्थानीय कमिट साझा नहीं कर सकेंगे। स्टॉक सेवा को हर आरक्षण ID का अनुरोध एक बार लागू करना होगा। ऑर्डर मॉड्यूल को परिणाम फिर पूछने या विफलता की भरपाई करने में सक्षम होना चाहिए। सेवाओं की सीमा बदलने पर भी **उपलब्ध मात्रा से अधिक बिक्री रोकना और हर भुगतान व शिपमेंट एक बार लागू करना** ज़रूरी है।
