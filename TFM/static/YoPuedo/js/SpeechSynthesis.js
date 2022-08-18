// MÉTODO DE SÍNTESIS DE VOZ

// Variable que se encarga de la síntesis
var synth = window.speechSynthesis;

function sintesisVoz(elementSpeech){

    // Cogemos el texto del elemento que queremos
    var texto = document.getElementById(elementSpeech).value;

    // "Traducimos" a voz el texto
    var speechUtterance = new SpeechSynthesisUtterance(texto);

    // Seleccionamos el idioma en el que lo tiene que decir (castellano)
    speechUtterance.voice = synth.getVoices()[14];

    // Mandamos al altavoz la "traducción" recogida
     synth.speak(speechUtterance);
}

