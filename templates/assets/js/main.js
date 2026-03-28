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

  $('select').niceSelect();

  // Access instance of plugin
  // Initialize datepicker properly (accepts dd/mm/yyyy in UI but submits ISO)
  try {
    $('.datepicker-here').each(function() {
      // air-datepicker initialization
      $(this).datepicker({
        language: 'en',
        dateFormat: 'dd/MM/yyyy',
        autoClose: true,
        onSelect: function(fd, d, picker) {
          // ensure total updates when user selects date
          updateReservationTotal();
        }
      });
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
  $('.timepicker').wickedpicker(options);

  $('.choose-car-slider').owlCarousel({
    loop:true,
    margin:30,
    smartSpeed: 800,
    nav: true,
    dots: false,
    navText: ["<i class='fa fa-chevron-left'></i>", "<i class='fa fa-chevron-right'></i>"],
    responsiveClass:true,
    responsive:{
        0:{
            items: 1,
            nav: true
        },
        768:{
            items: 2,
            nav: true
        },
        1000:{
            items:3,
            nav: true
        }
    }
  })

  $('.testimonial-slider').owlCarousel({
    loop:true,
    margin:0,
    smartSpeed: 800,
    nav: false,
    dots: true,
    //autoplay: true,
    responsiveClass:true,
    responsive:{
        0:{
            items: 1
        },
        1000:{
            items:1
        }
    }
  })

  $('.brand-slider').owlCarousel({
    loop:true,
    margin:30,
    smartSpeed: 800,
    nav: false,
    dots: false,
    //autoplay: true,
    responsiveClass:true,
    responsive:{
        0:{
            items: 1
        },
        575:{
          items: 2
        },
        1000:{
            items:3
        }
    }
  })

  $('.choose-car-slider-two').owlCarousel({
    loop:true,
    margin:30,
    smartSpeed: 800,
    dots: false,
    nav: true,
    navText: ["<i class='fa fa-chevron-left'></i>", "<i class='fa fa-chevron-right'></i>"],
    responsiveClass:true,
    responsive:{
        0:{
            items: 1
        },
        768:{
            items: 3
        },
        1000:{
            items:4,
            nav: true
        }
    }
  });

  // Reservation form total calculation
  function parseDateYMD(s) {
    if (!s) return null;
    // Accept ISO YYYY-MM-DD or DD/MM/YYYY
    if (s.indexOf('-') !== -1) {
      var parts = s.split('-');
      if (parts.length !== 3) return null;
      return new Date(parts[0], parts[1] - 1, parts[2]);
    }
    if (s.indexOf('/') !== -1) {
      var parts = s.split('/');
      if (parts.length !== 3) return null;
      // assume DD/MM/YYYY
      return new Date(parts[2], parts[1] - 1, parts[0]);
    }
    // fallback: try native Date parsing (handles formats like 'March 28, 2026')
    var parsed = Date.parse(s);
    if (!isNaN(parsed)) return new Date(parsed);
    return null;
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
    }
    var extrasTotal = 0;
    form.find('.extra-checkbox:checked').each(function () {
      var p = parseFloat($(this).data('daily-price')) || 0;
      extrasTotal += p * days;
    });
    var total = (dailyRate * days) + extrasTotal;
    $('#reservation-total').text(total.toFixed(2));
    $('#reservation-total_inline').text(total.toFixed(2));
    $('#reservation-days').text(days);
  }

  // Bind events
  $(document).on('change', '#startDate, #endDate', updateReservationTotal);
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
    // If user not logged, show login modal instead of submitting
    if (!window.CURRENT_USER) {
      e.preventDefault();
      if (window.bootstrap && bootstrap.Modal) {
        var lmodal = new bootstrap.Modal(document.getElementById('loginPromptModal'));
        lmodal.show();
      } else {
        $('#loginPromptModal').modal('show');
      }
      return false;
    }
    // convert date inputs to ISO before submit to avoid backend ambiguity
    var sd = $('#startDate').val();
    var ed = $('#endDate').val();
    $('#startDate').val(formatToISO(sd));
    $('#endDate').val(formatToISO(ed));
    // allow submit to continue
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
      var v = $(this).val();
      if (v && /^\d{4}-\d{2}-\d{2}$/.test(v)){
        // convert YYYY-MM-DD -> DD/MM/YYYY for display
        var parts = v.split('-');
        var disp = parts[2] + '/' + parts[1] + '/' + parts[0];
        $(this).val(disp);
        // store original ISO in data attribute
        $(this).attr('data-iso-value', v);
      }
    });
  }

  $(document).ready(function(){
    normalizeInitialDateInputs();
    updateReservationTotal();
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

  // Intercept forms with .confirm-form to show a Bootstrap modal instead of native confirm()
  var pendingForm = null;
  $(document).on('submit', '.confirm-form', function(e) {
    e.preventDefault();
    pendingForm = this;
    var msg = $(this).data('confirm') || 'Tem a certeza?';
    $('#confirmModalMessage').text(msg);
    // support both bootstrap v5 and v4 APIs
    if (window.bootstrap && bootstrap.Modal) {
      var modal = new bootstrap.Modal(document.getElementById('confirmModal'));
      modal.show();
    } else {
      $('#confirmModal').modal('show');
    }
  });
  $('#confirmModalOk').on('click', function() {
    if (pendingForm) {
      pendingForm.submit();
      pendingForm = null;
    }
    if (window.bootstrap && bootstrap.Modal) {
      var modalEl = document.getElementById('confirmModal');
      var modal = bootstrap.Modal.getInstance(modalEl);
      if (modal) modal.hide();
    } else {
      $('#confirmModal').modal('hide');
    }
  });


})(jQuery);