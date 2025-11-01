# SaveHtml.py - Custom mitmproxy addon for PCAPdroid to save HTML responses to files

import os
import re
from datetime import datetime  # For timestamping if no filename

class SaveHtml:
    def __init__(self):
        # Directory to save captured HTML files (must be accessible, e.g., via "Enable files access" in PCAPdroid)
        self.save_dir = "/sdcard/PCAPdroid_captures/"
        # Create the directory if it doesn't exist
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        print("SaveHtml addon initialized. Saving to: " + self.save_dir)

    def done(self):
        # Cleanup if needed (e.g., close resources)
        print("SaveHtml addon unloaded.")
        pass

    def response(self, flow):
        # Check if it's a text/html response
        content_type = flow.response.headers.get('content-type', '').lower()
        if 'text/html' in content_type:
            # Decode the body (assume UTF-8; adjust if needed)
            try:
                body = flow.response.content.decode('utf-8')
            except UnicodeDecodeError:
                print("Error decoding response body as UTF-8. Skipping.")
                return

            # Get filename from content-disposition if available
            disposition = flow.response.headers.get('content-disposition', '')
            filename_match = re.search(r'filename="?([^";]+)"?', disposition)
            if filename_match:
                filename = filename_match.group(1)
            else:
                # Fallback: use timestamp and URL hash
                url_hash = hash(flow.request.pretty_url) % (10**8)  # Simple hash
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"captured_{timestamp}_{url_hash}.html"

            # Full save path
            save_path = os.path.join(self.save_dir, filename)

            # Save the HTML body to file
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(body)
                print(f"HTML response saved to: {save_path}")
            except IOError as e:
                print(f"Error saving file: {e}")

addons = [SaveHtml()]
