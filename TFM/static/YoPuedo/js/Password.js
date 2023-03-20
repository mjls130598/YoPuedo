// Función para escribir la contraseña en el input indicado
function escribirPassword(input, value){
    inputValue = document.getElementById(input).value;
    if((inputValue.length + value.length) < 16){
      if(inputValue)
        document.getElementById(input).value += value;
      else
        document.getElementById(input).value = value;
    }
}

// Botón para mostrar/ocultar contraseña en imágenes
function cambiarVisibilidad(id){
    var visibilidad = document.getElementById(id).style.display;
    if(visibilidad == "none")
      document.getElementById(id).style.display="block";
    else
      document.getElementById(id).style.display="none";
}