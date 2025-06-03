(function($) {
    $(document).ready(function() {
        console.log("Theme JS loaded, starting header time watcher");

        const startTimeHeader = new Date();
        const $timeSpentHeader = $('#time-spent-header');
        const $currentTimeHeader = $('#current-time-header');

        function updateTimeSpentHeader() {
            const currentTime = new Date();
            const timeDiff = currentTime - startTimeHeader;
            const seconds = Math.floor(timeDiff / 1000) % 60;
            const minutes = Math.floor(timeDiff / (1000 * 60)) % 60;
            const hours = Math.floor(timeDiff / (1000 * 60 * 60));

            $timeSpentHeader.text(
                `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
            );
        }

        function updateCurrentTimeHeader() {
            const now = new Date();
            const hours = now.getHours().toString().padStart(2, '0');
            const minutes = now.getMinutes().toString().padStart(2, '0');
            const seconds = now.getSeconds().toString().padStart(2, '0');
            $currentTimeHeader.text(`${hours}:${minutes}:${seconds}`);
        }

        // Initial update
        updateTimeSpentHeader();
        updateCurrentTimeHeader();

        // Update every second
        setInterval(updateTimeSpentHeader, 1000);
        setInterval(updateCurrentTimeHeader, 1000);
    });
})(django.jQuery);