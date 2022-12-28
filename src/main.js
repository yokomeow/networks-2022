function getRandomInt(max) {
    return Math.floor(Math.random() * Math.floor(max));
}

let colors = ['is-info', 'is-success', 'is-warning', 'is-danger', 'is-link'];

let begin = document.querySelector(".begin");
let progress = document.getElementById("prog");
let buttons = document.querySelector('.buttons');
let txt = document.getElementById('txt');

let length = 0;
let letters = {};

let counter = 0;

const url='http://0.0.0.0:5555';

function drawBoard() {
    fetch(url)
      .then(response => response.json())
      .then(json => {
        console.log('parsed json', json);
        length = json['length'];
        letters = json['letters'];
        //let rand = getRandomInt(colors.length);
        for (let index = 0; index < length; index++) {
            //console.log(`<button class='game-button button is-large ${colors[rand]}' id='${plain["words"][index]}'>${plain["words"][index]}</button>`);
            //if (json['attempts'] == 22) alert('Congrats! Now the AI will begin to pick up words for you!');
            if (json['attempts'] > 21){
                progress.remove();
                txt.innerText = "Keep training!";
            } else {
                progress.value = json['attempts'];
            }
            buttons.insertAdjacentHTML("beforeend",
                `<button class='game-button button is-large is-info' id='${json["words"][index]}'>${json["words"][index]}</button>`);
        }
      })
}


drawBoard();
begin.style.display = "none";
Game();


function Game() {
    document.addEventListener('keyup', press);
}


var count_right = 0;

var errors_count = 0;

let errs = [];

let en_letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

function press(e) {

    let elements_arr = document.querySelectorAll(".game-button");

    if (e.key == elements_arr[counter].id) {
        if (e.key != ' ') {
            elements_arr[counter].style.backgroundColor="#25fd80";
            count_right++; //  считаем правильные ответы
        } else {
            elements_arr[counter].style.backgroundColor="#25fd80";
        }

    } else {
        if (en_letters.indexOf(e.key) >= 0){
            errors_count++; // считаем ошибки
            elements_arr[counter].style.backgroundColor="#fd3232";
            errs.push(elements_arr[counter].id);
        }
        if (elements_arr[counter] == ' ') {
            elements_arr[counter].style.backgroundColor="#fd3232";
        }
    }
    counter++;
    if (counter == length){
        //document.location.reload();
        RestartGame()
    }
}

function send_results() {
    let json = {};
    json['letters'] = letters;
    json['mistakes'] = errs;

    console.log(json);

    var xhr = new XMLHttpRequest();
    xhr.open("POST", url+'/submit', true);
    xhr.setRequestHeader("Content-Type", "application/json");

    console.log(json);

    xhr.send(JSON.stringify(json));
}

function RestartGame() {

    let gb = document.querySelectorAll(".game-button");
    gb.forEach(el => el.remove());

    console.log(errs);

    counter = 0;

    send_results();
    console.log('results sent!');

    count_right = 0;
    errors_count = 0;
    drawBoard();

}
