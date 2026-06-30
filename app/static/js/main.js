const COLORS = [
  { bg: "rgba(217,164,65,0.18)", fg: "#D9A441" },
  { bg: "rgba(95,179,217,0.18)", fg: "#5FB3D9" },
  { bg: "rgba(63,174,122,0.18)", fg: "#3FAE7A" },
];

function initials(name) {
  return name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase();
}

function colorFor(key) {
  let hash = 0;
  for (let i = 0; i < key.length; i++) hash = (hash + key.charCodeAt(i)) % COLORS.length;
  return COLORS[hash];
}

function renderWinnerRow(w) {
  const c = colorFor(w.game || "?");
  const row = document.createElement("div");
  row.className = "winner-row";
  row.innerHTML = `
    <div class="winner-icon" style="background:${c.bg}; color:${c.fg};">${initials(w.game || "?")}</div>
    <div class="winner-info">
      <div class="winner-id">${w.masked_id}</div>
      <div class="winner-amt">+KSH ${Number(w.amount).toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
    </div>
    <div class="winner-game">${w.game}</div>
  `;
  return row;
}

let lastSeenIds = new Set();

async function refreshWinners() {
  const list = document.getElementById("winnerList");
  if (!list) return;

  try {
    const res = await fetch("/api/winners");
    if (!res.ok) throw new Error("bad response");
    const data = await res.json();

    if (!data.length) {
      list.innerHTML = '<div class="empty-note">No winners yet today.</div>';
      return;
    }

    list.innerHTML = "";
    data.forEach((w) => list.appendChild(renderWinnerRow(w)));
  } catch (err) {
    if (!list.children.length) {
      list.innerHTML = '<div class="empty-note">Could not load winners right now.</div>';
    }
  }
}

if (document.getElementById("winnerList")) {
  refreshWinners();
  setInterval(refreshWinners, 8000);
}
