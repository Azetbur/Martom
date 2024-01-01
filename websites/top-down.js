document.addEventListener("DOMContentLoaded", function () {
    var bulb_with_rays_img = document.getElementById("i1-turnOn");
    var bulb_wo_rays_img = document.getElementById("i1-turnOff");
    var skip_img = document.getElementById("skip-image");

    // Pre-setting the initial state of images via JavaScript
    bulb_with_rays_img.style.opacity = "1";
    bulb_wo_rays_img.style.opacity = "0";

    var onButtonDisabled = false; // Track whether the lightbulb button is disabled

    var button = document.getElementById("b1");

    // Manually specify each element
    var top_elements = [
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
    var bottom_elements = [
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

    var shadowShown = false;

    var increment = 2.5; // Assuming 5s total animation time, so half is 2.5s

    button.addEventListener("click", function () {
        // Calculate total animation time
        // Last element's delay + animation duration (assuming 5s total per element)
        var totalAnimationTime =
            (top_elements.length - 1) * increment * 1000 + 5000;

        if (true) {
            // Animate the lightbulb button
            if (bulb_with_rays_img.style.opacity == "1") {
                console.log("if");
                bulb_with_rays_img.style.opacity = "0";
                bulb_wo_rays_img.style.opacity = "1";
            } else {
                console.log("else");
                bulb_with_rays_img.style.opacity = "1";
                bulb_wo_rays_img.style.opacity = "0";
            }

            // Execute the code for button click
            console.log("Button clicked");

            // Disable the button at the start of the animation
            onButtonDisabled = true;

            if (!shadowShown) {
                top_elements.forEach((element, index) => {
                    let delay = index * increment; // Half of your animation time (assuming 5s total)

                    element.style.setProperty("--animation-delay", `${delay}s`);

                    element.classList.add("shadowTop");
                });

                bottom_elements.forEach((element, index) => {
                    let delay = index * increment; // Half of your animation time (assuming 5s total)

                    element.style.setProperty("--animation-delay", `${delay}s`);

                    element.classList.add("shadowBottom");
                });
            } else {
                top_elements.reverse();
                bottom_elements.reverse();

                top_elements.forEach((element, index) => {
                    let delay = index * increment;

                    element.style.setProperty("--animation-delay", `${delay}s`);

                    element.classList.remove("shadowTop");
                });

                bottom_elements.forEach((element, index) => {
                    let delay = index * increment;

                    element.style.setProperty("--animation-delay", `${delay}s`);

                    element.classList.remove("shadowBottom");
                });

                top_elements.reverse();
                bottom_elements.reverse();
            }

            shadowShown = !shadowShown;

            // Re-enable the button after the total animation time has passed
            setTimeout(function () {
                onButtonDisabled = false;
                console.log("Button re-enabled");
            }, totalAnimationTime);
        }
    });
});
