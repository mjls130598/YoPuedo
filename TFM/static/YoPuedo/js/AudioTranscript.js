// MÉTODO PARA TRANSCRIBIR LOS AUDIOS Y LOS VÍDEOS A TEXTO

audioURL = "https://mariajesuslopez.pythonanywhere.com/"
const APIKey = "69e712f90368467fa893f3b024fb0b42"
const refreshInterval = 5000

// Creamos conexión con el servidor que transcribe
const assembly = axios.create({
  baseURL: "https://api.assemblyai.com/v2",
  headers: {
    authorization: APIKey,
    "content-type": "application/json",
  },
})

const getTranscript = async (divDivSpinner, elemento, ) => {
  // Sends the audio file to AssemblyAI for transcription
  const response = await assembly.post("/transcript", {
    "audio_url": audioURL,
    "language_code": "es"
  })

  // Interval for checking transcript completion
  const checkCompletionInterval = setInterval(async () => {
    const transcript = await assembly.get(`/transcript/${response.data.id}`)
    const transcriptStatus = transcript.data.status

    if (transcriptStatus !== "completed") {
      console.log(`Transcript Status: ${transcriptStatus}`)
      divDivSpinner.style.display = "flex"

      if (transcriptStatus === "error"){
        elemento.textContent = "Ha ocurrido un error. Inténtelo más tarde";
        elemento.parentNode.removeChild(divDivSpinner)
        elemento.style.color = "red";
        clearInterval(checkCompletionInterval)
      }
    } else if (transcriptStatus === "completed") {
      console.log("\nTranscription completed!\n")
      let transcriptText = transcript.data.text
      console.log(`Your transcribed text:\n\n${transcriptText}`)
      elemento.textContent = transcriptText;
      elemento.style.color = "black";
      elemento.parentNode.removeChild(divDivSpinner)
      clearInterval(checkCompletionInterval)
    }
  }, refreshInterval)
}

function obtenerAudio(audioUrl, id){
    audioURL += audioUrl
    elemento = document.getElementById(id)

    var divDivSpinner = document.createElement("div")
    divDivSpinner.classList.add("d-flex")
    divDivSpinner.classList.add("justify-content-center")
    divDivSpinner.classList.add("align-items-center")
    divDivSpinner.classList.add("h-100")
    divDivSpinner.style.display = "none"

    var divSpinner = document.createElement("div")
    divSpinner.classList.add("spinner-border")
    divSpinner.classList.add("text-primary")
    divSpinner.setAttribute("role", "status")

    var spanSpinner = document.createElement("span")
    spanSpinner.classList.add("sr-only")

    divSpinner.appendChild(spanSpinner)
    divDivSpinner.appendChild(divSpinner)
    elemento.parentNode.insertBefore(divDivSpinner, elemento)

    console.log("Comenzamos con la transcripción")
    getTranscript(divDivSpinner, elemento)
}