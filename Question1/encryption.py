import sys
from pathlib import Path

# ---------- helpers ----------

def _wrap_in_half(c: str, start: str, end: str, k: int, forward: bool) -> str:
    """Shift a letter within [start..end] (length must be 13). Wraps modulo 13."""
    base = ord(start)
    span = ord(end) - base + 1  # should be 13
    if span != 13:
        raise ValueError("Half span must be 13 letters.")
    idx = ord(c) - base
    k = k % span
    new_idx = (idx + k) % span if forward else (idx - k) % span
    return chr(base + new_idx)

def build_maps(shift1: int, shift2: int):
    """Build encryption (enc) and decryption (dec) maps as dictionaries."""
    enc = {}

    # lowercase halves
    k1 = shift1 * shift2          # a–m forward by k1
    k2 = shift1 + shift2          # n–z backward by k2
    for o in range(ord('a'), ord('m') + 1):
        c = chr(o)
        enc[c] = _wrap_in_half(c, 'a', 'm', k1, forward=True)
    for o in range(ord('n'), ord('z') + 1):
        c = chr(o)
        enc[c] = _wrap_in_half(c, 'n', 'z', k2, forward=False)

    # uppercase halves
    k3 = shift1                    # A–M backward by k3
    k4 = shift2 ** 2               # N–Z forward by k4
    for o in range(ord('A'), ord('M') + 1):
        c = chr(o)
        enc[c] = _wrap_in_half(c, 'A', 'M', k3, forward=False)
    for o in range(ord('N'), ord('Z') + 1):
        c = chr(o)
        enc[c] = _wrap_in_half(c, 'N', 'Z', k4, forward=True)

    # inverse for decryption
    dec = {v: k for k, v in enc.items()}
    return enc, dec

def transform_text(text: str, mapping: dict) -> str:
    return ''.join(mapping.get(ch, ch) for ch in text)

# ---------- file functions ----------

def encrypt_file(raw_path: Path, enc_path: Path, shift1: int, shift2: int) -> None:
    enc_map, _ = build_maps(shift1, shift2)
    text = raw_path.read_text(encoding='utf-8')
    enc_text = transform_text(text, enc_map)
    enc_path.write_text(enc_text, encoding='utf-8')

def decrypt_file(enc_path: Path, dec_path: Path, shift1: int, shift2: int) -> None:
    _, dec_map = build_maps(shift1, shift2)
    text = enc_path.read_text(encoding='utf-8')
    dec_text = transform_text(text, dec_map)
    dec_path.write_text(dec_text, encoding='utf-8')

def verify_files(a: Path, b: Path) -> bool:
    return a.read_text(encoding='utf-8') == b.read_text(encoding='utf-8')

# ---------- CLI ----------

def main():
    raw = Path('raw_text.txt')
    enc = Path('encrypted_text.txt')
    dec = Path('decrypted_text.txt')

    # Allow optional CLI args: python encryption.py 3 5
    if len(sys.argv) >= 3:
        try:
            shift1 = int(sys.argv[1])
            shift2 = int(sys.argv[2])
        except ValueError:
            print("Shift arguments must be integers. Example: python encryption.py 3 5")
            return
    else:
        try:
            shift1 = int(input("Enter shift1 (integer): ").strip())
            shift2 = int(input("Enter shift2 (integer): ").strip())
        except Exception:
            print("Invalid input. Please enter integers for shift1 and shift2.")
            return

    if not raw.exists():
        print("raw_text.txt not found in the current folder.")
        return

    encrypt_file(raw, enc, shift1, shift2)
    decrypt_file(enc, dec, shift1, shift2)

    ok = verify_files(raw, dec)
    print("Verification:", "SUCCESS ✅" if ok else "FAILED ❌")
    if ok:
        print(f"Created {enc.name} and {dec.name}")

if __name__ == "__main__":
    main()
