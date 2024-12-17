import numpy as np
import trimesh
import pickle
import matplotlib.pyplot as plt
import os 
import math

# Description : Lit un fichier pickle et retourne son contenu.
# Paramètres :
# # dict_path : Chemin vers le fichier pickle.
# Retourne : Un dictionnaire (ou tout autre objet sérialisé dans le pickle).
def read_pkl(dict_path):
    output = open(dict_path,'rb')
    dict = pickle.load(output)
    return dict

# Description : Crée une matrice de rotation 4x4 autour d'un axe donné (X, Y ou Z) pour un angle donné en degrés.
# Paramètres :
# # axis : Axe de rotation, doit être 'X', 'Y' ou 'Z'.
# # angle_degrees : Angle de rotation en degrés.
# Retourne : Une matrice de rotation 4x4 de type numpy.array.
def create_rotation_matrix(axis, angle_degrees):
    # Convertir l'angle en radians
    angle_radians = np.radians(angle_degrees)
    # Déterminer le vecteur de direction en fonction de l'axe
    if axis.upper() == 'X':    direction = [1, 0, 0]
    elif axis.upper() == 'Y':  direction = [0, 1, 0]
    elif axis.upper() == 'Z':  direction = [0, 0, 1]
    else: raise ValueError("L'axe doit être 'X', 'Y' ou 'Z'.")
    # Créer la matrice de rotation
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=angle_radians,  # Angle en radians
        direction=direction,  # Axe de rotation
        point=[0, 0, 0])  # Centre de rotation (origine)
    return rotation_matrix

# Description : Ajoute un cube dans un fichier .obj.
# Paramètres :
# # obj_file : Objet fichier ouvert pour écriture.
# # center : Coordonnées [x,y,z] du centre du cube.
# # color : Couleur [r,g,b] dans l'intervalle  [0,1].
# # vertex_offset : Décalage actuel des indices des sommets.
# # cube_size : Taille des côtés du cube.
# Retourne : Le nouveau décalage des indices des sommets après l'ajout du cube.
def add_cube_to_obj(obj_file, center, color, vertex_offset, cube_size):
    """
    Add a cube to an open .obj file.
    
    Parameters:
        obj_file (file object): The open file object to write to.
        center (list/tuple): The [x, y, z] coordinates of the cube's center.
        color (list/tuple): The [r, g, b] color values for the cube (0 to 1 range).
        vertex_offset (int): The current vertex index offset.
        cube_size (float): The length of the cube's sides.
    Returns:
        int: The updated vertex offset after adding the cube.
    """
    cx, cy, cz = center
    r, g, b = color
    half_size = cube_size / 2

    # Generate vertices for the cube
    cube_vertices = [
        [cx - half_size, cy - half_size, cz - half_size],
        [cx + half_size, cy - half_size, cz - half_size],
        [cx + half_size, cy + half_size, cz - half_size],
        [cx - half_size, cy + half_size, cz - half_size],
        [cx - half_size, cy - half_size, cz + half_size],
        [cx + half_size, cy - half_size, cz + half_size],
        [cx + half_size, cy + half_size, cz + half_size],
        [cx - half_size, cy + half_size, cz + half_size],
    ]

    # Write vertices to the file
    for vertex in cube_vertices:
        obj_file.write(f"v {vertex[0]} {vertex[1]} {vertex[2]} {r * 255} {g * 255} {b * 255}\n")

    # Generate faces for the cube (6 faces, 2 triangles per face)
    cube_faces = [
        [0, 1, 2], [0, 2, 3],  # Bottom face
        [4, 5, 6], [4, 6, 7],  # Top face
        [0, 1, 5], [0, 5, 4],  # Front face
        [2, 3, 7], [2, 7, 6],  # Back face
        [1, 2, 6], [1, 6, 5],  # Right face
        [3, 0, 4], [3, 4, 7],  # Left face
    ]

    # Write faces to the file
    for face in cube_faces:
        obj_file.write(f"f {' '.join(str(idx + vertex_offset + 1) for idx in face)}\n")

    # Return the updated vertex offset
    return vertex_offset + 8  # Each cube adds 8 vertices

# Description : Génère deux fichiers .obj :
# Avec un modèle et 12 positions de caméra.
# Avec un modèle et 8 positions de caméra.
# Paramètres :
# # mesh_modelnet : Objet 3D pour le premier modèle.
# # cams_modelnet_mesh : Positions des caméras pour le premier modèle.
# # name_modelnet : Nom pour le fichier de sortie du premier modèle.
# # mesh_us : Objet 3D pour le second modèle.
# # cams_us : Positions des caméras pour le second modèle.
# # categorie_us : Nom pour le fichier de sortie du second modèle.
# # dir_outputs : Répertoire de sauvegarde des fichiers générés.
# Retourne : Aucun.
def show_cams(mesh_modelnet, cams_modelnet_mesh, name_modelnet, mesh_us, cams_us, categorie_us,  dir_outputs, US_obj, ):
    ## OBJ file with (12 cameras + obj)
    # Vertices and faces of the model user study
    verts_mesh_modelnet = np.array(mesh_modelnet.vertices)
    faces_mesh_modelnet = np.array(mesh_modelnet.faces) 
    # colors : Blanc cam 1 --> Jaune cam 4 ---> Rouge cam 10 --> Rouge foncé cam 12
    colormap = plt.get_cmap('hot'); colors_modelnet = colormap(np.linspace(0, 1, 12))[::-1] 
    with open(os.path.join(dir_outputs, name_modelnet+"_modelNet40+12cam.obj"), 'w') as obj_file:
        # Write vertices
        for vertex in verts_mesh_modelnet:
            obj_file.write(f"v {vertex[0]} {vertex[1]} {vertex[2]} 128 128 128\n")      
        # Write 12 cameras positions
        vertex_offset = len(verts_mesh_modelnet)
        for cube_center, cube_color in zip(cams_modelnet_mesh[:, :3], colors_modelnet[:,:3]):  
            vertex_offset = add_cube_to_obj(obj_file, cube_center, cube_color, vertex_offset, cube_size=0.3)
        # Write faces
        for face in faces_mesh_modelnet:
            # Convert face indices to 1-based indexing
            obj_file.write(f"f {' '.join(str(idx + 1) for idx in face)}\n")   
            
    ################################################################################"" 
    ## OBJ file with (8 cameras + obj)
    # Vertices and faces of the model user study
    if US_obj :
        verts_mesh_us = np.array(mesh_us.vertices)
        faces_mesh_us = np.array(mesh_us.faces) 
        # colors : Jaune cam 1 --> Vert cam 3 ---> Bleu cam 5 --> Bleu foncé cam 8
        colormap = plt.get_cmap('hot'); colors_us = colormap(np.linspace(0, 1, 8))[::-1] 
        # Write obj
        with open(os.path.join(dir_outputs, categorie_us+"_us+8cam.obj"), 'w') as obj_file:
            # Write vertices
            for vertex in verts_mesh_us:
                obj_file.write(f"v {vertex[0]} {vertex[1]} {vertex[2]} 128 128 128\n")      
            # Write 8 cameras positions
            vertex_offset = len(verts_mesh_us)
            for cube_center, cube_color in zip(cams_us[:, :3], colors_us[:,:3]):  
                vertex_offset = add_cube_to_obj(obj_file, cube_center, cube_color, vertex_offset, cube_size=0.3)
            # Write faces
            for face in faces_mesh_us:
                # Convert face indices to 1-based indexing
                obj_file.write(f"f {' '.join(str(idx + 1) for idx in face)}\n")   

## Description : Génère un fichier .obj avec un modèle (mesh) et des caméras (cams) olorées (colors)
def show_some_cams(mesh, name, cams, colors, dir_outputs) : # Vertices and faces of the model user study
    verts_mesh = np.array(mesh.vertices)
    faces_mesh = np.array(mesh.faces) 
    # colors : Blanc cam 1 --> Jaune cam 4 ---> Rouge cam 10 --> Rouge foncé cam 12
    colormap = plt.get_cmap('hot'); colors_modelnet = colormap(np.linspace(0, 1, 12))[::-1] 
    with open(os.path.join(dir_outputs, name+".obj"), 'w') as obj_file:
        # Write vertices
        for vertex in verts_mesh:
            obj_file.write(f"v {vertex[0]} {vertex[1]} {vertex[2]} 128 128 128\n")      
        # Write 12 cameras positions
        vertex_offset = len(verts_mesh)
        for k in range(len(cams)):  
            vertex_offset = add_cube_to_obj(obj_file, cams[k], colors[k], vertex_offset, cube_size=0.3)
        # Write faces
        for face in faces_mesh:
            # Convert face indices to 1-based indexing
            obj_file.write(f"f {' '.join(str(idx + 1) for idx in face)}\n")   

# Description : Calcule la position d'une caméra sur une sphère en la plaçant à une distance donnée du centre.
# Paramètres :
# # R_sphere : Rayon de la sphère.
# # cam_rep_etude : Coordonnées initiales de la caméra [x,y,z].
# # centroid_rep_etude : Coordonnées du centre de la sphère [x,y,z].
# Retourne : Coordonnées ajustées de la caméra sur la sphère [x,y,z].
def put_cam_on_sphere(R_sphere, cam_rep_etude, centroid_rep_etude):
    # on place la camera sur la sphère des 40 caméras
    # O : centroid, A point à trouver et C : camera
    # on veut que OC et OA soit colinaires et ||OA|| = R 
    [xo, yo, zo] = centroid_rep_etude; [xc, yc, zc] = cam_rep_etude
    # distance OC :
    d = math.sqrt((xo-xc)**2 + (yo-yc)**2 +(zo-zc)**2)
    # le rayon correspond à k*R = d
    k = d/R_sphere
    # si colinaireas alors OC = k*OA --> k = (xc-xo)/(xa-xo) = (yc-yo)/(ya-yo) = (zc-zo)/(za-zo)
    xa = ((xc-xo)/k) + xo
    ya = ((yc-yo)/k) + yo
    za = ((zc-zo)/k) + zo
    cam_rep_etude_sphere = [xa,ya,za]
    return cam_rep_etude_sphere

# Description : Calcule le produit vectoriel entre deux vecteurs 3D.
def cross(a, b):
    c = np.array([a[1]*b[2] - a[2]*b[1],
         a[2]*b[0] - a[0]*b[2],
         a[0]*b[1] - a[1]*b[0]])

    return c

# Description : Calcule le centroïde d'un maillage 3D pondéré par l'aire de ses faces.
# Paramètres :
# # a_faces : Tableau contenant les indices des sommets pour chaque face (N×3).
# # a_coords : Coordonnées 3D des sommets du maillage (M×3).
# Retourne : Le centroïde [x,y,z].
def get_centroid(a_faces, a_coords):
    area_total = 0
    centroid = np.array([0,0,0])
    for face in a_faces:
        v0 = a_coords[face[0],:]
        v1 = a_coords[face[1],:]
        v2 = a_coords[face[2],:]
        center = (v0+v1+v2)/3
        T_area = np.linalg.norm(cross(v1-v2, v0-v2))*0.5
        area_total = area_total + T_area
        centroid = centroid + T_area*center

    centroid = centroid/area_total
    return centroid

#Description : Calcule la probabilité d'une valeur donnée sous une distribution gaussienne 3D.
# Paramètres :
# # mu : cam etude 
# # x : cam issue d'une image 
def gaussian(sig, mu, x):
    # coeff 
    coef_denom = math.pow((2*math.pi), 3/2)*math.pow(sig, 3)
    coef = 1/coef_denom
    # exponentielle
    vect_diff = np.array(x) - np.array(mu)
    puissance = -1* (np.dot(vect_diff, vect_diff)) / (2*math.pow(sig, 2))
    return coef*np.exp(puissance)   


# A partir du mesh aligné à l'US, on applique les memes transformations au 12 caméras de ModelNet40
# Pour les places dans le repère US (=cams_modelnet_mesh)
# Puis on détermine les coordonnées de la cam BVS dans le repère US (=cam_bvs_model et num_cam_bvs_model)
def bvs_cams_modelnet_aligned(path_mesh, path_mesh_modelnet_aligned, dir_bvs, cams_modelnet):
    # Transformation du mesh de ModelNet40 en mesh de l'étude utilisateur
    transformations = read_pkl(path_mesh_modelnet_aligned.replace(".obj", ".pkl"))
    # Transformation des 12 cameras pour mettre dans le repère de l'étude utilisateur comme le modèle 
    cams_modelnet_mesh = cams_modelnet.copy()
    for n in range(0, len(transformations)):
        # Rotation Rn
        R = transformations[f"transformations{n}"]
        cams_modelnet_mesh = np.dot(R, cams_modelnet_mesh.T).T
        
    ## BVS ATTENTION DANS LE CALCULS DE LA BVS ON A BOUCLE SUR RANGE(1,13) ET NON PAS SUR RANGE(0,12)
    num_cam_bvs_modelnet = read_pkl(os.path.join(dir_bvs, os.path.basename(path_mesh)+"_bvs.pkl"))['bvs'].split('_')[-1]
    cam_bvs_modelnet = cams_modelnet_mesh[int(num_cam_bvs_modelnet)-1][:3]    
    return cams_modelnet_mesh, cam_bvs_modelnet, num_cam_bvs_modelnet

# cameras_modelnet : cameras BVS de ModelNet40 DANS LE REPERE US !!!!
# cameras_US : caméras de l'US considérées dans le repère US
def poids_modelnet_sur_US(df, camera_modelnet, centroid_modelnet, cameras_US, R_sphere, I_us, J_us, sigma=0.58, precision=2):
    # Projection de la caméra BVS de ModelNet40 sur la sphère des caméras de l'US
    camera_modelnet_sphere = put_cam_on_sphere(R_sphere, camera_modelnet, centroid_modelnet)#; print("Camera modelnet sur la sphere : ", camera_modelnet_sphere)
    poids = []
    for k in range(len(cameras_US)):
        # poids de cam_sphere vis à vis de cam_etude_k
        poids_k = np.round(gaussian(sigma, cameras_US[k, :3], camera_modelnet_sphere), precision) # ;print("Poids de la caméra modelnet sur la caméra US ", int(I_us[k]), J_us[k], labels_us[k], ": ", poids_k)
        poids.append(poids_k)
        
    # Add the list poids as the 16 last columns of df and at the last row
    for k in range(len(poids)):
        df.loc[len(df)-1, f"{int(I_us[k])}-{J_us[k]}"] = np.round(poids[k]/sum(poids), precision)
    return df, camera_modelnet_sphere