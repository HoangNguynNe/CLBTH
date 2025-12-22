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
            document.body.classList.add('christmas-dark-mode');
            document.documentElement.classList.add('christmas-dark-mode');
        }
    }
    
    // Run immediately
    checkDarkMode();

    // Run on DOMContentLoaded just in case
    document.addEventListener('DOMContentLoaded', checkDarkMode);
})();

document.addEventListener('DOMContentLoaded', function() {
    // Disable snow on problem detail pages
    if (window.location.pathname.indexOf('/problem/') === 0) {
        return;
    }

    // 1. Custom Snow Effect
    var snowContainer = document.createElement('div');
    snowContainer.id = 'snow-container';
    snowContainer.style.position = 'fixed';
    snowContainer.style.top = '0';
    snowContainer.style.left = '0';
    snowContainer.style.width = '100%';
    snowContainer.style.height = '100%';
    snowContainer.style.pointerEvents = 'none';
    snowContainer.style.zIndex = '2147483647'; // Max z-index to ensure visibility
    document.body.appendChild(snowContainer);

    var isDarkMode = document.body.classList.contains('christmas-dark-mode');
    var snowColor = isDarkMode ? "#ffffff" : "#D42426";
    var snowflakeCount = 25; // Reduced density
    var shapes = ['❄', '❅', '❆', '•', '+']; // Multiple shapes

    function createSnowflake() {
        var snowflake = document.createElement('div');
        snowflake.classList.add('snowflake');
        
        // Randomize properties
        var size = Math.random() * 15 + 10; // Smaller size: 10px to 25px
        var left = Math.random() * 100; // 0% to 100%
        var durationFall = Math.random() * 10 + 10; // Slower fall: 10s to 20s
        var durationSway = Math.random() * 4 + 3; // Slower sway: 3s to 7s
        var delay = Math.random() * 5; // 0s to 5s
        var opacity = Math.random() * 0.4 + 0.1; // Lighter opacity: 0.1 to 0.5

        snowflake.style.fontSize = size + 'px';
        snowflake.style.left = left + 'vw';
        snowflake.style.opacity = opacity;
        snowflake.style.color = snowColor;
        snowflake.innerText = shapes[Math.floor(Math.random() * shapes.length)];
        
        // Remove CSS Mask settings as we are using text now
        snowflake.style.backgroundColor = 'transparent';

        var animations = ['fall', 'sway'];
        var durations = [durationFall + 's', durationSway + 's'];
        var delays = ['-' + delay + 's', '-' + delay + 's'];

        // Randomly add spin class
        if (Math.random() > 0.5) {
            snowflake.classList.add('spin');
            var durationSpin = Math.random() * 4 + 2; // 2s to 6s
            animations.push('spin');
            durations.push(durationSpin + 's');
            delays.push('-' + delay + 's');
        }
        
        snowflake.style.animationName = animations.join(', ');
        snowflake.style.animationDuration = durations.join(', ');
        snowflake.style.animationDelay = delays.join(', ');

        snowContainer.appendChild(snowflake);
    }

    for (var i = 0; i < snowflakeCount; i++) {
        createSnowflake();
    }

    // Check if intro has been shown in this session
    if (!sessionStorage.getItem('christmas2025_intro_shown')) {
        
        // 2. Merry Christmas Text
        var greeting = document.createElement('div');
        greeting.id = 'christmas-greeting';
        greeting.innerText = 'Merry Christmas 2025';
        greeting.style.position = 'fixed';
        greeting.style.top = '50%';
        greeting.style.left = '50%';
        greeting.style.transform = 'translate(-50%, -50%)';
        greeting.style.fontSize = '5rem';
        greeting.style.fontWeight = 'bold';
        greeting.style.color = '#D42426';
        greeting.style.textShadow = '2px 2px 4px #FFFFFF, 0 0 20px #F8B229';
        greeting.style.zIndex = '2147483647'; // Max z-index
        greeting.style.pointerEvents = 'none';
        greeting.style.opacity = '0';
        greeting.style.transition = 'opacity 2s ease-in-out';
        greeting.style.fontFamily = "'Mountains of Christmas', cursive, sans-serif"; 
        
        // Add Google Font
        var fontLink = document.createElement('link');
        fontLink.href = 'https://fonts.googleapis.com/css2?family=Mountains+of+Christmas:wght@700&display=swap';
        fontLink.rel = 'stylesheet';
        document.head.appendChild(fontLink);

        document.body.appendChild(greeting);

        // Animation sequence for text
        setTimeout(function() {
            greeting.style.opacity = '1'; // Fade in
            setTimeout(function() {
                greeting.style.opacity = '0'; // Fade out
                setTimeout(function() {
                    greeting.remove(); // Remove from DOM
                }, 2000);
            }, 3000); // Stay for 3 seconds
        }, 500);

        // Mark as shown for this session
        sessionStorage.setItem('christmas2025_intro_shown', 'true');
    }
});
