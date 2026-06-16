"""
=============================================================
  AI Classroom Anomaly Detection System
  Detects:
    1. Standing on bench
    2. Fighting / aggressive movement
    3. Head-down (sleeping) for extended time
=============================================================
  Requirements:
    pip install ultralytics opencv-python numpy
  Models downloaded automatically on first run.
=============================================================
"""

import cv2
import numpy as np
import json
import os
import datetime
import time
from collections import defaultdict, deque

# ─────────────────────────────────────────────
#  1. CONFIGURATION  (edit these as needed)
# ─────────────────────────────────────────────
VIDEO_SOURCE       = "fight1.mp4"          # path to your video file (or 0 for webcam)
CONFIG_FILE        = "multi_zone_config.json"
RECORD_DIR         = "anomaly_recordings"
FRAME_SKIP         = 4           # 1=max accuracy, 3=max speed

# --- Timelapse Configuration ---
TIMELAPSE_FPS      = 1           # Frames per second to save for the continuous log
TIMELAPSE_DIR      = "timelapse_logs"
TIMELAPSE_FILE     = os.path.join(TIMELAPSE_DIR, "continuous_1fps_log.mp4")

# --- Thresholds (tune to your camera angle / classroom size) ---
STANDING_HEIGHT_RATIO   = 1.5   # person bbox height vs avg seated height
STANDING_ANKLE_MARGIN   = 30     # px: how high ankle must be above zone top
FIGHT_VELOCITY_THRESH   = 22     # px/frame avg wrist speed to flag as aggressive
FIGHT_IOU_THRESH        = 0.08   # bbox overlap between two people to be "close"
FIGHT_CONFIRM_FRAMES    = 6      # consecutive high-velocity frames before alert
SLEEP_HEAD_DROP_PX      = 150     # px: how far nose drops below shoulder to count
SLEEP_NOSE_CONF_THRESH  = 0.15   # if nose confidence < this, treat as hidden
SLEEP_DWELL_SECONDS     = 5     # seconds of head-down before alert fires

# ─────────────────────────────────────────────
#  YOLOv8 Pose keypoint indices (COCO order)
# ─────────────────────────────────────────────
KP_NOSE        = 0
KP_L_SHOULDER  = 5
KP_R_SHOULDER  = 6
KP_L_ELBOW     = 7
KP_R_ELBOW     = 8
KP_L_WRIST     = 9
KP_R_WRIST     = 10
KP_L_HIP       = 11
KP_R_HIP       = 12
KP_L_KNEE      = 13
KP_R_KNEE      = 14
KP_L_ANKLE     = 15
KP_R_ANKLE     = 16

# Create necessary folders
os.makedirs(RECORD_DIR, exist_ok=True)
os.makedirs(TIMELAPSE_DIR, exist_ok=True)


# ═════════════════════════════════════════════
#  2. CALIBRATION  (zone drawing UI)
# ═══════════════════════════════════════════





def compute_iou(boxA, boxB):
    """IoU between two [x1,y1,x2,y2] boxes."""
    xA = max(boxA[0], boxB[0]);  yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2]);  yB = min(boxA[3], boxB[3])
    inter = max(0, xB - xA) * max(0, yB - yA)
    if inter == 0:
        return 0.0
    areaA = (boxA[2]-boxA[0]) * (boxA[3]-boxA[1])
    areaB = (boxB[2]-boxB[0]) * (boxB[3]-boxB[1])
    return inter / float(areaA + areaB - inter)


def kp_xy(person, idx):
    """Return (x, y, confidence) for a keypoint. Returns (0,0,0) if missing."""
    if person is None or idx >= len(person):
        return (0, 0, 0)
    return (int(person[idx][0]), int(person[idx][1]), float(person[idx][2]))


def midpoint(a, b):
    return ((a[0]+b[0])//2, (a[1]+b[1])//2)


# ═════════════════════════════════════════════
#  4. ANOMALY DETECTORS
# ═════════════════════════════════════════════


class FightingDetector:
    """
    Detects fighting / aggressive movement.
    Logic:
      - Track wrist positions frame-by-frame per person (via track_id)
      - Compute average wrist velocity over a short window
      - Alert when high velocity AND two persons' bounding boxes overlap
    """

    def __init__(self, velocity_thresh=FIGHT_VELOCITY_THRESH,
                 iou_thresh=FIGHT_IOU_THRESH,
                 confirm_frames=FIGHT_CONFIRM_FRAMES):
        self.velocity_thresh  = velocity_thresh
        self.iou_thresh       = iou_thresh
        self.confirm_frames   = confirm_frames
        self.wrist_history    = defaultdict(lambda: deque(maxlen=12))
        self.alert_counter    = defaultdict(int)   # consecutive aggressive frames

    def _wrist_velocity(self, track_id):
        hist = list(self.wrist_history[track_id])
        if len(hist) < 3:
            return 0.0
        vels = []
        for i in range(1, len(hist)):
            for j in range(2):   # left, right wrist
                dx = hist[i][j][0] - hist[i-1][j][0]
                dy = hist[i][j][1] - hist[i-1][j][1]
                vels.append((dx**2 + dy**2) ** 0.5)
        return float(np.mean(vels)) if vels else 0.0

    def update(self, track_id, person_kpts):
        lw = kp_xy(person_kpts, KP_L_WRIST)
        rw = kp_xy(person_kpts, KP_R_WRIST)
        self.wrist_history[track_id].append(
            ((lw[0], lw[1]), (rw[0], rw[1]))
        )

    def detect(self, track_id, my_box, all_boxes, all_track_ids):
        """
        Returns True if this person is fighting.
        all_boxes / all_track_ids are lists for ALL people in the frame.
        """
        velocity = self._wrist_velocity(track_id)
        high_vel = velocity > self.velocity_thresh

        # Check proximity to any other person
        near_someone = False
        for i, other_id in enumerate(all_track_ids):
            if other_id == track_id:
                continue
            if compute_iou(my_box, all_boxes[i]) > self.iou_thresh:
                near_someone = True
                break

        if high_vel and near_someone:
            self.alert_counter[track_id] += 1
        else:
            self.alert_counter[track_id] = max(0, self.alert_counter[track_id] - 1)

        return self.alert_counter[track_id] >= self.confirm_frames

    def cleanup(self, active_ids):
        """Remove state for people who left the frame."""
        stale = [k for k in self.wrist_history if k not in active_ids]
        for k in stale:
            del self.wrist_history[k]
            self.alert_counter.pop(k, None)



    def cleanup(self, active_ids):
        stale = [k for k in list(self.head_down_since.keys()) if k not in active_ids]
        for k in stale:
            del self.head_down_since[k]
            self.alert_active.discard(k)


# ═════════════════════════════════════════════
#  5. DRAWING / OVERLAY HELPERS
# ═════════════════════════════════════════════

COLORS = {
    "standing": (0,   140, 255),   # orange
    "fighting": (0,   0,   255),   # red
    "sleeping": (255, 180, 0  ),   # blue-ish
    "safe":     (0,   220, 0  ),   # green
}

LABELS = {
    "standing": "!! STANDING ON BENCH !!",
    "fighting": "!! FIGHTING !!",
    "sleeping": "!! SLEEPING !!",
}


def draw_person(frame, bbox, anomalies, extra_text=""):
    x1, y1, x2, y2 = map(int, bbox)

    if anomalies:
        # Use color of first anomaly
        color = COLORS[anomalies[0]]
        for anom in anomalies:
            label = LABELS[anom]
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)
            y1 -= 22   # stack multiple labels upward
        cv2.rectangle(frame, (x1, int(bbox[1])), (x2, y2), color, 3)
    else:
        cv2.rectangle(frame, (x1, y1), (x2, y2), COLORS["safe"], 1)

    if extra_text:
        cv2.putText(frame, extra_text, (x1 + 4, y2 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


def draw_zones(frame, zones):
    for z in zones["sitting"]:
        overlay = frame.copy()
        cv2.fillPoly(overlay, [z], (0, 255, 100))
        cv2.addWeighted(overlay, 0.08, frame, 0.92, 0, frame)
        cv2.polylines(frame, [z], True, (0, 220, 80), 1)

    for z in zones["danger"]:
        cv2.polylines(frame, [z], True, (0, 0, 255), 2)


def draw_hud(frame, alerts_this_frame, frame_count, fps):
    h, w = frame.shape[:2]
    ts = datetime.datetime.now().strftime("%H:%M:%S")

    cv2.putText(frame, f"AI Monitor  {ts}  FPS:{fps:.1f}",
                (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (220, 220, 220), 1)

    y = 60
    for label, color in alerts_this_frame:
        cv2.putText(frame, label, (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)
        y += 26


# ═════════════════════════════════════════════
#  6. RECORDING MANAGER
# ═════════════════════════════════════════════

class RecordingManager:
    def __init__(self, directory, frame_size=(1280, 720), fps=15.0):
        self.directory  = directory
        self.frame_size = frame_size
        self.fps        = fps
        self.writers    = {}   # anomaly_type -> VideoWriter

    def write(self, frame, anomaly_types):
        for atype in anomaly_types:
            if atype not in self.writers:
                ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                path = os.path.join(self.directory, f"{atype}_{ts}.avi")
                fourcc = cv2.VideoWriter_fourcc(*"XVID")
                self.writers[atype] = cv2.VideoWriter(
                    path, fourcc, self.fps, self.frame_size)
                print(f"[REC] Started recording: {path}")
            self.writers[atype].write(frame)

    def stop(self, anomaly_type):
        if anomaly_type in self.writers:
            self.writers[anomaly_type].release()
            del self.writers[anomaly_type]
            print(f"[REC] Stopped recording for: {anomaly_type}")

    def stop_all(self):
        for w in self.writers.values():
            w.release()
        self.writers.clear()


# ═════════════════════════════════════════════
#  7. MAIN LOOP
# ═════════════════════════════════════════════

def main():
    # --- Zone calibration ---
    
    # --- Load model ---
    print("\n[INFO] Loading YOLOv8 pose model ...")
    from ultralytics import YOLO
    model = YOLO("yolov8s-pose.pt")
    model.to('cuda')
    print(f"[INFO] Using device: {model.device}")
    print("[INFO] Model ready.\n")

    cap = cv2.VideoCapture(VIDEO_SOURCE)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {VIDEO_SOURCE}")

    source_fps   = cap.get(cv2.CAP_PROP_FPS) or 25.0
    display_fps  = source_fps / FRAME_SKIP
    frame_w      = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_h      = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[INFO] Video: {frame_w}x{frame_h} @ {source_fps:.1f}fps  "
          f"(processing every {FRAME_SKIP} frames)")

    # --- Setup Timelapse Writer ---
    timelapse_fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # Set playback speed to match TIMELAPSE_FPS so it plays back slowly in real-time
    timelapse_writer = cv2.VideoWriter(TIMELAPSE_FILE, timelapse_fourcc, float(TIMELAPSE_FPS), (1280, 720))
    last_saved_time = time.time()
    save_interval = 1.0 / TIMELAPSE_FPS

    # --- Detectors ---
    
    fighting_det = FightingDetector()
    

    recorder     = RecordingManager(RECORD_DIR, frame_size=(1280, 720),
                                    fps=display_fps)

    # FPS counter
    fps_timer    = datetime.datetime.now()
    fps_display  = 0.0
    fps_frames   = 0

    frame_count  = 0
    active_anomaly_types = set()

    print("[INFO] Detection running. Press 'q' to quit, 'r' to delete zone config.\n")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_time = time.time()
        frame_count += 1
        if frame_count % FRAME_SKIP != 0:
            continue

        frame = cv2.resize(frame, (1280, 720))
        display = frame.copy()

        # --- Run tracker ---
        results = model.track(frame, persist=True, tracker="bytetrack.yaml",
                              verbose=False, conf=0.25, imgsz=960)

        frame_anomaly_types = set()
        alerts_hud          = []

        if (results[0].keypoints is not None and
                results[0].boxes.id is not None):

            kpts_all   = results[0].keypoints.data.cpu().numpy()    # (N, 17, 3)
            boxes_all  = results[0].boxes.xyxy.cpu().numpy()         # (N, 4)
            ids_all    = results[0].boxes.id.int().cpu().tolist()    # (N,)

            active_ids = set(ids_all)

            # Update wrist / sleep history for all people
            for i, tid in enumerate(ids_all):
                fighting_det.update(tid, kpts_all[i])

            # Per-person analysis
            for i, tid in enumerate(ids_all):
                person  = kpts_all[i]
                bbox    = boxes_all[i]
                anomalies_this_person = []
                extra   = f"ID:{tid}"

                # ── 1. STANDING ON BENCH ──────────────────────────
               
                # ── 2. FIGHTING ───────────────────────────────────
                if fighting_det.detect(tid, bbox,
                                       list(boxes_all), ids_all):
                    anomalies_this_person.append("fighting")
                    frame_anomaly_types.add("fighting")
                    alerts_hud.append(("!! FIGHTING DETECTED !!", COLORS["fighting"]))

              

            # Cleanup stale tracking state
            fighting_det.cleanup(active_ids)
           

        # --- Continuous 1 FPS Time-lapse Log ---
        # We save the 'display' frame so the tracking boxes are visible in the log
        if (current_time - last_saved_time) >= save_interval:
            timelapse_writer.write(display) 
            last_saved_time = current_time

        # --- Anomaly Recording ---
        newly_started = frame_anomaly_types - active_anomaly_types
        newly_stopped = active_anomaly_types - frame_anomaly_types

        if frame_anomaly_types:
            recorder.write(display, frame_anomaly_types)
            cv2.putText(display, "● REC", (1160, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        for atype in newly_stopped:
            recorder.stop(atype)

        active_anomaly_types = frame_anomaly_types

        # --- Overlays ---
        draw_zones(display, zones)

        # FPS
        fps_frames += 1
        elapsed = (datetime.datetime.now() - fps_timer).total_seconds()
        if elapsed >= 1.0:
            fps_display = fps_frames / elapsed
            fps_frames  = 0
            fps_timer   = datetime.datetime.now()

        draw_hud(display, alerts_hud, frame_count, fps_display)

        cv2.imshow("AI Classroom Monitor", display)
        

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("r"):
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
                print("[INFO] Zone config deleted. Restart to recalibrate.")
                break
    
    # --- Cleanup ---
    cap.release()
    recorder.stop_all()
    timelapse_writer.release()
    cv2.destroyAllWindows()
    print("\n[INFO] Done. Time-lapse saved successfully!")


if __name__ == "__main__":
    main()