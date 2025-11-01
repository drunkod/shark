# SaveEpub.py - Custom mitmproxy addon for PCAPdroid to save EPUB responses to files

import os
import re
from datetime import datetime  # For timestamping if no filename
import zlib  # For potential decompression

class SaveEpub:
    def __init__(self):
        # Directory to save captured EPUB files (must be accessible, e.g., via "Enable files access" in PCAPdroid)
        self.save_dir = "/sdcard/PCAPdroid_captures/"
        # Create the directory if it doesn't exist
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        print("SaveEpub addon initialized. Saving to: " + self.save_dir)

    def done(self):
        # Cleanup if needed (e.g., close resources)
        print("SaveEpub addon unloaded.")
        pass

    def response(self, flow):
        # Check if it's an application/epub+zip response
        content_type = flow.response.headers.get('content-type', '').lower()
        if 'application/epub+zip' in content_type:
            # Get the raw binary content
            body = flow.response.content  # This is bytes

            # Decompress if gzip-encoded
            content_encoding = flow.response.headers.get('content-encoding', '').lower()
            if 'gzip' in content_encoding:
                try:
                    body = zlib.decompress(body, 16 + zlib.MAX_WBITS)
                except zlib.error as e:
                    print(f"Error decompressing EPUB: {e}. Using raw body.")

            # Get filename from content-disposition if available
            disposition = flow.response.headers.get('content-disposition', '')
            filename_match = re.search(r'filename="?([^";]+)"?', disposition)
            if filename_match:
                filename = filename_match.group(1)
            else:
                # Fallback: use timestamp and URL hash
                url_hash = hash(flow.request.pretty_url) % (10**8)  # Simple hash
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"captured_{timestamp}_{url_hash}.epub"

            # Full save path
            save_path = os.path.join(self.save_dir, filename)

            # Save the EPUB binary to file
            try:
                with open(save_path, 'wb') as f:
                    f.write(body)
                print(f"EPUB response saved to: {save_path}")
            except IOError as e:
                print(f"Error saving file: {e}")

addons = [SaveEpub()]

