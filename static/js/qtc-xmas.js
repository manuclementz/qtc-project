function setupSnowflakes() {
    var particleCount = 500;
    var particleMax = 2000;
    var sky = document.querySelector('body');
    var canvas = document.createElement('canvas');
    canvas.style = 'pointer-events:none;';
    canvas.style.zIndex = -1;
    var ctx = canvas.getContext('2d');
    var width = sky.clientWidth;
    var height = Math.max(
        document.body.scrollHeight, document.body.offsetHeight,
        document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight
    );

    var i = 0;
    var active = false;
    var snowflakes = [];
    var snowflake;
    var lastFrameTime = performance.now(); // Timestamp of the last frame

    canvas.style.position = 'absolute';
    canvas.style.left = canvas.style.top = '0';

    var Snowflake = function () {
        this.x = 0;
        this.y = 0;
        this.vy = 0;
        this.vx = 0;
        this.r = 0;

        this.reset();
    };

    Snowflake.prototype.reset = function () {
        this.x = Math.random() * width;
        this.y = Math.random() * -height;
        this.vy = 50 + Math.random() * 30; // Speed in pixels per second
        this.vx = (0.5 - Math.random()) * 50; // Horizontal speed in pixels per second
        this.r = 1 + Math.random() * 2;
        this.o = 0.5 + Math.random() * 0.5;
    };

    function generateSnowFlakes() {
        snowflakes = [];
        for (i = 0; i < particleMax; i++) {
            snowflake = new Snowflake();
            snowflake.reset();
            snowflakes.push(snowflake);
        }
    }

    generateSnowFlakes();

    function update(timestamp) {
        var deltaTime = (timestamp - lastFrameTime) / 1000; // Time since the last frame in seconds
        lastFrameTime = timestamp;

        ctx.clearRect(0, 0, width, height);

        if (!active) {
            return;
        }

        for (i = 0; i < particleCount; i++) {
            snowflake = snowflakes[i];
            snowflake.y += snowflake.vy * deltaTime; // Adjusted for deltaTime
            snowflake.x += snowflake.vx * deltaTime; // Adjusted for deltaTime

            ctx.globalAlpha = snowflake.o;
            ctx.beginPath();
            ctx.arc(snowflake.x, snowflake.y, snowflake.r, 0, Math.PI * 2, false);
            ctx.closePath();
            ctx.fill();

            if (snowflake.y > height) {
                snowflake.reset();
            }
        }

        requestAnimFrame(update);
    }

    function onResize() {
        width = sky.clientWidth;
        height = sky.clientHeight;
        canvas.width = width;
        canvas.height = height;
        ctx.fillStyle = '#FFF';

        var wasActive = active;
        active = width > 300;

        if (!wasActive && active) {
            requestAnimFrame(update);
        }
    }

    window.requestAnimFrame = (function () {
        return (
            window.requestAnimationFrame ||
            window.webkitRequestAnimationFrame ||
            window.mozRequestAnimationFrame ||
            function (callback) {
                window.setTimeout(callback, 1000 / 60);
            }
        );
    })();

    onResize();
    window.addEventListener('resize', onResize, false);

    sky.appendChild(canvas);
}

window.onload = function () {
    setTimeout(setupSnowflakes, 500);
};

document.querySelectorAll('.qtc-grid-item div[contenteditable]').forEach(div => {
    div.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault(); 
        }
    });
});

document.querySelectorAll('.qtc-grid-item div[contenteditable]').forEach(div => {
    div.addEventListener('input', (event) => {
        const target = event.target;
        target.style.height = 'auto'; 
        target.style.height = `${target.scrollHeight}px`;
    });
});