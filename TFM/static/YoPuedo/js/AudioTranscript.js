// MÉTODO PARA TRANSCRIBIR LOS AUDIOS Y LOS VÍDEOS A TEXTO

audioURL = "https://mariajesuslopez.pythonanywhere.com/"
const APIKey = "69e712f90368467fa893f3b024fb0b42"
divID = ""

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
    audio_url: audioURL,
  })

  // Interval for checking transcript completion
  const checkCompletionInterval = setInterval(async () => {
    const transcript = await assembly.get(`/transcript/${response.data.id}`)
    const transcriptStatus = transcript.data.status

    if (transcriptStatus !== "completed") {
      console.log(`Transcript Status: ${transcriptStatus}`)
      document.getElementById(divId).value = transcript.data.text;
    } else if (transcriptStatus === "completed") {
      console.log("\nTranscription completed!\n")
      let transcriptText = transcript.data.text
      console.log(`Your transcribed text:\n\n${transcriptText}`)
      clearInterval(checkCompletionInterval)
    }
  }, refreshInterval)
}

function obtenerAudio(audioUrl, divId){
    audioURL += audioUrl
    divID = divId
    getTranscript()
}