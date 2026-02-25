var socket_control = io.connect('http://' + location.host + '/control');

// --- Connection status ---
var outputDesktop = document.getElementById('output-desktop');
var outputMobile = document.getElementById('output-mobile');

setInterval(function () {
    var text = socket_control.connected ? 'Connected' : 'Connecting';
    outputDesktop.textContent = 'Desktop: ' + text;
    outputMobile.textContent = 'Mobile: ' + text;
}, 1000);

// --- Tracking toggle ---
var trackingCheckbox = document.getElementById('tracking-checkbox');
var trackingStatus = document.getElementById('tracking-status');

trackingCheckbox.addEventListener('change', function () {
    socket_control.emit('tracking', { enabled: trackingCheckbox.checked });
});

socket_control.on('tracking_status', function (data) {
    trackingCheckbox.checked = data.active;
    trackingStatus.textContent = 'Tracking: ' + (data.active ? 'ON' : 'OFF');
});

// --- Detect mobile ---
var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

if (isMobile) {

    // Fire button
    var fireBtn = document.getElementById('button');
    fireBtn.addEventListener('touchstart', function (evt) {
        socket_control.emit('control', { data: { A: 1 } });
        evt.preventDefault();
    });

    // Joystick
    new Joystick('joystick-section');

} else {

    // --- Desktop mode ---
    var CANVAS_SIZE = 100;
    var SPEED = 2;
    var FRICTION = 0.69;
    var COORD_MAX = 300;
    var keys = {};

    var canvas = document.getElementById('canvas');
    var ctx = canvas.getContext('2d');
    canvas.width = CANVAS_SIZE;
    canvas.height = CANVAS_SIZE;

    var camera = { x: 150, y: 150, velX: 0, velY: 0 };

    var coordsX = document.getElementById('coords-x');
    var coordsY = document.getElementById('coords-y');

    function convertRatio(x, y, oldMin, oldMax, newMin, newMax) {
        var nx = ((x - oldMin) / (oldMax - oldMin)) * (newMax - newMin) + newMin;
        var ny = ((y - oldMin) / (oldMax - oldMin)) * (newMax - newMin) + newMin;
        return [Number(nx.toFixed(4)), Number(ny.toFixed(5))];
    }

    function update() {
        if (keys['w']) { if (camera.velY < SPEED) camera.velY++; }
        if (keys['s']) { if (camera.velY > -SPEED) camera.velY--; }
        if (keys['a']) { if (camera.velX > -SPEED) camera.velX--; }
        if (keys['d']) { if (camera.velX < SPEED) camera.velX++; }

        // Apply friction
        camera.velX *= FRICTION;
        camera.velY *= FRICTION;
        camera.x += camera.velX;
        camera.y += camera.velY;

        // Clamp
        if (camera.x > COORD_MAX) camera.x = COORD_MAX;
        if (camera.x < 0) camera.x = 0;
        if (camera.y > COORD_MAX) camera.y = COORD_MAX;
        if (camera.y < 0) camera.y = 0;

        // Convert to servo range and emit
        var coords = convertRatio(camera.x, camera.y, 0, COORD_MAX, -1, 1);
        socket_control.emit('control', { data: { position: coords } });

        // Draw canvas dot
        ctx.clearRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
        var display = convertRatio(camera.x, camera.y, 0, COORD_MAX, 0, CANVAS_SIZE);
        ctx.fillStyle = 'red';
        ctx.beginPath();
        ctx.arc(display[0], display[1], 5, 0, Math.PI * 2);
        ctx.fill();

        // Update coordinate display
        coordsX.textContent = 'X: ' + camera.x.toFixed(3);
        coordsY.textContent = 'Y: ' + camera.y.toFixed(3);

        requestAnimationFrame(update);
    }

    requestAnimationFrame(update);

    window.addEventListener('keydown', function (e) {
        keys[e.key] = true;
    });

    window.addEventListener('keyup', function (e) {
        keys[e.key] = false;
        if (e.key === ' ') {
            socket_control.emit('control', { data: { A: 1 } });
            e.preventDefault();
        }
    });
}

// --- Joystick (vanilla JS) ---
function Joystick(divId) {
    var container = document.getElementById(divId);
    var radius = 50;
    var sx = -1;
    var sy = -1;

    // Create base
    var base = document.createElement('div');
    base.className = 'joystick_base';
    base.style.width = (radius * 2) + 'px';
    base.style.height = (radius * 2) + 'px';
    base.style.display = 'none';
    document.body.appendChild(base);

    // Create nip
    var nip = document.createElement('div');
    nip.className = 'joystick_nip';
    nip.style.display = 'none';
    document.body.appendChild(nip);

    function onMove(evt) {
        var touch = evt.touches[0];
        var rect = container.getBoundingClientRect();
        var x = touch.clientX - rect.left;
        var y = touch.clientY - rect.top;

        // Check bounds
        if (touch.clientX < rect.left || touch.clientX > rect.right ||
            touch.clientY < rect.top || touch.clientY > rect.bottom) {
            return;
        }

        if (sx === -1) {
            // Start
            sx = x;
            sy = y;
            base.style.display = 'block';
            base.style.top = (sy - radius + rect.top) + 'px';
            base.style.left = (sx - radius + rect.left) + 'px';
            nip.style.display = 'block';
        }

        // Move nip if within radius
        if (Math.sqrt(Math.pow(x - sx, 2) + Math.pow(y - sy, 2)) < radius) {
            nip.style.top = (y - 25 + rect.top) + 'px';
            nip.style.left = (x - 25 + rect.left) + 'px';
        }

        var data = { position: [(x - sx) / radius, (y - sy) / radius] };
        socket_control.emit('control', { data: data });
        evt.preventDefault();
    }

    function onEnd(evt) {
        sx = -1;
        sy = -1;
        base.style.display = 'none';
        nip.style.display = 'none';
        socket_control.emit('control', { data: { position: [0.0, 0.0] } });
        evt.preventDefault();
    }

    container.addEventListener('touchstart', onMove);
    container.addEventListener('touchmove', onMove);
    container.addEventListener('touchend', onEnd);

    // Prevent context menu
    container.addEventListener('contextmenu', function (evt) {
        evt.preventDefault();
    });
}
