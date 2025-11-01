# Script to automate converting captured HTTP response text (headers + HTML body) to PDF.
# Assumes the captured content is saved as a text file (e.g., from PCAPdroid's decrypted view or export).
# Usage: python script.py input.txt (or pipe via stdin: cat input.txt | python script.py)
# Install WeasyPrint first: pip install weasyprint
# Handles gzip decompression if specified in headers (though your example seems pre-decoded).
# For external CSS/images: Place them in the working directory or modify paths in the HTML manually.

import sys
import zlib
from weasyprint import HTML

# Read input from file or stdin
if len(sys.argv) > 1:
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        content = f.read()
else:
    content = sys.stdin.read()

# Split headers and body (assuming \n\n separates them)
parts = content.split('\n\n', 1)
if len(parts) == 2:
    headers_text, body = parts
else:
    headers_text = ''
    body = content # No headers, assume raw HTML

# Parse headers into dict (skip non-key:value lines like status)
headers = {}
for line in headers_text.split('\n'):
    if ':' in line:
        key, value = line.split(':', 1)
        headers[key.strip().lower()] = value.strip()

# Decompress if gzip (convert str to bytes, decompress, back to str)
if 'content-encoding' in headers and 'gzip' in headers['content-encoding']:
    try:
        body_bytes = body.encode('utf-8') # Assume UTF-8; adjust if needed
        decompressed = zlib.decompress(body_bytes, 16 + zlib.MAX_WBITS)
        body = decompressed.decode('utf-8')
    except zlib.error as e:
        print(f"Error decompressing: {e}. Using raw body.")
    except UnicodeError as e:
        print(f"Encoding error: {e}. Check content encoding.")

# Convert HTML body to PDF
HTML(string=body).write_pdf('output.pdf')
print("PDF saved as output.pdf")
