### Full Step-by-Step Tutorial: Pipeline from Capturing Traffic in PCAPdroid to Saving HTML as PDF

This tutorial outlines the complete pipeline for capturing network traffic using PCAPdroid (an open-source Android app for traffic analysis), decrypting it (if TLS-encrypted), exporting the data, extracting the HTTP response body (e.g., your HTML template), and automatically converting it to a PDF. The process assumes you're working on an Android device for capture and a computer (Windows, macOS, or Linux) for processing and conversion. It's designed to be as automated as possible without manually pasting HTML into scripts.

The pipeline handles scenarios like your example (decrypted HTTP/2 response with HTML body). Key tools include PCAPdroid for capture, tshark (command-line version of Wireshark, open-source) for extraction, and a Python script using WeasyPrint for PDF conversion. All steps use open-source tools.

#### Prerequisites
- **PCAPdroid**: Install from Google Play, F-Droid, or GitHub (https://github.com/emanuele-f/PCAPdroid). No root needed for basic capture, but root enables full TLS decryption.
- **Wireshark/tshark**: Download and install Wireshark (includes tshark) from https://www.wireshark.org/. tshark is used for CLI extraction.
- **Python 3.x**: Install Python, then run `pip install weasyprint` (open-source library for HTML-to-PDF). WeasyPrint requires system dependencies like Pango and Cairo—see https://weasyprint.readthedocs.io/en/stable/installation.html.
- **Transfer tools**: Use USB, email, or cloud (e.g., Google Drive) to move files from Android to your computer.
- Enable TLS decryption in PCAPdroid if needed (Settings > TLS Decryption; may require root and CA certificate installation for full access).

If your traffic is HTTPS, ensure decryption is enabled to get plaintext HTML bodies in the export.

#### Step 1: Configure and Capture Traffic in PCAPdroid
PCAPdroid intercepts traffic via a virtual VPN and can decrypt TLS for plaintext viewing/export.
1. Open PCAPdroid on your Android device.
2. Go to Settings (gear icon) > Dump Mode. Select "PCAP File" for direct local saving (easiest for this pipeline). Alternatively, use "HTTP Server" for network download or "UDP/TCP Exporter" for real-time streaming to a PC.


3. (Optional) Enable TLS Decryption in Settings if your target traffic (e.g., HTTPS) needs decryption for plaintext HTTP bodies. For non-root, it's limited; root allows full decryption.
4. (Optional) Set an "App Filter" in the Status tab to capture only from a specific app (e.g., your browser).
5. Tap the play button (▶️) to start capture. Accept the VPN prompt if it's your first time.
6. Use the target app/browser to generate traffic (e.g., load the webpage that produces your HTTP/2 response with HTML).
7. Monitor in the "Connections" tab: Tap a connection to view details, including plaintext request/response headers and body (if decrypted). You can copy text here manually if needed, but for automation, proceed to export.
8. Tap the stop button (■) to end capture.

#### Step 2: Export the Captured Data
Export as a PCAP file, which includes decrypted traffic (plaintext HTTP bodies if decryption was enabled).
- **Using PCAP File Mode** (Recommended for Simplicity):
1. After starting capture (Step 1), a file picker appears—choose a name (e.g., `capture.pcap`) and save location (e.g., Downloads).
2. Stop capture: A dialog offers to share, delete, or keep the file.
3. Transfer the `.pcap` file to your computer (e.g., via USB or sharing).


- **Alternative: HTTP Server Mode** (For Network Transfer):
1. Select this mode in Settings.
2. Start capture and note the URL (e.g., `http://192.168.1.10:8080`).
3. On your PC (same network), open the URL in a browser to download the PCAP (stop capture to finalize).
4. For real-time Wireshark: Use `curl -NLs [URL] | wireshark -k -i -` (Linux).


- **Alternative: UDP/TCP Exporter** (For Real-Time Streaming):
1. Set remote IP/port in Settings (e.g., your PC's IP and port 1234).
2. On PC (Linux): Use `nc -lvp 1234 | wireshark -k -i -` (TCP) or `udp_receiver.py` script (UDP, download from PCAPdroid GitHub).
3. Start/stop capture; save the streamed data as PCAP on PC.


- **Export Connections as CSV/JSON** (Metadata Only, Not Full Bodies):
1. In the Connections tab, tap the menu > Export > CSV or JSON.
2. This saves metadata (e.g., IPs, SNI, stats) but not full HTTP bodies—use PCAP for complete payloads.



The PCAP file now contains your captured packets, including decrypted HTTP responses.

#### Step 3: Extract the HTTP Response Body from the PCAP File
Use tshark to export HTTP objects (e.g., HTML bodies) as text files. This automates extraction without manual copying.
1. Open a terminal/command prompt on your computer.
2. Run: `tshark -r capture.pcap --export-objects http,output_dir`
- `-r capture.pcap`: Input PCAP file.
- `--export-objects http,output_dir`: Exports HTTP objects (e.g., response bodies like HTML) to a directory named `output_dir` (create it first if needed).
- This creates files like `do7j4mk5.html` (from your example's content-disposition header).






3. For specific filtering (e.g., only responses):
- `tshark -r capture.pcap -Y http.response -T fields -e http.file_data > response_body.txt`
- `-Y http.response`: Filter to HTTP responses.
- `-T fields -e http.file_data`: Extracts the response body as text.
- Redirect `>` to save to a file.






4. If headers are needed: `tshark -r capture.pcap -Y http -T fields -e http.request.full_uri -e http.response.code -e http.file_data`
5. For large PCAPs or more requests: Increase limits if needed (tshark handles >1000 by default).


6. Verify: Open `output_dir` or `response_body.txt`—it should contain your HTML (e.g., starting with ``).

If the body is chunked or gzipped, tshark handles decompression automatically if it's HTTP.

For images/CSS (e.g., your `djtj40muk4ld.png` or `bookmate.css`), they'll export separately—download them manually if referenced in HTML and place in the same folder for PDF rendering.

#### Step 4: Convert the Extracted HTML to PDF Using the Automated Script
Use the Python script (modified from previous) to convert the text file (headers + body or just body) to PDF. It handles input files, decompression, and conversion.
1. Save this script as `convert_to_pdf.py`:
```python
# Automated script: Takes input file (e.g., from tshark extraction) and outputs PDF.
# Run: python convert_to_pdf.py response_body.txt
# Handles gzip if in headers.

import sys
import zlib
from weasyprint import HTML

if len(sys.argv) < 2:
print("Usage: python convert_to_pdf.py input.txt")
sys.exit(1)

with open(sys.argv[1], 'r', encoding='utf-8') as f:
content = f.read()

# Split headers and body
parts = content.split('\n\n', 1)
if len(parts) == 2:
headers_text, body = parts
else:
body = content

# Parse headers
headers = {k.strip().lower(): v.strip() for line in headers_text.split('\n') if ':' in line for k, v in [line.split(':', 1)]}

# Decompress if gzip
if 'content-encoding' in headers and 'gzip' in headers['content-encoding']:
try:
body_bytes = body.encode('utf-8')
body = zlib.decompress(body_bytes, 16 + zlib.MAX_WBITS).decode('utf-8')
except Exception as e:
print(f"Decompression error: {e}. Using raw body.")

# Convert to PDF
HTML(string=body).write_pdf('output.pdf')
print("PDF saved as output.pdf")
```
2. Run: `python convert_to_pdf.py response_body.txt` (or your extracted file).
3. Output: `output.pdf` with rendered HTML (styles, images if local).
4. If multiple files from `--export-objects`: Run the script on each HTML file.

#### Step 5: Verify and Troubleshoot
1. Open `output.pdf` in a viewer (e.g., Sumatra PDF or Okular, open-source).
2. Common issues:
- No decryption: Enable in PCAPdroid and retry capture.
- Missing assets: Edit HTML to use absolute paths or download referenced files.
- Large files: Split PCAP if needed (`editcap` from Wireshark).
- Errors in script: Ensure WeasyPrint is installed; test with your example HTML.
3. For full automation: Chain in a bash script (e.g., capture export > tshark extract > Python convert).

This pipeline works end-to-end: Capture on mobile, export PCAP, extract on PC, convert to PDF. For scripting full automation (e.g., batch processing), extend the Python script to loop over extracted files.



If you need adjustments (e.g., for specific OS), provide details!
