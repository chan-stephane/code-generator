function update_type(){
    var el = event.target;
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


async function call(url, data) {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: url,
            type: "POST",
            data: JSON.stringify(data),
            contentType: "application/json",
            xhrFields: {
                responseType: "blob"
            },
            success: function(response) {
                resolve(response);
            },
            error: function(xhr, status, error) {
                reject(error);
            }
        });
    });
}

function load(){
    $('#copyright').text(` © ${new Date().getFullYear()} Stéphane CHAN HIOU KONG`);
}

function loaderComponent(){
    var component = $('<div>').addClass('w-10 h-10 border-4 border-t-blue-500 border-gray-300 rounded-full animate-spin');
    $('#img-div').empty().append(component);
}

async function generate(){
    loaderComponent()
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
    try {
        const response = await call(endpoints + "/" + type_code + "/generate", data_formatted);
        var url = URL.createObjectURL(response);
        var url_download = url;
        if(type_code == 'qr-code'){
            const response_download = await call(endpoints + "/" + type_code + "/download", data_formatted);
            url_download = URL.createObjectURL(response_download);
        }
        Toastify({
            text: "Generated successfully",
            backgroundColor: "rgb(75, 230, 134)",
            close: true
        }).showToast();
        var img = $('<img>').attr('src',url).addClass('w-50 h-50');
        $('#img-div').append(img);
        var downloadButton = $('<a>').attr({
            href: url_download,
            id:'btn-dwn',
            download: 'code_by_code-generator.png',    
            class: 'ml-4 mt-2 px-4 py-2 bg-indigo-600 text-white rounded-full inline-flex items-center justify-center'
        }).text('Download Image');
        if ($('#btn-dwn').length > 0) {
            $('#btn-dwn').remove();
        }
        $('#btn').after(downloadButton);
        $('#img-div').empty().append(img);
    } catch (error) {
        if ($('#btn-dwn').length > 0) {
            $('#btn-dwn').remove();
        }
        Toastify({
            text: "Error on generate your image",
            backgroundColor: "rgb(230, 108, 81)",
            close: true
        }).showToast();
    }
}

$(document).ready(function() {
    load();
});