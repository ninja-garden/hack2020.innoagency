"use strict";

var textField = document.getElementById("uid");
var button = document.getElementById("submit_id");
var resultBlock = document.getElementById("user_info");
const get_info_url = "api/v1/get_user_info";

function get_and_fill_data() {
    let uid = textField.value;
    
    if (uid === "") {
        resultBlock.innerHTML = "Введите ID пользователя!";
        return;
    }

    let onSuccess = function(uinfo) {
        let info = "Пользователь найден.<br>" +
            "ID: " + uinfo.id + "<br>";
        if (uinfo.age !== null)
            info += "Возраст: " + uinfo.age + " года.<br>";
        if (uinfo.sex !== null) 
            info += "Пол: " + (uinfo.sex ? "Мужской" : "Женский") + ".<br>";
        if (uinfo.name !== null || uinfo.surname !== null)
            info += "Имя: ";
        if (uinfo.name !== null)
            info += uinfo.name + " ";
        if (uinfo.midname !== null)
            info += uinfo.midname + " ";
        if (uinfo.surname !== null)
            info += uinfo.surname;
        info += "<br>";

        // Tables.
        info += "<div class = \"table\">";
        info += "<div class=\"row header\">";
        info += "<div class=\"cell\">Предпочтения (книги)</div><div class=\"cell\">Рекомендации (книги)</div>";
        info += "</div>";
        if (uinfo.likes_books !== null || uinfo.suggestions_books !== null) {
            info += "<div class=\"row\">";
            info += "<div class=\"cell\">" + (uinfo.likes_books === null ? "<i>Предпочтений не найдено</i>" : uinfo.likes_books) + "</div>"
            info += "<div class=\"cell\">" + (uinfo.suggestions_books === null ? "<i>Рекомендаций не найдено</i>" : uinfo.suggestions_books) + "</div>"
            info += "</div>";
        }
        info += "</div>";

        info += "<div class = \"table\">";
        info += "<div class=\"row header\">";
        info += "<div class=\"cell\">Предпочтения (кружки)</div><div class=\"cell\">Рекомендации (кружки)</div>";
        info += "</div>";
        if (uinfo.likes_books !== null || uinfo.suggestions_books !== null) {
            info += "<div class=\"row\">";
            info += "<div class=\"cell\">" + (uinfo.likes_hobbies === null ? "<i>Предпочтений не найдено</i>" : uinfo.likes_hobbies) + "</div>"
            info += "<div class=\"cell\">" + (uinfo.suggestions_hobbies === null ? "<i>Рекомендаций не найдено</i>" : uinfo.suggestions_hobbies) + "</div>"
            info += "</div>";
        }
        info += "</div>";

        info += "<div class = \"table\">\n";
        info += "<div class=\"row header\">";
        info += "<div class=\"cell\">Предпочтения (мероприятия)</div><div class=\"cell\">Рекомендации (мероприятия)</div>";
        info += "</div>";
        if (uinfo.likes_books !== null || uinfo.suggestions_books !== null) {
            info += "<div class=\"row\">";
            info += "<div class=\"cell\">" + (uinfo.likes_events === null ? "<i>Предпочтений не найдено</i>" : uinfo.likes_events) + "</div>"
            info += "<div class=\"cell\">" + (uinfo.suggestions_events === null ? "<i>Рекомендаций не найдено</i>" : uinfo.suggestions_events) + "</div>"
            info += "</div>";
        }
        info += "</div>";

        resultBlock.innerHTML = info;
    };

    let onFail = function(errData, textStatus, errorThrown ) {
        let info = "Ошибка при получении результата: " + errData.responseJSON.error;
        if (errData.status === 400)
            info += "<br>Перепроверьте ID пользователя.";

        resultBlock.innerHTML = info;
    };

    $.get(get_info_url + "?uid=" + uid)
        .done(onSuccess)
        .fail(onFail);
}

button.addEventListener("click", get_and_fill_data);
