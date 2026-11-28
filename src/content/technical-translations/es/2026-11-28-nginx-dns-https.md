---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-28-nginx-dns-https",
  "routeSlug": "2026-11-28-nginx-dns-https",
  "kind": "post",
  "title": "Conectar Duck DNS con Nginx con ayuda de la IA: del DNS a HTTPS",
  "description": "Sigue una petición externa hasta la aplicación, distingue una espera agotada de un error de proxy y comprueba el certificado y su renovación.",
  "categories": [
    "tips"
  ],
  "tags": [
    "self-hosting",
    "nginx",
    "dns",
    "https"
  ],
  "sourcePath": "src/content/posts/en/2026-11-28-nginx-dns-https.md",
  "sourceSha256": "921090516e1cb08c80387f75bf13f1ef2b554b81ad242843948943262a48f77e",
  "draftSha256": "4d79bb75905768ae63cb637605ff14b43b011f5191b8fe76eed10074cf31de25",
  "manifestPath": ".pipeline/technical-translations/batch-1571/manifest.json",
  "manifestSha256": "ce67844b72beb7d028d68ceb5fab80ea752b9cf1879179e92a69310b0ac23029",
  "publishedAt": "2026-11-28T04:45:08.727Z",
  "updatedAt": "2026-11-28T04:45:08.727Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 229,
    "approvedAt": "2026-11-28T04:45:08.727Z",
    "basis": "Explicit item 157 publication approval for both item 155 and 156 follow-up guides in all nine site languages."
  }
}
---

Supongamos que dispones de un servidor Linux con IPv4 pública y un nombre de Duck DNS. Una aplicación destinada al público ya escucha en `127.0.0.1:8080` en la misma máquina que Nginx. La aplicación de notas anterior era un ejercicio local. Aquí se usa otra aplicación preparada para su publicación.

## Pide a la IA un plan que puedas comprobar

> Quiero conectar mi nombre de Duck DNS a Nginx en Linux con IPv4 pública. La aplicación se ejecuta en el mismo host en `127.0.0.1:8080`. Usa `example.com` en lugar del dominio real. Dame los comandos y los resultados esperados para comprobar, en orden, el registro DNS A, el acceso externo al puerto, el proxy inverso y HTTPS. Si el DNS es correcto, ¿cómo distingo un tiempo de espera agotado de un `502`? Indica el cambio mínimo de configuración y cómo revertirlo. Pregúntame por los valores desconocidos y no ejecutes nada.

No envíes tokens ni claves SSH. Revisa la respuesta tramo por tramo.

![Resolver el nombre → Acceder al puerto HTTP → Seleccionar el host de Nginx → Comprobar la respuesta de la app → Verificar HTTPS y la renovación](/assets/diagrams/technical/es-2026-11-28-nginx-dns-https.svg)

## Comprueba el DNS y la aplicación local

Sustituye `example.com` por tu nombre en todos los ejemplos. Actualiza Duck DNS para que A apunte a tu IPv4 pública. Publica AAAA solo si la conexión externa por IPv6 funciona de extremo a extremo. Aquí Nginx escucha en IPv4. Consulta el DNS con dig y ejecuta curl en el servidor para comprobar que la aplicación devuelve su respuesta habitual. [Duck DNS](https://www.duckdns.org/spec.jsp) · [Let’s Encrypt · IPv6](https://letsencrypt.org/docs/ipv6-support/)

```sh
dig +short example.com A
dig +short example.com AAAA
curl --fail --show-error http://127.0.0.1:8080/
```

## Envía la petición HTTP a la aplicación

Guarda una copia de la configuración activa. Añade este bloque server en el contexto http del sitio con tu nombre de host real. Comprueba la configuración con `nginx -t` y, solo si pasa, recárgala con el gestor de servicios de tu sistema. [NGINX · proxy_pass](https://nginx.org/en/docs/beginners_guide.html#proxy) · [nginx -t](https://nginx.org/en/docs/switches.html)

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Desde otra red, solicita el sitio por HTTP. Deberías recibir el mismo contenido. Si el DNS es correcto pero la espera se agota, revisa primero la línea, el reenvío del puerto y el cortafuegos. Si Nginx devuelve `502`, comprueba la respuesta local de la aplicación y el puerto de destino. Para revertir el cambio, restaura la copia, compruébala y recarga la configuración.

```sh
curl --fail --show-error http://example.com/
```

## Verifica HTTPS y ensaya la renovación

Con el complemento de Nginx para Certbot instalado y el puerto TCP `80` accesible desde fuera, HTTP-01 puede validar el nombre. Guarda primero la configuración HTTP que funciona, ya que el complemento puede instalar el certificado y modificar Nginx. Ejecuta Certbot en el servidor, comprueba HTTPS desde otra red y prueba la renovación en el servidor. [Let’s Encrypt · HTTP-01 / DNS-01](https://letsencrypt.org/docs/challenge-types/) · [Certbot](https://eff-certbot.readthedocs.io/en/stable/using.html)

```sh
sudo certbot --nginx -d example.com
```

```sh
curl --fail --show-error https://example.com/
```

```sh
sudo certbot renew --dry-run
```

Anota la respuesta HTTPS externa, el nombre de dominio del certificado y el resultado del simulacro. Si el puerto TCP `80` está bloqueado, DNS-01 permite validar el control del nombre en una zona DNS que administres. Los visitantes siguen necesitando una ruta HTTPS funcional, normalmente por el puerto TCP `443`.

Contrastamos el procedimiento con la documentación oficial. No cambiamos la configuración real del DNS, el cortafuegos ni el servidor, ni ejecutamos Certbot, emitimos certificados o probamos un despliegue público.

[Práctica local con la aplicación de notas](https://youdozi.github.io/en/posts/2026-11-28-self-hosting-ai-notes/) · [Cuatro servicios de subdominios gratuitos para alojar Nginx en casa](https://youdozi.github.io/en/posts/2026-11-28-nginx-free-subdomains/)
