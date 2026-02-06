(function() {
    function checkDarkMode() {
        var isDarkMode = false;
        if (typeof window.use_darkmode !== 'undefined') {
            isDarkMode = window.use_darkmode;
        } else if (document.cookie.indexOf('darkmode=1') !== -1) {
            isDarkMode = true;
        } else if (document.querySelector('link[href*="darkmode.css"]')) {
            isDarkMode = true;
        }

        if (isDarkMode) {
            document.body.classList.add('tet-dark-mode');
            document.documentElement.classList.add('tet-dark-mode');
        }
    }
    
    checkDarkMode();
    document.addEventListener('DOMContentLoaded', checkDarkMode);
})();

document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname.indexOf('/problem/') === 0) {
        return;
    }
    if (window.location.pathname.indexOf('/assignments/') !== -1 ) {
        return;
    }
    var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    var isLowEndDevice = navigator.hardwareConcurrency <= 4 || isMobile;
    var isVeryLowEnd = navigator.hardwareConcurrency <= 2 || (isMobile && window.innerWidth < 400);
    if (prefersReducedMotion) {
        console.log('Tet2026: Reduced motion enabled, minimal effects');
        isVeryLowEnd = true;
    }
    var perfSettings = {
        petalCount: isVeryLowEnd ? 5 : (isLowEndDevice ? 10 : 20),
        fireworkEnabled: !isVeryLowEnd,
        fireworkInterval: isLowEndDevice ? 8000 : 4000,
        bottomFireworkEnabled: !isLowEndDevice,
        cursorTrailEnabled: !isMobile && !isVeryLowEnd,
        maxCursorFlowers: isLowEndDevice ? 8 : 15,
        lixiEnabled: !isVeryLowEnd,
        lixiInterval: isLowEndDevice ? 10000 : 5000,
        fireworkSparks: isLowEndDevice ? 0.5 : 1,
    };
    
    console.log('Tet2026 Performance:', isVeryLowEnd ? 'Very Low' : (isLowEndDevice ? 'Low' : 'High'), perfSettings);

    var isDarkMode = document.body.classList.contains('tet-dark-mode');
    var petalContainer = document.createElement('div');
    petalContainer.id = 'tet-petal-container';
    petalContainer.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:2147483646;overflow:hidden;';
    document.body.appendChild(petalContainer);

    var petalCount = 20;
    var petalTypes = [
        { emoji: '🌸', color: '#FFB6C1' },
        { emoji: '🌸', color: '#FF69B4' },
        { emoji: '✿', color: '#FFD700' }, 
        { emoji: '❀', color: '#FFA500' },
        { emoji: '✾', color: '#FFB6C1' },
    ];

    function createPetal() {
        var petal = document.createElement('div');
        petal.classList.add('tet-petal');
        
        var type = petalTypes[Math.floor(Math.random() * petalTypes.length)];
        var size = Math.random() * 20 + 15;
        var left = Math.random() * 100;
        var duration = Math.random() * 8 + 10;
        var delay = Math.random() * 5;
        var opacity = Math.random() * 0.5 + 0.3;

        petal.innerHTML = type.emoji;
        petal.style.cssText = `
            position: fixed;
            top: -50px;
            left: ${left}vw;
            font-size: ${size}px;
            opacity: ${opacity};
            color: ${type.color};
            animation: tetFall ${duration}s linear ${delay}s infinite, tetSway ${Math.random() * 4 + 3}s ease-in-out infinite;
            pointer-events: none;
            z-index: 2147483646;
            will-change: transform;
        `;
        
        petalContainer.appendChild(petal);
    }

    for (var i = 0; i < perfSettings.petalCount; i++) {
        createPetal();
    }
    if (!perfSettings.fireworkEnabled) {
        console.log('Tet2026: Fireworks disabled for performance');
    }
    
    var fireworkContainer = document.createElement('div');
    fireworkContainer.id = 'tet-firework-container';
    fireworkContainer.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:2147483645;overflow:hidden;';
    document.body.appendChild(fireworkContainer);

    var fireworkColors = ['#FF0000', '#FFD700', '#FF69B4', '#00FF00', '#87CEEB', '#FF4500', '#FFFF00', '#FF1493'];

    function createFirework() {
        var x = Math.random() * window.innerWidth;
        var y = Math.random() * (window.innerHeight * 0.5); 
        
        var firework = document.createElement('div');
        firework.classList.add('tet-firework');
        firework.style.cssText = `
            position: fixed;
            left: ${x}px;
            top: ${y}px;
            width: 0;
            height: 0;
            pointer-events: none;
        `;
        var sizeType = Math.random();
        var numSparks, baseSize, baseDistance;
        var isWillow = Math.random() < 0.3;
        
        if (sizeType < 0.2) {
            numSparks = 10 + Math.floor(Math.random() * 8);
            baseSize = 4;
            baseDistance = 30;
        } else if (sizeType < 0.5) {
            numSparks = 18 + Math.floor(Math.random() * 10);
            baseSize = 5;
            baseDistance = 50;
        } else if (sizeType < 0.8) {
            numSparks = 28 + Math.floor(Math.random() * 15);
            baseSize = 6;
            baseDistance = 70;
        } else {
            numSparks = 45 + Math.floor(Math.random() * 25);
            baseSize = 7;
            baseDistance = 90;
        }
        
        numSparks = Math.floor(numSparks * perfSettings.fireworkSparks);
        var mainColor = fireworkColors[Math.floor(Math.random() * fireworkColors.length)];
        var secondColor = fireworkColors[Math.floor(Math.random() * fireworkColors.length)];
        
        for (var i = 0; i < numSparks; i++) {
            var spark = document.createElement('div');
            var angle = (i / numSparks) * 360 + (Math.random() * 15 - 7.5);
            var color = Math.random() > 0.6 ? mainColor : secondColor;
            var distance = baseDistance + Math.random() * baseDistance;
            var size = baseSize + Math.random() * (baseSize * 0.8);
            var duration = isWillow ? (1.5 + Math.random() * 1) : (1 + Math.random() * 0.8);
            var animName = isWillow ? 'tetSparkleWillow' : 'tetSparkle';
            spark.classList.add('tet-spark');
            spark.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                background: ${color};
                border-radius: 50%;
                box-shadow: 0 0 ${size * 2}px ${color};
                animation: ${animName} ${duration}s ease-out forwards;
                transform: rotate(${angle}deg) translateY(-${distance}px);
                --spark-distance: ${distance}px;
                --spark-angle: ${angle}deg;
                will-change: transform, opacity;
            `;
            
            firework.appendChild(spark);
        }
        var numTwinkles = Math.floor(numSparks * (isLowEndDevice ? 0.2 : 0.6));
        for (var j = 0; j < numTwinkles; j++) {
            var twinkle = document.createElement('div');
            var tAngle = Math.random() * 360;
            var tDistance = (baseDistance * 0.3) + Math.random() * (baseDistance * 1.2);
            var tSize = 2 + Math.random() * 3;
            var tDelay = Math.random() * 0.5;
            var tDuration = 0.8 + Math.random() * 1;
            
            twinkle.style.cssText = `
                position: absolute;
                width: ${tSize}px;
                height: ${tSize}px;
                background: #FFFFFF;
                border-radius: 50%;
                box-shadow: 0 0 ${tSize * 3}px #FFFFFF;
                animation: tetTwinkle ${tDuration}s ease-in-out ${tDelay}s forwards;
                transform: rotate(${tAngle}deg) translateY(-${tDistance}px);
                opacity: 0;
                will-change: transform, opacity;
            `;
            
            firework.appendChild(twinkle);
        }
        
        fireworkContainer.appendChild(firework);
        
        setTimeout(function() {
            firework.remove();
        }, 3500);
    }

    var currentPath = window.location.pathname;
    var isHomepage = currentPath === '/' || currentPath === '';
    var isMemberPage = currentPath.startsWith('/user/') || currentPath.startsWith('/users');
    var isAboutPage = currentPath.startsWith('/about') || currentPath.startsWith('/gioi-thieu');
    var isHomeworkPage = currentPath.startsWith('/homework');
    var isFirstVisit = !sessionStorage.getItem('tet_firework_welcomed');
    var isTabVisible = !document.hidden;

    document.addEventListener('visibilitychange', function() {
        isTabVisible = !document.hidden;
    });
    
    if (isHomeworkPage) {
        fireworkContainer.style.display = 'none';
    } else {
        var fireworkInterval, fireworkChance;
        var bottomFireworkInterval, bottomFireworkChance;
        
        if (isHomepage || isMemberPage) {
            fireworkInterval = 3000;
            fireworkChance = 0.5;
            bottomFireworkInterval = 2500;
            bottomFireworkChance = 0.6;
        } else if (isAboutPage) {
            fireworkInterval = 2000;
            fireworkChance = 0.7;
            bottomFireworkInterval = 1800;
            bottomFireworkChance = 0.75;
        } else {
            fireworkInterval = 5000;
            fireworkChance = 0.3;
            bottomFireworkInterval = 4500;
            bottomFireworkChance = 0.35;
        }
        
        if (isLowEndDevice) {
            fireworkInterval = Math.max(fireworkInterval, perfSettings.fireworkInterval);
            bottomFireworkInterval = Math.max(bottomFireworkInterval, perfSettings.fireworkInterval);
            fireworkChance *= 0.5;
            bottomFireworkChance *= 0.5;
        }
        
        if (isFirstVisit && perfSettings.fireworkEnabled) {
            sessionStorage.setItem('tet_firework_welcomed', 'true');
            
            var welcomeBurstCount = 0;
            var maxWelcomeBursts = isLowEndDevice ? 10 : 20;
            var welcomeInterval = setInterval(function() {
                if (!isTabVisible) return;
                
                var numFireworks = isLowEndDevice ? 1 : (2 + Math.floor(Math.random() * 3));
                for (var w = 0; w < numFireworks; w++) {
                    setTimeout(function() {
                        if (isTabVisible) {
                            createFirework();
                            if (Math.random() > 0.5 && perfSettings.bottomFireworkEnabled) createBottomFirework();
                        }
                    }, w * 150);
                }
                welcomeBurstCount++;
                
                if (welcomeBurstCount >= maxWelcomeBursts) {
                    clearInterval(welcomeInterval);
                }
            }, isLowEndDevice ? 800 : 500);
        } else if (perfSettings.fireworkEnabled) {
            var initialCount = isLowEndDevice ? 1 : 3;
            setTimeout(function() {
                for (var i = 0; i < initialCount; i++) {
                    setTimeout(createFirework, i * 500);
                }
            }, 1000);
            
            if (perfSettings.bottomFireworkEnabled) {
                setTimeout(function() {
                    createBottomFirework();
                    if (!isLowEndDevice) {
                        setTimeout(createBottomFirework, 800);
                        setTimeout(createBottomFirework, 1600);
                    }
                }, 2000);
            }
        }

        if (perfSettings.fireworkEnabled) {
            setInterval(function() {
                if (!isTabVisible) return;
                
                if (Math.random() < fireworkChance) {
                    createFirework();
                }
            }, fireworkInterval);
        }
        
        if (perfSettings.bottomFireworkEnabled) {
            setInterval(function() {
                if (!isTabVisible) return;
                
                if (Math.random() < bottomFireworkChance) {
                    createBottomFirework();
                }
            }, bottomFireworkInterval);
        }
    }

    function createBottomFirework() {
        if (!perfSettings.bottomFireworkEnabled) return;
        
        var startX = Math.random() * window.innerWidth;
        var startY = window.innerHeight;
        var endY = window.innerHeight * (0.3 + Math.random() * 0.3); 

        var rocket = document.createElement('div');
        rocket.style.cssText = `
            position: fixed;
            left: ${startX}px;
            bottom: 0;
            width: 4px;
            height: 15px;
            background: linear-gradient(to top, #FF4500, #FFD700);
            border-radius: 2px;
            z-index: 2147483645;
            pointer-events: none;
            box-shadow: 0 0 10px #FFD700, 0 0 20px #FF4500;
        `;
        document.body.appendChild(rocket);
        
        // Animation bay lên
        var rocketY = startY;
        var rocketSpeed = 8 + Math.random() * 4;
        
        var rocketInterval = setInterval(function() {
            rocketY -= rocketSpeed;
            rocket.style.bottom = (startY - rocketY) + 'px';
            
            // Khi đạt đỉnh, nổ pháo hoa
            if (rocketY <= endY) {
                clearInterval(rocketInterval);
                rocket.remove();
                createExplosion(startX, window.innerHeight - (startY - rocketY));
            }
        }, 16);
    }
    
    function createExplosion(x, y) {
        var explosion = document.createElement('div');
        explosion.style.cssText = `
            position: fixed;
            left: ${x}px;
            top: ${y}px;
            width: 0;
            height: 0;
            pointer-events: none;
            z-index: 2147483645;
        `;
        document.body.appendChild(explosion);

        var explosionType = Math.random();
        var numSparks, baseSize, baseDistance;
        var isWillow = Math.random() < 0.35;
        
        if (explosionType < 0.15) {
            numSparks = 15 + Math.floor(Math.random() * 10);
            baseSize = 4;
            baseDistance = 50;
        } else if (explosionType < 0.45) {
            numSparks = 28 + Math.floor(Math.random() * 15);
            baseSize = 5;
            baseDistance = 80;
        } else if (explosionType < 0.75) {
            numSparks = 45 + Math.floor(Math.random() * 20);
            baseSize = 6;
            baseDistance = 110;
        } else {
            numSparks = 60 + Math.floor(Math.random() * 30);
            baseSize = 7;
            baseDistance = 140;
        }
        
        numSparks = Math.floor(numSparks * perfSettings.fireworkSparks);
        
        var mainColor = fireworkColors[Math.floor(Math.random() * fireworkColors.length)];
        var secondColor = fireworkColors[Math.floor(Math.random() * fireworkColors.length)];
        for (var i = 0; i < numSparks; i++) {
            var spark = document.createElement('div');
            var angle = (i / numSparks) * 360 + (Math.random() * 20 - 10);
            var distance = baseDistance + Math.random() * (baseDistance * 0.6);
            var color = Math.random() > 0.5 ? mainColor : secondColor;
            var size = baseSize + Math.random() * (baseSize * 0.8);
            var duration = isWillow ? (1.2 + Math.random() * 0.8) : (0.8 + Math.random() * 0.7);
            var animName = isWillow ? 'tetBottomSparkleWillow' : 'tetBottomSparkle';
            
            spark.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                background: ${color};
                border-radius: 50%;
                box-shadow: 0 0 ${size * 2}px ${color};
                left: 0;
                top: 0;
                opacity: 1;
                transform: rotate(${angle}deg) translateY(0);
                animation: ${animName} ${duration}s ease-out forwards;
                --spark-distance: ${distance}px;
                --spark-angle: ${angle}deg;
                will-change: transform, opacity;
            `;
            
            explosion.appendChild(spark);
        }

        var numTwinkles = Math.floor(numSparks * (isLowEndDevice ? 0.2 : 0.5));
        for (var j = 0; j < numTwinkles; j++) {
            var twinkle = document.createElement('div');
            var tAngle = Math.random() * 360;
            var tDistance = (baseDistance * 0.2) + Math.random() * (baseDistance * 1.3);
            var tSize = 2 + Math.random() * 3;
            var tDelay = Math.random() * 0.4;
            var tDuration = 0.6 + Math.random() * 0.8;
            
            twinkle.style.cssText = `
                position: absolute;
                width: ${tSize}px;
                height: ${tSize}px;
                background: #FFFFFF;
                border-radius: 50%;
                box-shadow: 0 0 ${tSize * 3}px #FFFFFF;
                animation: tetTwinkle ${tDuration}s ease-in-out ${tDelay}s forwards;
                transform: rotate(${tAngle}deg) translateY(-${tDistance}px);
                opacity: 0;
                left: 0;
                top: 0;
            `;
            
            explosion.appendChild(twinkle);
        }
        setTimeout(function() {
            explosion.remove();
        }, 3000);
    }

    var leftLantern = document.createElement('div');
    leftLantern.classList.add('tet-lantern', 'tet-lantern-left');
    leftLantern.innerHTML = '🏮';
    leftLantern.style.cssText = `
        position: fixed;
        top: 55px;
        left: 5px;
        font-size: 35px;
        z-index: 999;
        animation: tetSwing 3s ease-in-out infinite;
        filter: drop-shadow(0 3px 6px rgba(255,0,0,0.4));
        pointer-events: none;
    `;
    
    var rightLantern = document.createElement('div');
    rightLantern.classList.add('tet-lantern', 'tet-lantern-right');
    rightLantern.innerHTML = '🏮';
    rightLantern.style.cssText = `
        position: fixed;
        top: 55px;
        right: 5px;
        font-size: 35px;
        z-index: 999;
        animation: tetSwing 3s ease-in-out infinite reverse;
        filter: drop-shadow(0 3px 6px rgba(255,0,0,0.4));
        pointer-events: none;
    `;
    
    document.body.appendChild(leftLantern);
    document.body.appendChild(rightLantern);

    if (!sessionStorage.getItem('tet2026_intro_shown')) {

        var fontLink = document.createElement('link');
        fontLink.href = 'https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Playfair+Display:wght@700&display=swap';
        fontLink.rel = 'stylesheet';
        document.head.appendChild(fontLink);

        var overlay = document.createElement('div');
        overlay.id = 'tet-greeting-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(ellipse at center, rgba(139,0,0,0.9) 0%, rgba(80,0,0,0.95) 100%);
            z-index: 2147483647;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            opacity: 0;
            transition: opacity 0.5s ease-in-out;
            pointer-events: none;
        `;

        var yearText = document.createElement('div');
        yearText.innerHTML = 'CLB TIN HỌC KHÓA 11 ';
        yearText.style.cssText = `
            font-size: 2rem;
            color: #FFD700;
            margin-bottom: 20px;
            text-shadow: 0 0 20px rgba(255,215,0,0.8);
        `;

        var greeting = document.createElement('div');
        greeting.id = 'tet-greeting';
        greeting.innerHTML = 'CHÚC MỪNG NĂM MỚI';
        greeting.style.cssText = `
            font-size: 4rem;
            font-weight: bold;
            color: #FFD700;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.5), 0 0 30px rgba(255,215,0,0.5);
            font-family: 'Playfair Display', 'Times New Roman', serif;
            margin-bottom: 15px;
            text-align: center;
            line-height: 1.3;
        `;

        var subGreeting = document.createElement('div');
        subGreeting.innerHTML = 'TẾT BÍNH TỴ 2026';
        subGreeting.style.cssText = `
            font-size: 2.5rem;
            color: #FF6B6B;
            font-family: 'Dancing Script', cursive;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            margin-bottom: 30px;
        `;

        var wishes = document.createElement('div');
        wishes.innerHTML = '🎊 An Khang Thịnh Vượng 🎊<br>🧧 Vạn Sự Như Ý 🧧';
        wishes.style.cssText = `
            font-size: 1.5rem;
            color: #FFFFFF;
            text-align: center;
            line-height: 2;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
        `;

        var decorTop = document.createElement('div');
        decorTop.innerHTML = '🌸 🏮 🏮 🌸';
        decorTop.style.cssText = `
            position: absolute;
            top: 50px;
            font-size: 2.5rem;
            animation: tetPulse 2s ease-in-out infinite;
        `;

        var decorBottom = document.createElement('div');
        decorBottom.innerHTML = '🧧 🎉 🌺 🎉 🧧';
        decorBottom.style.cssText = `
            position: absolute;
            bottom: 50px;
            font-size: 2.5rem;
            animation: tetPulse 2s ease-in-out infinite 0.5s;
        `;

        overlay.appendChild(decorTop);
        overlay.appendChild(yearText);
        overlay.appendChild(greeting);
        overlay.appendChild(subGreeting);
        overlay.appendChild(wishes);
        overlay.appendChild(decorBottom);
        document.body.appendChild(overlay);

        setTimeout(function() {
            overlay.style.opacity = '1';
            
            setTimeout(function() {
                overlay.style.opacity = '0';
                setTimeout(function() {
                    overlay.remove();
                }, 600);
            }, 4000);
        }, 300);

        sessionStorage.setItem('tet2026_intro_shown', 'true');
    }

    function createFloatingLiXi() {
        var lixi = document.createElement('div');
        lixi.classList.add('tet-lixi-float');
        var size = Math.random() * 30 + 40;
        lixi.innerHTML = '<img src="/static/images/tet2026/li-xi.svg" style="width:' + size + 'px;height:auto;">';
        var startX = Math.random() * window.innerWidth;
        var startY = window.innerHeight + 50;
        
        lixi.style.cssText = `
            position: fixed;
            left: ${startX}px;
            top: ${startY}px;
            z-index: 2147483644;
            pointer-events: none;
            animation: tetFloatUp ${Math.random() * 5 + 8}s linear forwards;
            filter: drop-shadow(0 3px 6px rgba(0,0,0,0.3));
        `;
        
        document.body.appendChild(lixi);
        
        setTimeout(function() {
            lixi.remove();
        }, 15000);
    }

    if (perfSettings.lixiEnabled) {
        setInterval(function() {
            if (Math.random() > 0.7) {
                createFloatingLiXi();
            }
        }, perfSettings.lixiInterval);
    }

    if (perfSettings.cursorTrailEnabled) {
        var cursorFlowers = [
            { emoji: '🌸', color: '#FFB6C1' },
            { emoji: '🌸', color: '#FF69B4' },
            { emoji: '✿', color: '#FFD700' },
            { emoji: '❀', color: '#FFA500' },
            { emoji: '🌺', color: '#FF6B6B' },
        ];
        
        var lastMouseX = 0, lastMouseY = 0;
        var mouseThrottle = 0;
        var flowerTrail = [];
        var maxFlowers = perfSettings.maxCursorFlowers; 
    
        document.addEventListener('mousemove', function(e) {
            var now = Date.now();
            if (now - mouseThrottle < 50) return; 
            mouseThrottle = now;
            var distance = Math.sqrt(Math.pow(e.clientX - lastMouseX, 2) + Math.pow(e.clientY - lastMouseY, 2));
            lastMouseX = e.clientX;
            lastMouseY = e.clientY;
            if (distance < 20) return;
            
            createCursorFlower(e.clientX, e.clientY);
        });
        
        function createCursorFlower(x, y) {
            var flower = document.createElement('div');
            var type = cursorFlowers[Math.floor(Math.random() * cursorFlowers.length)];
            var size = Math.random() * 12 + 14;
            var offsetX = (Math.random() - 0.5) * 20;
            var offsetY = (Math.random() - 0.5) * 20;
            var rotation = Math.random() * 360;
            
            flower.innerHTML = type.emoji;
            flower.className = 'tet-cursor-flower';
            flower.style.cssText = `
                position: fixed;
                left: ${x + offsetX}px;
                top: ${y + offsetY}px;
                font-size: ${size}px;
                color: ${type.color};
                pointer-events: none;
                z-index: 2147483647;
                opacity: 0.9;
                transform: rotate(${rotation}deg);
                transition: opacity 1s ease;
                will-change: opacity;
            `;
            document.body.appendChild(flower);
            setTimeout(function() {
                flower.style.opacity = '0';
            }, 100);
            
            setTimeout(function() {
                if (flower.parentNode) flower.remove();
            }, 1200);
        }
    } 
    var tetDate = new Date('2026-02-17T00:00:00+07:00');
    
    var countdownContainer = document.createElement('div');
    countdownContainer.id = 'tet-countdown';
    countdownContainer.innerHTML = `
        <div class="tet-countdown-inner">
            <div class="tet-countdown-title">🎊 Đếm ngược Tết Bính Tỵ 2026 🎊</div>
            <div class="tet-countdown-timer">
                <div class="tet-countdown-item">
                    <span class="tet-countdown-number" id="tet-days">00</span>
                    <span class="tet-countdown-label">Ngày</span>
                </div>
                <div class="tet-countdown-separator">:</div>
                <div class="tet-countdown-item">
                    <span class="tet-countdown-number" id="tet-hours">00</span>
                    <span class="tet-countdown-label">Giờ</span>
                </div>
                <div class="tet-countdown-separator">:</div>
                <div class="tet-countdown-item">
                    <span class="tet-countdown-number" id="tet-minutes">00</span>
                    <span class="tet-countdown-label">Phút</span>
                </div>
                <div class="tet-countdown-separator">:</div>
                <div class="tet-countdown-item">
                    <span class="tet-countdown-number" id="tet-seconds">00</span>
                    <span class="tet-countdown-label">Giây</span>
                </div>
            </div>
            <button id="tet-countdown-close" title="Đóng">✕</button>
        </div>
    `;
    document.body.appendChild(countdownContainer);

    function updateCountdown() {
        var now = new Date();
        var diff = tetDate - now;
        
        if (diff <= 0) {
            document.getElementById('tet-days').textContent = '🎉';
            document.getElementById('tet-hours').textContent = 'Chúc';
            document.getElementById('tet-minutes').textContent = 'Mừng';
            document.getElementById('tet-seconds').textContent = 'Tết!';
            return;
        }
        
        var days = Math.floor(diff / (1000 * 60 * 60 * 24));
        var hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((diff % (1000 * 60)) / 1000);
        
        document.getElementById('tet-days').textContent = days.toString().padStart(2, '0');
        document.getElementById('tet-hours').textContent = hours.toString().padStart(2, '0');
        document.getElementById('tet-minutes').textContent = minutes.toString().padStart(2, '0');
        document.getElementById('tet-seconds').textContent = seconds.toString().padStart(2, '0');
    }
    
    updateCountdown();
    setInterval(updateCountdown, 1000);
    
    document.getElementById('tet-countdown-close').addEventListener('click', function() {
        countdownContainer.style.display = 'none';
        sessionStorage.setItem('tet_countdown_closed', 'true');
    });
    
    if (sessionStorage.getItem('tet_countdown_closed') === 'true') {
        countdownContainer.style.display = 'none';
    }
    function getCSRFToken() {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === 'csrftoken=') {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var isLoggedIn = window.user && window.user.id;

    // ==================== NEW YEAR GREETING MODAL ====================
    if (isLoggedIn) {
        // Kiểm tra và hiển thị modal lời chúc năm mới
        function initNewYearGreetingModal() {
            fetch('/api/new-year-greeting/check/', {
                method: 'GET',
                headers: { 'X-CSRFToken': getCSRFToken() }
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.success) {
                    // Hiển thị nút gửi lời chúc hỗ trợ nếu có quyền
                    if (data.can_send_supporter_greeting) {
                        createSupporterGreetingButton();
                    }
                    
                    // Hiển thị nút test cho superadmin
                    if (data.is_superadmin) {
                        createTestGreetingButton();
                    }
                    
                    // Hiển thị modal nếu cần
                    if (data.should_show) {
                        loadAndShowNewYearGreeting();
                    }
                }
            })
            .catch(function(e) { console.error('Check new year greeting error:', e); });
        }
        
        // Tạo nút gửi lời chúc hỗ trợ
        function createSupporterGreetingButton() {
            var supporterBtn = document.createElement('div');
            supporterBtn.id = 'nyg-supporter-btn-container';
            supporterBtn.innerHTML = `
                <button id="nyg-supporter-btn" class="nyg-supporter-btn" title="Gửi lời chúc năm mới tới toàn thể học viên">
                    🎊 Gửi lời chúc năm mới tới toàn thể học viên
                </button>
            `;
            document.body.appendChild(supporterBtn);
            
            document.getElementById('nyg-supporter-btn').addEventListener('click', function() {
                showSupporterGreetingForm();
            });
        }
        
        // Tạo nút test cho superadmin
        function createTestGreetingButton() {
            var testBtn = document.createElement('div');
            testBtn.id = 'nyg-test-btn-container';
            testBtn.innerHTML = `
                <button id="nyg-test-btn" class="nyg-test-btn" title="Test modal lời chúc năm mới">
                    🧪 Test Modal
                </button>
            `;
            document.body.appendChild(testBtn);
            
            document.getElementById('nyg-test-btn').addEventListener('click', function() {
                loadAndShowNewYearGreeting();
            });
        }
        
        // Form gửi lời chúc hỗ trợ
        function showSupporterGreetingForm() {
            var formModal = document.createElement('div');
            formModal.id = 'nyg-supporter-form-modal';
            formModal.className = 'nyg-modal-overlay nyg-active';
            formModal.innerHTML = `
                <div class="nyg-supporter-form">
                    <button class="nyg-supporter-form-close">&times;</button>
                    <div class="nyg-form-header">
                        <h3>🎊 Gửi lời chúc năm mới</h3>
                    </div>
                    <div class="nyg-form-body">
                        <div class="nyg-form-group">
                            <label>Tên hiển thị:</label>
                            <input type="text" id="nyg-display-name" placeholder="Tên của bạn..." maxlength="100">
                        </div>
                        <div class="nyg-form-group">
                            <label>Lời chúc của bạn:</label>
                            <textarea id="nyg-message" placeholder="Nhập lời chúc năm mới của bạn..." maxlength="500" rows="5"></textarea>
                            <div class="nyg-char-count"><span id="nyg-char-current">0</span>/500</div>
                        </div>
                        <div id="nyg-form-status" class="nyg-form-status"></div>
                        <button id="nyg-submit-btn" class="nyg-submit-btn">🎉 Gửi lời chúc</button>
                    </div>
                </div>
            `;
            document.body.appendChild(formModal);
            
            // Close button
            formModal.querySelector('.nyg-supporter-form-close').addEventListener('click', function() {
                formModal.remove();
            });
            
            // Click outside to close
            formModal.addEventListener('click', function(e) {
                if (e.target === formModal) {
                    formModal.remove();
                }
            });
            
            // Character count
            var textarea = document.getElementById('nyg-message');
            textarea.addEventListener('input', function() {
                document.getElementById('nyg-char-current').textContent = this.value.length;
            });
            
            // Submit
            document.getElementById('nyg-submit-btn').addEventListener('click', function() {
                var displayName = document.getElementById('nyg-display-name').value.trim();
                var message = document.getElementById('nyg-message').value.trim();
                var status = document.getElementById('nyg-form-status');
                
                if (!message) {
                    status.textContent = '❌ Vui lòng nhập lời chúc!';
                    status.className = 'nyg-form-status error';
                    return;
                }
                
                status.textContent = 'Đang gửi...';
                status.className = 'nyg-form-status';
                
                fetch('/api/new-year-greeting/submit/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({
                        message: message,
                        display_name: displayName
                    })
                })
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    if (data.success) {
                        status.textContent = '✅ ' + data.message;
                        status.className = 'nyg-form-status success';
                        // Ẩn nút gửi sau khi gửi thành công
                        var btn = document.getElementById('nyg-supporter-btn-container');
                        if (btn) btn.remove();
                        setTimeout(function() {
                            formModal.remove();
                        }, 2000);
                    } else {
                        status.textContent = '❌ ' + data.error;
                        status.className = 'nyg-form-status error';
                    }
                })
                .catch(function(e) {
                    status.textContent = '❌ Lỗi kết nối!';
                    status.className = 'nyg-form-status error';
                });
            });
        }

        function loadAndShowNewYearGreeting() {
            fetch('/api/new-year-greeting/list/', {
                method: 'GET',
                headers: { 'X-CSRFToken': getCSRFToken() }
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.success) {
                    showNewYearGreetingModal(data.greetings, data.year);
                }
            })
            .catch(function(e) { console.error('Load new year greetings error:', e); });
        }

        function showNewYearGreetingModal(greetings, year) {
            // Tạo các trang
            var pages = [];
            
            // Trang 1: Giới thiệu CLB + Chúc mừng năm mới
            pages.push({
                type: 'intro',
                content: `
                    <div class="nyg-intro-page">
                        <div class="nyg-intro-decorations">
                            <span class="nyg-intro-deco top-left">🌸</span>
                            <span class="nyg-intro-deco top-right">🌸</span>
                        </div>
                        <div class="nyg-clb-logo">
                            <img src="/static/icons/icon.png" alt="CLB Tin Học">
                        </div>
                        <div class="nyg-intro-text">
                            <div class="nyg-clb-name">CLB TIN HỌC KHÓA 11 - KHOA TOÁN TIN</div>
                            <div class="nyg-clb-univ">Trường Đại Học Sư Phạm - Đại Học Đà Nẵng</div>
                        </div>
                        <div class="nyg-divider">
                            <span class="nyg-divider-line"></span>
                            <span class="nyg-divider-line"></span>
                        </div>
                        <div class="nyg-new-year-text">
                            <div class="nyg-happy">XIN GỬI LỜI</div>
                            <div class="nyg-year">CHÚC MỪNG NĂM MỚI ${year}</div>
                            <div class="nyg-year-subtitle">TẾT BÍNH TỴ</div>
                        </div>
                        <div class="nyg-intro-hint">
                            <span class="nyg-hint-icon">👉</span>
                            <span class="nyg-hint-text">Bấm tiếp theo để nhận những lời chúc nhé!</span>
                        </div>
                    </div>
                `
            });

            // Trang 2: Lời chúc của CLB
            if (greetings.clb_wishes && greetings.clb_wishes.length > 0) {
                greetings.clb_wishes.forEach(function(wish) {
                    if (wish) {
                        pages.push({
                            type: 'clb_wish',
                            content: `
                                <div class="nyg-wish-page nyg-clb-wish-page">
                                    <div class="nyg-wish-decorations">
                                        <span class="nyg-deco left">🌸</span>
                                        <span class="nyg-deco right">🌸</span>
                                    </div>
                                    ${wish.title ? '<div class="nyg-wish-title">' + wish.title + '</div>' : ''}
                                    <div class="nyg-wish-message">${wish.message.replace(/\n/g, '<br>')}</div>
                                    <div class="nyg-wish-author">— ${wish.author} —</div>
                                </div>
                            `
                        });
                    }
                });
            }

            // Trang: Lời chúc superadmin
            if (greetings.superadmin_wishes && greetings.superadmin_wishes.length > 0) {
                greetings.superadmin_wishes.forEach(function(wish) {
                    if (wish) {
                        pages.push({
                            type: 'superadmin_wish',
                            content: `
                                <div class="nyg-wish-page nyg-superadmin-wish-page">
                                    <div class="nyg-wish-decorations">
                                        <span class="nyg-deco left">✨</span>
                                        <span class="nyg-deco right">✨</span>
                                    </div>
                                    ${wish.title ? '<div class="nyg-wish-title">' + wish.title + '</div>' : ''}
                                    <div class="nyg-wish-message">${wish.message.replace(/\n/g, '<br>')}</div>
                                    <div class="nyg-wish-author">— BAN CHỦ NHIỆM CLBTH - ${wish.author} —</div>
                                </div>
                            `
                        });
                    }
                });
            }

            // Trang: Lời chúc hỗ trợ (6-8 người/trang)
            if (greetings.supporter_wishes && greetings.supporter_wishes.length > 0) {
                var supporterPages = [];
                var supportersPerPage = 6;
                for (var i = 0; i < greetings.supporter_wishes.length; i += supportersPerPage) {
                    supporterPages.push(greetings.supporter_wishes.slice(i, i + supportersPerPage));
                }
                
                supporterPages.forEach(function(pageWishes, pageIndex) {
                    var wishesHTML = pageWishes.map(function(wish) {
                        if (!wish) return '';
                        return `
                            <div class="nyg-supporter-card">
                                <div class="nyg-supporter-message">${wish.message.replace(/\n/g, '<br>')}</div>
                                <div class="nyg-supporter-author">Hỗ trợ — ${wish.author}</div>
                            </div>
                        `;
                    }).join('');
                    
                    pages.push({
                        type: 'supporter_wishes',
                        content: `
                            <div class="nyg-wish-page nyg-supporter-wish-page">
                                <div class="nyg-page-title">Lời chúc từ các anh chị hỗ trợ</div>
                                <div class="nyg-supporter-grid">${wishesHTML}</div>
                            </div>
                        `
                    });
                });
            }

            // Trang cuối: Lời kết thúc
            if (greetings.ending) {
                pages.push({
                    type: 'ending',
                    content: `
                        <div class="nyg-wish-page nyg-ending-page">
                            <div class="nyg-wish-decorations">
                                <span class="nyg-deco left">🎊</span>
                                <span class="nyg-deco right">🎊</span>
                            </div>
                            ${greetings.ending.title ? '<div class="nyg-wish-title">' + greetings.ending.title + '</div>' : ''}
                            <div class="nyg-wish-message">${greetings.ending.message.replace(/\n/g, '<br>')}</div>
                            <div class="nyg-ending-footer">
                                <div class="nyg-ending-clb">CLB Tin Học</div>
                                <div class="nyg-ending-meet">Hẹn gặp lại trong buổi sinh hoạt đầu năm!</div>
                            </div>
                        </div>
                    `
                });
            } else {
                // Trang kết thúc mặc định
                pages.push({
                    type: 'ending',
                    content: `
                        <div class="nyg-wish-page nyg-ending-page">
                            <div class="nyg-wish-decorations">
                                <span class="nyg-deco left">🎊</span>
                                <span class="nyg-deco right">🎊</span>
                            </div>
                            <div class="nyg-wish-title">Chúc Mừng Năm Mới ${year}!</div>
                            <div class="nyg-wish-message">
                                Chúc bạn một năm mới tràn đầy sức khỏe, hạnh phúc và thành công!<br><br>
                                Cảm ơn bạn đã đồng hành cùng CLB Tin Học!
                            </div>
                            <div class="nyg-ending-footer">
                                <div class="nyg-ending-clb">CLB TIN HỌC KHÓA 11</div>
                                <div class="nyg-ending-meet">Hẹn gặp lại trong buổi sinh hoạt đầu năm!</div>
                            </div>
                        </div>
                    `
                });
            }

            // Tạo modal
            var modal = document.createElement('div');
            modal.id = 'nyg-modal';
            modal.className = 'nyg-modal-overlay';
            
            var pagesHTML = pages.map(function(page, index) {
                return '<div class="nyg-page" data-page="' + index + '" style="' + (index === 0 ? '' : 'display:none;') + '">' + page.content + '</div>';
            }).join('');
            
            var dotsHTML = pages.map(function(page, index) {
                return '<span class="nyg-dot' + (index === 0 ? ' active' : '') + '" data-page="' + index + '"></span>';
            }).join('');

            modal.innerHTML = `
                <div class="nyg-modal-content">
                    <div class="nyg-fireworks-bg"></div>
                    <div class="nyg-pages-container">
                        ${pagesHTML}
                    </div>
                    <div class="nyg-navigation">
                        <button class="nyg-nav-btn nyg-prev" style="visibility:hidden;">❮ Quay lại</button>
                        <div class="nyg-dots">${dotsHTML}</div>
                        <button class="nyg-nav-btn nyg-next">Tiếp theo ❯</button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            // Navigation logic
            var currentPage = 0;
            var totalPages = pages.length;
            
            // Kiểm tra thiết bị yếu cho modal effects
            var modalIsMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
            var modalIsLowEnd = navigator.hardwareConcurrency <= 4 || modalIsMobile;
            var modalIsVeryLowEnd = navigator.hardwareConcurrency <= 2 || (modalIsMobile && window.innerWidth < 500);
            
            // Tạo hoa đào trong modal - tối ưu cho thiết bị yếu
            function createModalPetal() {
                // Bỏ qua nếu thiết bị quá yếu
                if (modalIsVeryLowEnd && Math.random() > 0.5) return;
                
                var petal = document.createElement('div');
                var petalTypes = [
                    { emoji: '🌸', color: '#FFB6C1' },
                    { emoji: '🌸', color: '#FF69B4' },
                    { emoji: '✿', color: '#FFD700' }, 
                    { emoji: '❀', color: '#FFA500' },
                ];
                var type = petalTypes[Math.floor(Math.random() * petalTypes.length)];
                var size = Math.random() * 25 + 20;
                var left = Math.random() * 100;
                var duration = modalIsLowEnd ? (Math.random() * 4 + 6) : (Math.random() * 6 + 8);
                
                petal.innerHTML = type.emoji;
                petal.style.cssText = 
                    'position: fixed;' +
                    'top: -50px;' +
                    'left: ' + left + 'vw;' +
                    'font-size: ' + size + 'px;' +
                    'opacity: 0.7;' +
                    'color: ' + type.color + ';' +
                    'animation: tetFall ' + duration + 's linear forwards;' +
                    'pointer-events: none;' +
                    'z-index: 2147483648;' +
                    'will-change: transform;';
                
                modal.appendChild(petal);
                setTimeout(function() { if (petal.parentNode) petal.remove(); }, duration * 1000);
            }
            
            // Tạo pháo hoa trong modal - tối ưu cho thiết bị yếu
            function createModalFirework() {
                // Bỏ qua hoàn toàn nếu thiết bị quá yếu
                if (modalIsVeryLowEnd) return;
                
                var x = Math.random() * window.innerWidth;
                var y = Math.random() * (window.innerHeight * 0.5);
                var fireworkColors = ['#FF0000', '#FFD700', '#FF69B4', '#00FF00', '#87CEEB', '#FF4500', '#FFFF00', '#FF1493'];
                
                var firework = document.createElement('div');
                firework.style.cssText = 
                    'position: fixed;' +
                    'left: ' + x + 'px;' +
                    'top: ' + y + 'px;' +
                    'width: 0;' +
                    'height: 0;' +
                    'pointer-events: none;' +
                    'z-index: 2147483648;';
                
                // Giảm số sparks cho thiết bị yếu
                var numSparks = modalIsLowEnd ? (15 + Math.floor(Math.random() * 10)) : (30 + Math.floor(Math.random() * 20));
                var baseSize = modalIsLowEnd ? 5 : 6;
                var baseDistance = modalIsLowEnd ? 60 : 80;
                var mainColor = fireworkColors[Math.floor(Math.random() * fireworkColors.length)];
                var secondColor = fireworkColors[Math.floor(Math.random() * fireworkColors.length)];
                
                for (var i = 0; i < numSparks; i++) {
                    var spark = document.createElement('div');
                    var angle = (i / numSparks) * 360 + (Math.random() * 15 - 7.5);
                    var color = Math.random() > 0.5 ? mainColor : secondColor;
                    var distance = baseDistance + Math.random() * baseDistance;
                    var size = baseSize + Math.random() * 3;
                    var duration = 1 + Math.random() * 0.8;
                    
                    // Bỏ box-shadow cho thiết bị yếu để giảm tải GPU
                    var boxShadow = modalIsLowEnd ? '' : ('box-shadow: 0 0 ' + (size * 2) + 'px ' + color + ';');
                    
                    spark.style.cssText = 
                        'position: absolute;' +
                        'width: ' + size + 'px;' +
                        'height: ' + size + 'px;' +
                        'background: ' + color + ';' +
                        'border-radius: 50%;' +
                        boxShadow +
                        'animation: tetSparkle ' + duration + 's ease-out forwards;' +
                        'transform: rotate(' + angle + 'deg) translateY(-' + distance + 'px);' +
                        '--spark-distance: ' + distance + 'px;' +
                        '--spark-angle: ' + angle + 'deg;' +
                        'will-change: transform, opacity;';
                    
                    firework.appendChild(spark);
                }
                
                modal.appendChild(firework);
                setTimeout(function() { if (firework.parentNode) firework.remove(); }, 2500);
            }
            
            function showPage(index) {
                if (index < 0 || index >= totalPages) return;
                
                // Hide current page
                var currentEl = modal.querySelector('.nyg-page[data-page="' + currentPage + '"]');
                if (currentEl) currentEl.style.display = 'none';
                
                // Show new page
                var newEl = modal.querySelector('.nyg-page[data-page="' + index + '"]');
                if (newEl) {
                    newEl.style.display = 'flex';
                    newEl.style.animation = 'nygFadeIn 0.5s ease-out';
                }
                
                // Tạo hiệu ứng cho các trang đặc biệt
                var pageType = pages[index] ? pages[index].type : '';
                
                // Lời chúc CLB: pháo hoa + hoa đào (giảm số lượng và giãn thời gian cho thiết bị yếu)
                if (pageType === 'clb_wish') {
                    if (modalIsVeryLowEnd) {
                        // Thiết bị rất yếu: chỉ 2 hoa đào, không pháo hoa
                        setTimeout(function() { createModalPetal(); }, 200);
                        setTimeout(function() { createModalPetal(); }, 600);
                    } else if (modalIsLowEnd) {
                        // Thiết bị yếu/mobile: 2 pháo hoa, 3 hoa đào, giãn thời gian
                        setTimeout(function() { createModalFirework(); }, 200);
                        setTimeout(function() { createModalFirework(); }, 800);
                        setTimeout(function() { createModalPetal(); }, 100);
                        setTimeout(function() { createModalPetal(); }, 500);
                        setTimeout(function() { createModalPetal(); }, 900);
                    } else {
                        // Thiết bị mạnh: đầy đủ hiệu ứng
                        setTimeout(function() { createModalFirework(); }, 100);
                        setTimeout(function() { createModalFirework(); }, 400);
                        setTimeout(function() { createModalFirework(); }, 700);
                        setTimeout(function() { createModalPetal(); }, 0);
                        setTimeout(function() { createModalPetal(); }, 200);
                        setTimeout(function() { createModalPetal(); }, 400);
                        setTimeout(function() { createModalPetal(); }, 600);
                        setTimeout(function() { createModalPetal(); }, 800);
                    }
                }
                
                // Lời chúc Superadmin: hoa đào (giảm số lượng cho thiết bị yếu)
                if (pageType === 'superadmin_wish') {
                    if (modalIsVeryLowEnd) {
                        // Thiết bị rất yếu: chỉ 2 hoa đào
                        setTimeout(function() { createModalPetal(); }, 200);
                        setTimeout(function() { createModalPetal(); }, 600);
                    } else if (modalIsLowEnd) {
                        // Thiết bị yếu/mobile: 4 hoa đào, giãn thời gian
                        setTimeout(function() { createModalPetal(); }, 0);
                        setTimeout(function() { createModalPetal(); }, 350);
                        setTimeout(function() { createModalPetal(); }, 700);
                        setTimeout(function() { createModalPetal(); }, 1050);
                    } else {
                        // Thiết bị mạnh: đầy đủ 8 hoa đào
                        setTimeout(function() { createModalPetal(); }, 0);
                        setTimeout(function() { createModalPetal(); }, 150);
                        setTimeout(function() { createModalPetal(); }, 300);
                        setTimeout(function() { createModalPetal(); }, 450);
                        setTimeout(function() { createModalPetal(); }, 600);
                        setTimeout(function() { createModalPetal(); }, 750);
                        setTimeout(function() { createModalPetal(); }, 900);
                        setTimeout(function() { createModalPetal(); }, 1050);
                    }
                }
                
                // Update dots
                modal.querySelectorAll('.nyg-dot').forEach(function(dot) {
                    dot.classList.remove('active');
                });
                var activeDot = modal.querySelector('.nyg-dot[data-page="' + index + '"]');
                if (activeDot) activeDot.classList.add('active');
                
                currentPage = index;
                
                // Update buttons
                var prevBtn = modal.querySelector('.nyg-prev');
                var nextBtn = modal.querySelector('.nyg-next');
                
                prevBtn.style.visibility = currentPage === 0 ? 'hidden' : 'visible';
                
                if (currentPage === totalPages - 1) {
                    nextBtn.textContent = '✓ Hoàn thành';
                    nextBtn.classList.add('nyg-finish');
                } else {
                    nextBtn.textContent = 'Tiếp theo ❯';
                    nextBtn.classList.remove('nyg-finish');
                }
            }
            
            modal.querySelector('.nyg-prev').addEventListener('click', function() {
                showPage(currentPage - 1);
            });
            
            modal.querySelector('.nyg-next').addEventListener('click', function() {
                if (currentPage === totalPages - 1) {
                    // Đánh dấu đã xem và đóng
                    fetch('/api/new-year-greeting/seen/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCSRFToken()
                        },
                        body: JSON.stringify({})
                    })
                    .then(function() {
                        modal.classList.add('nyg-closing');
                        setTimeout(function() {
                            modal.remove();
                        }, 500);
                    })
                    .catch(function() {
                        modal.remove();
                    });
                } else {
                    showPage(currentPage + 1);
                }
            });
            
            // Click on dots
            modal.querySelectorAll('.nyg-dot').forEach(function(dot) {
                dot.addEventListener('click', function() {
                    var pageIndex = parseInt(this.getAttribute('data-page'));
                    showPage(pageIndex);
                });
            });
            
            // Show modal with animation
            setTimeout(function() {
                modal.classList.add('nyg-active');
            }, 100);
        }
        
        // Khởi động modal sau 1 giây
        setTimeout(initNewYearGreetingModal, 1000);
    }
    // ==================== END NEW YEAR GREETING MODAL ====================

    if (isLoggedIn) {
        var wishContainer = document.createElement('div');
        wishContainer.id = 'tet-wish-container';
        wishContainer.innerHTML = `
            <button id="tet-send-wish-btn" class="tet-wish-btn" title="Gửi lời chúc">
                ✉️ Gửi lời chúc
                <span id="tet-remaining-badge" class="tet-remaining-badge">7</span>
            </button>
            <button id="tet-mailbox-btn" class="tet-wish-btn" title="Hòm thư">
                📬 Hòm thư
                <span id="tet-unread-badge" class="tet-unread-badge">0</span>
            </button>
        `;
        document.body.appendChild(wishContainer);

    var sendWishModal = document.createElement('div');
    sendWishModal.id = 'tet-send-wish-modal';
    sendWishModal.className = 'tet-modal-overlay';
    sendWishModal.innerHTML = `
        <div class="tet-modal">
            <div class="tet-modal-header">
                <h3>✉️ Gửi lời chúc Tết</h3>
                <button class="tet-modal-close" data-modal="send">&times;</button>
            </div>
            <div class="tet-modal-body">
                <div class="tet-form-group">
                    <label>Người nhận:</label>
                    <input type="text" id="tet-receiver-search" placeholder="Nhập tên người dùng..." autocomplete="off">
                    <div id="tet-receiver-dropdown" class="tet-dropdown"></div>
                    <input type="hidden" id="tet-receiver-id">
                    <div id="tet-selected-receiver" class="tet-selected-receiver"></div>
                </div>
                <div class="tet-form-group" id="tet-broadcast-group" style="display:none;">
                    <label class="tet-checkbox-label">
                        <input type="checkbox" id="tet-broadcast-checkbox">
                        🌟 Gửi cho tất cả mọi người
                    </label>
                </div>
                <div class="tet-form-group">
                    <label>Lời chúc (tối đa 500 ký tự):</label>
                    <textarea id="tet-wish-message" placeholder="Viết lời chúc của bạn..." maxlength="500" rows="4"></textarea>
                    <div class="tet-char-count"><span id="tet-char-count">0</span>/500</div>
                </div>
                <div id="tet-send-status" class="tet-status"></div>
                <button id="tet-submit-wish" class="tet-submit-btn">Gửi lời chúc</button>
            </div>
        </div>
    `;
    document.body.appendChild(sendWishModal);

    var mailboxModal = document.createElement('div');
    mailboxModal.id = 'tet-mailbox-modal';
    mailboxModal.className = 'tet-modal-overlay';
    mailboxModal.innerHTML = `
        <div class="tet-modal tet-mailbox-modal">
            <div class="tet-modal-header">
                <h3>📬 Hòm thư lời chúc</h3>
                <button class="tet-modal-close" data-modal="mailbox">&times;</button>
            </div>
            <div class="tet-modal-body">
                <div id="tet-envelopes-container" class="tet-envelopes-container"></div>
                <div id="tet-no-wishes" class="tet-no-wishes" style="display:none;">
                    Bạn chưa nhận được lời chúc nào 😢
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(mailboxModal);

    var viewWishModal = document.createElement('div');
    viewWishModal.id = 'tet-view-wish-modal';
    viewWishModal.className = 'tet-view-wish-overlay';
    viewWishModal.innerHTML = `
        <button class="tet-view-wish-close">&times;</button>
        <div class="tet-envelope-animation" id="tet-envelope-animation">
            <div class="tet-envelope-wrapper">
                <div class="tet-envelope-outer">
                    <div class="tet-envelope-flap"></div>
                    <div class="tet-envelope-body">
                        <div class="tet-letter">
                            <div class="tet-letter-content">
                                <div class="tet-letter-sender" id="tet-letter-sender"></div>
                                <div class="tet-letter-divider">🌸 ❀ 🌸</div>
                                <div class="tet-letter-message" id="tet-letter-message"></div>
                                <div class="tet-letter-date" id="tet-letter-date"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(viewWishModal);

    var setLimitModal = document.createElement('div');
    setLimitModal.id = 'tet-set-limit-modal';
    setLimitModal.className = 'tet-modal-overlay';
    setLimitModal.innerHTML = `
        <div class="tet-modal tet-set-limit-modal">
            <div class="tet-modal-header">
                <h3>⚙️ Đặt giới hạn gửi</h3>
                <button class="tet-modal-close" data-modal="set-limit">&times;</button>
            </div>
            <div class="tet-modal-body">
                <div class="tet-limit-user-info">
                    <span>Người dùng: </span>
                    <strong id="tet-limit-username">---</strong>
                </div>
                <div class="tet-limit-current">
                    <span>Đã gửi: </span><span id="tet-limit-sent">0</span>
                    <span> / Giới hạn hiện tại: </span><span id="tet-limit-current">7</span>
                </div>
                <div class="tet-form-group">
                    <label>Giới hạn mới (0-100):</label>
                    <input type="number" id="tet-limit-input" min="0" max="100" value="7">
                </div>
                <input type="hidden" id="tet-limit-user-id">
                <div id="tet-limit-status" class="tet-status"></div>
                <button id="tet-submit-limit" class="tet-submit-btn">💾 Lưu giới hạn</button>
            </div>
        </div>
    `;
    document.body.appendChild(setLimitModal);

    var wishStats = { sent_count: 0, is_superadmin: false, unread_count: 0, max_send: 7 };
    var wishList = [];
    var searchTimeout = null;

    function loadWishStats() {
        fetch('/api/tet-wishes/stats/', {
            method: 'GET',
            headers: { 'X-CSRFToken': getCSRFToken() }
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) {
                wishStats = data;
                updateStatsDisplay();
                updateUnreadBadge(data.unread_count);

                if (data.is_superadmin) {
                    document.getElementById('tet-broadcast-group').style.display = 'block';
                }
            }
        })
        .catch(function(e) { console.error('Load stats error:', e); });
    }
    
    function updateStatsDisplay() {
        var badge = document.getElementById('tet-remaining-badge');
        if (badge) {
            var remaining = wishStats.is_superadmin ? '∞' : (wishStats.max_send - wishStats.sent_count);
            badge.textContent = remaining;
        }
    }
    
    function updateUnreadBadge(count) {
        var badge = document.getElementById('tet-unread-badge');
        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.classList.add('show');
        } else {
            badge.classList.remove('show');
        }
    }

    document.getElementById('tet-receiver-search').addEventListener('input', function(e) {
        var query = e.target.value.trim();
        clearTimeout(searchTimeout);
        
        if (query.length < 2) {
            document.getElementById('tet-receiver-dropdown').innerHTML = '';
            document.getElementById('tet-receiver-dropdown').style.display = 'none';
            return;
        }
        
        searchTimeout = setTimeout(function() {
            fetch('/api/tet-wishes/search-users/?q=' + encodeURIComponent(query), {
                method: 'GET',
                headers: { 'X-CSRFToken': getCSRFToken() }
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var dropdown = document.getElementById('tet-receiver-dropdown');
                if (data.users && data.users.length > 0) {
                    dropdown.innerHTML = data.users.map(function(user) {
                        var disabled = !user.can_send ? ' tet-user-disabled' : '';
                        var note = !user.can_send ? ' (Đã gửi)' : '';
                        var setLimitBtn = wishStats.is_superadmin ? 
                            '<span class="tet-set-limit-btn" data-id="' + user.id + '" data-name="' + user.username + '" title="Đặt giới hạn">⚙️</span>' : '';
                        return '<div class="tet-dropdown-item' + disabled + '" data-id="' + user.id + '" data-name="' + user.username + '">' +
                            '<span class="tet-user-name">' + user.display_name + ' (@' + user.username + ')' + note + '</span>' + setLimitBtn + '</div>';
                    }).join('');
                    dropdown.style.display = 'block';

                    dropdown.querySelectorAll('.tet-dropdown-item:not(.tet-user-disabled) .tet-user-name').forEach(function(item) {
                        item.addEventListener('click', function() {
                            var parent = this.closest('.tet-dropdown-item');
                            selectReceiver(parent.dataset.id, parent.dataset.name);
                        });
                    });
                    dropdown.querySelectorAll('.tet-set-limit-btn').forEach(function(btn) {
                        btn.addEventListener('click', function(e) {
                            e.stopPropagation();
                            openSetLimitModal(this.dataset.id, this.dataset.name);
                        });
                    });
                } else {
                    dropdown.innerHTML = '<div class="tet-dropdown-item tet-no-result">Không tìm thấy</div>';
                    dropdown.style.display = 'block';
                }
            });
        }, 300);
    });
    
    function selectReceiver(id, name) {
        document.getElementById('tet-receiver-id').value = id;
        document.getElementById('tet-receiver-search').value = '';
        document.getElementById('tet-receiver-search').style.display = 'none';
        document.getElementById('tet-receiver-dropdown').style.display = 'none';
        
        var selectedDiv = document.getElementById('tet-selected-receiver');
        selectedDiv.innerHTML = '👤 ' + name + ' <span class="tet-remove-receiver" onclick="window.clearSelectedReceiver()">✕</span>';
        selectedDiv.classList.add('show');
    }
    
    window.clearSelectedReceiver = function() {
        document.getElementById('tet-receiver-id').value = '';
        document.getElementById('tet-receiver-search').style.display = 'block';
        document.getElementById('tet-selected-receiver').classList.remove('show');
    };

    function openSetLimitModal(userId, username) {
        document.getElementById('tet-limit-user-id').value = userId;
        document.getElementById('tet-limit-username').textContent = username;
        document.getElementById('tet-limit-status').innerHTML = '';
        document.getElementById('tet-limit-status').className = 'tet-status';

        fetch('/api/tet-wishes/get-limit/?user_id=' + userId, {
            method: 'GET',
            headers: { 'X-CSRFToken': getCSRFToken() }
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) {
                document.getElementById('tet-limit-sent').textContent = data.sent_count;
                document.getElementById('tet-limit-current').textContent = data.max_wishes;
                document.getElementById('tet-limit-input').value = data.max_wishes;
            }
        });
        
        document.getElementById('tet-set-limit-modal').classList.add('active');
    }

    document.getElementById('tet-submit-limit').addEventListener('click', function() {
        var userId = document.getElementById('tet-limit-user-id').value;
        var maxWishes = document.getElementById('tet-limit-input').value;
        var statusEl = document.getElementById('tet-limit-status');
        
        if (!userId || maxWishes === '') {
            statusEl.innerHTML = '❌ Thiếu thông tin';
            statusEl.className = 'tet-status tet-status-error';
            return;
        }
        
        statusEl.innerHTML = '⏳ Đang lưu...';
        statusEl.className = 'tet-status';
        
        fetch('/api/tet-wishes/set-limit/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                user_id: parseInt(userId),
                max_wishes: parseInt(maxWishes)
            })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) {
                statusEl.innerHTML = '✅ ' + data.message;
                statusEl.className = 'tet-status tet-status-success';
                document.getElementById('tet-limit-current').textContent = maxWishes;
            } else {
                statusEl.innerHTML = '❌ ' + data.error;
                statusEl.className = 'tet-status tet-status-error';
            }
        })
        .catch(function(e) {
            statusEl.innerHTML = '❌ Lỗi kết nối';
            statusEl.className = 'tet-status tet-status-error';
        });
    });
    document.querySelector('#tet-set-limit-modal .tet-modal-close').addEventListener('click', function() {
        document.getElementById('tet-set-limit-modal').classList.remove('active');
    });
    document.getElementById('tet-wish-message').addEventListener('input', function(e) {
        document.getElementById('tet-char-count').textContent = e.target.value.length;
    });
    document.getElementById('tet-submit-wish').addEventListener('click', function() {
        var receiverId = document.getElementById('tet-receiver-id').value;
        var message = document.getElementById('tet-wish-message').value.trim();
        var isBroadcast = document.getElementById('tet-broadcast-checkbox').checked;
        var statusEl = document.getElementById('tet-send-status');
        
        if (!isBroadcast && !receiverId) {
            statusEl.innerHTML = '❌ Vui lòng chọn người nhận';
            statusEl.className = 'tet-status tet-status-error';
            return;
        }
        
        if (!message) {
            statusEl.innerHTML = '❌ Vui lòng nhập lời chúc';
            statusEl.className = 'tet-status tet-status-error';
            return;
        }
        
        statusEl.innerHTML = '⏳ Đang gửi...';
        statusEl.className = 'tet-status';
        
        fetch('/api/tet-wishes/send/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                receiver_id: receiverId,
                message: message,
                is_broadcast: isBroadcast
            })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) {
                statusEl.innerHTML = '✅ ' + data.message;
                statusEl.className = 'tet-status tet-status-success';

                document.getElementById('tet-wish-message').value = '';
                document.getElementById('tet-char-count').textContent = '0';
                window.clearSelectedReceiver();
                document.getElementById('tet-broadcast-checkbox').checked = false;
                loadWishStats();
                setTimeout(function() {
                    sendWishModal.classList.remove('active');
                    statusEl.innerHTML = '';
                }, 2000);
            } else {
                statusEl.innerHTML = '❌ ' + data.error;
                statusEl.className = 'tet-status tet-status-error';
            }
        })
        .catch(function(e) {
            statusEl.innerHTML = '❌ Lỗi kết nối';
            statusEl.className = 'tet-status tet-status-error';
        });
    });
    function loadWishes() {
        fetch('/api/tet-wishes/list/', {
            method: 'GET',
            headers: { 'X-CSRFToken': getCSRFToken() }
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) {
                wishList = data.wishes;
                renderEnvelopes();
                updateUnreadBadge(data.unread_count);
            }
        });
    }
    
    function renderEnvelopes() {
        var container = document.getElementById('tet-envelopes-container');
        var noWishes = document.getElementById('tet-no-wishes');
        
        if (wishList.length === 0) {
            container.innerHTML = '';
            noWishes.style.display = 'block';
            return;
        }
        
        noWishes.style.display = 'none';
        container.innerHTML = '';
        
        wishList.forEach(function(wish, index) {
            var envelope = document.createElement('div');
            var isSuper = wish.is_from_superadmin;
            var sizeClass = isSuper ? 'tet-envelope-super' : '';
            var unreadClass = !wish.is_read ? 'tet-envelope-unread' : 'tet-envelope-read';
            
            envelope.className = 'tet-envelope ' + sizeClass + ' ' + unreadClass;
            envelope.dataset.index = index;
            envelope.innerHTML = isSuper ? 
                '<img src="/static/images/tet2026/li-xi.svg" class="tet-lixi-img" alt="Lì xì"><span class="tet-super-badge">⭐ Từ CLBTH</span>' : 
                '<img src="/static/images/tet2026/li-xi.svg" class="tet-lixi-img" alt="Lì xì">';
            
            envelope.addEventListener('click', function() {
                openEnvelope(index);
            });
            
            container.appendChild(envelope);
            
            setTimeout(function() {
                envelope.classList.add('tet-envelope-visible');
            }, index * 100);
        });
    }
    
    function openEnvelope(index) {
        var wish = wishList[index];
        if (!wish) return;

        document.getElementById('tet-letter-sender').textContent = wish.sender_name;
        document.getElementById('tet-letter-message').textContent = wish.message;
        document.getElementById('tet-letter-date').textContent = '📅 ' + wish.created_at;
 
        if (wish.is_from_superadmin) {
            for (var i = 0; i < 5; i++) {
                setTimeout(function() {
                    createFirework();
                    createBottomFirework();
                }, i * 300);
            }
        }

        mailboxModal.classList.remove('active');
        viewWishModal.style.display = 'flex';
        setTimeout(function() {
            viewWishModal.classList.add('tet-view-wish-active');
            document.getElementById('tet-envelope-animation').classList.add('tet-envelope-opened');
        }, 50);

        if (!wish.is_read) {
            fetch('/api/tet-wishes/mark-read/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({ wish_id: wish.id })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.success) {
                    wishList[index].is_read = true;
                    loadWishStats();
                }
            });
        }
    }
    document.getElementById('tet-send-wish-btn').addEventListener('click', function() {
        sendWishModal.classList.add('active');
    });
    
    document.getElementById('tet-mailbox-btn').addEventListener('click', function() {
        loadWishes();
        mailboxModal.classList.add('active');
    });
    document.querySelectorAll('.tet-modal-close').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var modalType = this.dataset.modal;
            if (modalType === 'send') sendWishModal.classList.remove('active');
            if (modalType === 'mailbox') mailboxModal.classList.remove('active');
        });
    });
    
    document.querySelector('.tet-view-wish-close').addEventListener('click', function() {
        viewWishModal.classList.remove('tet-view-wish-active');
        document.getElementById('tet-envelope-animation').classList.remove('tet-envelope-opened');
        setTimeout(function() {
            viewWishModal.style.display = 'none';
            loadWishes();
            mailboxModal.classList.add('active');
        }, 500);
    });
    [sendWishModal, mailboxModal].forEach(function(modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });
    document.addEventListener('click', function(e) {
        if (!e.target.closest('#tet-receiver-search') && !e.target.closest('#tet-receiver-dropdown')) {
            document.getElementById('tet-receiver-dropdown').style.display = 'none';
        }
    });

    setTimeout(loadWishStats, 500);
    
    } // End of isLoggedIn check
});

var tetStyles = document.createElement('style');
tetStyles.textContent = `
    @keyframes tetFall {
        0% { top: -50px; transform: translateX(0) rotate(0deg); }
        25% { transform: translateX(30px) rotate(90deg); }
        50% { transform: translateX(-20px) rotate(180deg); }
        75% { transform: translateX(25px) rotate(270deg); }
        100% { top: 110vh; transform: translateX(-10px) rotate(360deg); }
    }
    
    @keyframes tetSway {
        0%, 100% { transform: translateX(0); }
        50% { transform: translateX(40px); }
    }
    
    @keyframes tetSwing {
        0%, 100% { transform: rotate(-10deg); }
        50% { transform: rotate(10deg); }
    }
    
    @keyframes tetSparkle {
        0% { opacity: 1; transform: rotate(var(--angle, 0deg)) translateY(0) scale(1); }
        100% { opacity: 0; transform: rotate(var(--angle, 0deg)) translateY(-80px) scale(0); }
    }
    
    @keyframes tetGlow {
        0% { opacity: 1; transform: scale(1); }
        100% { opacity: 0; transform: scale(3); }
    }
    
    @keyframes tetBottomSparkle {
        0% { 
            opacity: 1; 
            transform: rotate(var(--spark-angle)) translateY(0) scale(1); 
        }
        70% {
            opacity: 0.8;
            transform: rotate(var(--spark-angle)) translateY(calc(var(--spark-distance) * -0.8)) scale(0.8);
        }
        100% { 
            opacity: 0; 
            transform: rotate(var(--spark-angle)) translateY(calc(var(--spark-distance) * -1)) scale(0.3); 
        }
    }
    
    @keyframes tetBottomSparkleWillow {
        0% { 
            opacity: 1; 
            transform: rotate(var(--spark-angle)) translateY(0) scale(1); 
        }
        40% {
            opacity: 0.9;
            transform: rotate(var(--spark-angle)) translateY(calc(var(--spark-distance) * -0.6)) scale(0.9);
        }
        100% { 
            opacity: 0; 
            transform: rotate(var(--spark-angle)) translateY(calc(var(--spark-distance) * -0.3 + 80px)) scale(0.2); 
        }
    }
    
    @keyframes tetSparkleWillow {
        0% { 
            opacity: 1; 
            transform: rotate(var(--spark-angle)) translateY(0) scale(1); 
        }
        40% {
            opacity: 0.9;
            transform: rotate(var(--spark-angle)) translateY(calc(var(--spark-distance) * -0.7)) scale(0.85);
        }
        100% { 
            opacity: 0; 
            transform: rotate(var(--spark-angle)) translateY(calc(var(--spark-distance) * -0.2 + 100px)) scale(0.15); 
        }
    }
    
    @keyframes tetTwinkle {
        0% { 
            opacity: 0;
            transform: rotate(var(--angle, 0deg)) translateY(var(--distance, -30px)) scale(0.5);
        }
        20% { 
            opacity: 1;
            transform: rotate(var(--angle, 0deg)) translateY(var(--distance, -30px)) scale(1.2);
        }
        40% {
            opacity: 0.7;
            transform: rotate(var(--angle, 0deg)) translateY(var(--distance, -30px)) scale(0.8);
        }
        60% {
            opacity: 1;
            transform: rotate(var(--angle, 0deg)) translateY(var(--distance, -30px)) scale(1);
        }
        80% {
            opacity: 0.5;
            transform: rotate(var(--angle, 0deg)) translateY(var(--distance, -30px)) scale(0.6);
        }
        100% { 
            opacity: 0;
            transform: rotate(var(--angle, 0deg)) translateY(var(--distance, -30px)) scale(0);
        }
    }
    
    @keyframes tetExplosionRing {
        0% { 
            transform: scale(1); 
            opacity: 1; 
        }
        100% { 
            transform: scale(8); 
            opacity: 0; 
        }
    }
    
    @keyframes tetPulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    @keyframes tetFloatUp {
        0% { 
            transform: translateY(0) rotate(0deg) scale(1); 
            opacity: 1; 
        }
        50% {
            transform: translateY(-50vh) rotate(15deg) scale(1.1);
            opacity: 0.8;
        }
        100% { 
            transform: translateY(-120vh) rotate(-10deg) scale(0.8); 
            opacity: 0; 
        }
    }
    
    @keyframes tetSparkleOut {
        0% { transform: scale(1) rotate(0deg); opacity: 1; }
        100% { transform: scale(0) rotate(180deg); opacity: 0; }
    }
    
    @keyframes tetCursorFlower {
        0% { 
            transform: scale(0.5) rotate(0deg) translateY(0); 
            opacity: 1; 
        }
        30% {
            transform: scale(1.2) rotate(45deg) translateY(-10px);
            opacity: 0.9;
        }
        100% { 
            transform: scale(0.3) rotate(180deg) translateY(-60px); 
            opacity: 0; 
        }
    }
    
    @keyframes tetShine {
        0%, 100% { filter: brightness(1) drop-shadow(0 0 5px rgba(255,215,0,0.5)); }
        50% { filter: brightness(1.3) drop-shadow(0 0 15px rgba(255,215,0,0.8)); }
    }
    
    .tet-corner-decor {
        position: fixed;
        z-index: 9998;
        pointer-events: none;
        animation: tetShine 3s ease-in-out infinite;
    }
    
    .tet-corner-tl {
        top: 60px;
        left: 60px;
    }
    
    .tet-corner-tr {
        top: 60px;
        right: 60px;
    }
    
    /* Countdown Styles */
    #tet-countdown {
        position: fixed;
        bottom: 20px;
        left: 20px;
        z-index: 10000;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .tet-countdown-inner {
        background: linear-gradient(135deg, #DC143C 0%, #8B0000 100%);
        border: 2px solid #FFD700;
        border-radius: 12px;
        padding: 8px 15px;
        box-shadow: 0 4px 15px rgba(139,0,0,0.4);
        position: relative;
    }
    
    .tet-countdown-title {
        color: #FFD700;
        font-size: 11px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    
    .tet-countdown-timer {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 5px;
    }
    
    .tet-countdown-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 38px;
    }
    
    .tet-countdown-number {
        color: #FFFFFF;
        font-size: 20px;
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        line-height: 1;
    }
    
    .tet-countdown-label {
        color: #FFD700;
        font-size: 10px;
        text-transform: uppercase;
        margin-top: 2px;
    }
    
    .tet-countdown-separator {
        color: #FFD700;
        font-size: 24px;
        font-weight: bold;
        animation: tetPulse 1s ease-in-out infinite;
    }
    
    #tet-countdown-close {
        position: absolute;
        top: -8px;
        right: -8px;
        width: 20px;
        height: 20px;
        min-width: 20px;
        min-height: 20px;
        max-width: 20px;
        max-height: 20px;
        border-radius: 50%;
        background: #8B0000;
        color: #FFFFFF;
        border: 1px solid #FFD700;
        cursor: pointer;
        font-size: 12px;
        font-weight: normal;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
        line-height: 1;
        padding: 0;
        box-sizing: border-box;
        aspect-ratio: 1 / 1;
    }
    
    #tet-countdown-close:hover {
        background: #DC143C;
        transform: scale(1.1);
    }
    
    /* Wish System Styles */
    #tet-wish-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 10001;
        display: flex;
        flex-direction: row;
        gap: 8px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .tet-wish-btn {
        padding: 10px 16px;
        border: 2px solid #FFD700;
        border-radius: 20px;
        background: linear-gradient(135deg, #DC143C 0%, #8B0000 100%);
        color: #FFD700;
        font-size: 13px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(139,0,0,0.4), 0 0 10px rgba(255,215,0,0.2);
        display: flex;
        align-items: center;
        gap: 6px;
        white-space: nowrap;
    }
    
    .tet-wish-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(139,0,0,0.5), 0 0 15px rgba(255,215,0,0.4);
        background: linear-gradient(135deg, #FF1A1A 0%, #B22222 100%);
    }
    
    .tet-remaining-badge {
        background: rgba(255,255,255,0.9);
        color: #8B0000;
        font-size: 11px;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 8px;
        min-width: 16px;
        text-align: center;
        display: inline-block;
    }
    
    .tet-unread-badge {
        background: #FFD700;
        color: #8B0000;
        font-size: 10px;
        font-weight: bold;
        padding: 2px 5px;
        border-radius: 8px;
        min-width: 16px;
        text-align: center;
        display: none;
    }
    
    .tet-unread-badge.show {
        display: inline-block;
        animation: badgePulse 1.5s ease-in-out infinite;
    }
    
    @keyframes badgePulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.15); }
    }
    
    /* Modal Styles */
    .tet-modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.7);
        z-index: 10002;
        display: flex;
        justify-content: center;
        align-items: center;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
    }
    
    .tet-modal-overlay.active {
        opacity: 1;
        visibility: visible;
    }
    
    .tet-modal {
        background: linear-gradient(135deg, #FFF8DC 0%, #FFFACD 100%);
        border: 4px solid #DC143C;
        border-radius: 20px;
        width: 90%;
        max-width: 420px;
        max-height: 85vh;
        overflow: hidden;
        transform: scale(0.8) translateY(30px);
        transition: transform 0.3s ease;
        box-shadow: 0 10px 40px rgba(139,0,0,0.5), 0 0 30px rgba(255,215,0,0.2);
    }
    
    .tet-mailbox-modal {
        max-width: 95vw;
        width: 95vw;
        max-height: 90vh;
        height: 85vh;
    }
    
    .tet-mailbox-modal .tet-modal-body {
        height: calc(100% - 60px);
        max-height: none;
        overflow-y: auto;
    }
    
    .tet-modal-overlay.active .tet-modal {
        transform: scale(1) translateY(0);
    }
    
    .tet-modal-header {
        background: linear-gradient(135deg, #DC143C 0%, #8B0000 100%);
        color: #FFD700;
        padding: 15px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .tet-modal-header h3 {
        margin: 0;
        font-size: 18px;
        font-weight: bold;
    }
    
    .tet-modal-close {
        width: 28px;
        height: 28px;
        border: 2px solid #FFD700;
        border-radius: 50%;
        background: transparent;
        color: #FFD700;
        font-size: 18px;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1;
    }
    
    .tet-modal-close:hover {
        background: #FFD700;
        color: #8B0000;
    }
    
    .tet-modal-body {
        padding: 20px;
        max-height: 65vh;
        overflow-y: auto;
    }
    
    /* Form Styles */
    .tet-form-group {
        margin-bottom: 15px;
        position: relative;
    }
    
    .tet-form-group label {
        display: block;
        color: #8B0000;
        font-weight: bold;
        margin-bottom: 6px;
        font-size: 14px;
    }
    
    .tet-form-group input[type="text"],
    .tet-form-group textarea {
        width: 100%;
        padding: 10px 14px;
        border: 2px solid #DC143C;
        border-radius: 10px;
        font-size: 14px;
        outline: none;
        transition: all 0.3s ease;
        box-sizing: border-box;
        font-family: inherit;
    }
    
    .tet-form-group input[type="text"]:focus,
    .tet-form-group textarea:focus {
        border-color: #FFD700;
        box-shadow: 0 0 8px rgba(255,215,0,0.4);
    }
    
    .tet-form-group textarea {
        resize: vertical;
        min-height: 100px;
    }
    
    .tet-dropdown {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 2px solid #DC143C;
        border-top: none;
        border-radius: 0 0 10px 10px;
        max-height: 150px;
        overflow-y: auto;
        z-index: 100;
        display: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .tet-dropdown-item {
        padding: 10px 14px;
        cursor: pointer;
        transition: background 0.2s ease;
        color: #333;
        font-size: 14px;
        border-bottom: 1px solid #eee;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .tet-dropdown-item .tet-user-name {
        flex: 1;
    }
    
    .tet-set-limit-btn {
        padding: 4px 8px;
        border-radius: 4px;
        cursor: pointer;
        transition: background 0.2s, transform 0.2s;
        font-size: 16px;
    }
    
    .tet-set-limit-btn:hover {
        background: rgba(220, 20, 60, 0.1);
        transform: scale(1.2);
    }
    
    .tet-dropdown-item:last-child {
        border-bottom: none;
    }
    
    .tet-dropdown-item:hover {
        background: #FFF8DC;
    }
    
    .tet-dropdown-item.tet-user-disabled {
        color: #999;
        cursor: not-allowed;
        background: #f5f5f5;
    }
    
    .tet-dropdown-item.tet-no-result {
        color: #999;
        cursor: default;
        text-align: center;
    }
    
    /* Set limit modal */
    .tet-set-limit-modal {
        width: 400px !important;
        max-width: 90vw !important;
    }
    
    .tet-limit-user-info {
        padding: 12px;
        background: linear-gradient(135deg, #FFF8DC 0%, #FFEFD5 100%);
        border-radius: 8px;
        margin-bottom: 15px;
        font-size: 16px;
    }
    
    .tet-limit-user-info strong {
        color: #DC143C;
    }
    
    .tet-limit-current {
        padding: 10px 12px;
        background: #f5f5f5;
        border-radius: 8px;
        margin-bottom: 15px;
        font-size: 14px;
        color: #666;
    }
    
    .tet-limit-current span:nth-child(2),
    .tet-limit-current span:nth-child(4) {
        font-weight: bold;
        color: #DC143C;
    }
    
    .tet-selected-receiver {
        display: none;
        align-items: center;
        gap: 10px;
        padding: 8px 12px;
        background: linear-gradient(135deg, #DC143C 0%, #8B0000 100%);
        border-radius: 20px;
        color: #FFD700;
        margin-top: 8px;
        font-size: 14px;
    }
    
    .tet-selected-receiver.show {
        display: flex;
    }
    
    .tet-remove-receiver {
        cursor: pointer;
        font-weight: bold;
        margin-left: auto;
        padding: 2px 6px;
        border-radius: 50%;
        transition: background 0.2s;
    }
    
    .tet-remove-receiver:hover {
        background: rgba(255,255,255,0.2);
    }
    
    .tet-checkbox-label {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 14px;
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        border-radius: 10px;
        cursor: pointer;
        font-weight: bold;
        color: #8B0000;
        transition: all 0.3s ease;
    }
    
    .tet-checkbox-label:hover {
        box-shadow: 0 2px 8px rgba(255,165,0,0.4);
    }
    
    .tet-checkbox-label input {
        cursor: pointer;
        width: 16px;
        height: 16px;
    }
    
    .tet-char-count {
        text-align: right;
        font-size: 12px;
        color: #888;
        margin-top: 4px;
    }
    
    .tet-status {
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 12px;
        font-size: 14px;
        display: none;
    }
    
    .tet-status:not(:empty) {
        display: block;
    }
    
    .tet-status-error {
        background: #ffe6e6;
        color: #DC143C;
    }
    
    .tet-status-success {
        background: #e6ffe6;
        color: #228B22;
    }
    
    .tet-submit-btn {
        width: 100%;
        padding: 12px;
        background: linear-gradient(135deg, #DC143C 0%, #8B0000 100%);
        border: 2px solid #FFD700;
        border-radius: 25px;
        color: #FFD700;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .tet-submit-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(139,0,0,0.4);
        background: linear-gradient(135deg, #FF1A1A 0%, #B22222 100%);
    }
    
    /* Envelope Container */
    .tet-envelopes-container {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        justify-content: center;
        padding: 10px;
        min-height: 150px;
        position: relative;
    }
    
    .tet-no-wishes {
        text-align: center;
        color: #8B0000;
        font-size: 16px;
        padding: 40px 20px;
    }
    
    .tet-envelope {
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        opacity: 0;
        transform: scale(0.5);
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 10px;
    }
    
    .tet-lixi-img {
        width: 80px;
        height: auto;
        transition: all 0.3s ease;
    }
    
    .tet-envelope-super .tet-lixi-img {
        width: 120px;
    }
    
    .tet-envelope-read .tet-lixi-img {
        width: 55px;
    }
    
    .tet-envelope-visible {
        opacity: 1;
        transform: scale(1);
    }
    
    .tet-envelope:hover {
        transform: scale(1.15) rotate(-5deg);
    }
    
    .tet-envelope-super {
        filter: drop-shadow(0 0 12px rgba(255,215,0,0.8));
        order: -1;
        width: 100%;
        justify-content: center;
    }
    
    .tet-envelope-super.tet-envelope-read {
        width: auto;
        order: 10;
    }
    
    .tet-super-badge {
        font-size: 12px;
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #8B0000;
        padding: 4px 12px;
        border-radius: 12px;
        margin-top: 6px;
        white-space: nowrap;
        font-weight: bold;
    }
    
    .tet-envelope-read {
        opacity: 0.4;
        filter: grayscale(40%);
        order: 10;
    }
    
    .tet-envelope-read:hover {
        opacity: 0.7;
        filter: grayscale(20%);
    }
    
    .tet-envelope-unread::after {
        content: '';
        position: absolute;
        top: 0;
        right: 5px;
        width: 10px;
        height: 10px;
        background: #FFD700;
        border-radius: 50%;
        animation: pulse 1.5s ease-in-out infinite;
        box-shadow: 0 0 8px #FFD700;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.3); opacity: 0.7; }
    }
    
    /* View Wish Overlay */
    .tet-view-wish-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.9);
        z-index: 10003;
        display: none;
        justify-content: center;
        align-items: center;
    }
    
    .tet-view-wish-overlay.tet-view-wish-active {
        display: flex;
    }
    
    .tet-view-wish-close {
        position: absolute;
        top: 20px;
        right: 20px;
        width: 40px;
        height: 40px;
        border: 2px solid #FFD700;
        border-radius: 50%;
        background: transparent;
        color: #FFD700;
        font-size: 24px;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10004;
    }
    
    .tet-view-wish-close:hover {
        background: #FFD700;
        color: #8B0000;
    }
    
    /* Envelope Animation */
    .tet-envelope-animation {
        transform: scale(0.8);
        opacity: 0;
        transition: all 0.5s ease;
    }
    
    .tet-envelope-animation.tet-envelope-opened {
        transform: scale(1);
        opacity: 1;
    }
    
    .tet-envelope-wrapper {
        perspective: 1000px;
    }
    
    .tet-envelope-outer {
        position: relative;
        width: 450px;
        max-width: 90vw;
        height: auto;
    }
    
    .tet-envelope-flap {
        display: none;
    }
    
    .tet-envelope-body {
        background: linear-gradient(135deg, #DC143C 0%, #8B0000 100%);
        border: 4px solid #FFD700;
        border-radius: 15px;
        padding: 4px;
    }
    
    .tet-letter {
        background: linear-gradient(135deg, #FFF8DC 0%, #FFFACD 100%);
        border-radius: 15px;
        padding: 35px 40px;
        min-height: 250px;
    }
    
    .tet-letter-content {
        text-align: center;
    }
    
    .tet-letter-sender {
        color: #DC143C;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    
    .tet-letter-divider {
        font-size: 20px;
        margin: 20px 0;
        opacity: 0.8;
    }
    
    .tet-letter-message {
        color: #333;
        font-size: 20px;
        line-height: 1.9;
        white-space: pre-wrap;
        margin-bottom: 25px;
        padding: 10px 0;
    }
    
    .tet-letter-date {
        color: #888;
        font-size: 14px;
        margin-top: 15px;
    }
    
    .tet-wish-letter-from {
        color: #8B0000;
        font-size: 14px;
        font-style: italic;
    }
    
    .tet-wish-letter-close {
        position: absolute;
        top: 10px;
        right: 10px;
        width: 30px;
        height: 30px;
        border: 2px solid #DC143C;
        border-radius: 50%;
        background: transparent;
        color: #DC143C;
        font-size: 18px;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .tet-wish-letter-close:hover {
        background: #DC143C;
        color: white;
    }
    
    /* Envelope Opening Animation */
    .tet-envelope-opening {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 10004;
        animation: envelopeOpen 1s ease forwards;
    }
    
    @keyframes envelopeOpen {
        0% {
            transform: translate(-50%, -50%) scale(1);
        }
        50% {
            transform: translate(-50%, -50%) scale(3) rotateX(0deg);
        }
        100% {
            transform: translate(-50%, -50%) scale(3) rotateX(-30deg);
            opacity: 0;
        }
    }
    
    @media (max-width: 768px) {
        .tet-lantern { font-size: 28px !important; }
        .tet-corner-decor { display: none; }
        #tet-greeting { font-size: 2rem !important; }
        
        #tet-countdown {
            bottom: 10px;
            left: 10px;
        }
        
        .tet-countdown-number {
            font-size: 18px;
        }
        
        .tet-countdown-item {
            min-width: 35px;
        }
        
        .tet-countdown-title {
            font-size: 11px;
        }
        
        #tet-wish-container {
            right: 10px;
            bottom: 10px;
            flex-direction: row;
            gap: 6px;
        }
        
        .tet-wish-btn {
            padding: 8px 12px;
            font-size: 12px;
        }
        
        .tet-envelope {
            font-size: 35px;
        }
        
        .tet-envelope-super {
            font-size: 45px;
        }
        
        .tet-envelope-outer {
            width: 280px;
        }
    }
    
    @media (max-width: 480px) {
        .tet-countdown-title {
            font-size: 11px;
        }
        
        .tet-countdown-number {
            font-size: 16px;
        }
        
        #tet-wish-container {
            flex-direction: column;
            gap: 6px;
        }
        
        .tet-wish-btn {
            padding: 8px 14px;
            font-size: 11px;
        }
        
        .tet-modal {
            width: 95%;
            max-height: 90vh;
        }
        
        .tet-modal-body {
            padding: 15px;
        }
        
        .tet-envelope-outer {
            width: 260px;
        }
        
        .tet-letter {
            padding: 20px;
        }
        
        .tet-letter-message {
            font-size: 14px;
        }
    }
`;
document.head.appendChild(tetStyles);
