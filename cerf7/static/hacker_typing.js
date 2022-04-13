let field = document.getElementById("message_field");
let msg = "";

let i = 0;
let options = ["я большой фанат группы поддержки фпми", "ФОПФ отдельная страна внутри МФТИ\n" +
"Мой бро с ФБК, это жёстче ИГИЛ\n" +
"ФОПФ — это колыбель Ра\n" +
"Шестое общежитие (Фейс) — это Иремель 2\n" +
"Иремель 2, ублюдок!", "Сука, это Антихайп ФОПФ резерв, конвей и хай\n" +
"И агент ФПМИ отсосёт наши хуи\n" +
"Видишь агента — хуярь топором, Валера Киселёв горд нами\n" +
"Мой член не умеет брать анализы на ковид, но он в твоей гортани", "Привет. Это мы ебёмся. Это Вы и я. Мы трахаемся. Занимаемся любовью. Половой акт. Вы и я. Мой член совершил проникновение внутрь Вашей киски. До свидания. Привет. Это мы ебёмся. Это Вы и я. Мы трахаемся. Занимаемся любовью. Половой акт. Вы и я. Мой член совершил проникновение внутрь Вашей киски. До свидания. Привет. Это мы ебёмся. Это Вы и я. Мы трахаемся. Занимаемся любовью. Половой акт. Вы и я. Мой член совершил проникновение внутрь Вашей киски. До свидания."];
// options will be reworked to become an array of objects that correspond to plot events. it won't change much though
let isFinished = false;
msg = options[0];

field.addEventListener("keydown", function (e) {
    if (!isFinished) {
        e.preventDefault(); // backspace will only work if the message is finished
    }
    msg = updateText(msg); // update text on key press
});

function updateText(remainingMessage, typingSpeed = 3, speedDispersion = 3) {
    let typeCharacters = Math.round(typingSpeed + Math.random() * speedDispersion); // self explanatory
    if (typeCharacters >= remainingMessage.length) {
        field.value += remainingMessage;
        isFinished = true;
        remainingMessage = "";
    } else {
        field.value += remainingMessage.slice(0, typeCharacters);
        remainingMessage = remainingMessage.slice(typeCharacters);
    }
    if (field.value === "" && isFinished) {
        // message was typed and deleted, time for a new one
        i++;
        i = i % options.length; // we cycle through
        remainingMessage = options[i];
        isFinished = false;
    }
    return remainingMessage
}