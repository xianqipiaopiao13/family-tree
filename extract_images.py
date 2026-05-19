import re, base64, os, sys
from PIL import Image
from io import BytesIO

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
    fmt = m.group(1)  # jpeg, png, etc.
    b64 = m.group(2)
    try:
        data = base64.b64decode(b64)
    except Exception as e:
        print(f'Error decoding image {count}: {e}', file=sys.stderr)
        return m.group(0)

    fname = f'img_{count:03d}.jpg'
    fpath = os.path.join(out_dir, fname)

    try:
        if fmt == 'png':
            # Convert PNG to JPEG for smaller size
            img = Image.open(BytesIO(data))
            if img.mode in ('RGBA', 'P', 'LA'):
                bg = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    bg.paste(img, mask=img.split()[3])
                elif img.mode == 'P':
                    img = img.convert('RGBA')
                    bg.paste(img, mask=img.split()[3])
                else:
                    bg.paste(img)
                img = bg
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(fpath, 'JPEG', quality=80, optimize=True)
        else:
            # JPEG: save as-is
            with open(fpath, 'wb') as f:
                f.write(data)
        count += 1
        return f'images/{fname}'
    except Exception as e:
        print(f'Error saving image {count}: {e}', file=sys.stderr)
        return m.group(0)

html = pattern.sub(replace_match, html)

out_path = html_path + '.light.html'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

orig_size = os.path.getsize(html_path)
new_size = os.path.getsize(out_path)
print(f'Extracted {count} images to {out_dir}/ (all JPEG, optimized)')
print(f'Original: {orig_size/1024/1024:.1f}MB')
print(f'New HTML: {new_size/1024/1024:.4f}MB ({new_size/1024:.1f}KB)')
print(f'Reduction: {(orig_size-new_size)/1024/1024:.1f}MB')
print(f'Output: {out_path}')
