const dates = Array.from({ length: 12 }, (_, i) => `${i + 1}월`);
const backgroundColors = ["blue", "green", "red", "yellow", "orange", "purple"];
const borderColors = ["rgba(0,0,255,0.3)", "rgba(0,255,0,0.3)", "rgba(255,0,0,0.3)", "rgba(255,255,0,0.3)", "rgba(255,165,0,0.3)", "rgba(128,0,128,0.3)"];
const yVal2020 = [
  [2.0, 5.33, 12.67, 10.0, 8.67, 14.0, 10.0, 6.0, 8.0, 4.0, 7.33, 12.0],
  [1.34, 4.7, 12.75, 13.42, 9.4, 10.07, 8.72, 6.71, 8.72, 5.37, 10.74, 8.05],
  [0.64, 9.55, 10.19, 8.92, 8.92, 11.46, 6.37, 5.73, 5.1, 12.74, 12.1, 8.28],
  [2.38, 6.35, 13.49, 14.29, 9.52, 9.52, 7.94, 7.14, 7.94, 8.73, 7.14, 5.56],
  [0.95, 10.48, 16.19, 12.38, 9.52, 8.57, 10.48, 7.62, 5.71, 1.9, 10.48, 5.71],
  [1.52, 4.55, 14.39, 9.85, 11.36, 7.58, 6.06, 8.33, 7.58, 6.82, 9.09, 12.88]
];
const yVal2021 = [
  [3.79, 3.03, 11.36, 16.67, 13.64, 12.88, 6.06, 4.55, 7.58, 8.33, 6.82, 5.3], 
[1.49, 6.72, 5.22, 14.18, 11.94, 11.19, 8.96, 8.21, 8.96, 10.45, 8.21, 4.48], 
[0.69, 5.52, 11.03, 13.79, 8.28, 11.03, 11.03, 8.97, 8.97, 6.21, 8.97, 5.52],
 [1.56, 7.81, 14.06, 10.94, 6.25, 11.72, 10.94, 7.03, 8.59, 12.5, 6.25, 2.34], 
 [2.44, 8.13, 13.01, 19.51, 13.01, 5.69, 8.94, 6.5, 7.32, 4.88, 7.32, 3.25], 
 [5.88, 5.88, 11.76, 13.73, 8.82, 14.71, 5.88, 5.88, 5.88, 10.78, 6.86, 3.92]
]
const yVal2022 = [
  [0.0, 6.21, 9.66, 7.59, 13.1, 8.97, 8.28, 8.97, 3.45, 12.41, 11.03, 10.34],
   [0.0, 5.65, 11.29, 10.48, 5.65, 13.71, 6.45, 8.06, 8.06, 9.68, 10.48, 10.48], 
   [0.0, 9.65, 10.53, 11.4, 9.65, 6.14, 13.16, 11.4, 5.26, 7.89, 9.65, 5.26],
    [0.83, 9.92, 8.26, 9.92, 14.88, 7.44, 7.44, 10.74, 5.79, 9.92, 9.92, 4.96],
     [0.0, 7.02, 11.4, 18.42, 13.16, 8.77, 6.14, 8.77, 7.02, 7.02, 5.26, 7.02],
      [0.0, 6.25, 12.5, 13.54, 4.17, 8.33, 12.5, 12.5, 7.29, 3.12, 9.38, 10.42]
    ]
const yVal2023 = [
  [1.72, 7.76, 11.21, 9.48, 9.48, 12.07, 6.03, 8.62, 9.48, 7.76, 6.9, 9.48],
 [0.68, 5.48, 10.27, 15.75, 11.64, 8.9, 9.59, 8.22, 8.22, 5.48, 6.85, 8.9],
  [1.42, 5.67, 12.06, 12.06, 9.93, 5.67, 7.8, 12.06, 7.09, 9.22, 8.51, 8.51], 
  [0.0, 5.6, 15.2, 12.8, 10.4, 7.2, 11.2, 12.8, 2.4, 5.6, 9.6, 7.2],
   [0.85, 7.69, 11.11, 11.97, 6.84, 9.4, 2.56, 10.26, 11.97, 7.69, 10.26, 9.4],
    [0.89, 8.04, 7.14, 16.07, 12.5, 11.61, 8.93, 5.36, 6.25, 5.36, 9.82, 8.04]
  ]

const yVal2020yy = [[0.0, 0.0, 8.33, 6.25, 10.42, 12.5, 4.17, 10.42, 12.5, 6.25, 8.33, 20.83], [0.0, 5.41, 16.22, 18.92, 13.51, 2.7, 2.7, 5.41, 10.81, 5.41, 8.11, 10.81], [0.0, 2.94, 8.82, 11.76, 11.76, 8.82, 2.94, 2.94, 5.88, 17.65, 14.71, 11.76], [0.0, 0.0, 3.7, 14.81, 11.11, 11.11, 7.41, 7.41, 11.11, 14.81, 7.41, 11.11], [4.17, 12.5, 16.67, 8.33, 8.33, 0.0, 12.5, 8.33, 8.33, 0.0, 8.33, 12.5], [2.63, 5.26, 7.89, 18.42, 15.79, 2.63, 5.26, 7.89, 7.89, 10.53, 2.63, 13.16]]
const yVal2021yy = [[7.5, 2.5, 0.0, 25.0, 15.0, 17.5, 0.0, 2.5, 7.5, 5.0, 15.0, 2.5], [2.44, 0.0, 4.88, 12.2, 12.2, 19.51, 9.76, 4.88, 4.88, 9.76, 12.2, 7.32], [2.17, 2.17, 10.87, 15.22, 13.04, 6.52, 15.22, 10.87, 10.87, 4.35, 2.17, 6.52], [2.56, 2.56, 5.13, 17.95, 5.13, 15.38, 15.38, 5.13, 5.13, 7.69, 12.82, 5.13], [4.76, 2.38, 11.9, 16.67, 23.81, 4.76, 4.76, 7.14, 4.76, 7.14, 7.14, 4.76], [9.68, 3.23, 9.68, 12.9, 6.45, 29.03, 0.0, 3.23, 0.0, 12.9, 9.68, 3.23]]
const yVal2022yy = [[0.0, 4.65, 2.33, 9.3, 18.6, 4.65, 11.63, 11.63, 4.65, 6.98, 9.3, 16.28], [0.0, 2.27, 2.27, 9.09, 4.55, 13.64, 9.09, 9.09, 9.09, 11.36, 15.91, 13.64], [0.0, 2.78, 8.33, 11.11, 5.56, 2.78, 19.44, 16.67, 8.33, 16.67, 8.33, 0.0], [2.13, 2.13, 4.26, 8.51, 17.02, 12.77, 10.64, 10.64, 6.38, 8.51, 10.64, 6.38], [0.0, 4.55, 9.09, 20.45, 13.64, 6.82, 4.55, 13.64, 4.55, 6.82, 4.55, 11.36], [0.0, 5.56, 5.56, 13.89, 2.78, 11.11, 11.11, 22.22, 2.78, 5.56, 2.78, 16.67]]
const yVal2023yy = [[0.0, 2.13, 6.38, 12.77, 6.38, 14.89, 8.51, 8.51, 10.64, 12.77, 10.64, 6.38], [1.64, 6.56, 8.2, 19.67, 13.11, 8.2, 8.2, 6.56, 4.92, 6.56, 6.56, 9.84], [2.56, 2.56, 7.69, 12.82, 15.38, 2.56, 10.26, 2.56, 7.69, 10.26, 12.82, 12.82], [0.0, 4.35, 13.04, 15.22, 8.7, 4.35, 10.87, 8.7, 2.17, 4.35, 15.22, 13.04], [0.0, 4.76, 7.14, 11.9, 7.14, 9.52, 2.38, 14.29, 9.52, 11.9, 11.9, 9.52], [0.0, 8.33, 6.25, 14.58, 12.5, 14.58, 6.25, 4.17, 6.25, 4.17, 14.58, 8.33]]


const yValArray = [yVal2020, yVal2021, yVal2022,yVal2023]
const yValyyArray = [yVal2020yy,yVal2021yy,yVal2022yy,yVal2023yy]
const chartElements = ["myChart","myChar2","myChart3", "myChart4"]
const charts = []
var max_num = 25
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
      scales: { yAxes: [{ ticks: { min: 0, max: max_num } }] },
    },
  };
  return chartConfig
}

const ctx = document.getElementById("myChart").getContext("2d");
let myChart = new Chart(ctx, dataset(yVal2020));
const ctx2 = document.getElementById("myChart2").getContext("2d");
let myChart2 = new Chart(ctx2, dataset(yVal2021));
const ctx3 = document.getElementById("myChart3").getContext("2d");
let myChart3 = new Chart(ctx3, dataset(yVal2022));
const ctx4 = document.getElementById("myChart4").getContext("2d");
let myChart4 = new Chart(ctx4, dataset(yVal2023));


function change80(){
  var count = 0;
  var title = document.getElementsByTagName("h1");
  title[0].innerText = "물품";

  var h4Elements = document.getElementsByTagName("h4");
  for (var i = 0; i < h4Elements.length; i++){
      h4Elements[i].innerText = "낙찰하한률 80.495%"; 
  }
  var imgElements = document.getElementsByTagName("img");
  for (var i =0; i<imgElements.length; i+=3){
      imgElements[i].src = `./images/${2020+count}amt.png`;
      imgElements[i+1].src = `./images/${2020+count}pre.png`;
      imgElements[i+2].src = `./images/${2020+count}amtpercent.png`;
      count += 1;
  }
  max_num = 25;
  myChart.destroy();
  myChart = new Chart(ctx, dataset(yVal2020))
  myChart2.destroy();
  myChart2 = new Chart(ctx2, dataset(yVal2021));
  myChart3.destroy();
  myChart3 = new Chart(ctx3, dataset(yVal2022));
  myChart4.destroy();
  myChart4 = new Chart(ctx4, dataset(yVal2023));
}
function change88(){
  var count = 0;
  var title = document.getElementsByTagName("h1");
  title[0].innerText = "용역";
  
  var h4Elements = document.getElementsByTagName("h4");
  for (var i = 0; i < h4Elements.length; i++){
      h4Elements[i].
      innerText = "낙찰하한률 88.75%";
  }
  var imgElements = document.getElementsByTagName("img");
  for (var i =0; i<imgElements.length; i+=3){
      imgElements[i].src = `./images/${2020+count}amtyy.png`;
      imgElements[i+1].src = `./images/${2020+count}preyy.png`;
      imgElements[i+2].src = `./images/${2020+count}amtyypercent.png`;
      count += 1;
  }
  max_num = 30;
  myChart.destroy();
  myChart = new Chart(ctx, dataset(yVal2020yy));
  myChart2.destroy();
  myChart2 = new Chart(ctx2, dataset(yVal2021yy));
  myChart3.destroy();
  myChart3 = new Chart(ctx3, dataset(yVal2022yy));
  myChart4.destroy();
  myChart4 = new Chart(ctx4, dataset(yVal2023yy));
}
