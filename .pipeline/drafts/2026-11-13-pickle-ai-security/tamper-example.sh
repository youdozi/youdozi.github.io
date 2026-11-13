cp secure-program/secure-program.js changed-program.js
printf '\n' >> changed-program.js
./target/debug/credential-enclave-verify program \
  --source changed-program.js \
  --release secure-program.release.json
echo $?
