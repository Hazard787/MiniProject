const pptxgen = require("C:/Users/abhin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/pptxgenjs");
const path = require("path");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Classroom Vision AI";
pptx.subject = "AI Classroom Anomaly Detection System";
pptx.title = "Classroom Vision AI - Corrected Presentation";
pptx.company = "Student Project";
pptx.lang = "en-US";
pptx.theme = {
  headFontFace: "Segoe UI Semibold",
  bodyFontFace: "Segoe UI",
  lang: "en-US",
};
pptx.defineLayout({ name: "CUSTOM_WIDE", width: 13.333, height: 7.5 });
pptx.layout = "CUSTOM_WIDE";
pptx.margin = 0;

const C = {
  bg: "06131E",
  panel: "0B2233",
  panel2: "0E2A3C",
  cyan: "61D2F5",
  cyan2: "9FE8FF",
  white: "EAF6FC",
  muted: "9FC1D1",
  green: "5CEBA9",
  amber: "FFC65A",
  red: "FF6464",
  blue: "3AA6FF",
};

const SLIDE_W = 13.333;
const SLIDE_H = 7.5;

function addBg(slide, section = "") {
  slide.background = { color: C.bg };
  for (let x = 0; x <= SLIDE_W; x += 0.4) {
    slide.addShape(pptx.ShapeType.line, {
      x, y: 0, w: 0, h: SLIDE_H,
      line: { color: "123346", transparency: 55, width: 0.4 },
    });
  }
  for (let y = 0; y <= SLIDE_H; y += 0.4) {
    slide.addShape(pptx.ShapeType.line, {
      x: 0, y, w: SLIDE_W, h: 0,
      line: { color: "123346", transparency: 60, width: 0.4 },
    });
  }
  slide.addShape(pptx.ShapeType.rect, {
    x: 0.15, y: 0.15, w: 13.03, h: 7.2,
    fill: { color: C.bg, transparency: 100 },
    line: { color: C.cyan, transparency: 35, width: 1 },
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 0.35, y: 0.78, w: 12.6, h: 0,
    line: { color: C.cyan, transparency: 40, width: 1 },
  });
  if (section) {
    slide.addText(section.toUpperCase(), {
      x: 10.55, y: 0.25, w: 2.25, h: 0.25,
      fontFace: "Segoe UI", fontSize: 7.8,
      color: C.muted, bold: true, align: "right",
      margin: 0,
    });
  }
}

function title(slide, t, sub = "", section = "") {
  addBg(slide, section);
  slide.addText(t, {
    x: 0.55, y: 0.28, w: 9.6, h: 0.45,
    fontFace: "Segoe UI Semibold", fontSize: 25,
    color: C.white, bold: true,
    margin: 0,
    fit: "shrink",
  });
  if (sub) {
    slide.addText(sub, {
      x: 0.56, y: 0.83, w: 12, h: 0.28,
      fontFace: "Segoe UI", fontSize: 10.5,
      color: C.muted,
      margin: 0,
      fit: "shrink",
    });
  }
}

function panel(slide, x, y, w, h, opts = {}) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    rectRadius: 0.06,
    fill: { color: opts.fill || C.panel, transparency: opts.transparency ?? 5 },
    line: { color: opts.line || C.cyan, transparency: opts.lineTransparency ?? 25, width: opts.width ?? 0.9 },
  });
}

function addBulletList(slide, items, x, y, w, h, size = 14, color = C.white) {
  const runs = [];
  items.forEach((item, idx) => {
    runs.push({ text: item, options: { bullet: { type: "ul" }, breakLine: idx < items.length - 1 } });
  });
  slide.addText(runs, {
    x, y, w, h, fontFace: "Segoe UI", fontSize: size,
    color, breakLine: false, fit: "shrink",
    margin: 0.05, paraSpaceAfterPt: 8, valign: "top",
  });
}

function callout(slide, label, value, x, y, w, h, color = C.cyan) {
  panel(slide, x, y, w, h, { fill: "071B29", line: color, lineTransparency: 20 });
  slide.addText(label, { x: x + 0.15, y: y + 0.13, w: w - 0.3, h: 0.2, fontSize: 7.5, color: C.muted, margin: 0 });
  slide.addText(value, { x: x + 0.15, y: y + 0.38, w: w - 0.3, h: 0.36, fontSize: 20, color, bold: true, margin: 0, fit: "shrink" });
}

function footer(slide, txt) {
  slide.addText(txt, {
    x: 0.55, y: 7.06, w: 12.25, h: 0.2,
    fontSize: 6.8, color: "7FAABC", margin: 0,
    fit: "shrink",
  });
}

function chip(slide, txt, x, y, w, color = C.cyan) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h: 0.34,
    fill: { color: "0A2638" },
    line: { color, transparency: 15, width: 0.7 },
  });
  slide.addText(txt, { x: x + 0.12, y: y + 0.08, w: w - 0.24, h: 0.12, fontSize: 8, color: C.white, margin: 0, align: "center", fit: "shrink" });
}

function flow(slide, nodes, x, y, w, h) {
  const gap = 0.18;
  const nw = (w - gap * (nodes.length - 1)) / nodes.length;
  nodes.forEach((n, i) => {
    const nx = x + i * (nw + gap);
    panel(slide, nx, y, nw, h, { fill: "0A2132" });
    slide.addText(n[0], { x: nx + 0.12, y: y + 0.14, w: nw - 0.24, h: 0.28, fontSize: 10.5, color: C.cyan2, bold: true, margin: 0, align: "center", fit: "shrink" });
    slide.addText(n[1], { x: nx + 0.12, y: y + 0.54, w: nw - 0.24, h: h - 0.65, fontSize: 8.3, color: C.white, margin: 0.02, align: "center", valign: "mid", fit: "shrink" });
    if (i < nodes.length - 1) {
      slide.addShape(pptx.ShapeType.chevron, {
        x: nx + nw - 0.02, y: y + h / 2 - 0.12, w: 0.22, h: 0.24,
        fill: { color: C.cyan, transparency: 10 },
        line: { color: C.cyan, transparency: 100 },
      });
    }
  });
}

function addBar(slide, x, y, w, h, val, max, color, label, value) {
  const bw = Math.max(0.04, (w * val) / max);
  slide.addShape(pptx.ShapeType.rect, { x, y, w, h, fill: { color: "123246" }, line: { color: "123246", transparency: 100 } });
  slide.addShape(pptx.ShapeType.rect, { x, y, w: bw, h, fill: { color }, line: { color, transparency: 100 } });
  slide.addText(label, { x, y: y - 0.22, w: 2.2, h: 0.18, fontSize: 7.8, color: C.muted, margin: 0 });
  slide.addText(value, { x: x + w + 0.12, y: y - 0.03, w: 1.2, h: 0.16, fontSize: 8.5, color: C.white, margin: 0 });
}

// 1
{
  const s = pptx.addSlide();
  addBg(s, "AI Classroom Safety");
  s.addText("Classroom Vision AI", { x: 0.7, y: 2.0, w: 8.5, h: 0.65, fontSize: 36, bold: true, color: C.white, margin: 0 });
  s.addText("Real-time anomaly detection with intelligent video storage", { x: 0.72, y: 2.75, w: 7.8, h: 0.36, fontSize: 15.5, color: C.cyan2, margin: 0 });
  flow(s, [["Stand", "bench/desk risk"], ["Sleep", "head-down dwell"], ["Fight", "aggressive motion"], ["Store", "1 FPS + event clips"]], 0.75, 4.0, 11.85, 1.2);
}

// 2 Agenda
{
  const s = pptx.addSlide();
  title(s, "Agenda", "Revised according to review comments", "Overview");
  const items = [
    ["01", "Introduction & problem statement"],
    ["02", "Input video stream and extracted features"],
    ["03", "Proposed pipeline and A1-A4 algorithms"],
    ["04", "Dataset/source, detection evidence, results and analysis"],
    ["05", "Impact, limitations, challenges and conclusion"],
  ];
  items.forEach((it, idx) => {
    const y = 1.45 + idx * 0.88;
    slideNum = it[0];
    panel(s, 1.1, y, 11.2, 0.58, { fill: "0A2132", lineTransparency: 45 });
    s.addText(slideNum, { x: 1.35, y: y + 0.14, w: 0.45, h: 0.2, fontSize: 12, bold: true, color: C.cyan, margin: 0 });
    s.addText(it[1], { x: 2.0, y: y + 0.12, w: 9.5, h: 0.22, fontSize: 13.5, color: C.white, margin: 0 });
  });
}

// 3 Introduction
{
  const s = pptx.addSlide();
  title(s, "Introduction", "Why classroom CCTV needs intelligent monitoring", "Context");
  panel(s, 0.75, 1.45, 7.0, 4.55, {});
  s.addText("Traditional CCTV records classroom activity, but incidents are often noticed only after manual review. Classroom Vision AI adds real-time computer vision on top of CCTV feeds to detect unsafe or unusual student behavior and preserve important evidence clips.", {
    x: 1.05, y: 1.86, w: 6.35, h: 1.38, fontSize: 15.5, color: C.white, margin: 0.04, fit: "shrink",
    breakLine: false,
  });
  addBulletList(s, [
    "Detects standing on benches, sleeping/head-down behavior and fighting",
    "Uses YOLO pose keypoints, bounding boxes and object tracking",
    "Reduces storage by logging normal footage at low FPS while saving anomaly clips at high FPS",
  ], 1.1, 3.65, 6.2, 1.65, 12.5);
  panel(s, 8.2, 1.45, 4.4, 4.55, { fill: "071B29" });
  s.addText("Backing", { x: 8.55, y: 1.82, w: 3.5, h: 0.3, fontSize: 18, color: C.cyan2, bold: true, margin: 0 });
  addBulletList(s, [
    "AI video anomaly detection is an active surveillance research area",
    "Event-driven analytics reduce review burden and focus on valuable video",
    "School CCTV adoption is increasing for safety monitoring",
  ], 8.55, 2.4, 3.55, 1.65, 11.2);
  chip(s, "Standing", 8.55, 4.75, 1.1, C.amber);
  chip(s, "Sleeping", 9.82, 4.75, 1.1, C.blue);
  chip(s, "Fighting", 11.08, 4.75, 1.1, C.red);
  footer(s, "Sources: Sensors 2023 video anomaly detection survey; Security Magazine event-driven analytics; Times of India report on CBSE CCTV safety norms.");
}

// 4 Problem statement
{
  const s = pptx.addSlide();
  title(s, "Problem Statement", "Simplified version for presentation clarity", "Problem");
  panel(s, 0.9, 1.55, 11.55, 1.2, { fill: "071B29", line: C.red });
  s.addText("Classroom CCTV records incidents, but it does not automatically understand student behavior.", { x: 1.25, y: 1.88, w: 10.9, h: 0.36, fontSize: 20, color: C.white, bold: true, margin: 0, fit: "shrink" });
  const cols = [
    ["Manual monitoring", "Staff cannot continuously watch every camera with full attention."],
    ["Late response", "Incidents are often reviewed after they happen, not prevented in real time."],
    ["Storage burden", "Full-FPS continuous recording wastes space during normal classroom periods."],
  ];
  cols.forEach((c, i) => {
    const x = 0.9 + i * 3.95;
    panel(s, x, 3.35, 3.55, 1.6, { fill: "0A2132" });
    s.addText(c[0], { x: x + 0.22, y: 3.65, w: 3.1, h: 0.25, fontSize: 15, bold: true, color: C.cyan2, margin: 0, fit: "shrink" });
    s.addText(c[1], { x: x + 0.22, y: 4.08, w: 3.05, h: 0.55, fontSize: 10.7, color: C.white, margin: 0.02, fit: "shrink" });
  });
}

// 5 Input
{
  const s = pptx.addSlide();
  title(s, "Input: Video Frame Stream", "The system treats CCTV as a time-series of frames", "Input");
  flow(s, [
    ["CCTV / RTSP / MP4", "video source"],
    ["Frame sequence", "t = 1, 2, 3..."],
    ["Frame sampling", "FRAME_SKIP controls speed"],
    ["Pose inference", "keypoints per person"],
    ["Tracking IDs", "same person over time"],
  ], 0.65, 1.35, 12.05, 1.25);
  panel(s, 0.85, 3.05, 5.65, 2.55);
  s.addText("Typical input fields", { x: 1.15, y: 3.36, w: 3.8, h: 0.28, fontSize: 17, bold: true, color: C.cyan2, margin: 0 });
  addBulletList(s, ["Source: webcam, CCTV RTSP link or recorded MP4", "Resolution: resized to 1280 x 720 for processing", "FPS: original FPS is used for dwell-time timing", "Output: annotated display + anomaly recordings"], 1.15, 3.9, 5.0, 1.3, 11.1);
  panel(s, 6.9, 3.05, 5.55, 2.55);
  s.addText("Why time-series matters", { x: 7.2, y: 3.36, w: 3.9, h: 0.28, fontSize: 17, bold: true, color: C.cyan2, margin: 0 });
  addBulletList(s, ["Sleeping needs duration over time", "Fighting needs motion between frames", "Storage decisions depend on normal vs anomaly time windows"], 7.2, 3.9, 4.85, 1.0, 11.1);
}

// 6 Features
{
  const s = pptx.addSlide();
  title(s, "Feature Extraction", "Features used by the rule-based anomaly modules", "Features");
  const features = [
    ["Pose keypoints", "Nose, shoulders, hips and wrists from YOLO pose."],
    ["Bounding box", "Person location, height, width and aspect ratio."],
    ["Track ID", "Maintains each student's state across frames."],
    ["Wrist velocity", "Motion speed used for fighting/aggression detection."],
    ["IoU / overlap", "Checks whether two people are close enough to interact."],
    ["Dwell time", "Confirms behavior only after it persists for a threshold."],
  ];
  features.forEach((f, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.85 + col * 6.1;
    const y = 1.35 + row * 1.45;
    panel(s, x, y, 5.5, 1.02, { fill: "0A2132" });
    s.addText(f[0], { x: x + 0.22, y: y + 0.18, w: 2.2, h: 0.22, fontSize: 14.5, bold: true, color: C.cyan2, margin: 0, fit: "shrink" });
    s.addText(f[1], { x: x + 2.3, y: y + 0.15, w: 2.85, h: 0.42, fontSize: 9.8, color: C.white, margin: 0.02, fit: "shrink" });
  });
}

// 7 Pipeline
{
  const s = pptx.addSlide();
  title(s, "Proposed Methodology: Pipeline", "Architecture slide removed; only processing pipeline retained", "Methodology");
  flow(s, [
    ["Input", "CCTV / MP4 feed"],
    ["Preprocess", "resize + frame skip"],
    ["YOLO Pose", "person boxes + 17 keypoints"],
    ["Tracking", "ByteTrack IDs"],
    ["Anomaly Logic", "A1, A2, A3"],
    ["Storage", "A4 smart retention"],
    ["Alert", "overlay + saved clips"],
  ], 0.45, 2.05, 12.45, 1.45);
  panel(s, 1.25, 4.45, 10.85, 1.1, { fill: "071B29" });
  s.addText("Pipeline output: real-time annotated classroom monitor + timestamped evidence clips for detected anomalies.", { x: 1.55, y: 4.82, w: 10.2, h: 0.25, fontSize: 14, color: C.white, align: "center", margin: 0, fit: "shrink" });
}

// 8 Algorithms
{
  const s = pptx.addSlide();
  title(s, "Algorithms Used", "Labeled as A1, A2, A3 and A4", "Algorithms");
  const algs = [
    ["A1", "Standing-on-Bench", "If person center lies in sitting zone and posture height exceeds learned seated baseline, flag unsafe standing."],
    ["A2", "Sleeping / Head Down", "If head-down or slumped posture persists beyond dwell threshold, flag sleeping."],
    ["A3", "Fighting / Aggression", "If wrist velocity is high and another person overlaps/stands close for confirm frames, flag fighting."],
    ["A4", "Smart Video Storage", "Normal video is stored at 1 FPS; anomaly windows are stored as high-FPS clips."],
  ];
  algs.forEach((a, i) => {
    const y = 1.35 + i * 1.12;
    panel(s, 0.85, y, 11.75, 0.8, { fill: "0A2132" });
    s.addText(a[0], { x: 1.1, y: y + 0.22, w: 0.6, h: 0.22, fontSize: 16, bold: true, color: C.cyan, margin: 0 });
    s.addText(a[1], { x: 1.85, y: y + 0.18, w: 2.55, h: 0.22, fontSize: 13.2, bold: true, color: C.cyan2, margin: 0, fit: "shrink" });
    s.addText(a[2], { x: 4.55, y: y + 0.13, w: 7.6, h: 0.32, fontSize: 9.8, color: C.white, margin: 0.02, fit: "shrink" });
  });
}

// 9 Data source
{
  const s = pptx.addSlide();
  title(s, "Dataset & Data Source", "Where the input/testing data comes from", "Data");
  panel(s, 0.85, 1.35, 5.75, 4.55);
  s.addText("Project test videos", { x: 1.15, y: 1.68, w: 3.8, h: 0.28, fontSize: 17, bold: true, color: C.cyan2, margin: 0 });
  addBulletList(s, ["did.mp4: standing-on-bench scenario", "sleep.mp4: sleeping/head-down scenario", "nat.mp4: fighting/aggression scenario", "These are used for demonstration and system validation."], 1.15, 2.12, 5.0, 1.5, 11.2);
  panel(s, 6.9, 1.35, 5.55, 4.55);
  s.addText("Model / public reference", { x: 7.2, y: 1.68, w: 4.5, h: 0.28, fontSize: 17, bold: true, color: C.cyan2, margin: 0 });
  addBulletList(s, ["YOLOv8s-pose is an official Ultralytics pose model.", "Pose model provides 17 human keypoints.", "UCF-Crime is a public surveillance anomaly dataset with real-world anomaly classes including fighting/assault-like events.", "For deployment, college CCTV samples should be collected with permission for local calibration."], 7.2, 2.12, 4.75, 1.9, 10.6);
  footer(s, "Sources: Ultralytics YOLOv8 / pose docs; UCF CRCV Real-world Anomaly Detection in Surveillance Videos dataset page.");
}

// 10 Detection has happened
{
  const s = pptx.addSlide();
  title(s, "Detection Evidence", "How the system shows that detection has happened", "Evidence");
  const ev = [
    ["Visual overlay", "Bounding boxes change color and labels show STANDING, SLEEPING or FIGHTING."],
    ["HUD alert", "A live alert appears at the top of the monitor with anomaly type and duration."],
    ["Recording trigger", "The system starts a timestamped clip in anomaly_recordings/."],
    ["Console log", "Recording start/stop messages confirm event capture."],
  ];
  ev.forEach((e, i) => {
    const x = 0.9 + (i % 2) * 6.05;
    const y = 1.55 + Math.floor(i / 2) * 1.8;
    panel(s, x, y, 5.5, 1.25, { fill: "0A2132" });
    s.addText(e[0], { x: x + 0.25, y: y + 0.25, w: 2.3, h: 0.25, fontSize: 15, bold: true, color: C.cyan2, margin: 0 });
    s.addText(e[1], { x: x + 0.25, y: y + 0.67, w: 4.95, h: 0.33, fontSize: 10.2, color: C.white, margin: 0.02, fit: "shrink" });
  });
  panel(s, 1.25, 5.45, 10.85, 0.75, { fill: "071B29", line: C.green });
  s.addText("This replaces vague “prediction happened” proof with visible detection, alert and saved-clip evidence.", { x: 1.55, y: 5.72, w: 10.15, h: 0.2, fontSize: 12.8, color: C.white, align: "center", margin: 0, fit: "shrink" });
}

// 11 Storage method
{
  const s = pptx.addSlide();
  title(s, "Smart Video Storage Method", "Lossy normal footage, high-detail anomaly evidence", "Storage");
  flow(s, [
    ["Normal period", "save 1 FPS summary"],
    ["Anomaly detected", "trigger event recording"],
    ["Event window", "save full-FPS clip"],
    ["After event", "return to low-FPS log"],
  ], 0.9, 1.55, 11.5, 1.3);
  panel(s, 0.95, 3.75, 5.55, 1.55, { fill: "0A2132" });
  s.addText("Why this is acceptable", { x: 1.25, y: 4.05, w: 3.8, h: 0.25, fontSize: 16, bold: true, color: C.cyan2, margin: 0 });
  s.addText("The method is lossy for normal footage, but not blindly lossy. Low-risk periods are summarized, while high-risk anomaly windows are preserved in detail.", { x: 1.25, y: 4.48, w: 4.85, h: 0.45, fontSize: 10.6, color: C.white, margin: 0.02, fit: "shrink" });
  panel(s, 6.85, 3.75, 5.55, 1.55, { fill: "0A2132" });
  s.addText("Practical safeguard", { x: 7.15, y: 4.05, w: 3.8, h: 0.25, fontSize: 16, bold: true, color: C.cyan2, margin: 0 });
  s.addText("For strict evidence needs, keep a short full-FPS rolling buffer, then retain long-term 1 FPS logs plus anomaly clips.", { x: 7.15, y: 4.48, w: 4.75, h: 0.45, fontSize: 10.6, color: C.white, margin: 0.02, fit: "shrink" });
}

// 12 Results
{
  const s = pptx.addSlide();
  title(s, "Results & Cost Impact", "1 FPS smart storage test on a 17-minute classroom clip", "Results");
  callout(s, "Original clip", "512 MB", 0.55, 1.2, 2.6, 0.9, C.amber);
  callout(s, "1 FPS output", "13 MB", 3.45, 1.2, 2.6, 0.9, C.green);
  callout(s, "Storage saved", "97.5%", 6.35, 1.2, 2.6, 0.9, C.cyan);
  callout(s, "Reduction ratio", "39.4x", 9.25, 1.2, 2.95, 0.9, C.cyan);
  panel(s, 0.75, 2.65, 5.65, 2.9);
  s.addText("Storage Reduction", { x: 1.0, y: 2.95, w: 3.0, h: 0.25, fontSize: 16, bold: true, color: C.cyan2, margin: 0 });
  addBar(s, 1.15, 3.75, 3.4, 0.28, 512, 512, C.amber, "Original", "512 MB");
  addBar(s, 1.15, 4.55, 3.4, 0.28, 13, 512, C.green, "1 FPS", "13 MB");
  s.addText("512 MB -> 13 MB", { x: 1.15, y: 5.06, w: 4.5, h: 0.2, fontSize: 12.5, color: C.white, margin: 0 });
  panel(s, 6.9, 2.65, 5.65, 2.9);
  s.addText("Projected 30-Day Storage", { x: 7.15, y: 2.95, w: 3.5, h: 0.25, fontSize: 16, bold: true, color: C.cyan2, margin: 0 });
  addBar(s, 7.3, 3.75, 3.3, 0.28, 1.24, 1.24, C.amber, "Full FPS", "1.24 TB");
  addBar(s, 7.3, 4.55, 3.3, 0.28, 0.0323, 1.24, C.green, "1 FPS", "32.3 GB");
  s.addText("Estimated for one camera using the measured 17-min sample rate.", { x: 7.3, y: 5.06, w: 4.55, h: 0.2, fontSize: 8.5, color: C.muted, margin: 0 });
  footer(s, "Measured result: 17-minute clip, 512 MB original, 13 MB after 1 FPS storage.");
}

// 13 Analysis
{
  const s = pptx.addSlide();
  title(s, "Analysis of Results", "What the numbers mean", "Analysis");
  panel(s, 0.85, 1.35, 3.65, 3.8, { fill: "0A2132" });
  s.addText("Storage finding", { x: 1.15, y: 1.7, w: 2.5, h: 0.25, fontSize: 16, bold: true, color: C.cyan2, margin: 0 });
  s.addText("The 1 FPS method reduced normal footage by 97.5%, proving that long idle classroom periods can be stored much more efficiently.", { x: 1.15, y: 2.2, w: 3.0, h: 1.15, fontSize: 12.2, color: C.white, margin: 0.02, fit: "shrink" });
  panel(s, 4.85, 1.35, 3.65, 3.8, { fill: "0A2132" });
  s.addText("Evidence trade-off", { x: 5.15, y: 1.7, w: 2.6, h: 0.25, fontSize: 16, bold: true, color: C.cyan2, margin: 0 });
  s.addText("Normal footage is lossy, so fast motion may be missed in the summary. This is why anomaly windows must be stored as high-FPS clips.", { x: 5.15, y: 2.2, w: 3.0, h: 1.15, fontSize: 12.2, color: C.white, margin: 0.02, fit: "shrink" });
  panel(s, 8.85, 1.35, 3.65, 3.8, { fill: "0A2132" });
  s.addText("Deployment meaning", { x: 9.15, y: 1.7, w: 2.8, h: 0.25, fontSize: 16, bold: true, color: C.cyan2, margin: 0 });
  s.addText("The method is practical for long-term retention if paired with detection, pre-buffer/post-buffer recording, and optional short-term full-FPS backup.", { x: 9.15, y: 2.2, w: 3.0, h: 1.15, fontSize: 12.2, color: C.white, margin: 0.02, fit: "shrink" });
  panel(s, 1.45, 5.65, 10.4, 0.7, { fill: "071B29", line: C.green });
  s.addText("Conclusion: the project optimizes storage without treating the low-FPS log as the only source of evidence.", { x: 1.75, y: 5.91, w: 9.8, h: 0.16, fontSize: 12.3, color: C.white, align: "center", margin: 0, fit: "shrink" });
}

// 14 Loss/impact
{
  const s = pptx.addSlide();
  title(s, "Loss & Infrastructure Impact", "Why the system matters beyond detection", "Impact");
  const impacts = [
    ["Incident loss", "Undetected fights or falls can cause injury and delayed intervention."],
    ["Operational loss", "Manual CCTV review consumes staff time and still misses short events."],
    ["Storage cost", "Full-FPS recording for every classroom increases disk/NVR/cloud cost."],
    ["System failure risk", "Missed detection can reduce evidence quality, so rolling buffer and human escalation are needed."],
  ];
  impacts.forEach((im, i) => {
    const x = 0.85 + (i % 2) * 6.05;
    const y = 1.45 + Math.floor(i / 2) * 1.7;
    panel(s, x, y, 5.55, 1.15, { fill: "0A2132", line: i === 3 ? C.amber : C.cyan });
    s.addText(im[0], { x: x + 0.25, y: y + 0.25, w: 2.5, h: 0.22, fontSize: 14.8, bold: true, color: C.cyan2, margin: 0 });
    s.addText(im[1], { x: x + 0.25, y: y + 0.65, w: 4.95, h: 0.32, fontSize: 10, color: C.white, margin: 0.02, fit: "shrink" });
  });
}

// 15 Benefits/SDG
{
  const s = pptx.addSlide();
  title(s, "Benefits & SDG Mapping", "Project value and alignment", "Value");
  panel(s, 0.85, 1.4, 5.7, 4.4);
  s.addText("Benefits", { x: 1.15, y: 1.75, w: 2.8, h: 0.28, fontSize: 18, bold: true, color: C.cyan2, margin: 0 });
  addBulletList(s, ["Real-time alerts for classroom safety", "Faster review through anomaly clips", "Lower long-term storage requirement", "Privacy-aware retention by reducing detailed normal footage"], 1.15, 2.28, 4.9, 1.55, 11.8);
  panel(s, 6.95, 1.4, 5.5, 4.4);
  s.addText("Primary SDG", { x: 7.25, y: 1.75, w: 2.8, h: 0.28, fontSize: 18, bold: true, color: C.cyan2, margin: 0 });
  s.addText("Goal 4: Quality Education", { x: 7.25, y: 2.35, w: 4.6, h: 0.34, fontSize: 19, bold: true, color: C.white, margin: 0, fit: "shrink" });
  s.addText("The system supports safer and more disciplined classrooms, improving the learning environment.", { x: 7.25, y: 3.0, w: 4.5, h: 0.52, fontSize: 12, color: C.white, margin: 0.02, fit: "shrink" });
  chip(s, "SDG 3: Well-being", 7.25, 4.35, 1.75, C.green);
  chip(s, "SDG 9: Innovation", 9.25, 4.35, 1.75, C.cyan);
}

// 16 Limitations
{
  const s = pptx.addSlide();
  title(s, "Limitations & Safeguards", "Practical deployment considerations", "Risk");
  const rows = [
    ["AI misses", "No model is 100% accurate; use confidence thresholds and human review."],
    ["Camera angle", "Pose accuracy depends on lighting, occlusion and view position."],
    ["Lossy storage", "1 FPS normal log may miss fast motion; preserve full-FPS anomaly clips."],
    ["Privacy", "Use approved camera placement, access control and retention policy."],
  ];
  rows.forEach((r, idx) => {
    const y = 1.35 + idx * 1.12;
    panel(s, 0.95, y, 11.45, 0.8, { fill: "0A2132" });
    s.addText(r[0], { x: 1.25, y: y + 0.2, w: 2.0, h: 0.22, fontSize: 14.5, bold: true, color: C.amber, margin: 0 });
    s.addText(r[1], { x: 3.3, y: y + 0.18, w: 8.4, h: 0.25, fontSize: 11.3, color: C.white, margin: 0, fit: "shrink" });
  });
}

// 17 Challenges end
{
  const s = pptx.addSlide();
  title(s, "Challenges & Future Improvements", "Moved near the end as requested", "Challenges");
  const ch = [
    ["False positives", "Tune thresholds using more local classroom samples."],
    ["More anomalies", "Add fall, running, crowding and restricted-zone entry detection."],
    ["Dataset expansion", "Collect permission-based campus CCTV samples for validation."],
    ["Deployment", "Integrate with NVR/RTSP camera feeds and role-based dashboard access."],
  ];
  ch.forEach((c, i) => {
    const x = 0.85 + (i % 2) * 6.05;
    const y = 1.45 + Math.floor(i / 2) * 1.75;
    panel(s, x, y, 5.55, 1.2, { fill: "0A2132" });
    s.addText(c[0], { x: x + 0.25, y: y + 0.25, w: 2.5, h: 0.22, fontSize: 14.8, bold: true, color: C.cyan2, margin: 0 });
    s.addText(c[1], { x: x + 0.25, y: y + 0.65, w: 4.9, h: 0.32, fontSize: 10.2, color: C.white, margin: 0.02, fit: "shrink" });
  });
}

// 18 Conclusion
{
  const s = pptx.addSlide();
  title(s, "Conclusion", "Classroom Vision AI combines safety detection with storage efficiency", "Close");
  panel(s, 1.05, 1.55, 11.25, 3.7, { fill: "071B29", line: C.green });
  s.addText("The proposed system detects three classroom anomalies in real time, records evidence clips, and reduces normal footage storage using a 1 FPS retention method.", {
    x: 1.55, y: 2.05, w: 10.25, h: 0.75, fontSize: 20, color: C.white, bold: true, align: "center", margin: 0.03, fit: "shrink",
  });
  s.addText("Measured storage result: 512 MB -> 13 MB for a 17-minute clip, achieving 97.5% storage saving.", {
    x: 1.75, y: 3.25, w: 9.85, h: 0.36, fontSize: 16, color: C.cyan2, align: "center", margin: 0, fit: "shrink",
  });
  s.addText("Final takeaway: practical when used as a hybrid system with low-FPS normal logs, high-FPS anomaly clips and human review.", {
    x: 1.75, y: 4.08, w: 9.85, h: 0.34, fontSize: 13.5, color: C.white, align: "center", margin: 0, fit: "shrink",
  });
}

pptx.writeFile({ fileName: path.resolve("Classroom_Vision_AI_fixed.pptx") });
