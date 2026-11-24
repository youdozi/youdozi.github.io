import {strict as assert} from "node:assert";
import {readFileSync} from "node:fs";
import {runInNewContext} from "node:vm";

assert.equal(readFileSync("dist/ads.txt", "utf8"), "google.com, pub-2488826942326109, DIRECT, f08c47fec0942fa0\n");
const privacy = JSON.parse(readFileSync("src/lib/privacy.json", "utf8"));
for (const [lang, copy] of Object.entries(privacy)) {
  const homepage = readFileSync(`dist/${lang}/index.html`, "utf8");
  const page = readFileSync(`dist/${lang}/privacy/index.html`, "utf8");
  const article = page.match(/<article class="privacy prose"[^>]*>([\s\S]*?)<\/article>/)?.[1] || "";
  assert.ok(homepage.includes(`href="/${lang}/privacy/"`), `${lang}: footer link`);
  assert.ok(article.includes(`>${copy.title}</h1>`), `${lang}: heading`);
  assert.ok(article.includes(`>${copy.analytics}</p>`) && article.includes(`>${copy.ads}</p>`), `${lang}: disclosure`);
  assert.ok(article.includes('href="https://policies.google.com/technologies/partner-sites"'), `${lang}: Google link`);
}
for (const path of ["dist/index.html", "dist/en/index.html", "dist/ko/index.html", "dist/en/posts/2026-11-02-ai-assisted-attack-defense/index.html"]) {
  const html = readFileSync(path, "utf8");
  assert.equal((html.match(/google-adsense-account/g) || []).length, 1, path);
  const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(match => match[1]).filter(script => script.includes("pagead/js/adsbygoogle.js"));
  assert.equal(scripts.length, 1, path);
  for (const hostname of ["youdozi.github.io", "localhost", "preview.example.com"]) {
    const appended = [];
    runInNewContext(scripts[0], {location: {hostname}, document: {createElement: () => ({}), head: {append: element => appended.push(element)}}});
    assert.equal(appended.length, hostname === "youdozi.github.io" ? 1 : 0, `${path}: ${hostname}`);
    if (appended.length) assert.deepEqual({...appended[0]}, {async: true, src: "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2488826942326109", crossOrigin: "anonymous"});
  }
}
console.log("AdSense output verified without network requests");
