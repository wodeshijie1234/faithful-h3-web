(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.FaithfulStoryboard = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  function recalculateShotTimes(shots) {
    let start = 0;
    return (Array.isArray(shots) ? shots : []).map((shot, index) => {
      const rawDuration = Number(shot.duration_seconds);
      const duration = Math.round(Math.max(0.5, Math.min(15, Number.isFinite(rawDuration) ? rawDuration : 3)) * 2) / 2;
      const normalized = {...shot, number: index + 1, start_seconds: Math.round(start * 10) / 10, duration_seconds: duration};
      start += duration;
      return normalized;
    });
  }

  function totalDuration(shots) {
    return recalculateShotTimes(shots).reduce((total, shot) => total + shot.duration_seconds, 0);
  }

  return {recalculateShotTimes, totalDuration};
});
