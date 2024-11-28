const sorjUi = {
    _enableCrt: true,
    isInitialLoad: true, // Track if it's the initial load
    

    toggleCrtEffect() {
      this._enableCrt = !this._enableCrt;
      this.setCrtPreference(this._enableCrt);
      this.updateCrtClassOnElements(false);
      this.updateCrtToggleIcon();
    },

    initCrt() {
      this._enableCrt = this.getCrtPreference();
      this.updateCrtClassOnElements(true); // Pass true to indicate initial load
      this.isInitialLoad = false; // Set to false after initial load completes
      this.updateCrtToggleIcon();
    },

    getCrtPreference() {
      let setting = localStorage.getItem("ENABLE_CRT");
      if (setting === null) {
        setting = "true";
      }
      return JSON.parse(setting);
    },
  
    setCrtPreference(value) {
      localStorage.setItem("ENABLE_CRT", JSON.stringify(value));
    },
  
    updateCrtToggleIcon() {
      const crtToggleIcon = document.getElementById("crt-toggle-icon");
      crtToggleIcon.classList.remove("bi-tv", "bi-tv-fill");
      crtToggleIcon.classList.add(this._enableCrt ? "bi-tv-fill" : "bi-tv");
    },
  
    updateCrtClassOnElements(isInitialLoad) {
      const dialogElements = document.querySelectorAll("dialog");
      const bodyElement = document.body;
  
      if (!isInitialLoad) { // Only animate if not on initial load
        bodyElement.classList.add("crt-fade-out");
        dialogElements.forEach((dialog) => dialog.classList.add("crt-fade-out"));
        
        // Wait for fade-out, then toggle the CRT class and fade-in
        setTimeout(() => {
          bodyElement.classList.toggle("crt", this._enableCrt);
          dialogElements.forEach((dialog) => dialog.classList.toggle("crt", this._enableCrt));
          
          bodyElement.classList.remove("crt-fade-out");
          bodyElement.classList.add("crt-fade-in");
          dialogElements.forEach((dialog) => {
            dialog.classList.remove("crt-fade-out");
            dialog.classList.add("crt-fade-in");
          });
  
          setTimeout(() => {
            bodyElement.classList.remove("crt-fade-in");
            dialogElements.forEach((dialog) => dialog.classList.remove("crt-fade-in"));
          }, 500); // Match the transition duration
        }, 500);
      } else {
        // Directly toggle CRT class without fade on initial load
        bodyElement.classList.toggle("crt", this._enableCrt);
        dialogElements.forEach((dialog) => dialog.classList.toggle("crt", this._enableCrt));
      }
    },

    hideElementWithFadeout(el) {
      el.style.opacity = 1;
    
      let opacity = 1;
      const fadeoutInterval = setInterval(() => {
        opacity -= 0.05;
        el.style.opacity = opacity;
      
      if (opacity <= 0) {
        clearInterval(fadeoutInterval);
        el.style.display = 'none'; 
      }
    }, 50);
  }
};
  
sorjUi.initCrt();

document.addEventListener("DOMContentLoaded", function(event) {
  const crtToggleBtn = document.getElementById("crt-toggle-btn");
  crtToggleBtn.addEventListener("click", () => sorjUi.toggleCrtEffect());

  const msglist = document.querySelector("#messages-list");
  if(msglist) {
    setTimeout(() => {sorjUi.hideElementWithFadeout(msglist)}, 2000);
  }
});
