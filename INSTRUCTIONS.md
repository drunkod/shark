### How to Use This Custom mitmproxy Addon in PCAPdroid

This addon captures decrypted HTTP responses with `content-type: text/html` and saves the HTML body to a file on your device (e.g., in `/sdcard/PCAPdroid_captures/`). It uses the filename from the `content-disposition` header if available (like "do7j4mk5.html" in your example), or generates one with a timestamp otherwise. This automates saving the HTML without manual extraction from PCAP files. After saving, transfer the HTML file to your computer and use the previous Python script to convert it to PDF.

Follow these steps to set it up (based on the PCAPdroid documentation you provided):

1. **Create the Addons Directory**:
   - On your Android device, create a directory like `/sdcard/PCAPdroid_addons/` (use a file manager app or ADB).

2. **Set the Addons Directory in PCAPdroid**:
   - Open PCAPdroid.
   - Go to Settings > TLS Decryption (ensure it's enabled for your target app or domain, e.g., add a rule for "books.yandex.ru" or your browser).
   - Tap the hamburger menu (three lines) > "Addons" > "Set user dir".
   - Select the `/sdcard/PCAPdroid_addons/` directory and tap "Allow" to grant read access.

3. **Enable Files Access (Required for Saving to SDCard)**:
   - In the same Addons menu, select "Enable files access" and grant the storage permission. This allows the addon to write files outside the app's private directory (e.g., to `/sdcard/`).

4. **Create and Transfer the Addon Script**:
   - Copy the Python script above into a file named `SaveHtml.py` on your computer.
   - Transfer it to the addons directory on your device:
     - Use ADB: `adb push SaveHtml.py /sdcard/PCAPdroid_addons/`
     - Or use a file manager to copy it via USB/email.

5. **Load and Enable the Addon**:
   - In PCAPdroid's Addons screen, tap the refresh icon (circular arrow) to load the script. "SaveHtml" should appear in the list.
   - Toggle it on to enable.
   - Restart the capture if already running.

6. **Start Capture with TLS Decryption**:
   - In PCAPdroid Settings > Dump Mode, choose your preferred mode (e.g., "PCAP File" for logging, but the addon works independently).
   - Tap the play button to start capture.
   - Ensure a decryption rule exists for your target (e.g., domain "books.yandex.ru" or the app generating the traffic). The addon only runs on decrypted connections.
   - Load the target page/app to trigger the HTTP response (e.g., the book download from Yandex).

7. **Verify the Save**:
   - Check the mitm addon log in PCAPdroid (Addons > View log) for messages like "HTML response saved to: /sdcard/PCAPdroid_captures/do7j4mk5.html".
   - Use a file manager to browse `/sdcard/PCAPdroid_captures/`—the HTML file should be there.
   - If the browser caches responses, add `--anticache` to "Additional mitmproxy options" in PCAPdroid Settings to prevent caching.

8. **Transfer and Convert to PDF**:
   - Transfer the saved HTML file to your computer (e.g., via USB or ADB: `adb pull /sdcard/PCAPdroid_captures/do7j4mk5.html .`).
   - Use the previous Python script: `python convert_to_pdf.py do7j4mk5.html` (it will handle the HTML and save as `output.pdf`).

### Notes and Customizations
- **Matching Criteria**: The addon saves any `text/html` response. To make it specific (e.g., only for Yandex books), add a check like `if 'books.yandex' in flow.request.pretty_url:` inside the `response` method.
- **Handling Images/CSS**: If the HTML references external assets (e.g., "bookmate.css" or "djtj4mk4ld.png"), download them separately and place in the same folder on your PC before conversion, or modify the HTML paths.
- **Limitations**: Based on mitmproxy docs, the `response` event provides full access to `flow.response.content` after the body is read. Addons run in PCAPdroid's Python environment, so no extra imports beyond basics (e.g., `os`, `re`, `datetime` should work). Test for errors in the log.
- **Research Insights**: From mitmproxy docs, addons use event hooks like `response(flow)` to access/modify HTTP data. We use it here to read `content` without modification (unlike the example's replace). The structure matches: a class with event methods, instantiated in `addons = []`.

If issues arise (e.g., file permissions), check PCAPdroid logs or adjust the save directory. For advanced tweaks, refer to the mitmproxy API for more events like `request` if needed.
