# macOS·Linux 셸, Git·curl·Rustup 및 네이티브 빌드 도구가 필요합니다.
# 새 작업 폴더에서 실행합니다. 아래 검증은 계정 로그인이나 실제 비밀번호를 사용하지 않습니다.
git clone https://github.com/pickle-com/credential-enclave.git
cd credential-enclave
git checkout cff16a343bf5bb7953e5b65df6ab3600107e127d
rustup toolchain install 1.100.0 --profile minimal
cargo +1.100.0 build --locked -p credential-enclave-verify
curl --fail --location \
  https://github.com/pickle-com/credential-enclave/releases/download/secure-program-v42/secure-program.release.json \
  --output secure-program.release.json
./target/debug/credential-enclave-verify program \
  --source secure-program/secure-program.js \
  --release secure-program.release.json
