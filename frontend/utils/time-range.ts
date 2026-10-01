function getTimeFromMins(mins: number) {
  const hours = Math.trunc(mins / 60);
  const minutes = mins % 60;
  return (
    String(hours).padStart(2, "0") + ":" + String(minutes).padStart(2, "0")
  );
}

export function isNowInTimeRange(timeRange?: string) {
  if (!timeRange) {
    return {
      isNow: false,
      start: "09:00",
      end: "20:00",
    };
  }

  const newTimeRange = timeRange.replace(/\s+/g, " ").trim();
  console.log('newTimeRange:', newTimeRange);
  const [start = "00:00", end = "00:00"] = newTimeRange.split("-");
  const now = new Date();

  const [startHour, startMinute] = start.split(":").map(Number);
  const [endHour, endMinute] = end.split(":").map(Number);

  const nowHour = now.getHours();
  const nowMinute = now.getMinutes();

  const nowTotal = nowHour * 60 + nowMinute;
  const startTotal = startHour * 60 + startMinute;
  const endTotal = endHour * 60 + endMinute;
  const isNow = nowTotal >= startTotal && nowTotal <= endTotal;

  return {
    isNow,
    start: getTimeFromMins(startTotal),
    end: getTimeFromMins(endTotal),
  };
}
