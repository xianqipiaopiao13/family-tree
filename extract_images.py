import re, base64, os, sys
from PIL import Image
from io import BytesIO

html_path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
out_dir = sys.argv[2] if len(sys.argv) > 2 else 'images'
MAX_SIZE = 1600  # max width/height in pixels
JPEG_QUALITY = 60

os.makedirs(out_dir, exist_ok=True)

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

orig_size = len(html.encode('utf-8'))

def resize_img(img):
    w, h = img.size
    if w <= MAX_SIZE and h <= MAX_SIZE:
        return img
    ratio = min(MAX_SIZE / w, MAX_SIZE / h)
    return img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

# Step 1: Extract all base64 images, convert to JPEG
pattern = re.compile(r'data:image/([a-z]+);base64,([A-Za-z0-9+/=]+)')
count = 0

def replace_match(m):
    global count
    fmt = m.group(1)
    b64 = m.group(2)
    try:
        data = base64.b64decode(b64)
    except Exception as e:
        print(f'Error decoding image {count}: {e}', file=sys.stderr)
        return m.group(0)

    fname = f'img_{count:03d}.jpg'
    fpath = os.path.join(out_dir, fname)
    quality = JPEG_QUALITY

    try:
        img = Image.open(BytesIO(data))
        if img.mode in ('RGBA', 'P', 'LA', 'PA'):
            bg = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                bg.paste(img, mask=img.split()[3])
            elif img.mode == 'P':
                img = img.convert('RGBA')
                bg.paste(img, mask=img.split()[3])
            elif img.mode == 'PA':
                bg.paste(img, mask=img.split()[3])
            else:
                bg.paste(img)
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        img = resize_img(img)
        # PNG originals may need higher quality for text/line art
        if fmt == 'png':
            quality = 70
        img.save(fpath, 'JPEG', quality=quality, optimize=True)
        count += 1
        return f'images/{fname}'
    except Exception as e:
        print(f'Error saving image {count}: {e}', file=sys.stderr)
        return m.group(0)

html = pattern.sub(replace_match, html)

# Step 2: Add lazy loading to all img tags
html = html.replace('<img ', '<img loading="lazy" decoding="async" ')

# Step 3: Write output, replacing the original file
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

new_size = os.path.getsize(html_path)
print(f'Extracted {count} images to {out_dir}/ (all JPEG, optimized)')
print(f'Original: {orig_size/1024/1024:.1f}MB')
print(f'New HTML: {new_size/1024/1024:.4f}MB ({new_size/1024:.1f}KB)')
print(f'Reduction: {(orig_size-new_size)/1024/1024:.1f}MB')
print(f'Added loading="lazy" to all img tags')
