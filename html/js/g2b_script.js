const dates = Array.from({ length: 12 }, (_, i) => `${i + 1}월`);

// 16 distinct colors for 16 rate bands (99.5% ~ 101.0%)
const g2bColors = [
  { bg: "#e6194b", border: "rgba(230,25,75,1)" },   // red
  { bg: "#3cb44b", border: "rgba(60,180,75,1)" },    // green
  { bg: "#ffe119", border: "rgba(255,225,25,1)" },   // yellow
  { bg: "#4363d8", border: "rgba(67,99,216,1)" },    // blue
  { bg: "#f58231", border: "rgba(245,130,49,1)" },   // orange
  { bg: "#911eb4", border: "rgba(145,30,180,1)" },   // purple
  { bg: "#42d4f4", border: "rgba(66,212,244,1)" },   // cyan
  { bg: "#f032e6", border: "rgba(240,50,230,1)" },   // magenta
  { bg: "#bfef45", border: "rgba(191,239,69,1)" },   // lime
  { bg: "#fabed4", border: "rgba(250,190,212,1)" },  // pink
  { bg: "#469990", border: "rgba(70,153,144,1)" },   // teal
  { bg: "#dcbeff", border: "rgba(220,190,255,1)" },  // lavender
  { bg: "#9A6324", border: "rgba(154,99,36,1)" },    // brown
  { bg: "#fffac8", border: "rgba(255,250,200,1)" },  // beige
  { bg: "#ffffff", border: "rgba(255,255,255,1)" },  // white
  { bg: "#000000", border: "rgba(0,0,0,1)" },        // black
];

const rateBands = Array.from({ length: 16 }, (_, i) => `${(99.5 + 0.1 * i).toFixed(1)}%`);

let allCharts = [];

function createG2bChart(canvasId, dataArrays, year, title, maxY) {
  const yDatasets = dataArrays.map((data, index) => ({
    label: rateBands[index],
    fill: false,
    lineTension: 0,
    backgroundColor: g2bColors[index].bg,
    borderColor: g2bColors[index].border,
    borderWidth: 2,
    data: data
  }));

  const config = {
    type: "line",
    data: {
      labels: dates,
      datasets: yDatasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      title: {
        display: true,
        text: `${year}년 나라장터 ${title}`,
        fontSize: 17,
        fontColor: "white",
      },
      legend: {
        labels: { fontColor: "white", fontSize: 10 },
        position: "top",
        display: true,
      },
      scales: {
        xAxes: [{ ticks: { fontColor: "white" } }],
        yAxes: [{ ticks: { min: 0, max: maxY, fontColor: "white" } }],
      },
      elements: {
        point: { radius: 2 }
      }
    },
  };

  const ctx = document.getElementById(canvasId).getContext("2d");
  const chart = new Chart(ctx, config);
  allCharts.push(chart);
}

function createG2bRateTable(containerId, percentages, counts, year) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";

  const caption = document.createElement("caption");
  caption.textContent = `${year}년 비율 집계표`;
  container.appendChild(caption);

  const table = document.createElement("table");

  // Header row: empty + 16 rate bands
  const headerRow = table.insertRow();
  const headers = [""].concat(rateBands);
  headers.forEach(h => {
    const th = document.createElement("th");
    th.textContent = h;
    headerRow.appendChild(th);
  });

  // 12 rows (one per month)
  for (let m = 0; m < 12; m++) {
    const row = table.insertRow();
    const monthCell = row.insertCell();
    monthCell.textContent = `${m + 1}월`;

    for (let b = 0; b < 16; b++) {
      const cell = row.insertCell();
      cell.textContent = percentages[b][m];
    }
  }

  // Totals row
  const totalRow = table.insertRow();
  const totalLabel = totalRow.insertCell();
  totalLabel.textContent = "총합";
  totalLabel.style.fontWeight = "bold";

  for (let b = 0; b < 16; b++) {
    const cell = totalRow.insertCell();
    const total = counts[b].reduce((a, c) => a + c, 0);
    cell.textContent = total;
    cell.style.fontWeight = "bold";
  }

  container.appendChild(table);
}

function createG2bAmtTable(containerId, counts, year) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";

  const caption = document.createElement("caption");
  caption.textContent = `${year}년 수량 집계표`;
  container.appendChild(caption);

  const table = document.createElement("table");

  // Header
  const headerRow = table.insertRow();
  ["", "수량", "비율"].forEach(h => {
    const th = document.createElement("th");
    th.textContent = h;
    headerRow.appendChild(th);
  });

  // Sum per band
  const bandTotals = counts.map(band => band.reduce((a, c) => a + c, 0));
  const grandTotal = bandTotals.reduce((a, c) => a + c, 0);

  for (let b = 0; b < 16; b++) {
    const row = table.insertRow();
    [rateBands[b], bandTotals[b], grandTotal > 0 ? (bandTotals[b] / grandTotal * 100).toFixed(2) + "%" : "0%"].forEach(v => {
      const cell = row.insertCell();
      cell.textContent = v;
    });
  }

  // Total row
  const totalRow = table.insertRow();
  ["총합", grandTotal, "100%"].forEach(v => {
    const cell = totalRow.insertCell();
    cell.textContent = v;
    cell.style.fontWeight = "bold";
  });

  container.appendChild(table);
}

// Build sections dynamically
async function init() {
  try {
    const response = await fetch("data/g2bRateData.json");
    const data = await response.json();

    const years = Object.keys(data).sort().reverse();
    const sectionsDiv = document.getElementById("sections");

    years.forEach((year, idx) => {
      const yearData = data[year];

      const item = document.createElement("div");
      item.className = "item";

      // 그래프 + 비율집계표 (가로 배치)
      const row = document.createElement("span");

      // 그래프: responsive 모드로 부모 크기에 맞추려면 wrap div 필요
      const chartWrap = document.createElement("div");
      chartWrap.className = "chart-wrap";

      const rateCanvas = document.createElement("canvas");
      rateCanvas.id = `g2bRateChart${idx}`;
      chartWrap.appendChild(rateCanvas);
      row.appendChild(chartWrap);

      const rateTableDiv = document.createElement("div");
      rateTableDiv.className = "rateTable g2b-rateTable-right";
      rateTableDiv.id = `g2bRateTable${idx}`;
      row.appendChild(rateTableDiv);

      item.appendChild(row);

      sectionsDiv.appendChild(item);

      // Render chart and tables — y축 max를 데이터 최댓값에 맞춰 동적 설정
      const maxPct = Math.max(...yearData.percentages.flat());
      const maxY = Math.max(30, Math.ceil(maxPct / 10) * 10 + 5);

      createG2bChart(`g2bRateChart${idx}`, yearData.percentages, year, "예가율 비율", maxY);
      createG2bRateTable(`g2bRateTable${idx}`, yearData.percentages, yearData.counts, year);
    });

  } catch (error) {
    console.error("데이터 로드 실패:", error);
    document.getElementById("sections").innerHTML = "<h2 style='color:red;text-align:center;'>g2bRateData.json 로드 실패. g2b_generate_data.py를 먼저 실행해주세요.</h2>";
  }
}

init();
