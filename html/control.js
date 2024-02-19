function change80(){
    var count = 0;
    var title = document.getElementsByTagName("h2");
    title[0 ].innerText = "물품";

    var h4Elements = document.getElementsByTagName("h4");
    for (var i = 0; i < h4Elements.length; i++){
        h4Elements[i].innerText = "낙찰하한률 80.495%"; 
    }
    var imgElements = document.getElementsByTagName("img");
    for (var i =0; i<imgElements.length; i+=2){
        imgElements[i].src = `./images/${2020+count}amt.png`;
        imgElements[i+1].src = `./images/${2020+count}pre.png`;
        count += 1;
    }
}
function change88(){
    var count = 0;
    var title = document.getElementsByTagName("h2");
    title[0].innerText = "용역";
    
    var h4Elements = document.getElementsByTagName("h4");
    for (var i = 0; i < h4Elements.length; i++){
        h4Elements[i].
        innerText = "낙찰하한률 88.75%";
    }
    var imgElements = document.getElementsByTagName("img");
    for (var i =0; i<imgElements.length; i+=2){
        imgElements[i].src = `./images/${2020+count}amtyy.png`;
        imgElements[i+1].src = `./images/${2020+count}preyy.png`;
        count += 1;
    }
}
