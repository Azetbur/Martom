var INCREMENT = 2.5; // Assuming 5s total animation time, so half is 2.5s
let TOTAL_ANIMATION_TIME = (9 - 1) * INCREMENT * 1000 + 5000;

// Enum indicating in which state the "lights" are currently in
const LightState = {
    ON: "on",
    OFF: "off",
    TURNING_ON: "turning on",
    TURNING_OFF: "turning off",
};

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
    constructor(bulb_with_rays_image, bulb_without_rays_image, skip_overlay_image) {
        console.log("created lightbulb button");
        console.log(bulb_with_rays_image);

        this.bulb_with_rays = document.getElementById(bulb_with_rays_image);
        this.bulb_wo_rays = document.getElementById(bulb_without_rays_image);
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
            this.bulb_with_rays.style.opacity = "1";
            this.bulb_wo_rays.style.opacity = "0";
        } else {
            this.bulb_with_rays.style.opacity = "0";
            this.bulb_wo_rays.style.opacity = "1";
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
        "i1-turnOn",
        "i1-turnOff",
        "skip-image"
    );
});
