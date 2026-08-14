const test = require("node:test");
const assert = require("node:assert/strict");

const { recalculateShotTimes } = require("../static/storyboard.js");
const { detectPanelBoxesFromPixels } = require("../static/panel-detector.js");

test("edited shot durations recalculate a timeline that always starts at zero", () => {
  const shots = recalculateShotTimes([
    { duration_seconds: 2.2, visual_action: "Opening" },
    { duration_seconds: 3.8, visual_action: "Reveal" },
  ]);

  assert.deepEqual(shots.map(shot => shot.start_seconds), [0, 2]);
  assert.deepEqual(shots.map(shot => shot.duration_seconds), [2, 4]);
  assert.deepEqual(shots.map(shot => shot.number), [1, 2]);
});

test("a clean white gutter splits two comic panels in reading order", () => {
  const width = 100;
  const height = 40;
  const pixels = new Uint8ClampedArray(width * height * 4).fill(255);
  for (let y = 2; y < 38; y += 1) {
    for (let x = 2; x < 47; x += 1) setGray(pixels, width, x, y, 40);
    for (let x = 53; x < 98; x += 1) setGray(pixels, width, x, y, 80);
  }

  const boxes = detectPanelBoxesFromPixels(pixels, width, height);

  assert.equal(boxes.length, 2);
  assert.ok(boxes[0].x < boxes[1].x);
  assert.ok(boxes.every(box => box.width > 0.4 && box.height > 0.8));
});

test("a blank region below a gutter is not treated as a comic panel", () => {
  const width = 80;
  const height = 100;
  const pixels = new Uint8ClampedArray(width * height * 4).fill(255);
  for (let y = 2; y < 46; y += 1) {
    for (let x = 2; x < 78; x += 1) setGray(pixels, width, x, y, 55);
  }

  const boxes = detectPanelBoxesFromPixels(pixels, width, height);

  assert.equal(boxes.length, 1);
  assert.ok(boxes[0].height < 0.6);
});

function setGray(pixels, width, x, y, value) {
  const offset = (y * width + x) * 4;
  pixels[offset] = value;
  pixels[offset + 1] = value;
  pixels[offset + 2] = value;
  pixels[offset + 3] = 255;
}
