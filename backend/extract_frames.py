import os
import cv2
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app)

# Geçici olarak kaydedilecek video dosyasının yolu
video_save_path = "uploaded_video.ts"
output_folder = "frames"  # Karelerin kaydedileceği klasör

# Çıktı klasörünü oluştur
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def extract_frames(video_path, output_folder):
    """Video dosyasından belirli aralıklarla kare yakalar ve kaydeder."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Video dosyası açılamadı")
        return

    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))  # Video karesi hızı
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Toplam kare sayısı
    duration = frame_count / frame_rate  # Video süresi (saniye cinsinden)
    minutes = int(duration / 60)  # Video süresi (dakika cinsinden)

    print(f"Video süresi: {minutes} dakika")

    # Her dakika bir kare almak için gerekli kare sayısı
    capture_interval_frames = frame_rate * 60

    frame_number = 0
    image_number = 1

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_number % capture_interval_frames == 0:
            output_path = os.path.join(output_folder, f"{image_number}.jpg")
            cv2.imwrite(output_path, frame)
            print(f"Kare kaydedildi: {output_path}")
            image_number += 1
        
        frame_number += 1

    cap.release()
    print("İşlem tamamlandı")

@app.route('/upload_video', methods=['POST'])
def upload_video():
    """Video dosyasını yükler ve kareleri çıkarır"""
    file = request.files.get('video')
    if not file:
        return jsonify({'error': 'No video uploaded'}), 400

    file.save(video_save_path)

    # Kare çıkarma iş parçacığını başlat
    thread = threading.Thread(target=extract_frames, args=(video_save_path, output_folder))
    thread.start()
    
    return jsonify({'message': 'Video uploaded successfully and frames are being extracted.'}), 200

@app.route('/frames', methods=['GET'])
def list_frames():
    """Çıkarılan karelerin listesini döndüren endpoint"""
    try:
        files = os.listdir(output_folder)
        return jsonify(files), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/frames/<filename>', methods=['GET'])
def get_frame(filename):
    """Çıkarılan kareleri döndüren endpoint"""
    return send_from_directory(output_folder, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)