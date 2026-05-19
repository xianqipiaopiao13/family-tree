import re, base64, os, sys

html_path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
out_dir = sys.argv[2] if len(sys.argv) > 2 else 'images'

os.makedirs(out_dir, exist_ok=True)

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Find all data:image/... base64 URIs
pattern = re.compile(r'data:image/([a-z]+);base64,([A-Za-z0-9+/=]+)')

count = 0

def replace_match(m):
    global count
    fmt = m.group(1)  # jpeg or png
    b64 = m.group(2)
    ext = 'jpg' if fmt == 'jpeg' else 'png'
    fname = f'img_{count:03d}.{ext}'
    fpath = os.path.join(out_dir, fname)
    try:
        data = base64.b64decode(b64)
        with open(fpath, 'wb') as f:
            f.write(data)
        count += 1
        return f'images/{fname}'
    except Exception as e:
        print(f'Error decoding image {count}: {e}', file=sys.stderr)
        return m.group(0)

html = pattern.sub(replace_match, html)

out_path = html_path + '.light.html'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

orig_size = os.path.getsize(html_path)
new_size = os.path.getsize(out_path)
print(f'Extracted {count} images to {out_dir}/')
print(f'Original: {orig_size/1024/1024:.1f}MB')
print(f'New HTML: {new_size/1024:.1f}KB ({new_size/1024:.1f}KB)')
print(f'Reduction: {(orig_size-new_size)/1024/1024:.1f}MB')
print(f'Output: {out_path}')
