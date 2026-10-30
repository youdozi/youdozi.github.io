---
language: "en"
translationKey: "2026-10-30-node2shell-brotli-runtime-patching"
routeSlug: "2026-10-30-node2shell-brotli-runtime-patching"
kind: "post"
categories: ["security"]
tags: ["node2shell", "nodejs", "brotli", "security"]
publishedAt: "2026-10-30T13:30:11.134567+00:00"
updatedAt: "2026-10-30T13:30:11.134567+00:00"
title: "Node2Shell Response: Trace Brotli Decompression and Verify Node.js Rollout"
description: "Check CVE-2026-111497 fixes, Brotli input paths and misleading version labels. Collect runtime evidence and distinguish installation from adoption by every worker and replica."
reviewedAt: "2026-10-30"
reviewStatus: "revised"
reviewScope: "Primary security advisories and API documentation; local read-only runtime evidence examples. No exploit reproduction, target discovery or production remediation."
reviewSources: ["https://nodejs.org/en/blog/vulnerability/october-2026-security-releases", "https://nodejs.org/en/blog/release/v22.23.4", "https://nodejs.org/en/blog/release/v24.22.1", "https://nodejs.org/en/blog/release/v26.12.1", "https://github.com/nodejs/node/blob/v24.22.1/deps/brotli/c/common/version.h", "https://expressjs.com/en/resources/middleware/body-parser/", "https://nodejs.org/docs/latest-v24.x/api/process.html"]
---
Node2Shell remediation means replacing Node.js with a fixed runtime and verifying adoption by every worker that decompresses untrusted Brotli data. The [Node.js security advisory](https://nodejs.org/en/blog/vulnerability/october-2026-security-releases) identifies **CVE-2026-111497** as an out-of-bounds write in its bundled Brotli decoder. Updating npm packages and replacing the runtime are separate operations.

## Does every use of Brotli have the same exposure?

The relevant path **decompresses** compressed input. Malformed attacker-supplied Brotli data handled by `node:zlib` can corrupt process memory, leading to crashes, memory disclosure or remote code execution. Compressing outgoing responses with Brotli or enabling HTTP/2 alone does not establish that path. The Node.js project classifies this issue as High.

Trace automatic decompression of external HTTP responses, uploads, files and queue jobs as well as request bodies. For example, the [body-parser documentation](https://expressjs.com/en/resources/middleware/body-parser/) describes automatic Brotli inflation. Check the installed middleware version and options; failing to find `brotliDecompress` in application code does not establish non-exposure. A background job can decompress external data without an internet-facing listening port.

## Which Node.js releases contain the fix?

Checked on October 30, 2026, the following table lists the official security releases containing this CVE’s fix. It does not freeze the latest recommended version. Check the same supplier’s supported release and follow-up notices when deploying.

| Node.js branch | Official fixed release |
| --- | --- |
| 22.x | [22.23.4](https://nodejs.org/en/blog/release/v22.23.4) |
| 24.x | [24.22.1](https://nodejs.org/en/blog/release/v24.22.1) |
| 26.x | [26.12.1](https://nodejs.org/en/blog/release/v26.12.1) |

For distribution, embedded-product or custom builds, use the supplier’s full package revision and fix evidence. Do not apply these numeric thresholds to a different major branch. The Node.js advisory treats end-of-life branches as affected too; absence from the table does not establish safety.

In particular, `process.versions.brotli` alone is insufficient. The [Brotli version source in patched Node.js 24.22.1](https://github.com/nodejs/node/blob/v24.22.1/deps/brotli/c/common/version.h) still declares `1.2.0`. The [release record](https://nodejs.org/en/blog/release/v24.22.1) explicitly lists the cherry-picked fix. Establish the fixed runtime artifact’s provenance rather than relying on the library label.

## Record evidence from the process itself

![Read the example process PID, executable, Node version and Brotli label, then emit JSON](/assets/diagrams/2026-10-30-node2shell-brotli-runtime-patching-en.svg)

The diagram follows startup of the example application below. It reads information within the same process and prints JSON without comparing versions, discovering services or deciding patch status. Output from a new CLI invocation is not a substitute for evidence from an existing service.

With Node.js 22 or later, save these two files in a new directory. They read properties documented in the [process reference](https://nodejs.org/docs/latest-v24.x/api/process.html) without network requests, decompression or environment-variable output.

### `runtime-evidence.mjs`

```javascript
export function runtimeEvidence() {
  return {
    scope: 'this-process-only',
    pid: process.pid,
    executable: process.execPath,
    node: process.version,
    brotliLabel: process.versions.brotli ?? null,
    platform: process.platform,
    arch: process.arch,
  };
}
```

### `app.mjs`

```javascript
import {runtimeEvidence} from './runtime-evidence.mjs';

console.log(JSON.stringify(runtimeEvidence(), null, 2));
```

```sh
node app.mjs
```

The local check used an official Node.js 24.22.1 container and returned JSON with `node` equal to `v24.22.1` and `brotliLabel` equal to `1.2.0`. PID, path, OS and architecture vary by environment. This demonstrates that a fixed build can retain the old Brotli label; it does not test exploitation or a production deployment.

For a real service, introduce equivalent startup logging through its deployment process and restrict access to those operational logs. Connect the record to the service manager, process and image digest. Paths and PIDs do not belong in public HTTP responses. Starting a separate diagnostic process does not verify replacement of existing workers.

## What remains after installing the package?

1. Record each service’s Node.js executable, supplier, full package version or image digest, processes, workers and replicas. Host `node -v` or a Dockerfile tag alone does not establish the runtime in a running container.
2. Trace the libraries connecting inputs to the Brotli decoder. Keep runtime fix status separate from input exposure. Failing to locate a decompression path within the investigation scope does not patch an unfixed runtime.
3. Obtain a compatible fixed runtime through a trusted channel. Rebuild and roll out container images; replace the actual executable used by process managers and managed platforms too. Do not assume a system Brotli library update replaces a bundled copy.
4. Verify new running evidence for every worker and replica, then check normal API calls, external response processing, background jobs and error rates. Replacing installation files or leaving old replicas running is not verified adoption.

If patching is delayed, consider rejecting or bypassing untrusted Brotli decompression at the actual data path. Removing `br` from `Accept-Encoding` alone does not block every input path. A successful valid-data compression/decompression round trip or a clean `npm audit` also cannot establish that this CVE is fixed.

## Is this the same issue as PHP2Shell?

They are separate flaws. PHP2Shell’s two CVEs concern PHP engine request state; Node2Shell concerns the Brotli decoder. The same Brotli CVE can nevertheless appear in other products, so follow each product’s advisory. The [PHP2Shell response guide](/en/posts/2026-10-30-php2shell-runtime-patching/) explains the distinction between the PHP Windows Brotli rebuild and the PHP engine fixes.

A crash alone does not prove compromise, and missing traces do not exclude it. If compromise is suspected, preserve evidence in a restricted location and investigate or rebuild from a trusted source separately from patching.
