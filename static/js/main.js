var socket_status = io.connect('http://'+location.host+"/status");
var socket_control = io.connect('http://'+location.host+"/control");


/******************************************
  DOCREADY
  *****************************************/
  $(document).ready(function(){
    /* connected display */
    
    setInterval(function(){
        if(socket_control.connected){
            $('#output-desktop').html('Desktop: Connected');
            $('#output-mobile').html('Mobile: Connected');
        }else{
            $('#output-desktop').html('Desktop: Connecting');
            $('#output-mobile').html('Mobile: Connecting');
        }
    }, 1000);

    // Mobile
    if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
        
        // Fire Button event
        $(document).on('touchstart touchmove', '#button', function(evt){
            socket_control.emit('control', {data:{"A":1}});
            evt.preventDefault();
        });
    
        // Joystick
        var joystick = new Joystick("joystick-section", 0, {}, "position");

        // Prevent click
        window.oncontextmenu = function(evt){
            evt.preventDefault();
            evt.stopPropagation();
            return false;
        }
    
    }
    // Desktop
    else {

        var canvas_size = 100;
        var speed = 2;
        var friction = 0.69;
        var keys = [];
        var canvas = document.getElementById("canvas");
        var ctx = canvas.getContext("2d");
        canvas.width = canvas_size;
        canvas.height = canvas_size;
        
        var camera = {
            x: 150,
            y: 150,
            velY: 0,
            velX: 0,
            color: "red"
        };
        
        function update() {
            // Check if keys are pressed
            if (keys['w']) {
                if (camera.velY < speed) {
                    camera.velY++;
                }
            }
            if (keys['a']) {
                if (camera.velX > -speed) {
                    camera.velX--;
                }
            }            
            if (keys['s']) {
                if (camera.velY > -speed) {
                    camera.velY--;
                }
            }
            if (keys['d']) {
                if (camera.velX < speed) {
                    camera.velX++;
                }
            }

            // Clear previous red dot
            ctx.clearRect(0, 0, canvas_size, canvas_size);
            updateCamera(camera);

            // Run main control loop
            setTimeout(update, 10);
        }
        
        function updateCamera(camera) {
            camera.velY *= friction;
            camera.y += camera.velY;
            camera.velX *= friction;
            camera.x += camera.velX;
        
            // Convert position to servo position
            var coords = convertRatio( camera.x, camera.y, 0, 300, -1, 1);
            var camera_x = camera.x;
            var camera_y = camera.y;


            // Handle canvas overflow, not a good solution?
            
            if (camera.x >= 300) {
                camera.x = 300;
            } else if (camera.x <= 0) {
                camera.x = 0;
            }
            if (camera.y > 300) {
                camera.y = 300;
            } else if (camera.y <= 0) {
                camera.y = 0;
            }

            // Why is existing range 0 to 300?
            //console.log(camera.x,camera.y);

            // Convert position to canvas position
            var new_values = convertRatio( camera_x, camera_y, 0, 300, 0, canvas_size);

            // Draw new dot on cavas
            ctx.fillStyle = camera.color;
            ctx.beginPath();
            ctx.arc(new_values[0], new_values[1], 5, 0, Math.PI * 2);
            ctx.fill();

            // Update Coords
            $('#coords-x').html('X: '+ camera.x.toFixed(3));
            $('#coords-y').html('Y: '+ camera.y.toFixed(3));

            // Send control command via Websockets, try to don't send if still?
            socket_control.emit('control', {data:{"position":coords}});
        }

        // Convert ranges from one to another
        function convertRatio(x,y, old_min, old_max, new_min, new_max){
          var newX = ( (x - old_min) / (old_max - old_min) ) * (new_max - new_min) + new_min;
          var newY = ( (y - old_min) / (old_max - old_min) ) * (new_max - new_min) + new_min;
          return [ Number(newX.toFixed(4)), Number(newY.toFixed(5)) ];
        
        }
        
        // Start main control loop
        update();
       
        // Push key events into keys object
        window.addEventListener("keydown", function (e) {
            keys[e.key] = true;
        });
        
        // Set key events to false in keys object, handle space event for firing 
        window.addEventListener("keyup", function (e) {
            keys[e.key] = false;
            // Space to fire on desktop
            if (e.key === ' ') {
                console.log('Space pressed'); 
                socket_control.emit('control', {data:{"A":1}});
                e.preventDefault();
            }
        });
    }

});

var Joystick = function(divname,num, socket, name){

        this.divname = "#"+divname; // so we can use jquery
        this.num = num;
        this.socket = socket;
        this.name = name;
        this.radius = 50;
        this.sx = -1;
        this.sy = -1;
        this.offset = $(this.divname).offset();

       /* create base div */
        $('<div class="joystick_base" id="'+divname+'_base_'+num+'">').appendTo('body');
        $(this.divname+"_base_"+num).css("width",(this.radius*2)+"px");
        $(this.divname+"_base_"+num).css("height",(this.radius*2)+"px");
        $('<div class="joystick_nip" id="'+divname+'_overlay_'+num+'">').appendTo('body');

        /* create listener */
        $(this.divname).bind('touchstart touchmove mousemove', {parentObj:this}, function(evt){
            var parentobj = evt.data.parentObj;
            var touch = evt.originalEvent.targetTouches[0];
            var offset = $(parentobj.divname).offset();
            var x = touch.clientX - offset.left;
            var y = touch.clientY - offset.top;

            if (!(
                touch.clientX <= $(this).offset().left || touch.clientX >= $(this).offset().left + $(this).outerWidth() ||
                touch.clientY <= $(this).offset().top  || touch.clientY >= $(this).offset().top + $(this).outerHeight())){
                if(parentobj.sx == -1){
                    parentobj.start(x,y);
                }else{
                    parentobj.handle(x,y);
                }

                // send data via websockets
                var data = {}
                data[parentobj.name] = [(x-parentobj.sx)/parentobj.radius, (y-parentobj.sy)/parentobj.radius];
                socket_control.emit('control', {data:data});
                //console.log(data);
            }
            evt.preventDefault();
        });

        $(this.divname).bind('touchend', {parentObj:this}, function(evt){
            var parentobj = evt.data.parentObj;
            parentobj.sx = -1;
            parentobj.sy = -1;
            $('#output'+parentobj.num).html("joystick end");
            $(parentobj.divname+"_overlay_"+parentobj.num).css("display","none");
            $(parentobj.divname+"_base_"+parentobj.num).css("display","none");

            // send data via websockets to snap back to home
            var data = {}
            data[parentobj.name] = [0.0,0.0];
            socket_control.emit('control', {data:data});
            evt.preventDefault();
        })
    }

Joystick.prototype.start = function(sx,sy){
        
        this.sx = sx;
        this.sy = sy;

        $(this.divname+'_overlay_'+this.num).css("display","block");
        $(this.divname+'_overlay_'+this.num).css("top", (this.sy-25+this.offset.left)+"px");
        $(this.divname+'_overlay_'+this.num).css("left" ,(this.sx-25+this.offset.top)+"px");

        $(this.divname+'_base_'+this.num).css("display","block");
        $(this.divname+'_base_'+this.num).css("top", (this.sy-this.radius+this.offset.top)+"px");
        $(this.divname+'_base_'+this.num).css("left" ,(this.sx-this.radius+this.offset.left)+"px");
    }

Joystick.prototype.handle = function(x,y){
       
        // calculate relative coordinates to starting point
        if(Math.sqrt(Math.pow(x-this.sx,2)+Math.pow(y-this.sy, 2)) < this.radius){
            //$('#output'+this.num).html("joystick move:"+ ((x-this.sx)/this.radius).toFixed(1) + ":" + ((y-this.sy)/this.radius).toFixed(1));
            $(this.divname+'_overlay_'+this.num).css("top", (y-25+this.offset.top)+"px");
            $(this.divname+'_overlay_'+this.num).css("left" ,(x-25+this.offset.left)+"px");
        }
    }

