(function($) {
    window.SCROLL = window.SCROLL || {};

    SCROLL.initPageTree = function() {
        $('a.ht-nav-page-link.current').parents('li').addClass('active open').removeClass('collapsed');
        $('a.ht-nav-page-link:not(.current)').parents('li.sidebar-hierarchy-level-2:not(.active) > ul').hide();
        var hightlightLink = $('li.sidebar-hierarchy-level-1.active.open>a').attr('href');
        $(".header-main-tab-bar-item>a[href='"+hightlightLink+"']").addClass('active');

        $('ul.ht-pages-nav-top').on('click', '.sp-toggle', function() {
            var li = $(this).parent('li');
            if (li.is('.collapsed')) {
                li.
                    removeClass('collapsed')
                    .addClass('open');
            } else if (li.is('.open')) {
                li.
                    removeClass('open')
                    .addClass('collapsed');
            } else {
                // we don't have children -> no-op
            }
        });
    };

})($);
