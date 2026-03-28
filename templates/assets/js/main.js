(function($){
  "user strict";

  $(document).on('ready',function() {
    background();
  });

  $(window).on("load", function() {
    checkSize();
    $(window).resize(checkSize);
    //preloader
    $("#preloader").delay(300).animate({
      "opacity" : "0"
      }, 500, function() {
      $("#preloader").css("display","none");
    });
  });


  function background() {
    var img=$('.bg_img');
    img.css('background-image', function () {
    var bg = ('url(' + $(this).data('background') + ')');
    return bg;
    });
  }

  
  //Function to the css rule
  function checkSize(){
    if (window.matchMedia('(max-width: 1199px)').matches) {
        // js code for responsive drop-down-menu-item with swing effect
        $(".navbar-collapse>ul>li>a, .navbar-collapse ul.sub-menu>li>a").on("click", function() {
          var element = $(this).parent("li");
          if (element.hasClass("open")) {
            element.removeClass("open");
            element.find("li").removeClass("open");
            element.find("ul").slideUp(500,"linear");
          }
          else {
            element.addClass("open");
            element.children("ul").slideDown();
            element.siblings("li").children("ul").slideUp();
            element.siblings("li").removeClass("open");
            element.siblings("li").find("li").removeClass("open");
            element.siblings("li").find("ul").slideUp();
          }
        });
      }
    }

    // menu options custom affix
  var fixed_top = $(".header-section");
  $(window).on("scroll", function(){
      if( $(window).scrollTop() > 50){  
          fixed_top.addClass("animated fadeInDown menu-fixed");
      }
      else{
          fixed_top.removeClass("animated fadeInDown menu-fixed");
      }
  });

  //js code for mobile menu 
  $(".menu-toggle").on("click", function() {
      $(this).toggleClass("is-active");
  });

  try {
    if ($.fn && $.fn.niceSelect) {
      $('select').niceSelect();
    } else {
      console.warn('[UX DEBUG] niceSelect plugin not available, skipping init');
    }
  } catch(e) {
    console.warn('[UX DEBUG] niceSelect init error', e);
  }

  // Access instance of plugin
  // Initialize datepicker properly (accepts dd/mm/yyyy in UI but submits ISO)
  try {
    // Ensure Portuguese localization exists for the datepicker (fallback)
    try {
      if (window.$ && $.fn && $.fn.datepicker && !$.fn.datepicker.language['pt']) {
        $.fn.datepicker.language['pt'] = {
          days: ['Domingo','Segunda','Terça','Quarta','Quinta','Sexta','Sábado'],
          daysShort: ['Dom','Seg','Ter','Qua','Qui','Sex','Sáb'],
          daysMin: ['D','S','T','Q','Q','S','S'],
          months: ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'],
          monthsShort: ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'],
          today: 'Hoje',
          clear: 'Limpar',
          dateFormat: 'dd/MM/yyyy',
          timeFormat: 'hh:ii aa',
          firstDay: 1
        };
      }
    } catch(e){}
    // ensure datepicker popup is above everything and clickable
    try { $('head').append('<style id="ux-datepicker-fix">.ui-datepicker{z-index:20000 !important;} .ui-datepicker .ui-datepicker-header .ui-datepicker-next, .ui-datepicker .ui-datepicker-header .ui-datepicker-prev{cursor:pointer;pointer-events:auto;}</style>'); } catch(e) {}

    $('.datepicker-here').each(function() {
      var $el = $(this);
      // Prefer jQuery UI datepicker to avoid conflicts with multiple plugins
      if (window.jQuery && jQuery.datepicker) {
        try {
          $el.datepicker('destroy');
        } catch(e){}
        try {
          $el.datepicker({
            dateFormat: 'dd/mm/yy',
            minDate: 0,
            appendTo: 'body',
            prevText: '&#8249;',
            nextText: '&#8250;',
            changeMonth: true,
            changeYear: true,
            showOtherMonths: false,
            monthNames: ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'],
            monthNamesShort: ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'],
            dayNamesMin: ['D','S','T','Q','Q','S','S'],
            dayNamesShort: ['Dom','Seg','Ter','Qua','Qui','Sex','Sáb'],
            beforeShow: function(input, inst) {
              // Garantir z-index alto depois do datepicker abrir
              setTimeout(function() {
                var dp = $('#ui-datepicker-div');
                /* dp.css({ 'z-index': '99999', 'width': '280px' }); */
                dp.find('.ui-datepicker-next, .ui-datepicker-prev').css({
                  'display': 'block',
                  'visibility': 'visible',
                  'opacity': '1',
                  'pointer-events': 'auto',
                  'cursor': 'pointer'
                });
              }, 1);
            },
            onSelect: function(dateText, inst) {
              try {
                var parts = dateText.split('/');
                if (parts.length === 3) {
                  var dd = parts[0].length===1?('0'+parts[0]):parts[0];
                  var mm = parts[1].length===1?('0'+parts[1]):parts[1];
                  var yy = parts[2];
                  if (yy.length === 2) {
                    var curYear = new Date().getFullYear();
                    var prefix = String(curYear).slice(0,2);
                    yy = prefix + yy;
                  }
                  $el.val(dd + '/' + mm + '/' + yy);
                  $el.trigger('change');
                }
              } catch(e){}
              try { updateReservationTotal(); } catch(e){}
              try { scheduleNormalize(this); } catch(e){}
            }
          });
          try { $el.data('datepicker-initialized', 'jquery-ui'); } catch(e) {}
          // Se o valor inicial for ISO (YYYY-MM-DD), converter para DD/MM/YYYY para display
          try {
            var initVal = $el.val();
            if (initVal && /^\d{4}-\d{2}-\d{2}$/.test(initVal)) {
              var p = initVal.split('-');
              $el.val(p[2] + '/' + p[1] + '/' + p[0]);
            }
          } catch(e){}
        } catch(e) { console.warn('[UX DEBUG] jQuery UI init failed', e); }
      } else if ($.fn && $.fn.datepicker && $.fn.datepicker.language) {
        // fallback to air-datepicker if jQuery UI is not available
        try {
          $el.datepicker({
            language: 'pt',
            dateFormat: 'dd/MM/yyyy',
            autoClose: true,
            minDate: new Date(),
            prevHtml: '<',
            nextHtml: '>',
            onSelect: function(fd, d, picker) {
              try {
                if (d instanceof Date && !isNaN(d)) {
                  var dd = (d.getDate()<10?('0'+d.getDate()):d.getDate());
                  var mm = ((d.getMonth()+1)<10?('0'+(d.getMonth()+1)):(d.getMonth()+1));
                  var yyyy = d.getFullYear();
                  $el.val(dd + '/' + mm + '/' + yyyy);
                }
              } catch(e) {}
              updateReservationTotal();
              try { scheduleNormalize(this); } catch(e){}
            }
          });
          try { $el.data('datepicker-initialized', 'air'); } catch(e) {}
        } catch(e) { console.warn('[UX DEBUG] air-datepicker init failed', e); }
      } else {
        // no datepicker available; leave input as-is
      }
    });
    // ensure the popup is on top
    $('.air-datepicker').css('z-index', 99999);
  } catch (e) {
    // ignore if plugin not available
    console.warn('datepicker init failed', e);
  }


  var options = {
    now: "12:35",
    twentyFour: false,
    title: 'Choose Your Time', 
  };
  try {
    if ($.fn && $.fn.wickedpicker) {
      $('.timepicker').wickedpicker(options);
    } else {
      console.warn('[UX DEBUG] wickedpicker plugin not available, skipping init');
    }
  } catch(e) { console.warn('[UX DEBUG] wickedpicker init error', e); }

  try {
    if ($.fn && $.fn.owlCarousel) {
      $('.choose-car-slider').owlCarousel({
        loop:true,
        margin:30,
        smartSpeed: 800,
        nav: true,
        dots: false,
        navText: ["<i class='fa fa-chevron-left'></i>", "<i class='fa fa-chevron-right'></i>"],
        responsiveClass:true,
        responsive:{
            0:{ items:1, nav:true },
            768:{ items:2, nav:true },
            1000:{ items:3, nav:true }
        }
      });
    } else console.warn('[UX DEBUG] owlCarousel not available: choose-car-slider skipped');
  } catch(e) { console.warn('[UX DEBUG] choose-car-slider init error', e); }

  try {
    if ($.fn && $.fn.owlCarousel) {
      $('.testimonial-slider').owlCarousel({
        loop:true,
        margin:0,
        smartSpeed:800,
        nav:false,
        dots:true,
        responsiveClass:true,
        responsive:{0:{items:1},1000:{items:1}}
      });
    }
  } catch(e) { console.warn('[UX DEBUG] testimonial-slider init error', e); }

  try {
    if ($.fn && $.fn.owlCarousel) {
      $('.brand-slider').owlCarousel({
        loop:true,
        margin:30,
        smartSpeed:800,
        nav:false,
        dots:false,
        responsiveClass:true,
        responsive:{0:{items:1},575:{items:2},1000:{items:3}}
      });
    }
  } catch(e) { console.warn('[UX DEBUG] brand-slider init error', e); }

  try {
    if ($.fn && $.fn.owlCarousel) {
      $('.choose-car-slider-two').owlCarousel({
        loop:true,
        margin:30,
        smartSpeed:800,
        dots:false,
        nav:true,
        navText:["<i class='fa fa-chevron-left'></i>","<i class='fa fa-chevron-right'></i>"],
        responsiveClass:true,
        responsive:{0:{items:1},768:{items:3},1000:{items:4,nav:true}}
      });
    }
  } catch(e) { console.warn('[UX DEBUG] choose-car-slider-two init error', e); }

  // Reservation form total calculation
  function parseDateYMD(s) {
    if (!s) return null;
    var v = String(s).trim();
    // helper: collapse duplicated year sequences like 20262026 -> 2026
    v = v.replace(/(\d{4})\1+/, '$1');
    // Accept ISO YYYY-MM-DD
    if (v.indexOf('-') !== -1) {
      var p = v.split('-');
      if (p.length === 3 && /^\d{4}$/.test(p[0]) && /^\d{1,2}$/.test(p[1]) && /^\d{1,2}$/.test(p[2])) {
        return new Date(p[0], p[1] - 1, p[2]);
      }
    }
    // Accept DD/MM/YYYY or DD/Month/YYYY (month name english/pt)
    if (v.indexOf('/') !== -1) {
      var q = v.split('/');
      if (q.length === 3) {
        var dd = q[0], mm = q[1], yyyy = q[2];
        // if month is numeric
        if (/^\d{1,2}$/.test(mm) && /^\d{4}$/.test(yyyy) && /^\d{1,2}$/.test(dd)) {
          return new Date(yyyy, mm - 1, dd);
        }
        // try map month names (English and Portuguese)
        var monthMap = {
          january:1, february:2, march:3, april:4, may:5, june:6, july:7, august:8, september:9, october:10, november:11, december:12,
          jan:1, feb:2, mar:3, apr:4, may:5, jun:6, jul:7, aug:8, sep:9, oct:10, nov:11, dec:12,
          janeiro:1, fevereiro:2, marco:3, março:3, abril:4, maio:5, junho:6, julho:7, agosto:8, setembro:9, outubro:10, novembro:11, dezembro:12
        };
        var mmnorm = mm.toLowerCase().replace(/[^a-záàâãéèêíóôõúç]/g, '');
        if (monthMap[mmnorm] && /^\d{4}$/.test(yyyy) && /^\d{1,2}$/.test(dd)) {
          return new Date(yyyy, monthMap[mmnorm] - 1, dd);
        }
      }
    }
    return null;
  }

  // Normalize date input value to DD/MM/YYYY when possible (handles month names and duplicated years)
  function normalizeDateInputValue(raw) {
    if (!raw) return '';
    var v = String(raw).trim();
    // collapse duplicated year sequences e.g. 20262026
    v = v.replace(/(\d{4})\1+/, '$1');
    // if ISO -> convert
    if (/^\d{4}-\d{1,2}-\d{1,2}$/.test(v)) {
      var parts = v.split('-');
      var disp = (parts[2].length===1?('0'+parts[2]):parts[2]) + '/' + (parts[1].length===1?('0'+parts[1]):parts[1]) + '/' + parts[0];
      return disp;
    }
    // if already DD/MM/YYYY -> normalize zero padding
    if (/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(v)) {
      var a = v.split('/');
      return (a[0].length===1?('0'+a[0]):a[0]) + '/' + (a[1].length===1?('0'+a[1]):a[1]) + '/' + a[2];
    }
    // try to parse DD/Month/YYYY (month name english/pt)
    var m = v.match(/^(\d{1,2})[\/-]([A-Za-záàâãéèêíóôõúç]+)[\/-](\d{4})$/);
    if (m) {
      var dd = m[1], mname = m[2].toLowerCase(), yy = m[3];
      var monthMap = {january:1,february:2,march:3,april:4,may:5,june:6,july:7,august:8,september:9,october:10,november:11,december:12,jan:1,feb:2,mar:3,apr:4,may:5,jun:6,jul:7,aug:8,sep:9,oct:10,nov:11,dec:12,janeiro:1,fevereiro:2,marco:3,março:3,abril:4,maio:5,junho:6,julho:7,agosto:8,setembro:9,outubro:10,novembro:11,dezembro:12};
      var mm = monthMap[mname.replace(/[^a-záàâãéèêíóôõúç]/g,'')];
      if (mm) return (dd.length===1?('0'+dd):dd) + '/' + (mm<10?('0'+mm):mm) + '/' + yy;
    }
    return v;
  }

  function daysBetween(start, end) {
    var msPerDay = 24 * 60 * 60 * 1000;
    return Math.max(0, Math.ceil((end - start) / msPerDay));
  }

  function updateReservationTotal() {
    var form = $('.reserva-form');
    if (!form.length) return;
    var dailyRate = parseFloat(form.data('daily-rate')) || 0;
    var sd = parseDateYMD($('#startDate').val());
    var ed = parseDateYMD($('#endDate').val());
    var days = 0;
    if (sd && ed) {
      days = daysBetween(sd, ed);
      if (!isFinite(days) || days < 0) days = 0;
    }
    // debug: log parsed dates/rate/days
    try { console.log('[UX DEBUG] updateReservationTotal', { dailyRate: dailyRate, startRaw: $('#startDate').val(), endRaw: $('#endDate').val(), startParsed: sd, endParsed: ed, days: days }); } catch(e) {}
    var extrasTotal = 0;
    form.find('.extra-checkbox:checked').each(function () {
      var p = parseFloat($(this).data('daily-price')) || 0;
      extrasTotal += p * days;
    });
    var total = (Number(dailyRate) * Number(days)) + Number(extrasTotal);
    if (!isFinite(total)) total = 0;
    $('#reservation-total').text(total.toFixed(2));
    $('#reservation-total_inline').text(total.toFixed(2));
    $('#reservation-days').text(days);
  }

  // Bind events
  $(document).on('change', '#startDate, #endDate', updateReservationTotal);
  // Normalize date value on blur/change to prevent malformed strings (month names, dup years)
  $(document).on('blur change', '.datepicker-here', function(){
    try {
      var v = $(this).val();
      var nv = normalizeDateInputValue(v);
      if (nv && nv !== v) {
        $(this).val(nv);
      }
    } catch(e){}
    try { updateReservationTotal(); } catch(e){}
  });
  $(document).on('change', '.extra-checkbox', updateReservationTotal);
  // Ensure dates are submitted in ISO format: YYYY-MM-DD
  function formatToISO(s) {
    if (!s) return '';
    if (s.indexOf('-') !== -1) {
      // assume already ISO
      return s;
    }
    if (s.indexOf('/') !== -1) {
      var parts = s.split('/');
      if (parts.length !== 3) return s;
      // DD/MM/YYYY -> YYYY-MM-DD
      return parts[2] + '-' + (parts[1].length===1?('0'+parts[1]):parts[1]) + '-' + (parts[0].length===1?('0'+parts[0]):parts[0]);
    }
    return s;
  }

  $(document).on('submit', '.reserva-form', function(e){
    // validate dates before submit
    var sd_raw = $('#startDate').val();
    var ed_raw = $('#endDate').val();
    var sd_d = parseDateYMD(sd_raw);
    var ed_d = parseDateYMD(ed_raw);
    var today = new Date();
    // zero time for comparison
    today.setHours(0,0,0,0);
    if (!sd_d || !ed_d) {
      e.preventDefault();
      alert('Por favor seleccione datas válidas de início e fim.');
      return false;
    }
    if (sd_d < today) {
      e.preventDefault();
      alert('A data de início não pode ser anterior a hoje.');
      return false;
    }
    if (ed_d <= sd_d) {
      e.preventDefault();
      alert('A data de fim deve ser posterior à data de início.');
      return false;
    }
    // convert date inputs to ISO before submit to avoid backend ambiguity
    $('#startDate').val(formatToISO(sd_raw));
    $('#endDate').val(formatToISO(ed_raw));
    // allow submit to continue
  });

  // Ensure totals are recalculated and any leftover modal backdrops removed just before submitting via the reserve button
  $(document).on('click', '.reserva-form button[type="submit"]', function(e){
    try {
      updateReservationTotal();
    } catch(err) {
      console.warn('[UX DEBUG] updateReservationTotal error', err);
    }
    // small defensive cleanup in case a backdrop is stuck
    setTimeout(function(){
      try { $('.modal-backdrop').remove(); } catch(e){}
      try { $('body').removeClass('modal-open'); } catch(e){}
    }, 20);
  });

  // Generic conversion for any form that contains startDate/endDate inputs (e.g., edit reservation)
  $(document).on('submit', 'form', function(e){
    var f = $(this);
    if (f.find('input[name="startDate"], input[name="endDate"]').length) {
      f.find('input[name="startDate"]').each(function(){
        var v = $(this).val();
        $(this).val(formatToISO(v));
      });
      f.find('input[name="endDate"]').each(function(){
        var v = $(this).val();
        $(this).val(formatToISO(v));
      });
    }
    // continue submit
  });
  // Initialize on page load
  // Normalize initial date inputs (show DD/MM/YYYY if server rendered ISO) and then update totals
  function normalizeInitialDateInputs(){
    $('.datepicker-here').each(function(){
      try {
        var v = $(this).val();
        var nv = normalizeDateInputValue(v);
        if (nv && nv !== v) $(this).val(nv);
      } catch(e){}
    });
  }

  // Schedule short-lived polling to catch programmatic mutations from other plugins
  function scheduleNormalize(el) {
    var $el = $(el);
    var attempts = 0;
    var id = setInterval(function(){
      attempts++;
      try {
        var v = $el.val();
        var nv = normalizeDateInputValue(v);
        if (nv && nv !== v) {
          $el.val(nv);
        }
      } catch(e){}
      if (attempts > 20) clearInterval(id); // ~2 seconds at 100ms
    }, 100);
  }

  $(document).ready(function(){
    normalizeInitialDateInputs();
    updateReservationTotal();
  });

  // Ensure datepicker inputs initialize on focus if initialization was skipped earlier
  $(document).on('focus', '.datepicker-here', function(){
    var $el = $(this);
    if ($el.data('datepicker-initialized')) return;
    try {
      if (window.jQuery && jQuery.datepicker) {
        // try jQuery UI init (conservative)
        $el.datepicker('destroy');
        $el.datepicker({
          dateFormat: 'dd/mm/yy',
          minDate: 0,
          appendTo: 'body',
          prevText: '<',
          nextText: '>',
          changeMonth: true,
          changeYear: true,
          monthNames: ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'],
          onSelect: function(dateText, inst) {
            try {
              var parts = dateText.split('/');
              if (parts.length === 3) {
                var dd = parts[0].length===1?('0'+parts[0]):parts[0];
                var mm = parts[1].length===1?('0'+parts[1]):parts[1];
                var yy = parts[2];
                if (yy.length === 2) {
                  var curYear = new Date().getFullYear();
                  var prefix = String(curYear).slice(0,2);
                  yy = prefix + yy;
                }
                $el.val(dd + '/' + mm + '/' + yy);
                $el.trigger('change');
              }
            } catch(e){}
            try { updateReservationTotal(); } catch(e){}
            try { scheduleNormalize(this); } catch(e){}
          }
        });
        $el.data('datepicker-initialized','jquery-ui');
        try { $el.datepicker('refresh'); } catch(e){}
      } else if ($.fn && $.fn.datepicker && $.fn.datepicker.language) {
        // fallback to air-datepicker
        $el.datepicker({
          language: 'pt',
          dateFormat: 'dd/MM/yyyy',
          autoClose: true,
          minDate: new Date(),
          prevHtml: '<',
          nextHtml: '>',
          onSelect: function(fd, d, picker) {
            try {
              if (d instanceof Date && !isNaN(d)) {
                var dd = (d.getDate()<10?('0'+d.getDate()):d.getDate());
                var mm = ((d.getMonth()+1)<10?('0'+(d.getMonth()+1)):(d.getMonth()+1));
                var yyyy = d.getFullYear();
                $el.val(dd + '/' + mm + '/' + yyyy);
              }
            } catch(e) {}
            try { updateReservationTotal(); } catch(e){}
            try { scheduleNormalize(this); } catch(e){}
          }
        });
        $el.data('datepicker-initialized','air');
      }
    } catch(e) {
      console.warn('[UX DEBUG] focus datepicker init failed', e);
    }
  });

  $('.blog-thumb-slider').owlCarousel({
    loop:true,
    margin:0,
    smartSpeed: 800,
    dots: false,
    nav: true,
    navText: ["<i class='fa fa-chevron-left'></i>", "<i class='fa fa-chevron-right'></i>"],
    responsiveClass:true,
    responsive:{
        0:{
            items: 1
        },
        1000:{
            items:1,
            nav: true
        }
    }
  });

    

  $( function() {
    $( "#slider-range" ).slider({
      range: true,
      min: 0,
      max: 500,
      values: [ 80, 300 ],
      slide: function( event, ui ) {
        $( "#amount" ).val( "$" + ui.values[ 0 ] + " - $" + ui.values[ 1 ] );
        // update hidden max_price field for search
        $("#max_price").val(ui.values[1]);
      }
    });
    $( "#amount" ).val( "$" + $( "#slider-range" ).slider( "values", 0 ) +
      " - $" + $( "#slider-range" ).slider( "values", 1 ) );
    $("#max_price").val($( "#slider-range" ).slider( "values", 1 ));
  } );

  // service grid and list view
  $(".view-style-toggle-area .grid-btn").on( "click", function() {
    $(".car-search-result-area").addClass("grid--view").removeClass("list--view");
    $(".car-item").removeClass("car-item--style2");
  });
  $(".view-style-toggle-area .list-btn").on( "click", function() {
    $(".car-search-result-area").addClass("list--view").removeClass("grid--view");
    $(".car-item").addClass("car-item--style2");
  });
  $(".view-style-toggle-area .view-btn").on( "click", function() {
    $(this).addClass("active").siblings().removeClass("active");
  });

   // Show or hide the sticky footer button
   $(window).on("scroll", function() {
    if ($(this).scrollTop() > 200) {
        $(".scroll-to-top").fadeIn(200);
    } else {
        $(".scroll-to-top").fadeOut(200);
    }
  });

  // Animate the scroll to top
  $(".scroll-to-top").on("click", function(event) {
    event.preventDefault();
    $("html, body").animate({scrollTop: 0}, 300);
  });

  // lightcase plugin init
  $('a[data-rel^=lightcase]').lightcase();

  // Intercept forms with .confirm-form and use native confirm() dialog
  $(document).on('submit', '.confirm-form', function(e) {
    var msg = $(this).data('confirm') || 'Tem a certeza?';
    if (!window.confirm(msg)) {
      e.preventDefault();
      return false;
    }
    // allow the form to submit normally
  });

  // Global debug hooks: log modal show/hide events and ensure no leftover backdrops remain
  try {
    $(document).on('shown.bs.modal', '.modal', function(e){
      console.log('[UX DEBUG] modal shown:', e.target && e.target.id);
    });
    $(document).on('hidden.bs.modal', '.modal', function(e){
      console.log('[UX DEBUG] modal hidden:', e.target && e.target.id);
      // small delay then remove any stray backdrops
      setTimeout(function(){
        if ($('.modal.show').length === 0) {
          try { $('.modal-backdrop').remove(); } catch(e){}
          try { $('body').removeClass('modal-open'); } catch(e){}
        }
      }, 50);
    });
  } catch(e) {
    // ignore if bootstrap/jQuery events not available
  }

  // Defensive cleanup after any form submission: ensure no leftover modal backdrop remains
  $(document).on('submit', 'form', function(){
    setTimeout(function(){
      if ($('.modal.show').length === 0) {
        try { $('.modal-backdrop').remove(); } catch(e){}
        try { $('body').removeClass('modal-open'); } catch(e){}
      }
    }, 300);
  });

  // Auto-show flash modal if server rendered a flash with category 'modal' or 'modal-error'
  try {
    $(function(){
      var fm = $('#flash-modal-msg');
      if (!fm.length) return;
      var msg = fm.data('message') || '';
      var type = fm.data('type') || '';
      var modalId = 'flashModalAuto';
      // Build a minimal Bootstrap modal and append to body
      var title = type === 'modal-error' ? 'Erro' : 'Aviso';
      var modalHtml = '' +
        '<div class="modal fade" id="' + modalId + '" tabindex="-1" role="dialog" aria-hidden="true">' +
          '<div class="modal-dialog modal-dialog-centered" role="document">' +
            '<div class="modal-content">' +
              '<div class="modal-header">' +
                '<h5 class="modal-title">' + title + '</h5>' +
                '<button type="button" class="close" data-dismiss="modal" aria-label="Close">' +
                  '<span aria-hidden="true">&times;</span>' +
                '</button>' +
              '</div>' +
              '<div class="modal-body">' + msg + '</div>' +
            '</div>' +
          '</div>' +
        '</div>';
      try { $('body').append(modalHtml); } catch(e) { console.warn('append flash modal failed', e); }
      // Show modal via Bootstrap if available, otherwise fallback to alert
      try {
        var $m = $('#' + modalId);
        if ($m && $m.modal) {
          $m.modal('show');
        } else {
          alert(msg);
        }
      } catch(e) {
        console.warn('show flash modal failed', e);
        try { alert(msg); } catch(_){}
      }
    });
  } catch(e) { console.warn('flash-modal init error', e); }


})(jQuery);