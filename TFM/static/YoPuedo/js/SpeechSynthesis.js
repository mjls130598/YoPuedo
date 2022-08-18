// MÉTODO DE SÍNTESIS DE VOZ

// Variable que se encarga de la síntesis
var synth = window.speechSynthesis;

function sintesisVoz(elementSpeech){

    // Cogemos el texto del elemento que queremos
    var texto = document.getElementById(elementSpeech).innerHTML;
    console.log("Sabemos el texto que se va a hablar");

    // "Traducimos" a voz el texto
    var speechUtterance = new SpeechSynthesisUtterance(texto);
    console.log("'Traducimos' texto a voz");

    // Seleccionamos el idioma en el que lo tiene que decir (castellano)
    speechUtterance.voice = synth.getVoices()[15];
    console.log("Seleccionamos idioma");

    // Mandamos al altavoz la "traducción" recogida
     synth.speak(speechUtterance);
     console.log("Hablamos texto");
}

