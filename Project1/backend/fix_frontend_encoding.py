from pathlib import Path
p = Path('../frontend/index.html')
raw = p.read_bytes()
try:
    text = raw.decode('utf-8')
except Exception:
    text = raw.decode('utf-16')
p.write_text(text, encoding='utf-8')
print('convert utf8 done', 'size', len(p.read_bytes()))
