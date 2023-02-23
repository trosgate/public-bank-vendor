
$(document).ready(function(){

    $('#line_two, #id_line_two_order, #id_line_two_issue, #line_three, #id_line_three_order, #id_line_three_issue, #line_four, #id_line_four_order, #id_line_four_issue').hide()
    $('#inventory-extras').click(function(){
      $('#line_two, #id_line_two_order, #id_line_two_issue').slideToggle(200)
      $('#line_three, #id_line_three_order, #id_line_three_issue').slideToggle(200)
      $('#line_four, #id_line_four_order, #id_line_four_issue').slideToggle(200)
    });
   
});
