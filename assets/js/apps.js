

function openApp(adress, name) {
    // document.getElementById("loading-app-screen").style.display = "block";
    
    // console.log(fullscreen);

    // if (fullscreen == true) {
    //     modalFS = document.getElementById("modFS");
    //     console.log("Vrai");
    //     modalFS.className = "modal-dialog modal-fullscreen";
    // } else {
    //     modalFS = document.getElementById("modFS");
    
    //     modalFS.className = "modal-dialog modal-xl";
    // }

    // const appModal = new bootstrap.Modal('#appModal', {
    //     keyboard: false
    // });
    // document.getElementById("app_name").innerHTML = name;
    // const textes = ["🧠 Traitement en cours...", "🏃‍♂️ Dans les starting-block !", "💻 Opération en cours...", "⏳ Patience, ça charge...", "🤺 On se chauffe !"];
    // const indiceAleatoire = Math.floor(Math.random() * textes.length);
    // document.getElementById("loading-text").innerHTML = textes[indiceAleatoire];
    // appModal.show();
    // const Frame = document.getElementById("app_frame");
    // Frame.src = "http://" + adress + "/";
    // Frame.onload = function() {
    //     console.log("Chargé !");
    //     document.getElementById("loading-app-screen").style.display = "none";
    // };

    new WinBox({
        title: name,
        icon: "/assets/images/logo.png",
        url: "http://" + adress + "/",
        background: "#DCDCDC",
        border: 3,
        class: "my-theme"
    });
}

