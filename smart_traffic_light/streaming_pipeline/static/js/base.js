function draw() {
  var simDivWindow=document.getElementById("contents");
  // Initializing traffic elements

  traffLightRedImg = new Image();
  traffLightRedImg.src="static/images/trafficLight_red.png";

  traffLightGreenImg = new Image();
  traffLightGreenImg.src="static/images/trafficLight_green.png";

  traffLightYellowImg = new Image();
  traffLightYellowImg.src="static/images/trafficLight_yellow.png";
  
  const canvas = document.getElementById("canvas");
  canvas.width  = simDivWindow.clientWidth; 
  canvas.height  = simDivWindow.clientHeight;
  
  if (canvas.getContext) {
    const ctx = canvas.getContext("2d");
    
    background = new Image();
    ctx.setTransform(1,0,0,1,0,0);
    background.onload = () => {
      ctx.drawImage(background,0,0,canvas.width,canvas.height);
    }
    background.src ="static/images/backgroundGrass.jpg";
    
    mainroad = new Image()
      mainroad.onload = () => {
        for (var i=0;i<=canvas.width;i+=100){
          console.log(i);
          ctx.setTransform(1,0,0,1,0,0);
          ctx.drawImage(mainroad, i, 300, 100, 100);
        }
    };
    mainroad.src = "static/images/1lane_road_horizontal.png"

    lane_2 = new Image()
    lane_2.onload = () => {
        for (var i=canvas.height;i>= canvas.height / 2 ;i-=100){
          console.log(i);
          ctx.setTransform(1,0,0,1,0,0);
          ctx.drawImage(lane_2, 900, i - 2, 100, 100);
        }
    };
    lane_2.src = "static/images/1lane_road_vertical.png"

  }
  }