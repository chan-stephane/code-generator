function update_type(){
    var el = event.target;
    if (el.value == 'bar-code'){
        $('#background').attr('disabled','disabled');
        $('#foreground').attr('disabled','disabled');
        $('#form-code').attr('disabled','disabled');
        $('#image-link').attr('disabled','disabled');
    }else{
        $('#background').removeAttr('disabled');
        $('#foreground').removeAttr('disabled');
        $('#form-code').removeAttr('disabled');
        $('#image-link').removeAttr('disabled');
    }
}

function initializeMode(){
    $('input[name="mode"]').on('change', function () {
        const selectedMode = $(this).val();
        if (selectedMode === 'generate') {
            $('#form-read').removeClass().addClass('hidden');
            $('#form-generate').removeClass();
            $('#img-div').empty();
        } else if (selectedMode === 'read') {
            $('#form-generate').removeClass().addClass('hidden');
            $('#form-read').removeClass();
            $('#img-div').empty();
        }
    });
}

function isHexadecimal(str) {
    const hexPattern = /^#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})$/;
    return hexPattern.test(str);
}

function isValidForm(str){
    return ['square','gapped_square','circle','rounded','vertical_bar','horizontal_bar'].includes(str);
}

function copy(){
    var el = $(event.target);
    var input = el.closest('div').prev().find('input');
    var textToCopy = input.val();
    el.text('Copied!');
    navigator.clipboard.writeText(textToCopy).then(function() {
        el.text('Copied!');
        Toastify({
            text: "Data copied!",
            backgroundColor: "rgb(75, 230, 134)",
            close: true
        }).showToast();
    }).catch(function(error) {
        el.text('Failed!');
        Toastify({
            text: "Failed to copy!",
            backgroundColor: "rgb(230, 108, 81)",
            close: true
        }).showToast();
    });
}

async function callGenerate(url, data) {
    return new Promise((resolve, reject) => {
        let error_msg = 'Error on generate qr code';
        $.ajax({
            url: url,
            type: "POST",
            data: JSON.stringify(data),
            contentType: "application/json",
            xhr: function() {
                var xhr = new XMLHttpRequest();
                xhr.onreadystatechange = function() {
                    if (xhr.readyState == 2) {
                        if (xhr.status == 200) {
                            xhr.responseType = "blob";
                        } else {
                            xhr.responseType = "json";
                        }
                    }
                    if (xhr.readyState == 4){
                        if (xhr.response && xhr.response.error) {
                            error_msg = xhr.response.error;
                        }
                    }
                };
                return xhr;
            },
            success: function(response) {
                resolve(response);
            },
            error: function(xhr, status, error) {
                reject(error_msg);
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

function loadResult(result){
    result.forEach(el => {
        var div = $('<div>').addClass('flex items-center gap-x-3 p-2');
        var img = $('<img>').attr({
            src:`data:image/jpeg;base64, ${el.image_base64}`,
            class: 'w-16 h-16'
        });
        var div_text = $('<div>').addClass('ml-5');
        var text = $('<input>').attr({
            class: 'w-full p-4 text-gray-800 bg-white disabled:opacity-80 border rounded-md shadow-sm block focus:border-indigo-600 font-medium',
            type: 'text',
            value: el.text,
            disabled: 'disabled'
        });
        var div_copy = $('<div>').addClass('ml-5');
        var copy = $('<button>').attr({
            class:'p-4 bg-indigo-600 text-white rounded-md',
            onclick:'copy()'
        }).text('Copy');
        div_text.append(text);
        div_copy.append(copy);
        div.append(img);
        div.append(div_text);
        div.append(div_copy);
        $('#img-div').append(div);
    });
}

async function read(){
    loaderComponent();
    var formData = new FormData();
    var fileInput = $('#image-file')[0];
    if (fileInput.files.length > 0) {
        var file = fileInput.files[0];
        var url = window.location.origin + "/read";
        var validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        if (validTypes.indexOf(file.type) === -1) {
            Toastify({
                text: "Please upload a valid image file (JPEG, PNG).",
                backgroundColor: "rgb(230, 108, 81)",
                close: true
            }).showToast();
            $('#img-div').empty();
            return;
        }
        formData.append('file', file);
        $.ajax({
            url: url,
            type: "POST",
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                if(response.length > 0){
                    $('#img-div').empty();
                    loadResult(response);
                    Toastify({
                        text: "Reading code successfully",
                        backgroundColor: "rgb(75, 230, 134)",
                        close: true
                    }).showToast();
                }else{
                    Toastify({
                        text: "No qr code or bar code found in the image.",
                        backgroundColor: "rgb(230, 108, 81)",
                        close: true
                    }).showToast();
                    $('#img-div').empty();
                }
            },
            error: function(xhr, status, error) {
                Toastify({
                    text: error,
                    backgroundColor: "rgb(230, 108, 81)",
                    close: true
                }).showToast();
                $('#img-div').empty();
            }
        });
    }else{
        Toastify({
            text: "Please upload an image file.",
            backgroundColor: "rgb(230, 108, 81)",
            close: true
        }).showToast();
        $('#img-div').empty();
    }
}

async function generate(){
    loaderComponent()
    var type_code = $('#type-code').find(":selected").val();
    var data = $('#data').val();
    var base_url = window.location.origin;
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
        data_formatted.image_url = $('#image-link').val();
    }
    try {
        const response = await callGenerate(base_url + "/" + type_code + "/generate", data_formatted);
        var url = URL.createObjectURL(response);
        var url_download = url;
        if(type_code == 'qr-code'){
            const response_download = await callGenerate(base_url + "/" + type_code + "/download", data_formatted);
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
        $('#img-div').empty();
        if ($('#btn-dwn').length > 0) {
            $('#btn-dwn').remove();
        }
        Toastify({
            text: error,
            backgroundColor: "rgb(230, 108, 81)",
            close: true
        }).showToast();
    }
}

$(document).ready(function() {
    load();
    initializeMode();
});