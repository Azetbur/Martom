var TimePick = (function () {

    'use strict';
 
    var Constructor = function (element) {

        var globalvar = {};
        globalvar.set_hour = {};
        globalvar.set_minute = {};

        if(document.getElementById("TimePickStyleSheet") == null) {
            MakeStyle();
        }

        var unique_id = RandomString(5);

        if(document.getElementById("TimePickBackgroundOverlay") == null) {
            let overlaydiv = document.createElement("div");
            overlaydiv.id= "TimePickBackgroundOverlay";
            document.body.insertBefore(overlaydiv, document.body.firstChild);
        }
        
        globalvar.elemets = document.querySelectorAll(element);
 
        for (var i = 0; i < globalvar.elemets.length; i++) {
            let timepickerbtn = globalvar.elemets[i];
            let TIMESARRAY = {};
            globalvar.elemets[i].setAttribute("TimePick", "input_" + unique_id + '_' + i);
            timepickerbtn.insertAdjacentHTML("afterend", `
            <button class="TimePick_BTN">
                <svg class="TimePick_ICON" id="${unique_id + '_' + i}" height="20" width="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M22 12C22 17.52 17.52 22 12 22C6.48 22 2 17.52 2 12C2 6.48 6.48 2 12 2C17.52 2 22 6.48 22 12Z" stroke="#292D32" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path> <path d="M15.71 15.18L12.61 13.33C12.07 13.01 11.63 12.24 11.63 11.61V7.51001" stroke="#292D32" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path></g></svg>
            
            
                <div class="TimePick_POPUP" id="popup_${unique_id + '_' + i}">
                    <div class="hour">
                        <div class="adjustbtn uparrow" data='{"type": "hour", "action": "up", "id":"${unique_id + '_' + i}"}'><svg fill="#D4D3E4" height="20px" width="20px" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="-30.7 -30.7 573.13 573.13" xml:space="preserve" stroke="#DDD" stroke-width="30"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <g> <g> <path d="M508.788,371.087L263.455,125.753c-4.16-4.16-10.88-4.16-15.04,0L2.975,371.087c-4.053,4.267-3.947,10.987,0.213,15.04 c4.16,3.947,10.667,3.947,14.827,0l237.867-237.76l237.76,237.76c4.267,4.053,10.987,3.947,15.04-0.213 C512.734,381.753,512.734,375.247,508.788,371.087z"></path> </g> </g> </g></svg>
                        </div>
                        <div id="label_hour_${unique_id + '_' + i}" class="label">00</div>
                        <div class="adjustbtn downarrow" data='{"type": "hour", "action": "down", "id":"${unique_id + '_' + i}"}'>
                        <svg fill="#D4D3E4" height="20px" width="20px" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="-30.7 -30.7 573.13 573.13" xml:space="preserve" stroke="#DDD" stroke-width="30" transform="rotate(180)"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <g> <g> <path d="M508.788,371.087L263.455,125.753c-4.16-4.16-10.88-4.16-15.04,0L2.975,371.087c-4.053,4.267-3.947,10.987,0.213,15.04 c4.16,3.947,10.667,3.947,14.827,0l237.867-237.76l237.76,237.76c4.267,4.053,10.987,3.947,15.04-0.213 C512.734,381.753,512.734,375.247,508.788,371.087z"></path> </g> </g> </g></svg></div>
                    </div>
                    <div class="minute">
                        <div class="adjustbtn uparrow" data='{"type": "minute", "action": "up", "id":"${unique_id + '_' + i}"}'><svg fill="#D4D3E4" height="20px" width="20px" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="-30.7 -30.7 573.13 573.13" xml:space="preserve" stroke="#DDD" stroke-width="30"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <g> <g> <path d="M508.788,371.087L263.455,125.753c-4.16-4.16-10.88-4.16-15.04,0L2.975,371.087c-4.053,4.267-3.947,10.987,0.213,15.04 c4.16,3.947,10.667,3.947,14.827,0l237.867-237.76l237.76,237.76c4.267,4.053,10.987,3.947,15.04-0.213 C512.734,381.753,512.734,375.247,508.788,371.087z"></path> </g> </g> </g></svg></div>
                        <div id="label_minute_${unique_id + '_' + i}" class="label">00</div>
                        <div class="adjustbtn downarrow" data='{"type": "minute", "action": "down", "id":"${unique_id + '_' + i}"}'><svg fill="#D4D3E4" height="20px" width="20px" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="-30.7 -30.7 573.13 573.13" xml:space="preserve" stroke="#DDD" stroke-width="30" transform="rotate(180)"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <g> <g> <path d="M508.788,371.087L263.455,125.753c-4.16-4.16-10.88-4.16-15.04,0L2.975,371.087c-4.053,4.267-3.947,10.987,0.213,15.04 c4.16,3.947,10.667,3.947,14.827,0l237.867-237.76l237.76,237.76c4.267,4.053,10.987,3.947,15.04-0.213 C512.734,381.753,512.734,375.247,508.788,371.087z"></path> </g> </g> </g></svg></div>
                    </div>
                    <div class="ampm"></div>
                </div>
            </button>`);

            if(globalvar.elemets[i].value){
                let previustimestr = globalvar.elemets[i].value;
                let previustimes = previustimestr.split(":");
                let uniquecode = `${unique_id + '_' + i}`;

                document.getElementById('label_hour_' + uniquecode).innerText = previustimes[0];
                document.getElementById('label_minute_' + uniquecode).innerText = previustimes[1];
            }
            else {
                globalvar.elemets[i].setAttribute("value", "00:00");
            }
            
        }
        
        let timepickpopupbtn = document.getElementsByClassName("TimePick_ICON");
        for(let i = 0; i < timepickpopupbtn.length; i++) {
            timepickpopupbtn[i].onclick = function () {
                let TimePick_POPUP = document.getElementsByClassName("TimePick_POPUP");
                for(let i = 0; i < TimePick_POPUP.length; i++) {
                    TimePick_POPUP[i].style.display = "none";
                }
                let currID = "popup_" + timepickpopupbtn[i].id;
                if(document.getElementById(currID).style.display == "flex"){
                    document.getElementById(currID).style.display = "none"
                    return;
                }
                document.getElementById(currID).style.display = "flex" 
            }
        }

        document.onclick = function(e){
            if(e.target.classList == 'before-line'){
                let TimePick_POPUP = document.getElementsByClassName("TimePick_POPUP");
                for(let i = 0; i < TimePick_POPUP.length; i++) {
                    TimePick_POPUP[i].style.display = "none";
                }
            }else if(e.target.classList == 'scroller'){
                let TimePick_POPUP = document.getElementsByClassName("TimePick_POPUP");
                for(let i = 0; i < TimePick_POPUP.length; i++) {
                    TimePick_POPUP[i].style.display = "none";
                }
            }else if(e.target.id == 'over-layer'){
                let TimePick_POPUP = document.getElementsByClassName("TimePick_POPUP");
                for(let i = 0; i < TimePick_POPUP.length; i++) {
                    TimePick_POPUP[i].style.display = "none";
                }
            }else if(e.target.id == 'NB'){
                let TimePick_POPUP = document.getElementsByClassName("TimePick_POPUP");
                for(let i = 0; i < TimePick_POPUP.length; i++) {
                    TimePick_POPUP[i].style.display = "none";
                }
            }else if(e.target.classList == 'grand'){
                let TimePick_POPUP = document.getElementsByClassName("TimePick_POPUP");
                for(let i = 0; i < TimePick_POPUP.length; i++) {
                    TimePick_POPUP[i].style.display = "none";
                }
            }
        };

       
        let adjustbtn = document.getElementsByClassName("adjustbtn");
        
        for(let i = 0; i < adjustbtn.length; i++) {

            adjustbtn[i].onclick = function () {
            let data = JSON.parse(adjustbtn[i].getAttribute("data"));

            let curr_hour = document.getElementById('label_hour_' + data.id).innerText;
            let curr_minute = document.getElementById('label_minute_' + data.id).innerText;

            if (curr_hour != "00") {
                globalvar.set_hour[data.id] = parseInt(curr_hour);
            }

            if (curr_minute != "00") {
                globalvar.set_minute[data.id] = parseInt(curr_minute);
            }

            if(data.type == 'hour' && data.action == 'up'){
                globalvar.set_hour[data.id] =  (globalvar.set_hour[data.id]) ?  (globalvar.set_hour[data.id]  + 1) : 0 + 1;
                globalvar.set_hour[data.id] = (globalvar.set_hour[data.id] == 24) ? 0 : globalvar.set_hour[data.id];
            }
            if(data.type == 'hour' && data.action == 'down'){
                globalvar.set_hour[data.id] = (globalvar.set_hour[data.id]) ?  (globalvar.set_hour[data.id]  - 1) : -1;
                globalvar.set_hour[data.id] = (globalvar.set_hour[data.id] == -1) ? 23 : globalvar.set_hour[data.id];
            }

            if(data.type == 'minute' && data.action == 'up'){
                globalvar.set_minute[data.id] = (globalvar.set_minute[data.id]) ?  (globalvar.set_minute[data.id] + 5) : 0 + 5;
                globalvar.set_minute[data.id] = (globalvar.set_minute[data.id] == 60) ? 0 : globalvar.set_minute[data.id];
            }
            if(data.type == 'minute' && data.action == 'down'){
                globalvar.set_minute[data.id] = (globalvar.set_minute[data.id]) ?  (globalvar.set_minute[data.id]  - 5) : -5;
                globalvar.set_minute[data.id] = (globalvar.set_minute[data.id] == -5) ? 55 : globalvar.set_minute[data.id];
            }

            let hrview = (globalvar.set_hour[data.id] == undefined) ? '00' : (globalvar.set_hour[data.id] < 10) ? ("0" + globalvar.set_hour[data.id]) : globalvar.set_hour[data.id];
            let mnview = (globalvar.set_minute[data.id] == undefined) ? '00' : (globalvar.set_minute[data.id] < 10) ? ("0" + globalvar.set_minute[data.id]) : globalvar.set_minute[data.id];
            
            document.getElementById('label_hour_' + data.id).innerText = hrview;
            document.getElementById('label_minute_' + data.id).innerText = mnview;

            document.querySelectorAll('input[TimePick=input_' + data.id + ']')[0].value = hrview + ":" + mnview;
            }
        }

        //private function
        function RandomString(length) {
            const characters ='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
            let result = '';
            const charactersLength = characters.length;
            for ( let i = 0; i < length; i++ ) {
                result += characters.charAt(Math.floor(Math.random() * charactersLength));
            }
            return result;
        }

        function MakeStyle(){
            var styles = `

            .TimePick_POPUP{
                position: absolute;
                height: 80px;
                width: 80px;
                background-color: #1e1e1e;
                border-radius: 3px;
                border: 1px solid #DDDDDD;
                display: flex;
                justify-content: center;
                align-items: center;
                box-shadow: rgba(17, 17, 26, 0.05) 0px 4px 16px, rgba(17, 17, 26, 0.05) 0px 8px 32px;
                z-index:500;
                margin-left: 112px;
                margin-top: 39px;
                display: none;
            }
            
            svg:active{
                fill: #0000;
                stroke: #0000;
            }
            
            .TimePick_BTN{
            /*    position: absolute;
                margin-left: 3vw;
                margin-top: 0.25vw;

                background-color: transparent;

                border: none;
                cursor: pointer;*/
            }
            
            .TimePick_ICON{
            /*    width: 1.25vw;*/
                opacity: 0.5;
            }
            
            .TimePick_ICON:hover{
                opacity: 1;
            }
            
            input{
                font-family: 'Nunito', sans-serif;
                font-size: 18px;

                padding: 8px 18px;
            /*    width: 4.25vw;
                height: 1.3vw;
                */

                border-width: 1px;
                border-style: solid;
                border-color: lightgray;

                background-color: white;

                border-radius: 0.2em;
            }
            
            #TimePickBackgroundOverlay{
                background-color:transparent;
                position:fixed; 
                top:0; left:0; right:0; bottom:0;
                display:block;
            }
            
            .label{
                font-family: 'Nunito', sans-serif;
                font-size: 20px;
                color: white;
            }
            
            .hour{
                display: flex;
                flex-direction: column;
                width: 35px;
            }
            
            .minute{
                display: flex;
                flex-direction: column;
                width: 35px;
            }`;
            var styleSheet = document.createElement("style");
            styleSheet.type = "text/css";
            styleSheet.id = "TimePickStyleSheet";
            styleSheet.innerText = styles;
            document.head.appendChild(styleSheet);
            return;
        }

        return globalvar;
    };

    return Constructor;
    
})(
/**********
 *************************************************************************
 *********** JAVASCRIPT MODULE TIME PICKER DONE BY KATHEESKUMAR **********
 ******************* MODIFIED & BUGS FIXED BY JH_BIZOY *******************
 ************************** Version: 2.0 *********************************
 *************************************************************************
 **********/
);




/* -------------------------------------------------------------*/
/* ================== Day Picker ===============================/*
/* -------------------------------------------------------------*/

const dropdowns = document.querySelectorAll('.dropdown');


dropdowns.forEach(dropdown => {
    const select = dropdown.querySelector('.select');
    const caret = dropdown.querySelector('.caret');
    const menu = dropdown.querySelector('.menu');
    const options = dropdown.querySelectorAll('.menu li');
    const selected = dropdown.querySelector('.selected');
    let TimePick_POPUP = document.getElementsByClassName("TimePick_POPUP");
                
    

    select.addEventListener('click', () => {
        select.classList.toggle('select-clicked');
        caret.classList.toggle('caret-rotate');
        menu.classList.toggle('menu-open');
        for(let i = 0; i < TimePick_POPUP.length; i++) {
            TimePick_POPUP[i].style.display = "none";
        }
        
    });

    document.addEventListener('click', e =>{
        if(!menu.contains(e.target) && e.target !== select  && e.target !== selected  && e.target !== caret){
            menu.classList.remove('menu-open');
            select.classList.remove('select-clicked');
            caret.classList.remove('caret-rotate');
        }
    });

    options.forEach(option => {
        option.addEventListener('click', ()=> {
            selected.innerText = option.innerText;
            select.classList.remove('select-clicked');
            caret.classList.remove('caret-rotate');
            menu.classList.remove('menu-open');
            options.forEach(option => {
                option.classList.remove('active');
            });
            option.classList.add('active');
        });
    });
    

});

/* ---------------------------------------------------------------*/
/* ================= Timer Adder and remover ====================*/
/* -------------------------------------------------------------*/

class AddRemove {
    constructor(parent1, parent2, add1, add2, cross) {
        this.parent1 = parent1;
        this.parent2 = parent2;
        this.add1 = add1;
        this.add2 = add2;
        this.cross = cross;
    }
    
    adder() {

        this.add1.addEventListener('click', () => {

            this.parent2.style.display = 'block';
            this.add2.style.display = 'block';
            this.add1.style.display = 'none';

            console.log("Timer Line added");
            
            
        });
    };

    remover(){
        this.cross.addEventListener('click',()=>{

            this.parent1.style.display = 'none';
            
            console.log("Timer Line removed");
        });
    }

    finalAdder() {

        this.add1.addEventListener('click', () => {

            this.parent2.style.display = 'block';
            this.add1.style.display = 'none';

            console.log("Timer Line added");
            
            this.cross.addEventListener('click',()=>{

                this.parent1.style.display = 'none';
                
                console.log("Timer Line removed");
            });
        });
    };

    finalRemover(){
        this.cross.addEventListener('click',()=>{
            this.parent2.style.display = 'none';
            console.log("Timer Line removed");
        });
    };
}

const AddRemove1 = new AddRemove (document.getElementById("parent-box"),document.getElementById("parent-box-01"),document.getElementById("add"),document.getElementById("add-01"),document.getElementById("cross"));

const AddRemove2 = new AddRemove (document.getElementById("parent-box-01"),document.getElementById("parent-box-02"),document.getElementById("add-01"),document.getElementById("add-02"),document.getElementById("cross-01"));

const AddRemove3 = new AddRemove (document.getElementById("parent-box-02"),document.getElementById("parent-box-03"),document.getElementById("add-02"),document.getElementById("add-03"),document.getElementById("cross-02"));

const AddRemove4 = new AddRemove (document.getElementById("parent-box-03"),document.getElementById("parent-box-04"),document.getElementById("add-03"),document.getElementById("add-04"),document.getElementById("cross-03"));

const AddRemove5 = new AddRemove (document.getElementById("parent-box-04"),document.getElementById("parent-box-05"),document.getElementById("add-04"),document.getElementById("add-05"),document.getElementById("cross-04"));

const AddRemove6 = new AddRemove (document.getElementById("parent-box-05"),document.getElementById("parent-box-06"),document.getElementById("add-05"),document.getElementById("add-06"),document.getElementById("cross-05"));

const AddRemove7 = new AddRemove (document.getElementById("parent-box-06"),document.getElementById("parent-box-07"),document.getElementById("add-06"),document.getElementById("add-07"),document.getElementById("cross-06"));

const AddRemove8 = new AddRemove (document.getElementById("parent-box-07"),document.getElementById("parent-box-08"),document.getElementById("add-07"),document.getElementById("add-08"),document.getElementById("cross-07"));

const AddRemove9 = new AddRemove (document.getElementById("parent-box-08"),document.getElementById("parent-box-09"),document.getElementById("add-08"),document.getElementById("add-09"),document.getElementById("cross-08"));

const AddRemove10 = new AddRemove (document.getElementById("parent-box-09"),document.getElementById("parent-box-10"),document.getElementById("add-09"),document.getElementById("add-10"),document.getElementById("cross-09"));

const AddRemove11 = new AddRemove (document.getElementById("parent-box-10"),document.getElementById("parent-box-11"),document.getElementById("add-10"),document.getElementById("add-11"),document.getElementById("cross-10"));

const AddRemove12 = new AddRemove (document.getElementById("parent-box-11"),document.getElementById("parent-box-12"),document.getElementById("add-11"),document.getElementById("add-12"),document.getElementById("cross-11"));

const AddRemove13 = new AddRemove (document.getElementById("parent-box-12"),document.getElementById("parent-box-13"),document.getElementById("add-12"),document.getElementById("add-13"),document.getElementById("cross-12"));

const AddRemove14 = new AddRemove (document.getElementById("parent-box-13"),document.getElementById("parent-box-14"),document.getElementById("add-13"),document.getElementById("add-14"),document.getElementById("cross-13"));

const AddRemove15 = new AddRemove (document.getElementById("parent-box-14"),document.getElementById("parent-box-15"),document.getElementById("add-14"),document.getElementById("add-15"),document.getElementById("cross-14"));

const AddRemove16 = new AddRemove (document.getElementById("parent-box-15"),document.getElementById("parent-box-16"),document.getElementById("add-15"),document.getElementById("add-16"),document.getElementById("cross-15"));

const AddRemove17 = new AddRemove (document.getElementById("parent-box-16"),document.getElementById("parent-box-17"),document.getElementById("add-16"),document.getElementById("add-17"),document.getElementById("cross-16"));

const AddRemove18 = new AddRemove (document.getElementById("parent-box-17"),document.getElementById("parent-box-18"),document.getElementById("add-17"),document.getElementById("add-18"),document.getElementById("cross-17"));

const AddRemove19 = new AddRemove (document.getElementById("parent-box-18"),document.getElementById("parent-box-19"),document.getElementById("add-18"),document.getElementById("add-19"),document.getElementById("cross-18"));

const AddRemove20 = new AddRemove( '',document.getElementById("parent-box-19"),'' ,'' ,document.getElementById("cross-19"));

AddRemove1.adder(); AddRemove1.remover(); AddRemove2.adder(); AddRemove2.remover(); 
AddRemove3.adder(); AddRemove3.remover(); AddRemove4.adder(); AddRemove4.remover();
AddRemove5.adder(); AddRemove5.remover(); AddRemove6.adder(); AddRemove6.remover(); 
AddRemove7.adder(); AddRemove7.remover(); AddRemove8.adder(); AddRemove8.remover();
AddRemove9.adder(); AddRemove9.remover(); AddRemove10.adder(); AddRemove10.remover(); 
AddRemove11.adder(); AddRemove11.remover(); AddRemove12.adder(); AddRemove12.remover();
AddRemove13.adder(); AddRemove13.remover(); AddRemove14.adder(); AddRemove14.remover();
AddRemove15.adder(); AddRemove15.remover(); AddRemove16.adder(); AddRemove16.remover();
AddRemove17.adder(); AddRemove17.remover(); AddRemove18.adder(); AddRemove18.remover();
AddRemove19.finalAdder(); AddRemove19.remover(); AddRemove20.finalRemover();

/* ---------------------------------------------------------------*/
/* ============ Hovering Bulb/ Clock/ Cog Button ================*/
/* -------------------------------------------------------------*/
/*
const timerButton = document.getElementById("b2");
let clockImg = document.getElementById("i2");

timerButton.addEventListener('mouseenter', ()=>{
    clockImg.src = "img/clockH.svg"
});
timerButton.addEventListener('mouseleave', ()=>{
    clockImg.src = "img/clock.svg"
});

const bulbButton = document.getElementById("b1");
let bulbImg = document.getElementById("lightbulb_image");
let bulbRaysImg = document.getElementById("lightbulb_ray_image");

bulbButton.addEventListener('mouseenter', ()=>{
    bulbImg.src = "img/lightbulbH.svg" 
    bulbRaysImg.src = "img/lightbulb_raysH.svg"
});
bulbButton.addEventListener('mouseleave', ()=>{
    bulbImg.src = "img/lightbulb.svg" 
    bulbRaysImg.src = "img/lightbulb_rays.svg"
});

const cogButton = document.getElementById("b3");
let cogImg = document.getElementById("i3");

cogButton.addEventListener('mouseenter', ()=>{
    cogImg.src = "img/cogH.svg"
});
cogButton.addEventListener('mouseleave', ()=>{
    cogImg.src = "img/cog.svg"
});
*/