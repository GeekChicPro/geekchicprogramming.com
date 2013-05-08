// Enables HotKeys for the site

jQuery.noConflict();
(function($) {
    $(document).ready(function() {

        $(document).keyup(function(e) {
            if (e.keyCode == 27) {
                window.location = "/admin/";
            }
        });

    });
})(jQuery);
