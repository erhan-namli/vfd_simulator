import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

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
//baseGeometry.scale(1, 0.2, 1); // Make the base thicker
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

//const shadow = new THREE.TextureLoader().load( 'three/ferrari_ao.png' );

// Ferrari Car Model Section

const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('three/draco/gltf/');


const loader = new GLTFLoader();
loader.setDRACOLoader( dracoLoader );

const bodyMaterial = new THREE.MeshPhysicalMaterial( {
    color: 0xff0000, metalness: 1.0, roughness: 0.5, clearcoat: 1.0, clearcoatRoughness: 0.03
} );

const detailsMaterial = new THREE.MeshStandardMaterial( {
    color: 0xffffff, metalness: 1.0, roughness: 0.5
} );

const glassMaterial = new THREE.MeshPhysicalMaterial( {
    color: 0xffffff, metalness: 0.25, roughness: 0, transmission: 1.0
} );

const wheels = [];

loader.load( 'models/mercedes.glb', function ( gltf ) {

    const carModel = gltf.scene.children[ 0 ];

    carModel.getObjectByName( 'body' ).material = bodyMaterial;

	carModel.getObjectByName( 'rim_fl' ).material = detailsMaterial;
	carModel.getObjectByName( 'rim_fr' ).material = detailsMaterial;
	carModel.getObjectByName( 'rim_rr' ).material = detailsMaterial;
	carModel.getObjectByName( 'rim_rl' ).material = detailsMaterial;
	carModel.getObjectByName( 'trim' ).material = detailsMaterial;

	carModel.getObjectByName( 'glass' ).material = glassMaterial;

	wheels.push(
		carModel.getObjectByName( 'wheel_fl' ),
		carModel.getObjectByName( 'wheel_fr' ),
		carModel.getObjectByName( 'wheel_rl' ),
		carModel.getObjectByName( 'wheel_rr' )
	);

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

   // carModel.rotation.z = Math.PI/2;

   // scene.add( carModel );

})

// Automatic rotation for testing
const rotateSpeed = 0.005;
const rotateDirection = 1; // 1 for clockwise, -1 for counterclockwise

var socket = io.connect('http://' + document.domain + ':' + location.port);

const autoRotate = function () {
    base.rotation.z += rotateSpeed * rotateDirection;
};


const animate = function () {
    requestAnimationFrame(animate);

    autoRotate()

    // Rotate the car
   // car.rotation.y += 0.01;

    renderer.render(scene, camera);
};

animate();