(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.FaithfulPanelDetector = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  function detectPanelBoxesFromPixels(pixels, width, height) {
    if (!pixels || width < 8 || height < 8 || pixels.length < width * height * 4) return [];
    const minimumWidth = Math.max(8, Math.round(width * 0.12));
    const minimumHeight = Math.max(8, Math.round(height * 0.12));
    const boxes = [];

    let minX = width, minY = height, maxX = -1, maxY = -1;
    for (let y = 0; y < height; y += 1) {
      for (let x = 0; x < width; x += 1) {
        const offset = (y * width + x) * 4;
        const brightness = (pixels[offset] + pixels[offset + 1] + pixels[offset + 2]) / 3;
        if (pixels[offset + 3] >= 24 && brightness < 238) {
          minX = Math.min(minX, x); minY = Math.min(minY, y);
          maxX = Math.max(maxX, x); maxY = Math.max(maxY, y);
        }
      }
    }
    if (maxX < minX || maxY < minY) return [];
    const contentRegion = {
      x: Math.max(0, minX - 1), y: Math.max(0, minY - 1),
      width: Math.min(width, maxX + 2) - Math.max(0, minX - 1),
      height: Math.min(height, maxY + 2) - Math.max(0, minY - 1),
    };

    function whiteRatio(region, axis, coordinate) {
      let white = 0;
      let count = 0;
      if (axis === "x") {
        const step = Math.max(1, Math.floor(region.height / 180));
        for (let y = region.y; y < region.y + region.height; y += step) {
          const offset = (y * width + coordinate) * 4;
          const brightness = (pixels[offset] + pixels[offset + 1] + pixels[offset + 2]) / 3;
          if (pixels[offset + 3] < 24 || brightness >= 238) white += 1;
          count += 1;
        }
      } else {
        const step = Math.max(1, Math.floor(region.width / 180));
        for (let x = region.x; x < region.x + region.width; x += step) {
          const offset = (coordinate * width + x) * 4;
          const brightness = (pixels[offset] + pixels[offset + 1] + pixels[offset + 2]) / 3;
          if (pixels[offset + 3] < 24 || brightness >= 238) white += 1;
          count += 1;
        }
      }
      return count ? white / count : 0;
    }

    function strongestGutter(region, axis) {
      const origin = axis === "x" ? region.x : region.y;
      const length = axis === "x" ? region.width : region.height;
      const edgeGuard = Math.max(2, Math.floor(length * 0.06));
      const runs = [];
      let runStart = null;
      for (let value = origin + edgeGuard; value < origin + length - edgeGuard; value += 1) {
        const white = whiteRatio(region, axis, value) >= 0.94;
        if (white && runStart === null) runStart = value;
        if ((!white || value === origin + length - edgeGuard - 1) && runStart !== null) {
          const runEnd = white ? value + 1 : value;
          if (runEnd - runStart >= 2) runs.push({start: runStart, end: runEnd});
          runStart = null;
        }
      }
      return runs.sort((a, b) => (b.end - b.start) - (a.end - a.start))[0] || null;
    }

    function split(region, depth) {
      if (depth >= 7 || boxes.length >= 40) return boxes.push(region);
      const vertical = region.width >= minimumWidth * 2 ? strongestGutter(region, "x") : null;
      const horizontal = region.height >= minimumHeight * 2 ? strongestGutter(region, "y") : null;
      const verticalScore = vertical ? (vertical.end - vertical.start) / region.width : 0;
      const horizontalScore = horizontal ? (horizontal.end - horizontal.start) / region.height : 0;
      if (!vertical && !horizontal) return boxes.push(region);
      if (verticalScore >= horizontalScore) {
        const left = {...region, width: vertical.start - region.x};
        const right = {...region, x: vertical.end, width: region.x + region.width - vertical.end};
        if (left.width < minimumWidth || right.width < minimumWidth) return boxes.push(region);
        split(left, depth + 1); split(right, depth + 1);
      } else {
        const top = {...region, height: horizontal.start - region.y};
        const bottom = {...region, y: horizontal.end, height: region.y + region.height - horizontal.end};
        if (top.height < minimumHeight || bottom.height < minimumHeight) return boxes.push(region);
        split(top, depth + 1); split(bottom, depth + 1);
      }
    }

    split(contentRegion, 0);
    return boxes
      .filter(box => box.width >= minimumWidth && box.height >= minimumHeight)
      .sort((a, b) => Math.abs(a.y - b.y) > height * 0.08 ? a.y - b.y : a.x - b.x)
      .map(box => ({
        x: round(box.x / width), y: round(box.y / height),
        width: round(box.width / width), height: round(box.height / height),
      }));
  }

  function round(value) { return Math.round(value * 10000) / 10000; }

  async function detectPanelBoxes(image) {
    const scale = Math.min(1, 1200 / Math.max(image.naturalWidth, image.naturalHeight));
    const width = Math.max(8, Math.round(image.naturalWidth * scale));
    const height = Math.max(8, Math.round(image.naturalHeight * scale));
    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    const context = canvas.getContext("2d", {willReadFrequently: true});
    context.drawImage(image, 0, 0, width, height);
    return detectPanelBoxesFromPixels(context.getImageData(0, 0, width, height).data, width, height);
  }

  return {detectPanelBoxesFromPixels, detectPanelBoxes};
});
