import cv2
import numpy as np
from ultralytics import YOLO

# ----------------------------------
# CONFIG
# ----------------------------------
VIDEO_SOURCE = "new.mp4"

BASELINE_FRAMES = 150

SHOULDER_OFFSET = 50
LEG_RATIO_THRESH = 1.3

CONFIRM_FRAMES = 3

KP_L_SHOULDER = 5
KP_R_SHOULDER = 6
KP_L_HIP = 11
KP_R_HIP = 12
KP_L_ANKLE = 15
KP_R_ANKLE = 16


def kp_xy(person, idx):
    return (
        float(person[idx][0]),
        float(person[idx][1]),
        float(person[idx][2])
    )


model = YOLO("yolov8s-pose.pt")

cap = cv2.VideoCapture(VIDEO_SOURCE)

frame_count = 0

baseline_shoulders = []
baseline_legs = []

track_counter = {}

while cap.isOpened():

    ret, frame = cap.read()

    if not ret:
        break

    frame_count += 1

    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        verbose=False,
        conf=0.25
    )

    if (
        results[0].keypoints is not None
        and results[0].boxes.id is not None
    ):

        kpts_all = results[0].keypoints.data.cpu().numpy()
        boxes_all = results[0].boxes.xyxy.cpu().numpy()
        ids_all = results[0].boxes.id.int().cpu().tolist()

        # ----------------------------------
        # BUILD BASELINE
        # ----------------------------------
        if frame_count <= BASELINE_FRAMES:

            for person in kpts_all:

                lsho = kp_xy(person, KP_L_SHOULDER)
                rsho = kp_xy(person, KP_R_SHOULDER)

                lhip = kp_xy(person, KP_L_HIP)
                rhip = kp_xy(person, KP_R_HIP)

                lank = kp_xy(person, KP_L_ANKLE)
                rank = kp_xy(person, KP_R_ANKLE)

                if max(lsho[2], rsho[2]) < 0.2:
                    continue

                shoulder_y = (
                    (lsho[1] + rsho[1]) / 2
                    if lsho[2] > 0.2 and rsho[2] > 0.2
                    else (
                        lsho[1]
                        if lsho[2] > rsho[2]
                        else rsho[1]
                    )
                )

                baseline_shoulders.append(
                    shoulder_y
                )

                if (
                    max(lhip[2], rhip[2]) > 0.2
                    and
                    max(lank[2], rank[2]) > 0.2
                ):

                    hip_y = (
                        (lhip[1] + rhip[1]) / 2
                    )

                    ankle_y = (
                        (lank[1] + rank[1]) / 2
                    )

                    leg_gap = ankle_y - hip_y

                    if leg_gap > 20:
                        baseline_legs.append(
                            leg_gap
                        )

        # ----------------------------------
        # DETECTION
        # ----------------------------------
        if (
            len(baseline_shoulders) > 20
            and
            len(baseline_legs) > 20
        ):

            median_shoulder = np.median(
                baseline_shoulders
            )

            median_leg = np.median(
                baseline_legs
            )

            for i, tid in enumerate(ids_all):

                person = kpts_all[i]
                box = boxes_all[i]

                lsho = kp_xy(person, KP_L_SHOULDER)
                rsho = kp_xy(person, KP_R_SHOULDER)

                lhip = kp_xy(person, KP_L_HIP)
                rhip = kp_xy(person, KP_R_HIP)

                lank = kp_xy(person, KP_L_ANKLE)
                rank = kp_xy(person, KP_R_ANKLE)

                if max(lsho[2], rsho[2]) < 0.2:
                    continue

                shoulder_y = (
                    (lsho[1] + rsho[1]) / 2
                    if lsho[2] > 0.2 and rsho[2] > 0.2
                    else (
                        lsho[1]
                        if lsho[2] > rsho[2]
                        else rsho[1]
                    )
                )

                shoulder_high = (
                    shoulder_y <
                    median_shoulder - SHOULDER_OFFSET
                )

                leg_extended = False

                if (
                    max(lhip[2], rhip[2]) > 0.2
                    and
                    max(lank[2], rank[2]) > 0.2
                ):

                    hip_y = (
                        lhip[1] + rhip[1]
                    ) / 2

                    ankle_y = (
                        lank[1] + rank[1]
                    ) / 2

                    leg_gap = ankle_y - hip_y

                    leg_extended = (
                        leg_gap >
                        median_leg * LEG_RATIO_THRESH
                    )

                standing = (
                    shoulder_high
                    and
                    leg_extended
                )

                if standing:
                    track_counter[tid] = (
                        track_counter.get(tid, 0) + 1
                    )
                else:
                    track_counter[tid] = 0

                x1, y1, x2, y2 = map(
                    int,
                    box
                )

                if (
                    track_counter[tid]
                    >= CONFIRM_FRAMES
                ):

                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 0, 255),
                        3
                    )

                    cv2.putText(
                        frame,
                        "STANDING ON BENCH",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 0, 255),
                        2
                    )

                else:

                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 0),
                        2
                    )

        cv2.putText(
            frame,
            f"Baseline Frames: {frame_count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

    cv2.imshow(
        "Standing On Bench Detector",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()