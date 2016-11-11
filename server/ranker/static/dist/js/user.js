$(document).ready(function() {
  $('.response-pill').on('click', function() {
      if ($(this).hasClass("new")) {
        if ($(this).text() === 'Enter new response here...') {
          $(this).empty();
          $(this).addClass("editing");
          analytics.track('Entered Response', {
           type: 'New',
           text: $(this).text()
          });
        } else if ($(this).hasClass("active")) {
          // do nothing
        } else {
          $(this).removeClass("editing");
          $(this).parent().append($(this).clone(true).text('Enter new response here...'));
          $(this).addClass("active");
          $(this).parent().parent().children('.response-box').append($(this));
          analytics.track('Entered Response', {
           type: 'New',
           text: $(this).text()
          });
        }
      } else if ($(this).hasClass("active")) {
        // do nothing
      } else {
        $(this).addClass("active");
        $(this).parent().parent().children('.response-box').append($(this));
        analytics.track('Entered Response', {
           type: 'Existing',
           text: '$(this).text()'
        });
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
        analytics.track('Entered Grade', {
          grade: 'Pass'
        });
      }
  });

  
  $('.response-binary-false').on('click', function() {
      if ($(this).hasClass("active")) {
        $(this).removeClass("active");
      } else {
        $(this).addClass("active");
        $(this).parent().children('.response-binary-true').removeClass("active");
        analytics.track('Entered Grade', {
          grade: 'Fail'
        });
      }
  });

  // Expand all the textareas to the size of their content
  $("textarea").each(function () {
      this.style.height = (this.scrollHeight+15)+'px';
  });
});

function copyToHiddenField(response_id) {
  console.log(response_id)
  $("#response" + response_id + "hidden").val($("#response" + response_id + "textarea").val())
}
