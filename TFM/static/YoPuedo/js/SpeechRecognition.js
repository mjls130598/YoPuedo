// MÉTODO QUE REALIZA EL RECONOCIMIENTO DE VOZ

// Variable para guardar el ID del input donde va a escribir
var inputSpeech = "";

// Variable booleana que indica si está activo o no el speech recognition
var encendido = false;

// 1º Comprobamos que se puede lanzar en ese navegador/dispositivo
if (!('webkitSpeechRecognition' in window)) {
    alert("No puede utilizar el micrófono en este navegador o dispositivo.");
}

// 2º Creamos y configuramos la instancia de SpeechRecognition
var recognition = new webkitSpeechRecognition();
recognition.continuous = true;
recognition.interimResults = true;
recognition.lang = "es-ES";

// 3º Creamos las acciones que se deben realizar si ocurre un error
recognition.onerror = function(event) {
    console.error(event);
};

// 4º Creamos las acciones que se deben realizar cuando se comienza la grabación
recognition.onstart = function() {
    console.log('Comienza el reconocimiento de voz');
};

// 5º Creamos las acciones que se deben realizar cuando se termina la grabación
recognition.onend = function() {
    console.log('Termina el reconocimiento de voz');
};

// 6º Creamos las acciones que se deben realizar cuando se recibe un resultado
recognition.onresult = function(event) {
    var interim_transcript = '';
    var final_transcript = '';

    for (var i = event.resultIndex; i < event.results.length; ++i) {
        // Verify if the recognized text is the last with the isFinal property
        if (event.results[i].isFinal) {
            final_transcript += event.results[i][0].transcript;
        } else {
            interim_transcript += event.results[i][0].transcript;
        }
    }

    // Choose which result may be useful for you

    console.log("Interim: ", interim_transcript);

    console.log("Final: ",final_transcript);

    console.log("Simple: ", event.results[0][0].transcript);

    document.getElementById(inputSpeech).value = final_transcript;
};

// Método que activa/apada el reconocimiento de voz desde el HTML
function reconocimientoVoz(input){

    inputSpeech = input;

    if(encendido){
        console.log("Apagamos reconocimiento");
        recognition.stop();
    }

    else{
        console.log("Activamos reconocimiento");
        recognition.start();
    }
}