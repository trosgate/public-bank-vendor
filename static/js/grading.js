
$(document).ready(function(){
 
    $('#id_marks1, #id_marks2, #id_marks3, #id_marks4, #id_marks5, #id_marks6, #id_marks7, #id_marks8, #id_marks9, #id_marks10').change(function(){
        var marks1 = $('#id_marks1').val();
        var marks2 = $('#id_marks2').val();
        var marks3 = $('#id_marks3').val();
        var marks4 = $('#id_marks4').val();
        var marks5 = $('#id_marks5').val();
        var marks6 = $('#id_marks6').val();
        var marks7 = $('#id_marks7').val();
        var marks8 = $('#id_marks8').val();
        var marks9 = $('#id_marks9').val();
        var marks10 = $('#id_marks10').val();
        var grand_total = marks1 * 1 + marks2 * 1 + marks3 * 1 + marks4 * 1 + marks5 * 1 + marks6 * 1 + marks7 * 1 + marks8 * 1 + marks9 * 1 + marks10 * 1
        
        $('#id_applicant_score').text(grand_total);

    });
   
   
});