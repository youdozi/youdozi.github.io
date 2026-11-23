---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-11-22-commerce-database-design",
  "routeSlug": "2026-11-22-commerce-database-design",
  "kind": "post",
  "title": "Datenbankdesign für E-Commerce: SKUs, Bestellungen, Bestand und Zahlungen",
  "description": "SKUs, Bestellpreise zum Kaufzeitpunkt, Bestandsreservierungen und Zahlungsversuche in PostgreSQL modellieren und zwei Sitzungen um das letzte Exemplar konkurrieren lassen.",
  "categories": [
    "architecture"
  ],
  "tags": [
    "ecommerce",
    "postgresql",
    "inventory",
    "payments"
  ],
  "sourcePath": "src/content/posts/en/2026-11-22-commerce-database-design.md",
  "sourceSha256": "da573ac023d969b02216c24993c872e842a6693607f8e3805fd988ce7d64bcf3",
  "draftSha256": "22423d5e7520d62b47cb89c042cc2ebf1bb64363bc0fd4e98bb3dc75322cdfab",
  "manifestPath": ".pipeline/technical-translations/batch-185/manifest.json",
  "manifestSha256": "3281e1d3e7c9b3abbb6c101d911dd0fcdee7dd54f7034838135f391123b6fb44",
  "publishedAt": "2026-11-23T00:19:14.218Z",
  "updatedAt": "2026-11-23T00:19:14.218Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 185,
    "approvedAt": "2026-11-23T00:19:14.218Z",
    "basis": "The site owner explicitly requested missing supported locales for the eight articles published in PRs #177–#184. This authorizes publication of the 48 editions enumerated in this batch."
  }
}
---

**Eine E-Commerce-Datenbank hält die aktuellen Angebotsbedingungen, die beim Checkout vereinbarten Beträge, den je Bestellung reservierten Bestand und die Ergebnisse des Zahlungsdienstleisters fest.** Der Gesamtbetrag von gestern muss auch nach einer Preisänderung morgen noch stimmen. Wenn heute nur ein Exemplar verfügbar ist, darf es von zwei gleichzeitigen Bestellungen nur eine reservieren. Das PostgreSQL-Beispiel zeigt die Tabellen und Constraints für beide Anforderungen.

Dieser Leitfaden baut auf dem [Beispiel zur letzten verfügbaren Einheit im vorherigen Artikel](/en/posts/2026-11-22-commerce-system-design-last-unit-of-stock/) auf. Vorausgesetzt werden ein Händler für physische Waren, ein Lager und Zahlungen in südkoreanischen Won (KRW). Bestand und Bestellungen verwenden dieselbe Datenbank. Rückgaben nach dem Versand und die Abrechnung haben jeweils ein eigenes fachliches Modell.

## Was für einen Kauf gespeichert werden muss

| Frage | Zu lesende oder zu schreibende Tabellen | Schlüssel und Werte |
| --- | --- | --- |
| Was kostet die schwarze Tastatur aktuell? | `product` → `sku` | Produkt-ID, verkäufliche SKU, aktueller Preis |
| Warum haben wir für die gestrige Bestellung 43.000 KRW berechnet? | `orders` → `order_item` | Bestell-ID, vereinbarte Menge, Stückpreis, Rabatt, Versandkosten |
| Welche Bestellung hat das letzte Exemplar reserviert? | `inventory`, `stock_reservation` | Physischer Lagerbestand je SKU und Reservierung je Bestellposition |
| Wie finden wir dieselbe Zahlung, wenn die Antwort des Dienstleisters verloren geht? | `payment_attempt`, `payment_event` | Zahlungsversuch je Bestellung, Transaktions-ID beim Dienstleister, Ereignis-ID |

In diesem Beispiel steht `product` für ein Angebot im Katalog und `sku` für eine bestellbare Variante wie die schwarze Tastatur. Eine Bestellposition referenziert die SKU und **speichert Artikelname, Variantenname und Stückpreis zum Zeitpunkt des Checkouts**. Ein Exemplar zu 42.000 KRW, ein Rabatt von 2.000 KRW und Versandkosten von 3.000 KRW ergeben 43.000 KRW. Die Bestellung kann den gespeicherten Gesamtbetrag direkt anzeigen. Bestellpositionen bleiben nach der Erstellung unveränderlich, weil sie die vereinbarten Beträge und reservierten Mengen festhalten. Soll eine SKU, die in einer Transaktion verwendet wurde, aus dem Verkauf genommen werden, markieren Sie sie als unverkäuflich. Erhalten Sie die Zeilen, auf die ältere Bestellungen verweisen, und vermeiden Sie kaskadierendes Löschen dieser Beziehungen.

## Das Modell mit PostgreSQL-Schlüsseln und Constraints ausdrücken

Führen Sie das folgende DDL einmal in einer leeren Übungsdatenbank aus. Das Beispiel vergibt die IDs explizit und speichert Geldbeträge als ganze Won. Es setzt voraus, dass der Checkout mehrere Warenkorbeinträge derselben SKU zu einer Bestellposition zusammenfasst. Daher identifiziert `(order_id, sku_id)` sowohl die Bestellposition als auch ihre Reservierung.

```sql
CREATE TABLE product (
    id bigint PRIMARY KEY,
    name text NOT NULL
);

CREATE TABLE sku (
    id bigint PRIMARY KEY,
    product_id bigint NOT NULL REFERENCES product(id),
    code text NOT NULL UNIQUE,
    option_name text NOT NULL,
    current_price_krw bigint NOT NULL CHECK (current_price_krw >= 0),
    sellable boolean NOT NULL
);

CREATE TABLE inventory (
    sku_id bigint PRIMARY KEY REFERENCES sku(id),
    on_hand integer NOT NULL CHECK (on_hand >= 0),
    held integer NOT NULL CHECK (held >= 0),
    allocated integer NOT NULL CHECK (allocated >= 0),
    CHECK (held <= on_hand - allocated)
);

CREATE TABLE orders (
    id bigint PRIMARY KEY,
    customer_id bigint NOT NULL,
    request_key text NOT NULL,
    request_hash text NOT NULL,
    status text NOT NULL CHECK (status IN ('PENDING_PAYMENT', 'CONFIRMED', 'CANCELLED')),
    total_krw bigint NOT NULL CHECK (total_krw >= 0),
    shipping_krw bigint NOT NULL CHECK (shipping_krw >= 0),
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (customer_id, request_key)
);

CREATE TABLE order_item (
    order_id bigint REFERENCES orders(id),
    sku_id bigint REFERENCES sku(id),
    item_name text NOT NULL,
    option_name text NOT NULL,
    quantity integer NOT NULL CHECK (quantity > 0),
    unit_price_krw bigint NOT NULL CHECK (unit_price_krw >= 0),
    discount_krw bigint NOT NULL CHECK (discount_krw >= 0),
    CHECK (discount_krw <= quantity * unit_price_krw::numeric),
    PRIMARY KEY (order_id, sku_id)
);

CREATE TABLE stock_reservation (
    order_id bigint,
    sku_id bigint REFERENCES inventory(sku_id),
    state text NOT NULL CHECK (state IN ('HELD', 'ALLOCATED', 'RELEASED', 'SHIPPED')),
    expires_at timestamptz NOT NULL,
    PRIMARY KEY (order_id, sku_id),
    FOREIGN KEY (order_id, sku_id) REFERENCES order_item(order_id, sku_id)
);

CREATE TABLE payment_attempt (
    id bigint PRIMARY KEY,
    order_id bigint NOT NULL REFERENCES orders(id),
    attempt_no integer NOT NULL CHECK (attempt_no > 0),
    provider text NOT NULL,
    merchant_account text NOT NULL,
    provider_request_key text NOT NULL,
    provider_payment_id text,
    amount_krw bigint NOT NULL CHECK (amount_krw >= 0),
    state text NOT NULL CHECK (state IN
        ('PENDING', 'UNKNOWN', 'PAID', 'CLOSED_UNPAID', 'REFUND_PENDING', 'REFUNDED')),
    UNIQUE (order_id, attempt_no),
    UNIQUE (provider, merchant_account, provider_request_key),
    UNIQUE (provider, merchant_account, provider_payment_id)
);

CREATE TABLE payment_event (
    provider text,
    merchant_account text,
    event_id text,
    received_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (provider, merchant_account, event_id)
);

CREATE INDEX orders_customer_history
    ON orders (customer_id, created_at DESC, id DESC);

CREATE INDEX reservation_expiry
    ON stock_reservation (expires_at, order_id, sku_id)
    WHERE state = 'HELD';
```

Der `CHECK`-Constraint erzwingt `held + allocated ≤ on_hand` in jeder Bestandszeile. Um zu prüfen, ob der Bestellbetrag mit den Positionen übereinstimmt oder ob die Mengen in aktiven Reservierungen zusammen `held` ergeben, muss man mehrere Zeilen lesen. Schreiben Sie die Beträge und Reservierungen in der Transaktion zur Bestellerstellung und gleichen Sie die gespeicherten Summen und Zähler regelmäßig mit den Einzelaufzeichnungen ab. [PostgreSQL-Dokumentation zu CHECK-Constraints](https://www.postgresql.org/docs/17/ddl-constraints.html#DDL-CONSTRAINTS-CHECK-CONSTRAINTS)

Wenn derselbe Kunde einen `request_key` erneut sendet, suchen Sie die bestehende Bestellung. Weicht der gespeicherte `request_hash` ab, liegt ein Konflikt durch die Wiederverwendung des Schlüssels vor. Da die Transaktions-ID des Dienstleisters beim Aufruf noch unbekannt sein kann, erlauben Sie zunächst `NULL`. Sobald die externe ID bekannt ist, muss sie pro Anbieter und Händlerkonto eindeutig sein. Der Schlüssel in `payment_event` verhindert die doppelte Verarbeitung desselben Ereignisses. Da dasselbe erfolgreiche Ergebnis mit unterschiedlichen Ereignis-IDs eintreffen kann, sichern Sie Versandaufträge zusätzlich mit einem eindeutigen Schlüssel pro Bestellung und mit geprüften Statusübergängen ab. [PostgreSQL-Dokumentation zu UNIQUE-Constraints](https://www.postgresql.org/docs/17/ddl-constraints.html#DDL-CONSTRAINTS-UNIQUE-CONSTRAINTS) · [Stripe-Hinweise zu doppelten Webhooks](https://docs.stripe.com/webhooks#handle-duplicate-events)

## Das letzte Exemplar mit einem bedingten UPDATE reservieren

![SKU und Menge aus der Bestellposition lesen. Ändert die bedingte Bestandsaktualisierung eine Zeile, im selben Statement die Reservierung einfügen und true zurückgeben. Sonst false zurückgeben und keine Reservierung einfügen.](/assets/diagrams/technical/de-2026-11-22-commerce-database-design.svg)

Der verfügbare Bestand ergibt sich aus `on_hand - allocated - held`. Unabhängig davon, welche Menge der Shop vorher angezeigt hat, **prüft der Checkout die Verfügbarkeit und erhöht die reservierte Menge im selben UPDATE**. Nur wenn das Update eine Zeile ändert, fügt die Funktion eine Reservierung ein. Scheitert das Einfügen durch einen SQL-Fehler, nimmt dasselbe Statement die Erhöhung von `held` zurück.

```sql
CREATE FUNCTION reserve_stock(p_order_id bigint, p_sku_id bigint,
                              p_expires_at timestamptz)
RETURNS boolean
LANGUAGE sql
AS $$
    WITH held_stock AS (
        UPDATE inventory AS i
           SET held = i.held + line.quantity
          FROM order_item AS line
         WHERE line.order_id = p_order_id
           AND line.sku_id = p_sku_id
           AND i.sku_id = line.sku_id
           AND i.on_hand - i.allocated - i.held >= line.quantity
         RETURNING i.sku_id
    ), reservation AS (
        INSERT INTO stock_reservation (order_id, sku_id, state, expires_at)
        SELECT p_order_id, sku_id, 'HELD', p_expires_at
        FROM held_stock
        RETURNING 1
    )
    SELECT EXISTS (SELECT 1 FROM reservation);
$$;
```

Legen Sie beim Checkout die Bestellung und ihre Positionen an, reservieren Sie jede SKU und erfassen Sie den ersten Zahlungsversuch und die zu veröffentlichende Arbeit in derselben Datenbanktransaktion. Liefert die Funktion für einen Artikel `false`, macht der Aufrufer die gesamte Transaktion rückgängig. Sperren Sie bei mehreren SKUs die Zeilen stets in derselben Reihenfolge, etwa nach aufsteigender SKU-ID. Bei einem wiederholten Checkout prüft der Aufrufer den eindeutigen Bestellschlüssel und überspringt die Funktion, wenn bereits reserviert wurde. Ein `ON CONFLICT DO NOTHING` beim Einfügen der Reservierung könnte den Zähler ohne zugehörige Reservierung erhöhen.

Rufen Sie den Zahlungsdienstleister erst nach dem lokalen Commit auf. Sobald die Zahlung bestätigt ist, setzen Sie die Reservierung auf `ALLOCATED` und übertragen Sie die Menge von `held` nach `allocated`. Die Freigabe einer Reservierung verringert nur `held`. Der Versand verringert `on_hand` und `allocated`. Um doppelte Abzüge zu verhindern, sperren Sie die Reservierungs- und Bestandszeilen in derselben Transaktion und prüfen den erwarteten Ausgangsstatus vor dem Übergang.

## Zwei Sitzungen um das letzte Exemplar konkurrieren lassen

Führen Sie das DDL aus, legen Sie die Funktion an und laden Sie anschließend die folgenden Daten in die Übungsdatenbank. Die beiden Bestellpositionen werden im Voraus angelegt, damit sich der Wettlauf um die Reservierung separat prüfen lässt.

```sql
INSERT INTO product VALUES (1, 'Keyboard');
INSERT INTO sku VALUES (101, 1, 'KB-BLK', 'Black', 42000, true);
INSERT INTO inventory VALUES (101, 1, 0, 0);

INSERT INTO orders (id, customer_id, request_key, request_hash,
                    status, total_krw, shipping_krw)
VALUES (41, 1001, 'checkout-a', 'fixture-a', 'PENDING_PAYMENT', 43000, 3000),
       (42, 1002, 'checkout-b', 'fixture-b', 'PENDING_PAYMENT', 43000, 3000);

INSERT INTO order_item
VALUES (41, 101, 'Keyboard', 'Black', 1, 42000, 2000),
       (42, 101, 'Keyboard', 'Black', 1, 42000, 2000);
```

Öffnen Sie zwei `psql`-Sitzungen mit derselben Datenbank. Führen Sie Folgendes in Sitzung **A** aus. Das Ergebnis ist `true`, die Transaktion bleibt offen.

```sql
BEGIN ISOLATION LEVEL READ COMMITTED;
SELECT reserve_stock(41, 101, now() + interval '10 minutes') AS reserved;
```

Solange die Transaktion von A offen ist, führen Sie in Sitzung **B** Folgendes aus. Das `SELECT` wartet beim Versuch, dieselbe Bestandszeile zu aktualisieren.

```sql
BEGIN ISOLATION LEVEL READ COMMITTED;
SELECT reserve_stock(42, 101, now() + interval '10 minutes') AS reserved;
```

Führen Sie in A `COMMIT;` aus. Sobald die Sperre freigegeben ist, prüft B die `WHERE`-Bedingung gegen die aktualisierte Zeile. Da nichts mehr verfügbar ist, gibt B `false` zurück. Beenden Sie die Übung mit `ROLLBACK;` in B. [PostgreSQL-Dokumentation zur Read-Committed-Isolation](https://www.postgresql.org/docs/17/transaction-iso.html#XACT-READ-COMMITTED)

```sql
SELECT sku_id, on_hand, held, allocated FROM inventory;
SELECT order_id, sku_id, state FROM stock_reservation ORDER BY order_id;
```

Das Beispiel lief mit zwei gleichzeitigen Datenbankverbindungen unter PostgreSQL 17.12. A führte den Commit aus, nachdem `pg_stat_activity` gezeigt hatte, dass B auf eine Sperre wartete. A gab `true` zurück, B gab `false` zurück. Die Endwerte von `on_hand / held / allocated` in `inventory` waren `1 / 1 / 0`. Für **Bestellung 41 blieb eine Reservierung in `HELD`**.

Als der Katalogpreis auf 45.000 KRW geändert wurde, blieb für Bestellung 41 der Stückpreis bei 42.000 KRW und der Gesamtbetrag bei 43.000 KRW. Nach Erhöhung des Bestands um ein Exemplar verletzte ein erneuter Aufruf der Reservierungsfunktion für Bestellung 41 den Eindeutigkeits-Constraint. `held` blieb bei 1. Die Übung prüfte die Konkurrenz der beiden Verbindungen und die SQL-Constraints. Aufrufe des Zahlungsdienstleisters, Wettläufe beim Ablauf der Reservierung und Produktionslast erfordern separate Tests.

## Indizes an den Abfragen der Anwendung ausrichten

Die Bestellhistorie eines Kunden verwendet eine Abfrage der Form `WHERE customer_id = … ORDER BY created_at DESC, id DESC LIMIT …`. Der zusammengesetzte Index im DDL entspricht dem Kundenfilter und der Sortierung. Der Bereinigungsjob für Reservierungen verwendet `WHERE state = 'HELD' AND expires_at <= now()`. Ein partieller Index schließt daher Reservierungen in anderen Status aus. Der Ablaufindex liefert die Kandidaten. Vor der Entscheidung über die Freigabe einer Reservierung nimmt der Job Sperren und prüft den Zahlungsstatus. [PostgreSQL-Dokumentation zu mehrspaltigen Indizes](https://www.postgresql.org/docs/17/indexes-multicolumn.html) · [PostgreSQL-Dokumentation zu partiellen Indizes](https://www.postgresql.org/docs/17/indexes-partial.html)
