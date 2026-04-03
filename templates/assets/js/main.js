(function($){
  "use strict";

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

  // Expose helper for debugging from the console
  try {
    if (typeof window !== 'undefined') {
      window.showModalMessage = showModalMessage;
    }
  } catch(e) { }

  
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
        // console.warn('[UX DEBUG] niceSelect plugin not available, skipping init');
    }
  } catch(e) {
      // console.warn('[UX DEBUG] niceSelect init error', e);
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
        } catch(e) { }
      } else {
        // no datepicker plugin available
      }
    });
    // ensure the popup is on top
    $('.air-datepicker').css('z-index', 99999);
  } catch (e) {
    // ignore if plugin not available
  }


      // console.warn('datepicker init failed', e);
  var options = {
    now: "12:35",
    twentyFour: false,
    title: 'Choose Your Time'
  };
  try {
    if ($.fn && $.fn.wickedpicker) {
      // Initialize each timepicker using the element's current value if present
      $('.timepicker').each(function() {
        var $t = $(this);
        var elVal = String($t.val() || '').trim();
        var nowStr = options.now;
        if (elVal) {
          var m = elVal.match(/^(\d{1,2}):(\d{2})\s*([AaPp][Mm])?$/);
          if (m) {
            var hh = parseInt(m[1], 10);
            var mm = m[2];
            var ampm = m[3];
            if (ampm) {
              ampm = ampm.toUpperCase();
              if (ampm === 'PM' && hh !== 12) hh += 12;
              if (ampm === 'AM' && hh === 12) hh = 0;
            }
            nowStr = (hh < 10 ? '0' + hh : '' + hh) + ':' + mm;
          }
        }
        $t.wickedpicker($.extend({}, options, { now: nowStr }));
      });
    } else {
      // wickedpicker not available
    }
  } catch(e) { }

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
    } else { /* owlCarousel not available */ }
  } catch(e) { }

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
  } catch(e) { }

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
  } catch(e) { }

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
  } catch(e) { }

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
    try { /* debug suppressed */ } catch(e) {}
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

  // Parse time strings like "12:35 PM", "5:35 PM", "17:35" -> {h,m}
  function parseTimeJS(s) {
    if (!s) return null;
    var v = String(s).trim();
    // normalize spaces and remove stray spaces around colon
    v = v.replace(/\s*:\s*/g, ':').replace(/\s+/g, ' ').trim();
    // try 12h with AM/PM
    var m = v.match(/^(\d{1,2}):(\d{2})\s*([AaPp][Mm])$/);
    if (m) {
      var hh = parseInt(m[1], 10);
      var mm = parseInt(m[2], 10);
      var ampm = m[3].toUpperCase();
      if (ampm === 'PM' && hh !== 12) hh += 12;
      if (ampm === 'AM' && hh === 12) hh = 0;
      return {h: hh, m: mm};
    }
    // try 24h
    var m2 = v.match(/^(\d{1,2}):(\d{2})$/);
    if (m2) {
      return {h: parseInt(m2[1], 10), m: parseInt(m2[2], 10)};
    }
    return null;
  }

  // Normalize time inputs to a consistent display format (h:mm AM/PM)
  function normalizeInitialTimeInputs(){
    $('.timepicker').each(function(){
      try {
        var v = $(this).val();
        if (!v) return;
        // clean up and parse
        var t = parseTimeJS(v);
        if (t) {
          var hh = t.h % 12 === 0 ? 12 : t.h % 12;
          var ampm = t.h >= 12 ? 'PM' : 'AM';
          var mm = (t.m < 10 ? '0' + t.m : t.m);
          $(this).val(hh + ':' + mm + ' ' + ampm);
        }
      } catch(e){}
    });
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
    // validate dates and times before submit (include times if provided)
    var sd_raw = $('#startDate').val();
    var ed_raw = $('#endDate').val();
    var st_raw = $('#startTime').val();
    var et_raw = $('#endTime').val();
    var sd_d = parseDateYMD(sd_raw);
    var ed_d = parseDateYMD(ed_raw);
    var today = new Date();
    today.setHours(0,0,0,0);
    if (!sd_d || !ed_d) {
      e.preventDefault();
      showModalMessage('Por favor seleccione datas válidas de início e fim.', 'Erro');
      return false;
    }
    // combine times when available
    var sd_dt = new Date(sd_d.getTime());
    var ed_dt = new Date(ed_d.getTime());
    var st = parseTimeJS(st_raw);
    var et = parseTimeJS(et_raw);
    if (st) sd_dt.setHours(st.h, st.m, 0, 0);
    else sd_dt.setHours(0,0,0,0);
    if (et) ed_dt.setHours(et.h, et.m, 0, 0);
    else ed_dt.setHours(23,59,59,0);

    if (sd_dt < today) {
      e.preventDefault();
      showModalMessage('A data de início não pode ser anterior a hoje.', 'Erro');
      return false;
    }
    if (ed_dt <= sd_dt) {
      e.preventDefault();
      showModalMessage('A data/hora de fim deve ser posterior à data/hora de início.', 'Erro');
      return false;
    }
    // convert date inputs to ISO before submit to avoid backend ambiguity
    $('#startDate').val(formatToISO(sd_raw));
    $('#endDate').val(formatToISO(ed_raw));
    // ensure payment method selected when present
    try {
      var pm = $(this).find('select[name="idPaymentMethod"]');
      if (pm.length && (!pm.val() || String(pm.val()).trim() === '')) {
        e.preventDefault();
        showModalMessage('Por favor seleccione um método de pagamento.', 'Erro');
        return false;
      }
    } catch(e) {}
    // allow submit to continue
  });

  // Validation for edit reservation form (separate handler)
  $(document).on('submit', '#edit-reservation-form', function(e){
    var form = $(this);
    var sd_raw = form.find('input[name="startDate"]').val();
    var ed_raw = form.find('input[name="endDate"]').val();
    var st_raw = form.find('input[name="startTime"]').val();
    var et_raw = form.find('input[name="endTime"]').val();
    var sd_d = parseDateYMD(sd_raw);
    var ed_d = parseDateYMD(ed_raw);
    var today = new Date(); today.setHours(0,0,0,0);
    if (!sd_d || !ed_d) {
      e.preventDefault();
      showModalMessage('Por favor seleccione datas válidas de início e fim.', 'Erro');
      return false;
    }
    var sd_dt = new Date(sd_d.getTime());
    var ed_dt = new Date(ed_d.getTime());
    var st = parseTimeJS(st_raw);
    var et = parseTimeJS(et_raw);
    if (st) sd_dt.setHours(st.h, st.m, 0, 0); else sd_dt.setHours(0,0,0,0);
    if (et) ed_dt.setHours(et.h, et.m, 0, 0); else ed_dt.setHours(23,59,59,0);
    if (sd_dt < today) {
      e.preventDefault();
      showModalMessage('A data de início não pode ser anterior a hoje.', 'Erro');
      return false;
    }
    if (ed_dt <= sd_dt) {
      e.preventDefault();
      showModalMessage('A data/hora de fim deve ser posterior à data/hora de início.', 'Erro');
      return false;
    }
    // convert dates to ISO format before submit
    form.find('input[name="startDate"]').val(formatToISO(sd_raw));
    form.find('input[name="endDate"]').val(formatToISO(ed_raw));
    // continue submit
  });

  // Ensure totals are recalculated and any leftover modal backdrops removed just before submitting via the reserve button
  $(document).on('click', '.reserva-form button[type="submit"]', function(e){
    try {
      updateReservationTotal();
    } catch(err) {
      // updateReservationTotal error suppressed
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

  // Normalize any startDate/endDate inputs on the page (covers inputs without datepicker class)
  function normalizeAllDateFields(){
    $('input[name="startDate"], input[name="endDate"]').each(function(){
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
    normalizeAllDateFields();
    normalizeInitialTimeInputs();
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
      // focus datepicker init failed (suppressed)
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
    // Allow server-provided min/max to initialize the slider. Fallback to defaults otherwise.
    try {
      // Read server-provided values from either the sidebar or top hidden inputs
      var serverMin = parseInt($("#min_price").val() || $("#top_min_price").val(), 10);
      var serverMax = parseInt($("#max_price").val() || $("#top_max_price").val(), 10);
      // Allow template to provide overall bounds and currency via window.__PRICE_FILTER
      var wf = window.__PRICE_FILTER || {};
      var overallMin = (typeof wf.overallMin === 'number') ? wf.overallMin : 0;
      var overallMax = (typeof wf.overallMax === 'number') ? wf.overallMax : ((typeof wf.overallMax === 'string') ? parseInt(wf.overallMax,10) || 500 : 500);
      var currency = wf.currency || '€';
      var defaultMin = (typeof wf.defaultMin === 'number') ? wf.defaultMin : 80;
      var defaultMax = (typeof wf.defaultMax === 'number') ? wf.defaultMax : Math.max(300, overallMax);
      var minVal = (isFinite(serverMin) && !isNaN(serverMin)) ? serverMin : defaultMin;
      var maxVal = (isFinite(serverMax) && !isNaN(serverMax)) ? serverMax : defaultMax;
      if (minVal < overallMin) minVal = overallMin;
      if (maxVal > overallMax) maxVal = overallMax;
      if (minVal > maxVal) {
        // swap if user accidentally provided inverted bounds
        var t = minVal; minVal = maxVal; maxVal = t;
      }

      $( "#slider-range" ).slider({
        range: true,
        min: overallMin,
        max: overallMax,
        values: [ minVal, maxVal ],
        slide: function( event, ui ) {
          $( "#amount" ).val( currency + ui.values[ 0 ] + " - " + currency + ui.values[ 1 ] );
          // update hidden min/max fields for search (sidebar + top form)
          $("#min_price").val(ui.values[0]);
          $("#max_price").val(ui.values[1]);
          try { $("#top_min_price").val(ui.values[0]); } catch(e) {}
          try { $("#top_max_price").val(ui.values[1]); } catch(e) {}
        }
      });

      $( "#amount" ).val( currency + $( "#slider-range" ).slider( "values", 0 ) +
        " - " + currency + $( "#slider-range" ).slider( "values", 1 ) );
      var v0 = $( "#slider-range" ).slider( "values", 0 );
      var v1 = $( "#slider-range" ).slider( "values", 1 );
      $("#min_price").val(v0);
      $("#max_price").val(v1);
      try { $("#top_min_price").val(v0); } catch(e) {}
      try { $("#top_max_price").val(v1); } catch(e) {}
    } catch(e) {
      // If slider plugin isn't available or any error occurs, fail silently
      try { $("#amount").val( (window.__PRICE_FILTER && window.__PRICE_FILTER.currency ? window.__PRICE_FILTER.currency : '€') + '80 - ' + (window.__PRICE_FILTER && window.__PRICE_FILTER.currency ? window.__PRICE_FILTER.currency : '€') + '300' ); } catch(_) {}
    }
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
  // Use a Bootstrap modal for confirmations instead of native confirm()
  $(document).on('submit', '.confirm-form', function(e) {
    var form = this;
    var msg = $(this).data('confirm') || 'Tem a certeza?';
    e.preventDefault();
    showModalConfirm(msg, function(confirmed){
      if (confirmed) {
        // submit the form programmatically
        form.submit();
      }
    });
    return false;
  });

  // Global debug hooks: log modal show/hide events and ensure no leftover backdrops remain
  try {
    $(document).on('shown.bs.modal', '.modal', function(e){ /* suppressed debug */ });
    $(document).on('hidden.bs.modal', '.modal', function(e){
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
          // fallback: alert
          alert(msg);
        }
      } catch(e) {
        console.warn('show flash modal failed', e);
        try { alert(msg); } catch(_){ }
      }
    });
  } catch(e) { console.warn('flash-modal init error', e); }

  // Helper: show a simple modal confirmation with callback
  function showModalConfirm(message, cb) {
    var id = 'confirmModalClient';
    $('#' + id).remove();
    var html = ''+
      '<div class="modal fade" id="'+id+'" tabindex="-1" role="dialog" aria-hidden="true">'+
        '<div class="modal-dialog modal-dialog-centered" role="document">'+
          '<div class="modal-content">'+
            '<div class="modal-header"><h5 class="modal-title">Confirmação</h5>'+
              '<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>'+
            '</div>'+
            '<div class="modal-body">'+message+'</div>'+
            '<div class="modal-footer">'+
              '<button type="button" class="btn btn-secondary" data-dismiss="modal" id="'+id+'_no">Cancelar</button>'+
              '<button type="button" class="btn btn-primary" id="'+id+'_yes">Confirmar</button>'+
            '</div>'+
          '</div>'+
        '</div>'+
      '</div>';
    try { $('body').append(html); } catch(e){ }
    var $m = $('#' + id);
    $m.modal('show');
    $m.on('click', '#'+id+'_yes', function(){
      $m.modal('hide');
      cb(true);
    });
    $m.on('hidden.bs.modal', function(){
      cb(false);
      setTimeout(function(){ $m.remove(); }, 200);
    });
  }

  // Helper: show a simple modal message (info/error)
  function showModalMessage(message, title) {
    // Use the same flash-modal markup used elsewhere to ensure consistent
    // behaviour and avoid stray backdrop/footer resizing issues.
    var autoId = 'flashModalAuto';
    $('#' + autoId).remove();
    var t = title || 'Aviso';
    var html = '' +
      '<div class="modal fade" id="' + autoId + '" tabindex="-1" role="dialog" aria-hidden="true">' +
        '<div class="modal-dialog modal-dialog-centered" role="document">' +
          '<div class="modal-content">' +
            '<div class="modal-header">' +
              '<h5 class="modal-title">' + t + '</h5>' +
              '<button type="button" class="close" data-dismiss="modal" aria-label="Close">' +
                '<span aria-hidden="true">&times;</span>' +
              '</button>' +
            '</div>' +
            '<div class="modal-body">' + message + '</div>' +
          '</div>' +
        '</div>' +
      '</div>';
    try { $('body').append(html); } catch(e){}
    var $m = $('#' + autoId);
    try {
      // remove only non-showing stray backdrops
      $('.modal-backdrop').not('.show').remove();
      // ensure modal is appended to body (avoid nested containers)
      try { $m.appendTo('body'); } catch(e){}
      if ($m && $m.modal) {
        $m.on('shown.bs.modal', function(){ /* modal shown */ });
        $m.modal('show');
        // short delay: if modal is not visible, force display and backdrop
        setTimeout(function(){
          var visible = $m.hasClass('show') || $m.is(':visible');
          if (!visible) {
            try {
              $m.addClass('show').css('display','block').attr('aria-hidden','false');
              $('body').addClass('modal-open');
              if ($('.modal-backdrop.show').length === 0) {
                $('<div class="modal-backdrop fade show"></div>').appendTo(document.body);
              }
              $m.css('z-index', 200000);
              /* forced display/backdrop (suppressed debug) */
            } catch(err) { }
          }
        }, 50);
        // Ensure close button/backdrop/ESC will remove the modal even if plugin misbehaves
        try {
          // close button
          $m.find('.close').off('click.modalClose').on('click.modalClose', function(ev){
            try { $m.modal && $m.modal('hide'); } catch(e) {}
            // fallback manual removal
            try { $m.removeClass('show').hide(); } catch(e) {}
            try { $('.modal-backdrop').remove(); } catch(e) {}
            try { $('body').removeClass('modal-open'); } catch(e) {}
            ev.preventDefault();
          });
          // clicking backdrop should close
          $(document).off('click.modalBackdrop').on('click.modalBackdrop', '.modal-backdrop', function(){
            try { $m.modal && $m.modal('hide'); } catch(e) {}
            try { $m.removeClass('show').hide(); } catch(e) {}
            try { $('.modal-backdrop').remove(); } catch(e) {}
            try { $('body').removeClass('modal-open'); } catch(e) {}
          });
          // ESC key
          $(document).off('keydown.modalEsc').on('keydown.modalEsc', function(e){
            if (e.key === 'Escape' || e.keyCode === 27) {
              try { $m.modal && $m.modal('hide'); } catch(e) {}
              try { $m.removeClass('show').hide(); } catch(e) {}
              try { $('.modal-backdrop').remove(); } catch(e) {}
              try { $('body').removeClass('modal-open'); } catch(e) {}
            }
          });
        } catch(e) { }
      } else {
        // bootstrap modal plugin missing; fallback
        try { alert(message); } catch(_){}
      }
    } catch(e) {
      try { alert(message); } catch(_){ }
    }
  }


})(jQuery);