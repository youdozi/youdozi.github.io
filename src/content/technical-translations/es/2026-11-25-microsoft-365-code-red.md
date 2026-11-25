---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-25-microsoft-365-code-red",
  "routeSlug": "2026-11-25-microsoft-365-code-red",
  "kind": "post",
  "title": "Lecciones del ‘Code Red’ de Microsoft 365: qué comprobar antes de mover el tráfico",
  "description": "Capacidad de recepción en la conmutación por error, carga de reconexión y registro compartido: lecciones de la caída de Microsoft 365.",
  "categories": [
    "architecture"
  ],
  "tags": [
    "microsoft-365",
    "incident-response",
    "failover",
    "load-shedding"
  ],
  "sourcePath": "src/content/posts/en/2026-11-25-microsoft-365-code-red.md",
  "sourceSha256": "2df9b4039ebb04013f04e21b144e3cb3780236a74b97dd9dcd885df36569a389",
  "draftSha256": "e55c3ccd9b06afe1cff63cd862280a019dea4acfd9f36d839e0f40306e37fcf0",
  "manifestPath": ".pipeline/technical-translations/batch-191/manifest.json",
  "manifestSha256": "3c11feea419e90c2b266ce8c92f61b8a1c397634ec1891b701c3c13c0a447504",
  "publishedAt": "2026-11-25T04:56:03.451Z",
  "updatedAt": "2026-11-25T04:56:03.451Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 194,
    "approvedAt": "2026-11-25T04:56:03.451Z",
    "basis": "User approved publication of this supplied manuscript in eight languages and authorized the localized diagrams on 2026-11-25; translation review is self-review, not human or native-speaker review."
  }
}
---

Cuando un servidor deja de responder, las solicitudes se desvían a servidores sanos. Normalmente esto evita que los usuarios noten la caída de unos pocos servidores. En la interrupción de noviembre de 2026 de Microsoft 365, el mismo mecanismo llevó el problema a otras regiones: los servidores receptores tenían el mismo defecto, que también se manifestó allí al aumentar la carga. [Copia del informe posterior al incidente de Microsoft](https://www.365fanatic.com/wp-content/uploads/2026/11/postincidentreport-mo1550821.pdf)

![La capacidad reducida, el tráfico de Teams y la demanda pico coinciden; el desvío lleva la carga a servidores con el mismo defecto.](/assets/diagrams/technical/es-2026-11-25-microsoft-365-code-red.svg)

La capacidad reducida, el tráfico de Teams y la demanda pico coinciden; el desvío lleva la carga a servidores con el mismo defecto.

## ¿Por qué apareció en noviembre un defecto introducido en julio?

Según el informe de Microsoft, el defecto estaba en una actualización de Windows para las puertas de enlace de red de Microsoft 365. Se desplegó durante varias semanas a partir de julio y no se observó impacto en clientes durante más de tres meses. Sin embargo, los servidores nuevos con más núcleos podían procesar más solicitudes de conexión simultáneamente, lo que podía aumentar la contención de bloqueos internos. Los servidores usados en las pruebas de carga tenían menos núcleos y el tráfico de prueba también difería del tráfico durante la interrupción. [Copia del informe posterior al incidente de Microsoft](https://www.365fanatic.com/wp-content/uploads/2026/11/postincidentreport-mo1550821.pdf)

El 12 de noviembre, con parte de la capacidad de las puertas de enlace fuera de servicio por tareas rutinarias, el tráfico de Teams pasó a puertas de enlace compartidas con Exchange Online. El servicio funcionó normalmente durante un tiempo. Cuando el uso en Norteamérica se acercó a su pico habitual, los servidores empezaron a dejar de responder y el desvío automático incrementó la carga de cada servidor restante. El desvío entre regiones también envió solicitudes a servidores con el mismo defecto. El informe registra **unas 23 horas y 50 minutos de impacto activo en clientes**; después continuaron el procesamiento del correo retrasado y la supervisión de la estabilidad. [Copia del informe posterior al incidente de Microsoft](https://www.365fanatic.com/wp-content/uploads/2026/11/postincidentreport-mo1550821.pdf)

## La conmutación por error también necesita un límite de recepción

Al diseñar una conmutación por error, hay que comprobar **cuánto más puede procesar ahora el destino**. Por ejemplo, si la región A necesita transferir 1.000 solicitudes y B tiene capacidad libre para 300 en el mismo intervalo, desviarlas todas puede causar una interrupción en ambas regiones. Se pueden priorizar las solicitudes esenciales y limitar la cola de los trabajos que admiten demora o rechazarlos temporalmente. Reducir deliberadamente las solicitudes aceptadas durante una sobrecarga se denomina **deslastre de carga (load shedding)**. [Guía de Microsoft Learn sobre limitación](https://learn.microsoft.com/en-us/azure/well-architected/design-guides/throttling)

El mismo principio se aplica a la recuperación. En este incidente, al volver al servicio los servidores recibieron solicitudes de reconexión acumuladas y dejaron de responder de nuevo. El equipo de operaciones puede devolver gradualmente las solicitudes a las instancias recuperadas y observar conjuntamente la tasa de conexiones correctas, la latencia y las colas. Las pruebas de carga deben combinar **tráfico pico, capacidad reducida por tareas rutinarias, conmutación por error y reconexión** en la misma generación de servidores que producción. Probar cada condición por separado puede pasar por alto problemas que surgen al coincidir. [Copia del informe posterior al incidente de Microsoft](https://www.365fanatic.com/wp-content/uploads/2026/11/postincidentreport-mo1550821.pdf)

## Chats separados, un registro de decisiones

Según memorandos internos revisados por Reuters, el personal de respuesta intercambió más de 11.000 mensajes en 11 salas de Teams. Los datos de diagnóstico estaban repartidos entre varios sistemas, lo que dificultaba ver de un vistazo qué hipótesis seguían activas y quién había decidido cada acción. Microsoft entró después en «Code Red», dando prioridad a prevenir recurrencias y mejorar la recuperación. La **recuperación mundial en una hora** publicada por Reuters es una meta interna para futuros incidentes. [Presentación en GeekNews](https://news.hada.io/topic?id=37797) · [Artículo de Reuters republicado](https://www.investing.com/news/stock-market-news/exclusivemicrosoft-declares-code-red-after-historic-outage-internal-memos-show-5048702)

Aunque cada equipo tenga su canal de investigación, se puede mantener un documento común del incidente. En la parte superior figuran **impacto actual en clientes, hechos confirmados, hipótesis activas y responsables, última acción y resultado, y hora del próximo aviso**. Por ejemplo, en lugar de solo «servidor reiniciado», se puede escribir «la tasa de conexiones correctas se recuperó brevemente tras el reinicio, pero volvió a caer al llegar las reconexiones». Quien releva al equipo puede decidir si repite la acción de inmediato o controla primero la entrada. También conviene comprobar si el acceso al documento comparte dependencias con el servicio que se está recuperando. [Google SRE: documento de estado del incidente](https://sre.google/sre-book/managing-incidents/#live-incident-state-document)

En el próximo simulacro, empiece con **una región con capacidad reducida durante la hora pico**. Determine cuántas solicitudes puede aceptar la región restante, qué funciones reducir primero y a qué velocidad devolver las solicitudes a los servidores recuperados. El criterio de finalización debe ir más allá de que los servidores estén encendidos: los usuarios deben poder volver a usar las funciones principales y la acumulación de solicitudes debe disminuir. Así se puede medir el objetivo de recuperación.

Lectura relacionada · [Comprobar la propagación de traceparent de RestClient en Spring Boot 4.2 (inglés)](https://youdozi.github.io/en/posts/2026-11-22-spring-boot-4-2-restclient-traceparent/)
