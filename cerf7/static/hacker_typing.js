let field = document.getElementById("message_field");

let msg = "Привет. Это мы ебёмся. Это Вы и я. Мы трахаемся. Занимаемся любовью. Половой акт. Вы и я. Мой член совершил проникновение внутрь Вашей киски. До свидания. Привет. Это мы ебёмся. Это Вы и я. Мы трахаемся. Занимаемся любовью. Половой акт. Вы и я. Мой член совершил проникновение внутрь Вашей киски. До свидания. Привет. Это мы ебёмся. Это Вы и я. Мы трахаемся. Занимаемся любовью. Половой акт. Вы и я. Мой член совершил проникновение внутрь Вашей киски. До свидания."
field.addEventListener("keydown", function (e) {
    msg = updateText(msg)
});

function updateText(remainingMessage, typingSpeed = 3) {
    if (remainingMessage.length === 0) {
        return "";
    }
    let typeCharacters = Math.round(typingSpeed + Math.random() * 3);
    if (typeCharacters >= remainingMessage.length) {
        field.value += remainingMessage
        remainingMessage = ""
    } else {
        field.value += remainingMessage.slice(0, typeCharacters)
        remainingMessage = remainingMessage.slice(typeCharacters)
    }
    return remainingMessage
}