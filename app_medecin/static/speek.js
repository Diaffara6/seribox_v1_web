// speech.js

// Fonction pour effectuer la synthèse vocale
function speak(text) {
    if ('speechSynthesis' in window) {
        const synth = window.speechSynthesis;
        const utterance = new SpeechSynthesisUtterance(text);
        synth.speak(utterance);
    } else {
        alert("L'API Web Speech n'est pas prise en charge dans ce navigateur.");
    }
}
