const dates = Array.from({ length: 12 }, (_, i) => `${i + 1}월`);
const backgroundColors = ["blue", "yellow", "green", "red", "purple","black"];
const borderColors = ["rgba(0,0,255,0.3)", "rgba(255,255,0,0.6)","rgba(0,255,0,0.3)", "rgba(255,0,0,0.6)", "rgba(255,0,255,0.3)", "rgba(0,0,0,0.6)"];

// 물품 비율 정보
const yValrate2020 = [
  [2.0, 5.33, 12.67, 10.0, 8.67, 14.0, 10.0, 6.0, 8.0, 4.0, 7.33, 12.0],
  [1.34, 4.7, 12.75, 13.42, 9.4, 10.07, 8.72, 6.71, 8.72, 5.37, 10.74, 8.05],
  [0.64, 9.55, 10.19, 8.92, 8.92, 11.46, 6.37, 5.73, 5.1, 12.74, 12.1, 8.28],
  [2.38, 6.35, 13.49, 14.29, 9.52, 9.52, 7.94, 7.14, 7.94, 8.73, 7.14, 5.56],
  [0.95, 10.48, 16.19, 12.38, 9.52, 8.57, 10.48, 7.62, 5.71, 1.9, 10.48, 5.71],
  [1.52, 4.55, 14.39, 9.85, 11.36, 7.58, 6.06, 8.33, 7.58, 6.82, 9.09, 12.88]
];
const yValrate2021 = [
  [3.79, 3.03, 11.36, 16.67, 13.64, 12.88, 6.06, 4.55, 7.58, 8.33, 6.82, 5.3], 
[1.49, 6.72, 5.22, 14.18, 11.94, 11.19, 8.96, 8.21, 8.96, 10.45, 8.21, 4.48], 
[0.69, 5.52, 11.03, 13.79, 8.28, 11.03, 11.03, 8.97, 8.97, 6.21, 8.97, 5.52],
 [1.56, 7.81, 14.06, 10.94, 6.25, 11.72, 10.94, 7.03, 8.59, 12.5, 6.25, 2.34], 
 [2.44, 8.13, 13.01, 19.51, 13.01, 5.69, 8.94, 6.5, 7.32, 4.88, 7.32, 3.25], 
 [5.88, 5.88, 11.76, 13.73, 8.82, 14.71, 5.88, 5.88, 5.88, 10.78, 6.86, 3.92]
]
const yValrate2022 = [
  [0.0, 6.21, 9.66, 7.59, 13.1, 8.97, 8.28, 8.97, 3.45, 12.41, 11.03, 10.34],
   [0.0, 5.65, 11.29, 10.48, 5.65, 13.71, 6.45, 8.06, 8.06, 9.68, 10.48, 10.48], 
   [0.0, 9.65, 10.53, 11.4, 9.65, 6.14, 13.16, 11.4, 5.26, 7.89, 9.65, 5.26],
    [0.83, 9.92, 8.26, 9.92, 14.88, 7.44, 7.44, 10.74, 5.79, 9.92, 9.92, 4.96],
     [0.0, 7.02, 11.4, 18.42, 13.16, 8.77, 6.14, 8.77, 7.02, 7.02, 5.26, 7.02],
      [0.0, 6.25, 12.5, 13.54, 4.17, 8.33, 12.5, 12.5, 7.29, 3.12, 9.38, 10.42]
    ]
const yValrate2023 = [
  [1.72, 7.76, 11.21, 9.48, 9.48, 12.07, 6.03, 8.62, 9.48, 7.76, 6.9, 9.48],
 [0.68, 5.48, 10.27, 15.75, 11.64, 8.9, 9.59, 8.22, 8.22, 5.48, 6.85, 8.9],
  [1.42, 5.67, 12.06, 12.06, 9.93, 5.67, 7.8, 12.06, 7.09, 9.22, 8.51, 8.51], 
  [0.0, 5.6, 15.2, 12.8, 10.4, 7.2, 11.2, 12.8, 2.4, 5.6, 9.6, 7.2],
   [0.85, 7.69, 11.11, 11.97, 6.84, 9.4, 2.56, 10.26, 11.97, 7.69, 10.26, 9.4],
    [0.89, 8.04, 7.14, 16.07, 12.5, 11.61, 8.93, 5.36, 6.25, 5.36, 9.82, 8.04]
  ]
// update
const yValrate2024 = [[21.43, 35.71, 42.86, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [20.0, 55.0, 25.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [5.0, 75.0, 20.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 81.82, 18.18, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [10.0, 70.0, 20.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [11.76, 58.82, 29.41, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
// 물품 수량 정보
const yValamt2020 = [
  [3, 8, 19, 15, 13, 21, 15, 9, 12, 6, 11, 18], 
[2, 7, 19, 20, 14, 15, 13, 10, 13, 8, 16, 12],
 [1, 15, 16, 14, 14, 18, 10, 9, 8, 20, 19, 13], 
 [3, 8, 17, 18, 12, 12, 10, 9, 10, 11, 9, 7], 
 [1, 11, 17, 13, 10, 9, 11, 8, 6, 2, 11, 6],
  [2, 6, 19, 13, 15, 10, 8, 11, 10, 9, 12, 17]
]
const yValamt2021 = [
  [5, 4, 15, 22, 18, 17, 8, 6, 10, 11, 9, 7],
   [2, 9, 7, 19, 16, 15, 12, 11, 12, 14, 11, 6],
    [1, 8, 16, 20, 12, 16, 16, 13, 13, 9, 13, 8],
     [2, 10, 18, 14, 8, 15, 14, 9, 11, 16, 8, 3],
      [3, 10, 16, 24, 16, 7, 11, 8, 9, 6, 9, 4],
       [6, 6, 12, 14, 9, 15, 6, 6, 6, 11, 7, 4]
      ]
const yValamt2022 = [
  [0, 9, 14, 11, 19, 13, 12, 13, 5, 18, 16, 15],
 [0, 7, 14, 13, 7, 17, 8, 10, 10, 12, 13, 13],
  [0, 11, 12, 13, 11, 7, 15, 13, 6, 9, 11, 6],
   [1, 12, 10, 12, 18, 9, 9, 13, 7, 12, 12, 6], 
   [0, 8, 13, 21, 15, 10, 7, 10, 8, 8, 6, 8], 
   [0, 6, 12, 13, 4, 8, 12, 12, 7, 3, 9, 10]
  ]
const yValamt2023 = [
  [2, 9, 13, 11, 11, 14, 7, 10, 11, 9, 8, 11],
   [1, 8, 15, 23, 17, 13, 14, 12, 12, 8, 10, 13],
    [2, 8, 17, 17, 14, 8, 11, 17, 10, 13, 12, 12],
     [0, 7, 19, 16, 13, 9, 14, 16, 3, 7, 12, 9],
      [1, 9, 13, 14, 8, 11, 3, 12, 14, 9, 12, 11],
       [1, 9, 8, 18, 14, 13, 10, 6, 7, 6, 11, 9]
      ]
const yValamt2024 = [[3, 5, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0], [4, 11, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 15, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 9, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 7, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0], [2, 10, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
// 용역 비율 정보
const yValrate2020yy = [
  [0.0, 0.0, 8.33, 6.25, 10.42, 12.5, 4.17, 10.42, 12.5, 6.25, 8.33, 20.83],
 [0.0, 5.41, 16.22, 18.92, 13.51, 2.7, 2.7, 5.41, 10.81, 5.41, 8.11, 10.81],
  [0.0, 2.94, 8.82, 11.76, 11.76, 8.82, 2.94, 2.94, 5.88, 17.65, 14.71, 11.76], 
  [0.0, 0.0, 3.7, 14.81, 11.11, 11.11, 7.41, 7.41, 11.11, 14.81, 7.41, 11.11],
   [4.17, 12.5, 16.67, 8.33, 8.33, 0.0, 12.5, 8.33, 8.33, 0.0, 8.33, 12.5],
    [2.63, 5.26, 7.89, 18.42, 15.79, 2.63, 5.26, 7.89, 7.89, 10.53, 2.63, 13.16]
  ]
const yValrate2021yy = [
  [7.5, 2.5, 0.0, 25.0, 15.0, 17.5, 0.0, 2.5, 7.5, 5.0, 15.0, 2.5],
   [2.44, 0.0, 4.88, 12.2, 12.2, 19.51, 9.76, 4.88, 4.88, 9.76, 12.2, 7.32],
    [2.17, 2.17, 10.87, 15.22, 13.04, 6.52, 15.22, 10.87, 10.87, 4.35, 2.17, 6.52],
     [2.56, 2.56, 5.13, 17.95, 5.13, 15.38, 15.38, 5.13, 5.13, 7.69, 12.82, 5.13], [4.76, 2.38, 11.9, 16.67, 23.81, 4.76, 4.76, 7.14, 4.76, 7.14, 7.14, 4.76], [9.68, 3.23, 9.68, 12.9, 6.45, 29.03, 0.0, 3.23, 0.0, 12.9, 9.68, 3.23]
    ]
const yValrate2022yy = [
  [0.0, 4.65, 2.33, 9.3, 18.6, 4.65, 11.63, 11.63, 4.65, 6.98, 9.3, 16.28],
   [0.0, 2.27, 2.27, 9.09, 4.55, 13.64, 9.09, 9.09, 9.09, 11.36, 15.91, 13.64],
    [0.0, 2.78, 8.33, 11.11, 5.56, 2.78, 19.44, 16.67, 8.33, 16.67, 8.33, 0.0],
     [2.13, 2.13, 4.26, 8.51, 17.02, 12.77, 10.64, 10.64, 6.38, 8.51, 10.64, 6.38],
      [0.0, 4.55, 9.09, 20.45, 13.64, 6.82, 4.55, 13.64, 4.55, 6.82, 4.55, 11.36],
       [0.0, 5.56, 5.56, 13.89, 2.78, 11.11, 11.11, 22.22, 2.78, 5.56, 2.78, 16.67]
      ]
const yValrate2023yy = 
[[0.0, 2.13, 6.38, 12.77, 6.38, 14.89, 8.51, 8.51, 10.64, 12.77, 10.64, 6.38],
 [1.64, 6.56, 8.2, 19.67, 13.11, 8.2, 8.2, 6.56, 4.92, 6.56, 6.56, 9.84],
  [2.56, 2.56, 7.69, 12.82, 15.38, 2.56, 10.26, 2.56, 7.69, 10.26, 12.82, 12.82],
   [0.0, 4.35, 13.04, 15.22, 8.7, 4.35, 10.87, 8.7, 2.17, 4.35, 15.22, 13.04],
    [0.0, 4.76, 7.14, 11.9, 7.14, 9.52, 2.38, 14.29, 9.52, 11.9, 11.9, 9.52],
     [0.0, 8.33, 6.25, 14.58, 12.5, 14.58, 6.25, 4.17, 6.25, 4.17, 14.58, 8.33]
    ]
    const yValrate2024yy = 
    [[50.0, 50.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [33.33, 66.67, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [25.0, 75.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [33.33, 66.67, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [28.57, 71.43, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
// 용역 수량 정보
const yValamt2020yy = [[0, 0, 4, 3, 5, 6, 2, 5, 6, 3, 4, 10], [0, 2, 6, 7, 5, 1, 1, 2, 4, 2, 3, 4], [0, 1, 3, 4, 4, 3, 1, 1, 2, 6, 5, 4], [0, 0, 1, 4, 3, 3, 2, 2, 3, 4, 2, 3], [1, 3, 4, 2, 2, 0, 3, 2, 2, 0, 2, 3], [1, 2, 3, 7, 6, 1, 2, 3, 3, 4, 1, 5]]
const yValamt2021yy = [[3, 1, 0, 10, 6, 7, 0, 1, 3, 2, 6, 1], [1, 0, 2, 5, 5, 8, 4, 2, 2, 4, 5, 3], [1, 1, 5, 7, 6, 3, 7, 5, 5, 2, 1, 3], [1, 1, 2, 7, 2, 6, 6, 2, 2, 3, 5, 2], [2, 1, 5, 7, 10, 2, 2, 3, 2, 3, 3, 2], [3, 1, 3, 4, 2, 9, 0, 1, 0, 4, 3, 1]]
const yValamt2022yy = [[0, 2, 1, 4, 8, 2, 5, 5, 2, 3, 4, 7], [0, 1, 1, 4, 2, 6, 4, 4, 4, 5, 7, 6], [0, 1, 3, 4, 2, 1, 7, 6, 3, 6, 3, 0], [1, 1, 2, 4, 8, 6, 5, 5, 3, 4, 5, 3], [0, 2, 4, 9, 6, 3, 2, 6, 2, 3, 2, 5], [0, 2, 2, 5, 1, 4, 4, 8, 1, 2, 1, 6]]
const yValamt2023yy = [[0, 1, 3, 6, 3, 7, 4, 4, 5, 6, 5, 3], [1, 4, 5, 12, 8, 5, 5, 4, 3, 4, 4, 6], [1, 1, 3, 5, 6, 1, 4, 1, 3, 4, 5, 5], [0, 2, 6, 7, 4, 2, 5, 4, 1, 2, 7, 6], [0, 2, 3, 5, 3, 4, 1, 6, 4, 5, 5, 4], [0, 4, 3, 7, 6, 7, 3, 2, 3, 2, 7, 4]]
const yValamt2024yy = [[2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [2, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [2, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

var max_num = 30
function dataset(set, year, title){
  const yDatasets = set.map((data, index) => ({
    label: `${Math.round((99.9 + 0.1*index)*10)/10}%`,
    fill: false,
    lineTension: 0,
    backgroundColor: backgroundColors[index],
    backgroundwidth: 0.5,
    borderColor: borderColors[index],
    borderWidth: 2,
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
        text: `${year}년 ${title} 예가율`,
        fontSize: 17,
  
      },
      legend: {
        position: 'top',
        display: true },
      scales: { yAxes: [{ ticks: { min: 0, max: max_num } 
      }]},
      elements: {
        point: {
          radius: 2,
        }
      }
    },
  };
  return chartConfig
}
// 물품 연도별 정보 배열
const yValRateArray = [yValrate2020, yValrate2021, yValrate2022,yValrate2023,yValrate2024]
const yValAmtArray = [yValamt2020, yValamt2021, yValamt2022,yValamt2023,yValamt2024]

// 용역 연도별 정보 배열
const yValyyRateArray = [yValrate2020yy,yValrate2021yy,yValrate2022yy,yValrate2023yy,yValrate2024yy]
const yValyyAmtArray = [yValamt2020yy,yValamt2021yy,yValamt2022yy,yValamt2023yy,yValamt2024yy]

// html 차트 id 모음
const amtChartElements = ["amtChart","amtChart2","amtChart3", "amtChart4","amtChart5"]
const rateChartElements = ["rateChart","rateChart2","rateChart3", "rateChart4", "rateChart5"]
const years = [2020, 2021, 2022, 2023,2024]

let Charts= []

// 물품 차트 만드는 반복문
function drawMpChart(){
  Charts.forEach(chart => {
    chart.destroy();
  });
  Charts = [];
  //물품 수량 그래프
  for (let i = 0; i < years.length; i++) {
    var ctx = document.getElementById(amtChartElements[i]).getContext("2d");
    var chart = new Chart(ctx, dataset(yValAmtArray[i], years[i], '수량별'));
    Charts.push(chart)
  }
  // 물품 비율 그래프
  for (let i = 0; i < years.length; i++) {
    if(i==years.length - 1){
      max_num = 100;
    }

    var ctx = document.getElementById(rateChartElements[i]).getContext("2d");
    var chart = new Chart(ctx, dataset(yValRateArray[i], years[i], '비율별'));
    Charts.push(chart)
  }
}

// 용역 차트 만드는 반복문
function drawYyChart(){
  Charts.forEach(chart => {
    chart.destroy();
  });
  Charts = [];
  for (let i = 0; i < years.length; i++) {
    var ctx = document.getElementById(amtChartElements[i]).getContext("2d");
    var chart = new Chart(ctx, dataset(yValyyAmtArray[i], years[i], '수량별'));
    Charts.push(chart)
  }
  // 물품 비율 그래프
  for (let i = 0; i < years.length; i++) {
    var ctx = document.getElementById(rateChartElements[i]).getContext("2d");
    var chart = new Chart(ctx, dataset(yValyyRateArray[i], years[i], '비율별'));
    Charts.push(chart)
  }
}

// 물품 display 랜더링
function change80(){
  var title = document.getElementsByTagName("h1");
  title[0].innerText = "물품";

  var h4Elements = document.getElementsByTagName("h4");
  for (var i = 0; i < h4Elements.length; i++){
      h4Elements[i].innerText = "낙찰하한률 80.495%"; 
  }
  drawMpChart();
  for (let i = 0; i < years.length; i++) {
    updateAmtTable(yValAmtArray[i],amtTableElements[i])
    updateRateTable(yValRateArray[i], rateTableElements[i])
  }
}

// 용역 display 랜더링
function change88(){
  var title = document.getElementsByTagName("h1");
  title[0].innerText = "용역";
  
  var h4Elements = document.getElementsByTagName("h4");
  for (var i = 0; i < h4Elements.length; i++){
      h4Elements[i].
      innerText = "낙찰하한률 88.75%";
  }
  drawYyChart()
  for (let i = 0; i < years.length; i++) {
    updateAmtTable(yValyyAmtArray[i],amtTableElements[i])
    updateRateTable(yValyyRateArray[i], rateTableElements[i])
  }
}

const percents = ['99.9%','100.0%','100.1%','100.2%','100.3%','100.4%', '총합'];
const amtTableElements = ["amtTable","amtTable2","amtTable3", "amtTable4","amtTable5"]
const rateTableElements = ["rateTable","rateTable2","rateTable3", "rateTable4","rateTable5"]

// 각 하위 배열의 합을 계산하여 sums 배열에 추가합니다.

// 2차원 배열 각각의 배열 합 1차원 배열로 리턴해주는 함수
function sumOfdata(data){
  sums = [];
  data.forEach(subArray => {
  const sum = subArray.reduce((acc, curr) => acc + curr, 0);
  sums.push(sum);});
  const sumOfsums = sums.reduce((accumulator, currentValue) => accumulator + currentValue, 0);
  sums.push(sumOfsums)
  const rateArray = sums.map(num => (num/sumOfsums * 100).toFixed(2)+'%');
  const arr = [sums, rateArray]
  return arr
}

headers = [[], '수량', '비율']

//change 
function createAmtTable(data, percents, id, year) {
  
  var sumData = sumOfdata(data)
  const container = document.getElementById(id);
  const caption = document.createElement('caption');
  caption.textContent = `${year}년 수량 집계표`;
  // 여기까진 caption

  container.insertBefore(caption, container.firstChild);
  // 테이블 요소 생성
  const table = document.createElement('table');
  // 첫 번째 행에는 월 정보를 추가
  const headerRow = table.insertRow();
  headers.forEach(header => {
    const th = document.createElement('th');
    th.textContent = header;
    headerRow.appendChild(th);
  });
  const transposed = []
  for (let i = 0; i < percents.length; i++) {
    transposed.push([]);
    transposed[i].push(percents[i]);
    for (let j = 0; j < sumData.length; j++) {
      transposed[i].push(sumData[j][i]);
    }
  }
  transposed.forEach(rowData => {
    const row = table.insertRow();
    rowData.forEach(value => {
      const cell = row.insertCell();
      cell.textContent = value;
    });
  });
  // 컨테이너에 테이블 추가
  container.appendChild(table);
}

function updateAmtTable (data,id) {
  var sumData = sumOfdata(data)
  // 변경할 테이블의 DOM 요소 가져오기
  const table = document.getElementById(id);
  for (let i = 1; i < 8; i++){
  table.getElementsByTagName("tr")[i].getElementsByTagName("td")[1].innerHTML = sumData[0][i-1]
  }
  for (let i = 1; i < 8; i++){
    table.getElementsByTagName("tr")[i].getElementsByTagName("td")[2].innerHTML = sumData[1][i-1]
    }
}
function updateRateTable(data, id){
  const table = document.getElementById(id);

  for (let i = 0; i < percents.length-1; i++){
    for (let j = 0; j < dates.length; j++)
    table.getElementsByTagName("tr")[j+1].getElementsByTagName("td")[i+1].innerHTML = data[i][j];
  }
}


function createRateTable(data, percents, id, year){
  const container = document.getElementById(id)
  const caption = document.createElement('caption');
  caption.textContent = `${year}년 비율 집계표`;
  container.insertBefore(caption, container.firstChild);
  //여기까진 caption
  const table = document.createElement('table');
  const headerRow = table.insertRow();
  percents.forEach(percent => {
    const th = document.createElement('th');
    th.textContent = percent;
    headerRow.appendChild(th);
  });
  const transposed = [];
  for (let i = 0; i < data[0].length; i++) {
    transposed.push([]);
    transposed[i].push(`${i+1}월`);
    for (let j = 0; j < data.length; j++) {
      transposed[i].push(data[j][i]);
    }
  }
  transposed.forEach(subArray => {
    const row = table.insertRow();
    subArray.forEach(value => {
      const cell = row.insertCell();
      cell.textContent = value;
    });
  });

  container.appendChild(table);
}

//초기 시작시 한번 그리고 시작

// drawMptable 함수로 나중에 묶을 것
for (let i = 0; i < years.length; i++) {
  createAmtTable(yValAmtArray[i], percents, amtTableElements[i], years[i]);
}
percents.pop(); // 총합 col 제거
percents.unshift('');
for (let i = 0; i < years.length; i++) {
  createRateTable(yValRateArray[i], percents, rateTableElements[i], years[i]);
}
drawMpChart()
