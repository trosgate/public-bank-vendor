// Coundown timer begins

let Clock = {
    totalSeconds: 0,
    start: function () {
      if (!this.interval) {
          var self = this;
          function pad(val) { return val > 9 ? val : "0" + val; }
          this.interval = setInterval(function () {
            self.totalSeconds += 1;
  
            document.getElementById("days").innerHTML = pad(Math.floor(self.totalSeconds / (60 *60 * 24)));
            document.getElementById("hours").innerHTML = pad(Math.floor(self.totalSeconds / (60 *60) % 24));
            document.getElementById("minutes").innerHTML = pad(Math.floor(self.totalSeconds / 60 % 60));
            document.getElementById("seconds").innerHTML = pad(parseInt(self.totalSeconds % 60));
        
        }, 1000);
      }
    },
  
    reset: function () {
      Clock.totalSeconds = null; 
      clearInterval(this.interval);
        document.getElementById("days").innerHTML = "00";
        document.getElementById("hours").innerHTML = "00";
        document.getElementById("minutes").innerHTML = "00";
        document.getElementById("seconds").innerHTML = "00";
    
        delete this.interval;
    },
    
    pause: function () {
      clearInterval(this.interval);
      delete this.interval;
    },

    resume: function () {
        this.start();
    },
  

  };
  
  
  document.getElementById("startButton").addEventListener("click", function () { Clock.start(); });
  document.getElementById("pauseButton").addEventListener("click", function () { Clock.pause(); });
  document.getElementById("resumeButton").addEventListener("click", function () { Clock.resume(); });
  document.getElementById("resetButton").addEventListener("click", function () { Clock.reset(); });
  
