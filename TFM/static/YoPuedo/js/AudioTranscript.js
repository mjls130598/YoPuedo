// MÉTODO PARA TRANSCRIBIR LOS AUDIOS Y LOS VÍDEOS A TEXTO

audioURL = "https://mariajesuslopez.pythonanywhere.com/"
const APIKey = "69e712f90368467fa893f3b024fb0b42"
h6ID = ""
const refreshInterval = 5000

// Creamos conexión con el servidor que transcribe
const assembly = axios.create({
  baseURL: "https://api.assemblyai.com/v2",
  headers: {
    authorization: APIKey,
    "content-type": "application/json",
  },
})

const getTranscript = async () => {
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
    } else if (transcriptStatus === "completed") {
      console.log("\nTranscription completed!\n")
      let transcriptText = transcript.data.text
      console.log(`Your transcribed text:\n\n${transcriptText}`)
      document.getElementById(h6ID).textContent = transcriptText;
      clearInterval(checkCompletionInterval)
    }
  }, refreshInterval)
}

function obtenerAudio(audioUrl, id){
    audioURL += audioUrl
    h6ID = id
    console.log("Comenzamos con la transcripción")
    getTranscript()
}