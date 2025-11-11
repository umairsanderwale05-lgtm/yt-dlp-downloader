from flask import Flask, request, render_template, send_file, jsonify
import yt_dlp
import os

# Flask app initialize
app = Flask(__name__)

# Download folder create karte hain agar na ho to
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ----------------------------
# Home Route
# ----------------------------
@app.route('/')
def index():
    return render_template('index.html')


# ----------------------------
# Get Video Info (Without Download)
# ----------------------------
@app.route('/info', methods=['POST'])
def get_info():
    url = request.form.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        ydl_opts = {'quiet': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            data = {
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'uploader': info.get('uploader')
            }

        return jsonify(data)

    except Exception as e:
        return jsonify({'error': f'⚠️ Unable to fetch video info: {str(e)}'}), 500


# ----------------------------
# Download Video (1080p MP4)
# ----------------------------
@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        # yt-dlp options
        ydl_opts = {
            'format': 'bestvideo[height<=720]+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s'
        }

        # Try downloading the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
            except Exception as e:
                return jsonify({
                    'error': '❌ Unable to download this video (may need login or age verification).'
                }), 400

            filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + ".mp4"

        # Return the file for download
        return send_file(filename, as_attachment=True)

    except Exception as e:
        return jsonify({'error': f'⚠️ Unexpected error: {str(e)}'}), 500


# ----------------------------
# Run Flask App
# ----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

