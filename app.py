from flask import Flask, render_template, Response, redirect, url_for, jsonify, request
import cv2
import sqlite3
import time
from detect import detect_weapon_from_frame
from alert import send_sms_alert

app = Flask(__name__)

camera_on = False
cap = None

# alert cooldown
last_alert_sent = 0
ALERT_INTERVAL = 20  # seconds


def get_db():
    return sqlite3.connect("weapon.db")


# ---------------- CAMERA STREAM ----------------
def generate_frames():
    global camera_on, cap, last_alert_sent

    cap = cv2.VideoCapture(0)

    while camera_on:
        success, frame = cap.read()
        if not success:
            break

        result = detect_weapon_from_frame(frame)

        if result:
            x1, y1, x2, y2 = result['box']

            # Draw bounding box
            cv2.rectangle(frame, (x1,y1), (x2,y2), (0,0,255), 3)
            cv2.putText(frame, result['name'].upper(),
                        (x1,y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.9, (0,0,255), 3)

            # Save DB
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO detections (weapon_name, image, datetime) VALUES (?, ?, ?)",
                (result['name'], result['image'], result['time'])
            )
            conn.commit()
            conn.close()

            # ---- ALERT CONTROL (IMPORTANT FIX) ----
            now = time.time()
            if now - last_alert_sent > ALERT_INTERVAL:
                try:
                    send_sms_alert(result['name'], result['time'])
                    print("Alert Sent Successfully")
                    last_alert_sent = now
                except Exception as e:
                    print("Alert Error:", e)
            else:
                print("Alert Cooldown Active")

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    if cap:
        cap.release()


# ---------------- SEARCH BY DATE ----------------
@app.route('/search', methods=['GET'])
def search():
    date = request.args.get('date')

    if not date:
        return jsonify([])

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT weapon_name, image, datetime
        FROM detections
        WHERE datetime LIKE ?
        ORDER BY id DESC
    """, (date + "%",))

    data = cur.fetchall()
    conn.close()

    return jsonify(data)


# ---------------- ROUTES ----------------
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/enable')
def enable():
    global camera_on
    camera_on = True
    return redirect(url_for('dashboard'))


@app.route('/disable')
def disable():
    global camera_on
    camera_on = False
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")


@app.route('/get_detections')
def get_detections():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT weapon_name, image, datetime
        FROM detections
        ORDER BY id DESC LIMIT 10
    """)
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(debug=True)
