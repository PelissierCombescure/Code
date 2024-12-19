
//////////////////////////////////////////////////////////////   
/// cd Code/Comparaison-User-study/Alignement/
/// python3 -m http.server 8000



// MAIN
// initialisation des variables
init_variable(true)
// let mesh_pas_aligned 
let mesh_not_aligned = []
// liste avec les meshs avec d'autres pbl
let mesh_pbl = []
// chemin des meshs
let meshes_tocheck = [];
const txtFilePath = 'paths/cup_meshes_aligned_ok.txt'; 
// Load the OBJ file from the correct relative path
const obj_file_path_source = 'Dataset-aligned/cup/test/cup_0094_SMPLER_centered_scaled_remeshing_iso_iter7_aligned.obj'; 
//const obj_file_path_source = 'Dataset-aligned/car/test/car_0229_SMPLER_centered_scaled_remeshing_iso_iter5_aligned_ok.obj'; 
const categorie = txtFilePath.split('.')[0].split('_').at(-1)
// Load paths from file and then call setUp_3D
loadPathsFromFile(txtFilePath, () => {
    console.log("meshes_tocheck", meshes_tocheck);
    setUp_3D(indice_mesh);  // Call setUp_3D after paths are loaded
});
// initialisation du canvas : load des images
setUp_3D(indice_mesh)
// action
animate()

//////////////////////////////////////////////////////////////
function init_variable(){
    // DATA github
    indice_mesh = 0 // indice du premier mesh à visionner
    mesh_courant = "nope" // nom des mesh 
    // nombre de mesh a visionner AU TOTAL
    num_tache = 0

    // Fenetre 3D
    scale_W_3D=0.5
    scale_H_3D=0.8
    W_3D = window.innerWidth*scale_W_3D
    H_3D = window.innerHeight*scale_H_3D

    // Rayon pour les cameras
    R = 1.8
    page_vues = true 
    // pour initialiser les claviers à chaque page
    premier_tour_page_vues = true
    enregistrement_not_aligned = false
    enregistrement_pbl = false
}

// Function to load paths from the text file
function loadPathsFromFile(path, callback) {
    fetch(path)
        .then(response => response.text())  // Read the file as text
        .then(data => {
            // Split the content by new lines to get an array of paths
            meshes_tocheck = data.split('\n')
                .map(line => line.trim())      // Remove any extra spaces or newlines
                .filter(line => line !== "");  // Filter out any empty lines
            
            nb_mesh = meshes_tocheck.length
            updateMeshCounter();

            // Call the callback once the data is loaded
            if (callback) callback();
        })
        .catch(error => {
            console.error('Error loading the file:', error);
        });
}

function displayFinishedMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.id = 'finished-message';
    messageDiv.style.position = 'absolute';
    messageDiv.style.top = '50%';
    messageDiv.style.left = '50%';
    messageDiv.style.transform = 'translate(-50%, -50%)';
    messageDiv.style.fontSize = '32px';
    messageDiv.style.color = 'white';
    messageDiv.style.textAlign = 'center';
    messageDiv.textContent = text;
    document.body.appendChild(messageDiv);
}

////////////////////////////////////////
////////////////////////////////////////
//            3D

function setUp_light(rayon, sc){
    const color = 0xFFFFFF;
    const intensity = 0.22;
    // Light
    const light1 = new THREE.AmbientLight( 0x404040 ); // soft white light
    sc.add( light1 );    
    const dir_light1 = new THREE.DirectionalLight(color, intensity);   
    dir_light1.position.set(rayon, 0, 0);
    sc.add(dir_light1);

    const light2 = new THREE.AmbientLight( 0x404040 ); // soft white light
    sc.add( light2 );    
    const dir_light2 = new THREE.DirectionalLight(color, intensity);   
    dir_light2.position.set(-rayon, 0, -0);
    sc.add(dir_light2);

    const light3 = new THREE.AmbientLight( 0x404040 ); // soft white light
    sc.add( light3 );    
    const dir_light3 = new THREE.DirectionalLight(color, intensity);   
    dir_light3.position.set(0, -rayon, 0);
    sc.add(dir_light3);

    const light4 = new THREE.AmbientLight( 0x404040 ); // soft white light
    sc.add( light4 );    
    const dir_light4 = new THREE.DirectionalLight(color, intensity);   
    dir_light4.position.set(0, rayon, -0);
    sc.add(dir_light4);
 
}

function loadOBJFromPath(path, sc) {
    const objLoader = new THREE.OBJLoader2(); 
    const xhr = new XMLHttpRequest();        
    xhr.open('GET', path, true);        
    xhr.responseType = 'text';        
    xhr.onload = function () {
        if (xhr.status === 200) {
            const objData = xhr.responseText;
            const object = objLoader.parse(objData);
            sc.add(object);
        } else {
            console.error('Failed to load the OBJ file:', xhr.status);
        }
    };
    xhr.onerror = function () {console.error('An error occurred while trying to load the OBJ file.');
    };
    xhr.send();
}

function updateMeshCounter() {
    const counterElement = document.getElementById("mesh-counter");
    counterElement.textContent = categorie+` -> Vérifié : ${indice_mesh} / ${nb_mesh}  -------  OK : Enter -- Not Ok : Space -- Autre PBL : Suppr ----- ${meshes_tocheck[indice_mesh]}`;
}

function setUp_3D(idx_mesh){
    if (meshes_tocheck.length === 0) {console.error("No meshes to load, meshes_tocheck is empty!");  }
    nb_mesh = meshes_tocheck.length

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // Caméra
    camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.01, 1000 );
    camera.position.x = 2;
    camera.position.y = 0;
    camera.position.z = 0;
    // oriantation camera
    idx_i = 2; idx_j = 3
    theta = 2*Math.PI * ( (2/8)*(idx_j==0) + (1/8)*(idx_j==1) + (-1/8)*(idx_j==3) + (-2/8)*(idx_j==4))
    delta = 2*Math.PI * (idx_i/8)
    camera.position.set(R*Math.cos(delta)*Math.cos(theta), R*Math.sin(theta), R*Math.sin(delta)*Math.cos(theta)) // repère JS
    camera.lookAt(0, 0, 0)

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // scene source de référence
    scene = new THREE.Scene();
    scene.add(camera)
    renderer = new THREE.WebGLRenderer( {
        antialias: true,
        preserveDrawingBuffer: true } );

    renderer.setSize(W_3D , H_3D);
    setUp_light(R, scene)    
    old_renderer = document.getElementById('renderer')
    if (old_renderer!=  null){
        old_renderer.parentElement.removeChild(old_renderer)
    }

    renderer.domElement.id = 'renderer'
    renderer.domElement.style.marginTop = (H_3D*0.04)+"px"; 
    document.body.appendChild( renderer.domElement );
    controls = new THREE.OrbitControls( camera );   

    // Afficher mesh courant
    //const obj_file_path = 'Dataset-aligned/car/test/car_0055_SMPLER_centered_scaled_remeshing_iso_iter5_aligned_us.obj';  // Adjust the path as needed
    obj_file_path = meshes_tocheck[idx_mesh];
    loadOBJFromPath(obj_file_path, scene);

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    /// Mesh a checker 
    scene_source = new THREE.Scene();
    scene_source.add(camera)
    renderer_source = new THREE.WebGLRenderer( {
        antialias: true,
        preserveDrawingBuffer: true } );
    renderer_source.setSize(W_3D , H_3D);
    setUp_light(R, scene_source)   
    // Center the renderer in the window
    renderer_source.domElement.style.position = 'absolute';
    renderer_source.domElement.style.left = '50%';

    old_renderer_source = document.getElementById('renderer_source')
    if (old_renderer_source!=  null){
        old_renderer_source.parentElement.removeChild(old_renderer_source)
    }
    renderer_source.domElement.id = 'renderer_source'
    renderer_source.domElement.style.marginTop = (H_3D*0.04)+"px"; 
    document.body.appendChild( renderer_source.domElement );
    controls = new THREE.OrbitControls( camera );
     // Adjust the path as needed
    // Call the function with the file path
    loadOBJFromPath(obj_file_path_source, scene_source);
}

function removeRenderers() {
    const rendererElement = document.getElementById('renderer');
    if (rendererElement) {
        rendererElement.parentElement.removeChild(rendererElement);
    }

    const rendererSourceElement = document.getElementById('renderer_source');
    if (rendererSourceElement) {
        rendererSourceElement.parentElement.removeChild(rendererSourceElement);
    }
}

////////////////////////////////////////
////////////////////////////////////////
//            CLAVIER
function action_clavier(event){
    switch (event.key){
        case  'Enter':
            console.log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> mesh OOOOOOOKKKK")
            action_mesh_ok()
            break;
        case  ' ':
            console.log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> mesh PPPAAAAAASSSSS aligne ")
            action_mesh_pas_ok()
            break;

        case "Delete":
            console.log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Autre PBL")
            action_autre_pbl()
            break;

        case "z":
            console.log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Retour arrière")
            action_retour()
            break;
    }
}

function init_clavier_vues(){document.addEventListener("keydown", action_clavier)

}

function action_mesh_ok(){
    indice_mesh = indice_mesh + 1
    updateMeshCounter();
    if (indice_mesh < nb_mesh){ 
        setUp_3D(indice_mesh)}
    else {
        page_vues = false
        if (mesh_not_aligned.length > 0) {enregistrement_not_aligned = true }
        else if (mesh_pbl.length > 0) {enregistrement_pbl = true}
        else {console.log("Tout est aligné")}
 }
}

function action_mesh_pas_ok(){
    mesh_not_aligned.push(meshes_tocheck[indice_mesh])
    action_mesh_ok()
}

function action_autre_pbl(){
    // TODO : sauvegarde nom dans un list
    mesh_pbl.push(meshes_tocheck[indice_mesh])
    action_mesh_ok()
}

function action_retour(){
    remove_element(mesh_not_aligned,meshes_tocheck[indice_mesh-1])
    remove_element(mesh_pbl,meshes_tocheck[indice_mesh-1])
    indice_mesh = indice_mesh - 1
    updateMeshCounter();
    setUp_3D(indice_mesh)
}

function remove_element(L,e){
    if (L.includes(e)) {
        // Find the index of the element to remove
        const index = L.indexOf(e);
        // Remove the element from the array
        if (index > -1) {
            L.splice(index, 1);
            console.log(`Removed: ${e} from ${L}`);
        }
    } else {
        console.log(`${e} is not in the ${L} list`);
    }
}


////////////////////////////////////////
// Sauvegarde list des mesh non alignés
function saveListToFile(list, filename) {
    // Convert the list to a string, each element on a new line
    const fileContent = list.join('\n');

    // Create a Blob object with the file content
    const blob = new Blob([fileContent], { type: 'text/plain' });

    // Create an object URL for the Blob object
    const url = URL.createObjectURL(blob);

    // Create a link element to trigger the download
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;  // Specify the filename for the download
    a.click();  // Trigger the download
    // Clean up the URL object
    URL.revokeObjectURL(url);
}

////////////////////////////////////////
////////////////////////////////////////
function animate() {
    // Temps à chaque animate
    time_animate = new Date().getTime()

    // page de choix
    if (page_vues && indice_mesh < nb_mesh){
        // on enlève les touches du clavier associé à la page tuto
        if(premier_tour_page_vues){
            init_clavier_vues()
            premier_tour_page_vues = false
        }
        // affichage 3D
        renderer.render(scene, camera);
        // affichage 3D
        renderer_source.render(scene_source, camera );
    }
    if (enregistrement_not_aligned) 
        {console.log('enregistrement_not_aligned')
        // Call the function to save the list to a file
        saveListToFile(mesh_not_aligned, categorie+'_meshes_not_aligned.txt')
        enregistrement_not_aligned = false     
        if (mesh_pbl.length > 0) {enregistrement_pbl = true}   
    }
    if (enregistrement_pbl){
        saveListToFile(mesh_pbl, categorie+'_meshes_PBL.txt')
        enregistrement_pbl = false
    }

    if (!page_vues && indice_mesh > nb_mesh -1 && !enregistrement_not_aligned && !enregistrement_pbl){
        console.log("FIIIIIIINNNNNN")
        removeRenderers();
        // Affichez le message "Fini" si ce n'est pas déjà fait
        if (!document.getElementById('finished-message')) {
            displayFinishedMessage("FINI !");        }
        return; 
    }
    
    // Boucle sur animate
    requestAnimationFrame( animate );
}
