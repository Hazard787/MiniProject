"""
=============================================================
  AI Classroom Anomaly Detection System
  Detects:
    1. Fighting / aggressive movement   (wrist velocity + proximity)
    2. Standing on bench                (baseline-calibrated pose)
  Features: Anomaly clip storage + compressed video recording
=============================================================
  Requirements:
    pip install ultralytics opencv-python numpy
=============================================================
"""

import cv2
import numpy as np
import os
import datetime
from collections import defaultdict, deque
from ultralytics import YOLO

# ─────────────────────────────────────────────
#  1. CONFIGURATION
# ─────────────────────────────────────────────
VIDEO_SOURCE        = "fight1.mp4"          # path to video file (or 0 for webcam)
RECORD_DIR          = "anomaly_recordings"
FRAME_SKIP          = 4                  # 1=max accuracy, 4=max speed

# --- Baseline (standing detector) ---
BASELINE_FRAMES     = 150                # frames used to learn seated posture
SHOULDER_OFFSET     = 50                 # px: shoulder must be this much higher than median
LEG_RATIO_THRESH    = 1.3                # leg gap must exceed median * this to count
ANKLE_ELEV_OFFSET   = 60                 # px: ankle must be this much ABOVE median ankle Y
                                         #     (lower Y value = higher in frame = on bench)
                                         #     60px makes it strict: floor-standing won't trigger
STAND_CONFIRM_FRAMES = 3                 # consecutive frames before standing alert

# --- Fight Detection ---
FIGHT_VELOCITY_THRESH   = 22             # px/frame avg wrist speed
FIGHT_IOU_THRESH        = 0.08           # bbox overlap to be "close"
FIGHT_CONFIRM_FRAMES    = 6              # consecutive frames before fight alert

# --- Recording ---
OUTPUT_CODEC        = "mp4v"
OUTPUT_EXT          = ".mp4"
POST_ANOMALY_BUFFER = 90                 # extra frames to record after anomaly ends

# ─────────────────────────────────────────────
#  YOLOv8 Pose keypoint indices (COCO order)
# ─────────────────────────────────────────────
KP_L_SHOULDER = 5
KP_R_SHOULDER = 6
KP_L_HIP      = 11
KP_R_HIP      = 12
KP_L_ANKLE    = 15
KP_R_ANKLE    = 16
KP_L_WRIST    = 9
KP_R_WRIST    = 10

# Colors (BGR)
COLOR_FIGHT = (0,   0, 255)   # red
COLOR_STAND = (0, 140, 255)   # orange
COLOR_SAFE  = (0, 220,   0)   # green

os.makedirs(RECORD_DIR, exist_ok=True)


# ═════════════════════════════════════════════
#  2. HELPERS
# ═════════════════════════════════════════════

def kp_xy(person, idx):
    """Return (x, y, conf) for keypoint idx."""
    if person is None or idx >= len(person):
        return (0.0, 0.0, 0.0)
    return (float(person[idx][0]), float(person[idx][1]), float(person[idx][2]))


def compute_iou(boxA, boxB):
    """IoU between two [x1,y1,x2,y2] boxes."""
    xA = max(boxA[0], boxB[0]);  yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2]);  yB = min(boxA[3], boxB[3])
    inter = max(0, xB - xA) * max(0, yB - yA)
    if inter == 0:
        return 0.0
    areaA = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    areaB = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    return inter / float(areaA + areaB - inter)


# ═════════════════════════════════════════════
#  3. STANDING DETECTOR
# ═════════════════════════════════════════════

class StandingDetector:
    """
    Baseline-calibrated standing-on-bench detector.

    Phase 1 — Baseline (first BASELINE_FRAMES frames):
        Collects median seated shoulder-Y and hip-to-ankle leg gap.

    Phase 2 — Detection:
        Triggers when BOTH conditions hold for STAND_CONFIRM_FRAMES in a row:
          • shoulder_y  <  median_shoulder - SHOULDER_OFFSET   (shoulders raised)
          • leg_gap     >  median_leg * LEG_RATIO_THRESH       (legs more extended)
    """

    def __init__(self):
        self.baseline_shoulders = []
        self.baseline_legs      = []
        self.baseline_ankles    = []   # absolute ankle Y when seated at floor level
        self.median_shoulder    = None
        self.median_leg         = None
        self.median_ankle       = None
        self.track_counter      = {}    # tid -> consecutive standing frames

    # ── Baseline ─────────────────────────────

    def add_baseline(self, person):
        """Feed one person's keypoints into the baseline pool."""
        lsho = kp_xy(person, KP_L_SHOULDER)
        rsho = kp_xy(person, KP_R_SHOULDER)
        lhip = kp_xy(person, KP_L_HIP)
        rhip = kp_xy(person, KP_R_HIP)
        lank = kp_xy(person, KP_L_ANKLE)
        rank = kp_xy(person, KP_R_ANKLE)

        if max(lsho[2], rsho[2]) < 0.2:
            return

        # Shoulder Y — use best visible side
        if lsho[2] > 0.2 and rsho[2] > 0.2:
            sho_y = (lsho[1] + rsho[1]) / 2
        else:
            sho_y = lsho[1] if lsho[2] > rsho[2] else rsho[1]
        self.baseline_shoulders.append(sho_y)

        # Leg gap (hip Y → ankle Y)
        # Only include in baseline if ankles are in the lower 60% of frame
        # (excludes people already standing on benches during calibration)
        if max(lhip[2], rhip[2]) > 0.2 and max(lank[2], rank[2]) > 0.2:
            hip_y   = (lhip[1] + rhip[1]) / 2
            ankle_y = (lank[1] + rank[1]) / 2
            # Skip if ankles are suspiciously high (top 40% of a 720p frame = y < 288)
            if ankle_y < 288:
                return
            gap = ankle_y - hip_y
            if gap > 20:
                self.baseline_legs.append(gap)
            self.baseline_ankles.append(ankle_y)   # absolute floor-level ankle Y

    def calibrate(self):
        """Compute medians once enough samples exist. Returns True when done."""
        if (len(self.baseline_shoulders) > 20 and
                len(self.baseline_legs) > 20 and
                len(self.baseline_ankles) > 20):
            self.median_shoulder = np.median(self.baseline_shoulders)
            self.median_leg      = np.median(self.baseline_legs)
            self.median_ankle    = np.median(self.baseline_ankles)
            return True
        return False

    @property
    def ready(self):
        return self.median_shoulder is not None and self.median_ankle is not None

    # ── Detection ────────────────────────────

    def detect(self, tid, person):
        """
        Returns True when standing is confirmed for this track ID.
        Returns False until calibrate() has succeeded.
        """
        if not self.ready:
            return False

        lsho = kp_xy(person, KP_L_SHOULDER)
        rsho = kp_xy(person, KP_R_SHOULDER)
        lhip = kp_xy(person, KP_L_HIP)
        rhip = kp_xy(person, KP_R_HIP)
        lank = kp_xy(person, KP_L_ANKLE)
        rank = kp_xy(person, KP_R_ANKLE)

        if max(lsho[2], rsho[2]) < 0.2:
            self.track_counter[tid] = 0
            return False

        # Shoulder Y
        if lsho[2] > 0.2 and rsho[2] > 0.2:
            sho_y = (lsho[1] + rsho[1]) / 2
        else:
            sho_y = lsho[1] if lsho[2] > rsho[2] else rsho[1]

        shoulder_high = sho_y < (self.median_shoulder - SHOULDER_OFFSET)

        # Leg gap + ankle elevation
        leg_extended   = False
        ankle_elevated = False
        if max(lhip[2], rhip[2]) > 0.2 and max(lank[2], rank[2]) > 0.2:
            hip_y   = (lhip[1] + rhip[1]) / 2
            ankle_y = (lank[1] + rank[1]) / 2
            leg_gap = ankle_y - hip_y
            leg_extended   = leg_gap > self.median_leg * LEG_RATIO_THRESH
            # Ankles on a bench are physically higher → smaller Y value in image coords
            ankle_elevated = ankle_y < (self.median_ankle - ANKLE_ELEV_OFFSET)

        # ALL three conditions must hold
        if shoulder_high and leg_extended and ankle_elevated:
            self.track_counter[tid] = self.track_counter.get(tid, 0) + 1
        else:
            self.track_counter[tid] = 0

        return self.track_counter.get(tid, 0) >= STAND_CONFIRM_FRAMES


# ═════════════════════════════════════════════
#  4. FIGHTING DETECTOR
# ═════════════════════════════════════════════

class FightingDetector:
    """
    Wrist-velocity + bbox-proximity fight detector.

    Triggers when BOTH hold for FIGHT_CONFIRM_FRAMES in a row:
      • avg wrist speed  >  FIGHT_VELOCITY_THRESH
      • person's bbox overlaps a neighbour's bbox by > FIGHT_IOU_THRESH
    """

    def __init__(self):
        self.wrist_history = defaultdict(lambda: deque(maxlen=12))
        self.alert_counter = defaultdict(int)

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
        self.wrist_history[track_id].append(((lw[0], lw[1]), (rw[0], rw[1])))

    def detect(self, track_id, my_box, all_boxes, all_track_ids):
        """Returns True if this person is flagged as fighting."""
        high_vel = self._wrist_velocity(track_id) > FIGHT_VELOCITY_THRESH
        near_someone = any(
            other_id != track_id and
            compute_iou(my_box, all_boxes[i]) > FIGHT_IOU_THRESH
            for i, other_id in enumerate(all_track_ids)
        )

        if high_vel and near_someone:
            self.alert_counter[track_id] += 1
        else:
            self.alert_counter[track_id] = max(0, self.alert_counter[track_id] - 1)

        return self.alert_counter[track_id] >= FIGHT_CONFIRM_FRAMES

    def cleanup(self, active_ids):
        stale = [k for k in self.wrist_history if k not in active_ids]
        for k in stale:
            del self.wrist_history[k]
            self.alert_counter.pop(k, None)


# ═════════════════════════════════════════════
#  5. RECORDING MANAGER  (per-anomaly-type)
# ═════════════════════════════════════════════

class RecordingManager:
    """
    Separate compressed clip per anomaly type ("fighting", "standing").
    Each writer has its own pre-roll buffer flush and post-event cooldown.
    """

    def __init__(self, directory, frame_size=(1280, 720), fps=15.0,
                 pre_buffer_sec=3):
        self.directory  = directory
        self.frame_size = frame_size
        self.fps        = fps
        self.pre_len    = int(fps * pre_buffer_sec)

        # Shared rolling pre-buffer (clean / unannotated frames)
        self.pre_buffer = deque(maxlen=self.pre_len)

        # Per-type state
        self._writers  = {}   # anomaly_type -> VideoWriter
        self._cooldown = {}   # anomaly_type -> frames remaining

    def buffer(self, clean_frame):
        """Call every frame with the unannotated frame."""
        self.pre_buffer.append(clean_frame.copy())

    def write(self, annotated_frame, active_types: set):
        """
        Call every processed frame.
        active_types: set of anomaly strings currently firing,
                      e.g. {"fighting"}, {"standing"}, {"fighting","standing"}, set()
        """
        all_managed = set(self._writers) | active_types

        for atype in all_managed:
            if atype in active_types:
                # Open writer if not already open; flush pre-buffer
                if atype not in self._writers:
                    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    path = os.path.join(self.directory,
                                        f"{atype}_{ts}{OUTPUT_EXT}")
                    fourcc = cv2.VideoWriter_fourcc(*OUTPUT_CODEC)
                    w = cv2.VideoWriter(path, fourcc, self.fps, self.frame_size)
                    for f in self.pre_buffer:
                        w.write(f)
                    self._writers[atype] = w
                    print(f"[REC] Started  → {path}")

                self._writers[atype].write(annotated_frame)
                self._cooldown[atype] = POST_ANOMALY_BUFFER

            else:
                # Anomaly stopped — count down cooldown then close
                if atype in self._writers:
                    self._writers[atype].write(annotated_frame)
                    self._cooldown[atype] = self._cooldown.get(atype, 0) - 1
                    if self._cooldown[atype] <= 0:
                        self._writers[atype].release()
                        del self._writers[atype]
                        self._cooldown.pop(atype, None)
                        print(f"[REC] Clip saved for: {atype}")

    @property
    def is_recording(self):
        return bool(self._writers)

    def stop_all(self):
        for w in self._writers.values():
            w.release()
        self._writers.clear()
        print("[REC] All writers closed.")


# ═════════════════════════════════════════════
#  6. DRAWING HELPERS
# ═════════════════════════════════════════════

def draw_person(frame, bbox, is_fighting, is_standing, track_id):
    x1, y1, x2, y2 = map(int, bbox)
    label_y = y1 - 10

    if is_fighting:
        cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR_FIGHT, 3)
        cv2.putText(frame, "!! FIGHTING !!", (x1, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, COLOR_FIGHT, 2)
        label_y -= 22

    if is_standing:
        cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR_STAND, 3)
        cv2.putText(frame, "STANDING ON BENCH", (x1, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, COLOR_STAND, 2)

    if not is_fighting and not is_standing:
        cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR_SAFE, 1)

    cv2.putText(frame, f"ID:{track_id}", (x1 + 4, y2 - 6),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)


def draw_hud(frame, active_anomalies, baseline_done, frame_count, fps, is_rec):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    cv2.putText(frame, f"AI Classroom Monitor  {ts}  FPS:{fps:.1f}",
                (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (220, 220, 220), 1)

    if not baseline_done:
        cv2.putText(frame,
                    f"Calibrating baseline... ({frame_count}/{BASELINE_FRAMES})",
                    (10, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200, 200, 0), 2)
    else:
        y = 58
        if "fighting" in active_anomalies:
            cv2.putText(frame, "!! FIGHTING DETECTED !!",
                        (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_FIGHT, 2)
            y += 28
        if "standing" in active_anomalies:
            cv2.putText(frame, "!! STANDING ON BENCH !!",
                        (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_STAND, 2)

    if is_rec:
        cv2.putText(frame, "● REC", (1160, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)


# ═════════════════════════════════════════════
#  7. MAIN LOOP
# ═════════════════════════════════════════════

def main():
    print("\n[INFO] Loading YOLOv8 pose model ...")
    model = YOLO("yolov8s-pose.pt")
    model.to('cuda')
    print(f"[INFO] Device: {model.device}\n")

    cap = cv2.VideoCapture(VIDEO_SOURCE)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {VIDEO_SOURCE}")

    source_fps  = cap.get(cv2.CAP_PROP_FPS) or 25.0
    display_fps = source_fps / FRAME_SKIP
    frame_w     = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_h     = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[INFO] Source: {frame_w}x{frame_h} @ {source_fps:.1f} fps  "
          f"(processing every {FRAME_SKIP} frames → ~{display_fps:.1f} fps)\n")

    standing_det = StandingDetector()
    fighting_det = FightingDetector()
    recorder     = RecordingManager(
        RECORD_DIR,
        frame_size=(1280, 720),
        fps=display_fps,
        pre_buffer_sec=3
    )

    fps_timer    = datetime.datetime.now()
    fps_display  = 0.0
    fps_frames   = 0
    frame_count  = 0
    baseline_done = False

    print("[INFO] Detection running. Press 'q' to quit.\n")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % FRAME_SKIP != 0:
            continue

        frame   = cv2.resize(frame, (1280, 720))
        display = frame.copy()

        recorder.buffer(frame)   # clean frame into pre-roll buffer

        results = model.track(frame, persist=True, tracker="bytetrack.yaml",
                               verbose=False, conf=0.25, imgsz=960)

        active_anomalies = set()

        if (results[0].keypoints is not None and
                results[0].boxes.id is not None):

            kpts_all   = results[0].keypoints.data.cpu().numpy()
            boxes_all  = results[0].boxes.xyxy.cpu().numpy()
            ids_all    = results[0].boxes.id.int().cpu().tolist()
            active_ids = set(ids_all)

            # ── Baseline collection ──────────────────────────────────
            if frame_count <= BASELINE_FRAMES * FRAME_SKIP:
                for person in kpts_all:
                    standing_det.add_baseline(person)

            # Lock in baseline as soon as enough samples exist
            if not baseline_done:
                baseline_done = standing_det.calibrate()
                if baseline_done:
                    print(f"[INFO] Baseline locked: "
                          f"shoulder_median={standing_det.median_shoulder:.1f}px  "
                          f"leg_median={standing_det.median_leg:.1f}px  "
                          f"ankle_median={standing_det.median_ankle:.1f}px")

            # ── Update fight wrist history ───────────────────────────
            for i, tid in enumerate(ids_all):
                fighting_det.update(tid, kpts_all[i])

            # ── Per-person detection ─────────────────────────────────
            for i, tid in enumerate(ids_all):
                person = kpts_all[i]
                bbox   = boxes_all[i]

                is_fighting = fighting_det.detect(
                    tid, bbox, list(boxes_all), ids_all)
                is_standing = standing_det.detect(tid, person)

                if is_fighting:
                    active_anomalies.add("fighting")
                if is_standing:
                    active_anomalies.add("standing")

                draw_person(display, bbox, is_fighting, is_standing, tid)

            fighting_det.cleanup(active_ids)

        # ── Recording ───────────────────────────────────────────────
        recorder.write(display, active_anomalies)

        # ── HUD & FPS counter ────────────────────────────────────────
        fps_frames += 1
        elapsed = (datetime.datetime.now() - fps_timer).total_seconds()
        if elapsed >= 1.0:
            fps_display = fps_frames / elapsed
            fps_frames  = 0
            fps_timer   = datetime.datetime.now()

        draw_hud(display, active_anomalies, baseline_done,
                 frame_count, fps_display, recorder.is_recording)

        cv2.imshow("AI Classroom Monitor", display)
        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break

    cap.release()
    recorder.stop_all()
    cv2.destroyAllWindows()
    print("\n[INFO] Done.")


if __name__ == "__main__":
    main()