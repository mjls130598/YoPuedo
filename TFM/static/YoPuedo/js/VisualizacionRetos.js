function cambiarColorCuerpo(id, content){
    switch(id){
        case "general":
            document.getElementById(content).style.backgroundColor = "#F7C985";
            document.getElementById(content).style.borderColor = "#F7C985";
        break;
        case "etapas":
            document.getElementById(content).style.backgroundColor = "#CAE8A6";
            document.getElementById(content).style.borderColor = "#CAE8A6";
        break;
        case "participantes":
            document.getElementById(content).style.backgroundColor = "#BBF1F7";
            document.getElementById(content).style.borderColor = "#BBF1F7";
        break;
        case "animadores":
            document.getElementById(content).style.backgroundColor = "#F0CEF6";
            document.getElementById(content).style.borderColor = "#F0CEF6";
        break;
        case "etapa-1":
            document.getElementById(content).style.backgroundColor = "#BCA5E5";
            document.getElementById(content).style.borderColor = "#BCA5E5";
        break;
        case "etapa-2":
            document.getElementById(content).style.backgroundColor = "#9BABFF";
            document.getElementById(content).style.borderColor = "#9BABFF";
        break;
        case "etapa-3":
            document.getElementById(content).style.backgroundColor = "#CAC9F3";
            document.getElementById(content).style.borderColor = "#CAC9F3";
        break;
        case "etapa-4":
            document.getElementById(content).style.backgroundColor = "#FCC2EF";
            document.getElementById(content).style.borderColor = "#FCC2EF";
        break;
        case "etapa-5":
            document.getElementById(content).style.backgroundColor = "#FD79A7";
            document.getElementById(content).style.borderColor = "#FD79A7";
        break;
        case "pruebas":
            document.getElementById(content).style.backgroundColor = "#FFD8D6";
            document.getElementById(content).style.borderColor = "#FFD8D6";
        break;
        case "animos":
            document.getElementById(content).style.backgroundColor = "#DAFBF8";
            document.getElementById(content).style.borderColor = "#DAFBF8";
        break;
    }
}

function cambiarPestana(id, content){
    elemento = document.getElementById(id + "-tab");
    $('#tab-pasos button[aria-controls="' + id + '"]').tab('show');
    elemento.classList.remove("d-none");
    cambiarColorCuerpo(id, content);
}

function cambiarPestanaEtapa(id, content){
    $('#tab-etapas button[aria-controls="' + id + '"]').tab('show');
    cambiarColorCuerpo(id, content);
}