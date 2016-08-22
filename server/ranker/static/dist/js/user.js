$(document).ready(function() {
  $('.response-pill').on('click', function() {
      if ($(this).hasClass("new")) {
        if ($(this).text() === 'Enter new response here...') {
          $(this).empty();
          $(this).addClass("editing");
        } else if ($(this).hasClass("active")) {
          // do nothing
        } else {
          $(this).removeClass("editing");
          $(this).parent().append($(this).clone(true).text('Enter new response here...'));
          $(this).addClass("active");
          $(this).parent().parent().children('.response-box').append($(this));
        }
      } else if ($(this).hasClass("active")) {
        // do nothing
      } else {
        $(this).addClass("active");
        $(this).parent().parent().children('.response-box').append($(this));
      }
  });
});


$(document).ready(function() {
  $('.response-binary-true').on('click', function() {
      if ($(this).hasClass("active")) {
        $(this).removeClass("active");
      } else {
        $(this).addClass("active");
        $(this).parent().children('.response-binary-false').removeClass("active");
      }
  });
  
  $('.response-binary-false').on('click', function() {
      if ($(this).hasClass("active")) {
        $(this).removeClass("active");
      } else {
        $(this).addClass("active");
        $(this).parent().children('.response-binary-true').removeClass("active");
      }
  });

  // Expand all the textareas to the size of their content
  $("textarea").each(function () {
      this.style.height = (this.scrollHeight+15)+'px';
  });
});
