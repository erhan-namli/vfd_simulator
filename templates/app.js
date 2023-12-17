// Set up the scene
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();

renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById("scene-container").appendChild(renderer.domElement);

// Create a car
const geometry = new THREE.BoxGeometry(1, 0.5, 0.5);
const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
const car = new THREE.Mesh(geometry, material);

// Create a thicker circular base
const baseGeometry = new THREE.CircleGeometry( 2, 32 ); 
//baseGeometry.scale(1, 0.2, 1); // Make the base thicker
const baseMaterial = new THREE.MeshBasicMaterial({ color: 0x888888, side: THREE.DoubleSide });
const base = new THREE.Mesh(baseGeometry, baseMaterial);

base.rotation.x = Math.PI / 2; // Make it horizontal
base.position.y = -2; // Adjust to place it under the car

car.position.z = -0.25

scene.add(base);

// Attach the car to the base
base.add(car);


// Set the camera position
camera.position.z = 5;

// Automatic rotation for testing
const rotateSpeed = 0.005;
const rotateDirection = 1; // 1 for clockwise, -1 for counterclockwise


// Set up animation
const animate = function () {
    requestAnimationFrame(animate);

    autoRotate()

    // Rotate the car
   // car.rotation.y += 0.01;

    renderer.render(scene, camera);
};

// Handle automatic rotation
const autoRotate = function () {
    base.rotation.z += rotateSpeed * rotateDirection;
};

// Handle window resize
window.addEventListener('resize', function () {
    const newWidth = window.innerWidth;
    const newHeight = window.innerHeight;

    camera.aspect = newWidth / newHeight;
    camera.updateProjectionMatrix();

    renderer.setSize(newWidth, newHeight);
});

// Start the animation
animate();
