# Pavel V2 reference configuration

This frozen configuration was supplied by Pavel as `geb-v2-colleague-repro.zip` and imported to preserve the original evidence. It includes the scripts, scenarios, tool schemas, fixtures, configuration, synthetic audio, historical traces, scoring and generated files from the bundle. The input WAVs are synthetic Piper speech. The archive covers the original protocol, including voice. The proposed unified benchmark uses text throughout.

The original ZIP SHA-256 is `acf5945b7f40528acac57f77c81c92646451c1e4cd84ef4cf66c8a1af4b0d017`. Git stores a lossless tar.xz repack in 17 numbered parts. Identical files are represented by hardlinks. All member names and bytes are preserved.

```bash
cat archive/pavel-v2.tar.xz.part-* > /tmp/pavel-v2.tar.xz
echo '68f788ff25642206bf839e73ffb0df7b716af2e37fe8c6338063b5620c8836bc  /tmp/pavel-v2.tar.xz' | sha256sum -c
mkdir -p /tmp/geb-pavel-v2
tar -xJf /tmp/pavel-v2.tar.xz -C /tmp/geb-pavel-v2
cd /tmp/geb-pavel-v2
sha256sum -c SHA256SUMS.txt
```

Pavel's README in the extracted bundle documents installation and the native llama.cpp reference setup. The frozen text subset has 29 scored Russian scenarios, three seeds (42, 43 and 44), a 0/1/2 rubric, and a published reference of **105/174**. The full historic score including voice is **60.2/100**.

The Ollama comparison uses a separately measured runtime on the Dell laptop. The original Qwen3 4B Instruct 2507 Q4_K_M GGUF matches the locally installed weight file byte-for-byte. Its full SHA-256 is `85e4a5b7b8ef0e48af0e8658f5aaab9c2324c76c1641493f4d1e25fce54b18b9`.

- [Task comparison](../../results/pavel-v2-task-comparison.md)
- [Related benchmarks](../../results/related-benchmarks.md)
