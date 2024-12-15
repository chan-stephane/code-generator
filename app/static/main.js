function load_copyright(){
    $('#copyright').text(` © ${new Date().getFullYear()} Stéphane CHAN HIOU KONG`);
}

function update_type(){
    var el = event.target;
    console.log(el.value);
    if (el.value == 'bar-code'){
        $('#background').attr('disabled','disabled');
        $('#foreground').attr('disabled','disabled');
        $('#form-code').attr('disabled','disabled');
    }else{
        $('#background').removeAttr('disabled');
        $('#foreground').removeAttr('disabled');
        $('#form-code').removeAttr('disabled');
    }
}

function isHexadecimal(str) {
    const hexPattern = /^#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})$/;
    return hexPattern.test(str);
}

function isValidForm(str){
    return ['square','gapped_square','circle','rounded','vertical_bar','horizontal_bar'].includes(str);
}

function generate(){
    var type_code = $('#type-code').find(":selected").val();
    var data = $('#data').val();
    var endpoints = window.location.origin;
    var background = '#ffffff';
    var color = '#000000';
    var form = 'square';
    var data_formatted = {
        data:data
    };
    if(type_code == 'qr-code'){
        let bg_temp = $('#background').val();
        let color_temp = $('#foreground').val();
        let form_temp = $('#form-code').val();
        
        data_formatted.bg_color = (isHexadecimal(bg_temp)) ? bg_temp : background;
        data_formatted.color = (isHexadecimal(color_temp)) ? color_temp : color;
        data_formatted.style_points = (isValidForm(form_temp)) ? form_temp : form;
    }
    console.log(data_formatted);
    $.ajax({
        url: endpoints + "/" + type_code + "/generate",
        type: "POST",
        data: JSON.stringify(data_formatted),
        contentType: "application/json",
        xhrFields: {
            responseType: "blob"
        },
        success: function(response) {
            var url = URL.createObjectURL(response);
            Toastify({
                text: "Generated successfully",
                backgroundColor: "rgb(75, 230, 134)",
                close: true
            }).showToast();
            var img = $('<img>').attr('src',url).addClass('w-50 h-50');
            $('#img-div').append(img);
            var downloadButton = $('<a>').attr({
                href: url,
                id:'btn-dwn',
                download: 'code.png',    
                class: 'ml-4 mt-2 px-4 py-2 bg-indigo-600 text-white rounded-full inline-flex items-center justify-center'
            }).text('Download Image');
            if ($('#btn-dwn').length > 0) {
                $('#btn-dwn').remove();
            }
            $('#btn').after(downloadButton);
            $('#img-div').empty().append(img);
        },
        error: function(xhr, status, error) {
            if ($('#btn-dwn').length > 0) {
                $('#btn-dwn').remove();
            }
            Toastify({
                text: "Error on generate your image",
                backgroundColor: "rgb(230, 108, 81)",
                close: true
            }).showToast();
        }
    });
}

$(document).ready(function() {
    load_copyright();
});