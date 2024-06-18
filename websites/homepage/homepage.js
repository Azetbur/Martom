var INCREMENT = 2.5; // Assuming 5s total animation time, so half is 2.5s
let TOTAL_ANIMATION_TIME = (9 - 1) * INCREMENT * 1000 + 5000;

// Enum indicating in which state the "lights" are currently in
const LightState = {
    ON: "on",
    OFF: "off",
    TURNING_ON: "turning on",
    TURNING_OFF: "turning off",
};

async function sendPostRequest(url) {
    const response = await fetch(url, {
        method: 'POST'
    });
}

class LightController {
    constructor(lightbulbButton) {

        console.log("LightController constructor");

        // Sets the light initial state of lights to off.
        this.currentState = LightState.OFF;

        // This timeout is used to set the light state to on/off after the "turning on/off" phase.
        this.timeout_changeState = null;

        // Initializing an object of the class which represents the "fast-forward"/skip button
        this.lightbulbButton = lightbulbButton;

        // Initializing an object of the class which represents the actual lights
        this.lights = new Lights();
    }

    press() {

        sendPostRequest('/press_bulb')

        switch (this.currentState) {
            case LightState.OFF:

                this.currentState = LightState.TURNING_ON;
                console.log("Changing 'LightState' to 'TURNING_ON'.");

                this.timeout_changeState = setTimeout(() => {
                    this.currentState = LightState.ON;

                    this.lightbulbButton.offerSkip(false);
                    this.lightbulbButton.showRays(false);
                }, TOTAL_ANIMATION_TIME);

                this.lightbulbButton.offerSkip(true);
                this.lights.turnOn();

                break;
            case LightState.TURNING_ON:

                this.currentState = LightState.ON;
                console.log("Changing 'LightState' to 'ON'.");

                clearTimeout(this.timeout_changeState);

                this.lightbulbButton.offerSkip(false);
                this.lightbulbButton.showRays(false);
                this.lights.jumpOnOff();

                break;
            case LightState.ON:

                this.currentState = LightState.TURNING_OFF;
                console.log("Changing 'LightState' to 'TURNING_OFF'.");

                this.timeout_changeState = setTimeout(() => {
                    this.currentState = LightState.OFF;

                    this.lightbulbButton.offerSkip(false);
                    this.lightbulbButton.showRays(true);
                }, TOTAL_ANIMATION_TIME);

                this.lightbulbButton.offerSkip(true);
                this.lights.turnOff();

                break;
            case LightState.TURNING_OFF:

                this.currentState = LightState.OFF;
                console.log("Changing 'LightState' to 'OFF'.");

                clearTimeout(this.timeout_changeState);

                this.lightbulbButton.offerSkip(false);
                this.lightbulbButton.showRays(true);
                this.lights.jumpOnOff();

                break;
        }
    }
}

class LightbulbButton {
    constructor(lightbulb, lightbulb_rays, skip_overlay_image) {

        this.bulb = document.getElementById(lightbulb);
        this.rays = document.getElementById(lightbulb_rays);
        console.log(lightbulb_rays);
        console.log('log');
        this.skip_img = document.getElementById(skip_overlay_image);

        this.lightController = new LightController(this);

        try {
            document.querySelector("#b1").addEventListener("click", (event) => {
                event.preventDefault();
                event.stopPropagation();
                console.log("pressed");
                this.lightController.press();
            });
        } catch (error) {
            console.error("Register listener for #b1", error);
            alert("Nastala chyba.");
        }
    }

    offerSkip(offer) {
        if (offer) {
            this.skip_img.style.opacity = "1";
        } else {
            this.skip_img.style.opacity = "0";
        }
    }

    showRays(show) {

        console.log("In showRays");

        if (show) {
            this.rays.style.opacity = "1";
        } else {
            this.rays.style.opacity = "0";
        }
    }
}

class Lights {
    constructor() {
        // Manually specifying each light element
        this.top_elements = [
            document.getElementById("s8-top"),
            document.getElementById("s2-top"),
            document.getElementById("s1-top"),
            document.getElementById("s7-top"),
            document.getElementById("s6-top"),
            document.getElementById("s5-top"),
            document.getElementById("s4-top"),
            document.getElementById("s3-top"),
            document.getElementById("s9-top"),
        ];

        // Manually specify each element
        this.bottom_elements = [
            document.getElementById("s8-bottom"),
            document.getElementById("s2-bottom"),
            document.getElementById("s1-bottom"),
            document.getElementById("s7-bottom"),
            document.getElementById("s6-bottom"),
            document.getElementById("s5-bottom"),
            document.getElementById("s4-bottom"),
            document.getElementById("s3-bottom"),
            document.getElementById("s9-bottom"),
        ];
    }
    
    turnOn() {
        this.top_elements.forEach((element, index) => {
            let delay = index * INCREMENT;
            
            element.style.transition = 'box-shadow 5s ease';
            element.style.transitionDelay = `${delay}s`;

            element.classList.add("shadowTop");
        });

        this.bottom_elements.forEach((element, index) => {
            let delay = index * INCREMENT;

            element.setAttribute("data-clicked", "true");
            element.style.transition = 'box-shadow 5s ease';
            element.style.transitionDelay = `${delay}s`;

            element.classList.add("shadowBottom");
        });
    }

    turnOff() {
        this.top_elements.reverse();
        this.bottom_elements.reverse();

        this.top_elements.forEach((element, index) => {
            let delay = index * INCREMENT;
            
            element.style.transition = 'box-shadow 5s ease';
            element.style.transitionDelay = `${delay}s`;

            element.classList.remove('shadowTop');
        });

        this.bottom_elements.forEach((element, index) => {
            let delay = index * INCREMENT;

            element.removeAttribute("data-clicked", "true");
            element.style.transition = 'box-shadow 5s ease';
            element.style.transitionDelay = `${delay}s`;

            element.classList.remove('shadowBottom');
        });

        this.top_elements.reverse();
        this.bottom_elements.reverse();
    }

    // Immidiatelly finish the transition currently in progress
    jumpOnOff() {

        this.top_elements.forEach(element => {
        
            // Overwrite transition to none so it stops
            element.style.transition = 'none';

        });
    
        this.bottom_elements.forEach(element => {

            // Overwrite transition to none so it stops
            element.style.transition = 'none';

        });
    }

}



document.addEventListener("DOMContentLoaded", function () {
    let lightbulbButton = new LightbulbButton(
        "lightbulb_image",
        "lightbulb_ray_image",
        "skip_image",
    );
});

/* ---------------------------------------------------------------*/
/* ====  Manually controlling each light element on click  ====  */
/* -------------------------------------------------------------*/

class LightHolder {
        constructor(bottomLight, topLight) {
        
            this.bottomLight = bottomLight;
            this.topLight = topLight;
            
        }

        click() {
            this.bottomLight.addEventListener("click", (event) => {
                event.stopPropagation();
    
                if(!this.bottomLight.dataset.clicked){   
                    this.bottomLight.setAttribute("data-clicked", "true");
    
                    console.log("Changing 'LightState' to 'TURNING_ON'.");
    
                    this.bottomLight.classList.add('shadowBottom');
                    this.bottomLight.style.transition = 'box-shadow 5s ease';
            
                    this.topLight.classList.add('shadowTop');
                    this.topLight.style.transition = 'box-shadow 5s ease';    
                }else{
                    this.bottomLight.removeAttribute("data-clicked", "true");
    
                    console.log("Changing 'LightState' to 'TURNING_OFF'.");
    
                    this.bottomLight.removeAttribute("style");
                    this.bottomLight.classList.remove('shadowBottom');

                    this.topLight.removeAttribute("style");
                    this.topLight.classList.remove('shadowTop');
                }
            });
        }
    }

    const LightHolder9 = new LightHolder(document.getElementById("s9-bottom"),document.getElementById("s9-top")); LightHolder9.click();
    const LightHolder8 = new LightHolder(document.getElementById("s8-bottom"),document.getElementById("s8-top")); LightHolder8.click();
    const LightHolder7 = new LightHolder(document.getElementById("s7-bottom"),document.getElementById("s7-top")); LightHolder7.click();
    const LightHolder6 = new LightHolder(document.getElementById("s6-bottom"),document.getElementById("s6-top")); LightHolder6.click();
    const LightHolder5 = new LightHolder(document.getElementById("s5-bottom"),document.getElementById("s5-top")); LightHolder5.click();
    const LightHolder4 = new LightHolder(document.getElementById("s4-bottom"),document.getElementById("s4-top")); LightHolder4.click();
    const LightHolder3 = new LightHolder(document.getElementById("s3-bottom"),document.getElementById("s3-top")); LightHolder3.click();
    const LightHolder2 = new LightHolder(document.getElementById("s2-bottom"),document.getElementById("s2-top")); LightHolder2.click();
    const LightHolder1 = new LightHolder(document.getElementById("s1-bottom"),document.getElementById("s1-top")); LightHolder1.click();

    /* ---------------------------------------------------------------*/
    /* ============ Code to make the Clock keep tiking ============  */
    /* -------------------------------------------------------------*/

    function startTime() {
        var today = new Date();
        var hr = today.getHours();
        var min = today.getMinutes();
        var sec = today.getSeconds();
        /*
        //12 hour format
        ap = (hr < 12) ? "<span>AM</span>" : "<span>PM</span>";
        hr = (hr == 0) ? 12 : hr;
        hr = (hr > 12) ? hr - 12 : hr;
        */
        //Add a zero in front of numbers<10
        hr = checkTime(hr);
        min = checkTime(min);
        sec = checkTime(sec);
        document.getElementById("clock").innerHTML = hr + ":" + min;
        
        var months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'];
        var days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        var curWeekDay = days[today.getDay()];
        var curDay = today.getDate();
        var curMonth = months[today.getMonth()];
        var curYear = today.getFullYear();
        var date = curWeekDay+", "+curDay+"/"+curMonth;
        document.getElementById("date").innerHTML = date;
        
        var time = setTimeout(function(){ startTime() }, 500);
    }
    function checkTime(i) {
        if (i < 10) {
            i = "0" + i;
        }
        return i;
    }

    /* ----------------------------------------------------------------------------*/
    /* ====  Slide up/down Timer Page on clicking the timer/back button  ====  */
    /* --------------------------------------------------------------------------*/
    

    class SlideUp {
        constructor(button, overlayer, innerlayer, blurrer) {
            this.button = button;
            this.overlayer = overlayer;
            this.innerlayer = innerlayer;
            this.blurrer = blurrer;
        }

        click() {
            this.button.addEventListener("click", (event) => {

                event.stopPropagation();
                if(!this.overlayer.dataset.clicked){
                    console.log("Timer page opened");

                    this.overlayer.setAttribute("data-clicked", "true");

                    this.overlayer.style.animation = 'transitionIn 1.6s ease forwards';
                    this.innerlayer.style.display = 'block';
                //    this.blurrer.style.display = 'none';
                }else{
                }
            });
        }
    }

    const SlideUp1 = new SlideUp (document.getElementById("b2"),document.getElementById("over-layer"),document.getElementById("inner-layer"),document.getElementById("bb1")); SlideUp1.click();
    
    class SlideDown {
        constructor(buttonL, overlayer, blurrer) {
            this.buttonL = buttonL;
            this.overlayer = overlayer;
            this.blurrer = blurrer;
        }

        click() {
            let TimePick_POPUP = document.getElementsByClassName("TimePick_POPUP");
            this.buttonL.addEventListener("click", (event) => {
                for(let i = 0; i < TimePick_POPUP.length; i++) {
                    TimePick_POPUP[i].style.display = "none";
                }
                event.stopPropagation();
                if(this.overlayer.dataset.clicked){
                    this.overlayer.removeAttribute("data-clicked", "true");
                    
                    console.log("Timer page closed");
                    this.overlayer.style.animation = 'transitionOut 1.3s ease forwards';
                //    this.blurrer.style.display = 'block';
                }else{
                }
            });
        }
    }

    const SlideDown1 = new SlideDown (document.getElementById("go-back"),document.getElementById("over-layer"),document.getElementById("bb1")); SlideDown1.click();


    