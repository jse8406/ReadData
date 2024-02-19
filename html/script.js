const dates = Array.from({ length: 12 }, (_, i) => `${i + 1}월`);
const backgroundColors = ["blue", "green", "red", "yellow", "orange", "purple"];
const borderColors = ["rgba(0,0,255,0.3)", "rgba(0,255,0,0.3)", "rgba(255,0,0,0.3)", "rgba(255,255,0,0.3)", "rgba(255,165,0,0.3)", "rgba(128,0,128,0.3)"];

const yValues = [7, 8, 8, 9, 9, 9, 10, 11, 14, 14, 15];

const yVal2020 = [
  [2.0, 5.33, 12.67, 10.0, 8.67, 14.0, 10.0, 6.0, 8.0, 4.0, 7.33, 12.0],
  [1.34, 4.7, 12.75, 13.42, 9.4, 10.07, 8.72, 6.71, 8.72, 5.37, 10.74, 8.05],
  [0.64, 9.55, 10.19, 8.92, 8.92, 11.46, 6.37, 5.73, 5.1, 12.74, 12.1, 8.28],
  [2.38, 6.35, 13.49, 14.29, 9.52, 9.52, 7.94, 7.14, 7.94, 8.73, 7.14, 5.56],
  [0.95, 10.48, 16.19, 12.38, 9.52, 8.57, 10.48, 7.62, 5.71, 1.9, 10.48, 5.71],
  [1.52, 4.55, 14.39, 9.85, 11.36, 7.58, 6.06, 8.33, 7.58, 6.82, 9.09, 12.88]
];
const yVal2021 = [[3.79, 3.03, 11.36, 16.67, 13.64, 12.88, 6.06, 4.55, 7.58, 8.33, 6.82, 5.3], [1.49, 6.72, 5.22, 14.18, 11.94, 11.19, 8.96, 8.21, 8.96, 10.45, 8.21, 4.48], [0.69, 5.52, 11.03, 13.79, 8.28, 11.03, 11.03, 8.97, 8.97, 6.21, 8.97, 5.52], [1.56, 7.81, 14.06, 10.94, 6.25, 11.72, 10.94, 7.03, 8.59, 12.5, 6.25, 2.34], [2.44, 8.13, 13.01, 19.51, 13.01, 5.69, 8.94, 6.5, 7.32, 4.88, 7.32, 3.25], [5.88, 5.88, 11.76, 13.73, 8.82, 14.71, 5.88, 5.88, 5.88, 10.78, 6.86, 3.92]]

const yVal2022 = [[0.0, 6.21, 9.66, 7.59, 13.1, 8.97, 8.28, 8.97, 3.45, 12.41, 11.03, 10.34], [0.0, 5.65, 11.29, 10.48, 5.65, 13.71, 6.45, 8.06, 8.06, 9.68, 10.48, 10.48], [0.0, 9.65, 10.53, 11.4, 9.65, 6.14, 13.16, 11.4, 5.26, 7.89, 9.65, 5.26], [0.83, 9.92, 8.26, 9.92, 14.88, 7.44, 7.44, 10.74, 5.79, 9.92, 9.92, 4.96], [0.0, 7.02, 11.4, 18.42, 13.16, 8.77, 6.14, 8.77, 7.02, 7.02, 5.26, 7.02], [0.0, 6.25, 12.5, 13.54, 4.17, 8.33, 12.5, 12.5, 7.29, 3.12, 9.38, 10.42]]
const yVal2023 = [[1.72, 7.76, 11.21, 9.48, 9.48, 12.07, 6.03, 8.62, 9.48, 7.76, 6.9, 9.48], [0.68, 5.48, 10.27, 15.75, 11.64, 8.9, 9.59, 8.22, 8.22, 5.48, 6.85, 8.9], [1.42, 5.67, 12.06, 12.06, 9.93, 5.67, 7.8, 12.06, 7.09, 9.22, 8.51, 8.51], [0.0, 5.6, 15.2, 12.8, 10.4, 7.2, 11.2, 12.8, 2.4, 5.6, 9.6, 7.2], [0.85, 7.69, 11.11, 11.97, 6.84, 9.4, 2.56, 10.26, 11.97, 7.69, 10.26, 9.4], [0.89, 8.04, 7.14, 16.07, 12.5, 11.61, 8.93, 5.36, 6.25, 5.36, 9.82, 8.04]]

function dataset(set){
  const yDatasets = set.map((data, index) => ({
    label: `${Math.round((99.9 + 0.1*index)*10)/10}%`,
    fill: false,
    lineTension: 0,
    backgroundColor: backgroundColors[index],
    borderColor: borderColors[index],
    data: data
  }));
  const chartConfig = {
    type: "line",
    data: {
      labels: dates,
      datasets: yDatasets,
    },
    options: {
      title:{
        display: true,
        text: '예가율 비율',
        fontSize: 17,
  
      },
      legend: {
        position: 'top',
        display: true },
      scales: { yAxes: [{ ticks: { min: 0, max: 20 } }] },
    },
  };
  return chartConfig
}

const yDatasets = yVal2020.map((data, index) => ({
  label: `${Math.round((99.9 + 0.1*index)*10)/10}%`,
  fill: false,
  lineTension: 0,
  backgroundColor: backgroundColors[index],
  borderColor: borderColors[index],
  data: data
}));

const chartConfig = {
  type: "line",
  data: {
    labels: dates,
    datasets: yDatasets,
  },
  options: {
    title:{
      display: true,
      text: '2020 예가율 비율',
      fontSize: 17,

    },
    legend: {
      position: 'top',
      display: true },
    scales: { yAxes: [{ ticks: { min: 0, max: 20 } }] },
  },
};

const ctx = document.getElementById("myChart").getContext("2d");
new Chart(ctx, dataset(yVal2020));
const ctx2 = document.getElementById("myChart2").getContext("2d");
new Chart(ctx2, dataset(yVal2021));
const ctx3 = document.getElementById("myChart3").getContext("2d");
new Chart(ctx3, dataset(yVal2022));
const ctx4 = document.getElementById("myChart4").getContext("2d");
new Chart(ctx4, dataset(yVal2023));
const ctx5 = document.getElementById("myChart5").getContext("2d");
new Chart(ctx5, dataset(yVal2021));
