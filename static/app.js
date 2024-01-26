import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let modelPath = 'static/models/mercedes.glb';

let currentCarModel = 0;

// GUI
var obj = {
        message: 'Hello World',
        modbus_connection: false,
        modbus_disconnect: function() {
            alert("Disconnect");
        },
        updateModbusConnection: function (newState) {
            this.modbus_connection = newState;
            console.log("Modbus Connection updated to:", newState);
            console.log(this.modbus_connection);

        },
        maxSize: 6.0,
        height: 10,
        noiseStrength: 10.2,
        growthSpeed: 0.2,
        type: 'three',
        car_model : 1,
        camera : 1,
        distance: 1


    };

    var gui = new dat.gui.GUI();

    gui.remember(obj);

    gui.add(obj, 'message');
    gui.add(obj, 'modbus_connection');
      /*  .onChange(function () {
    // Use the updateModbusConnection function with the desired state
    obj.updateModbusConnection(obj.modbus_connection);
});*/


    gui.add(obj, 'modbus_disconnect');

    gui.add(obj, 'maxSize').min(-10).max(10).step(0.25);
    gui.add(obj, 'height').step(5); // Increment amount

    gui.add(obj, 'camera', {Camera1:1, Camera2:2, Camera3:3}).onChange( function () {
        console.log("Kamera Değişti aq")
    })

    gui.add(obj, 'car_model', {Mercedes: 1, Ferrari: 2}).onChange(
        function() {

        let carModel = this.getValue();

        if (carModel == 1) {

            modelPath = 'static/models/mercedes.glb';
        } else if (carModel == 2) {

            modelPath = 'static/models/ferrari.glb'; // Replace 'ferrari.glb' with the actual path for the Ferrari model
        }
            console.log(modelPath + "model path");

        // Load the selected car model
        loader.load(modelPath, function (gltf) {
            // Remove the old car model
            base.remove(currentCarModel);

            let newCarModel = gltf.scene.children[0];

            currentCarModel = newCarModel;

            const mesh = new THREE.Mesh(
                new THREE.PlaneGeometry(0.655 * 4, 1.3 * 4),
                new THREE.MeshBasicMaterial({
                    map: shadow, blending: THREE.MultiplyBlending, toneMapped: false, transparent: true
                })
            );

            mesh.rotation.x = -Math.PI / 2;
            mesh.renderOrder = 2;
            newCarModel.add(mesh);

            newCarModel.position.z = 0;
            newCarModel.position.y = -0.5;
            base.add(newCarModel);
            newCarModel.rotation.x = 3 * Math.PI / 2;

            // Update the current car model reference
            carModel = newCarModel;
        });
        }
    )

    var f2 = gui.addFolder('Another Folder');
    f2.add(obj, 'noiseStrength');

    var f3 = f2.addFolder('Nested Folder');
    f3.add(obj, 'growthSpeed');

    obj['Button with a long description'] = function () {
      console.log('Button with a long description pressed');
    };

    gui.add(obj, 'Button with a long description');

    gui.add(obj, "distance").min(1).max(300).step(1)
    .onChange(
    function(){
      let yourVar = this.getValue();

    }
  )

// END OF GUI

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });

renderer.setPixelRatio( window.devicePixelRatio );

renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.85;

renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById("scene-container").appendChild(renderer.domElement);

// Create a thicker circular base
const baseGeometry = new THREE.CircleGeometry( 3, 32 );
const baseMaterial = new THREE.MeshBasicMaterial({ color: 0x888888, side: THREE.DoubleSide });
const base = new THREE.Mesh(baseGeometry, baseMaterial);

base.rotation.x = Math.PI / 2; // Make it horizontal
base.position.y = -2; // Adjust to place it under the car

const spotLight = new THREE.SpotLight(0xffffff,  3, 100, 0.22, 1);
spotLight.position.set(0, 25, 0);
spotLight.castShadow = true;
spotLight.shadow.bias = -0.0001;
scene.add(spotLight);

scene.add(base);

camera.position.z = 6;

const shadow = new THREE.TextureLoader().load( 'static/three/ferrari_ao.png' );

// Ferrari Car Model Section
const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('static/three/draco/gltf/');

const loader = new GLTFLoader();
loader.setDRACOLoader( dracoLoader );

loader.load( modelPath, function ( gltf ) {

    let carModel = gltf.scene.children[ 0 ];

    currentCarModel = carModel;

    console.log(carModel)

    const mesh = new THREE.Mesh(
        new THREE.PlaneGeometry( 0.655 * 4, 1.3 * 4 ),
        new THREE.MeshBasicMaterial( {
            map: shadow, blending: THREE.MultiplyBlending, toneMapped: false, transparent: true
        } )
    );

    mesh.rotation.x = - Math.PI / 2;
    mesh.renderOrder = 2;
    carModel.add( mesh );

    carModel.position.z = 0
    carModel.position.y = -0.5
    base.add(carModel)
    carModel.rotation.x = 3*Math.PI/2;
})

// Automatic rotation for testing
const rotateSpeed = 0.005;
const rotateDirection = 1; // 1 for clockwise, -1 for counterclockwise
let cal_data_forward = 1
let cal_data_backward = 1

const autoRotate = function () {
    base.rotation.z += rotateSpeed * rotateDirection;
};

// WS

var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('modbus_server_connected', function(data) {
    console.log("Debug1")
    modbusServerConnected();
})

socket.on('modbus_server_disconnected', function(data) {
    console.log("Debug1")
    modbusServerDisconnected();
})

socket.on("forward", function(data){
            rotateTable('forward');

            cal_data_forward = data.cal_data_forward
        console.log(cal_data_forward)
})
socket.on("stop", function(data){
            rotateTable('stop');
})

socket.on("backward", function(data){
            rotateTable('backward');

            cal_data_backward = data.cal_data_backward
})

let currentRotation = 0;
let rotationIntervalForward;
let rotationIntervalBackward;

function rotateTabletoDegree(degree){

}

function modbusServerConnected(){
    obj.updateModbusConnection(true);
    gui.updateDisplay();

}

function modbusServerDisconnected() {
     obj.updateModbusConnection(false);
     gui.updateDisplay();
}

function rotateTable(direction){

    clearInterval(rotationIntervalForward);
    clearInterval(rotationIntervalBackward);

    if(direction === 'forward'){

        rotationIntervalForward = setInterval(function () {
                currentRotation += Math.PI / 1800 / cal_data_forward
                base.rotation.z = currentRotation
    }, 100);
    }

    if(direction === 'backward'){

        clearInterval(rotationIntervalForward);
        rotationIntervalBackward = setInterval(function () {
                currentRotation -= Math.PI / 1800 / cal_data_backward
                base.rotation.z = currentRotation
    }, 100);

    }

    if(direction === 'stop') {

        clearInterval(rotationIntervalForward);
        clearInterval(rotationIntervalBackward);
    }
}

const animate = function () {
    requestAnimationFrame(animate);

    //autoRotate()

    renderer.render(scene, camera);
};

animate();