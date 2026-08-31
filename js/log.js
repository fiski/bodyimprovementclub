/* The box is a fixed 791x525 with one brush border export, so the table is
   always exactly ROW_COUNT rows: a shorter feed pads, a longer one truncates. */
const ROW_COUNT = 10;
const COLUMNS = ["member", "activity", "date", "stat"];
const EMPTY = { member: "", activity: "", date: "", stat: "" };

async function loadActivities() {
  return ACTIVITIES;
}

function pad(rows, n) {
  const out = rows.slice(0, n);
  while (out.length < n) out.push(EMPTY);
  return out;
}

function render(rows, tbody) {
  tbody.replaceChildren(...rows.map((row) => {
    const tr = document.createElement("tr");
    for (const column of COLUMNS) {
      const td = document.createElement("td");
      td.textContent = row[column];
      tr.append(td);
    }
    return tr;
  }));
}

async function main() {
  const tbody = document.querySelector(".log tbody");
  render(pad(await loadActivities(), ROW_COUNT), tbody);
}

main();
