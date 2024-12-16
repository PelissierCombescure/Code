import numpy as np
import trimesh
import pickle
import matplotlib.pyplot as plt
import os 
import math

def read_pkl(dict_path):
    output = open(dict_path,'rb')
    dict = pickle.load(output)
    return dict

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

def show_cams(mesh_modelnet, cams_modelnet_mesh, name_modelnet, mesh_us, cams_us, categorie_us,  dir_outputs):
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

def cross(a, b):
    c = np.array([a[1]*b[2] - a[2]*b[1],
         a[2]*b[0] - a[0]*b[2],
         a[0]*b[1] - a[1]*b[0]])

    return c
# a_faces est un array de taille nb_sommetx3 avec les indices des sommets de chauqe face
# a_coords est un array contenant les coordonnées 3D de tous les sommets du mesh
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

# mu : cam etude 
# x : cam issue d'une image 
def gaussian(sig, mu, x):
    # coeff 
    coef_denom = math.pow((2*math.pi), 3/2)*math.pow(sig, 3)
    coef = 1/coef_denom
    # exponentielle
    vect_diff = np.array(x) - np.array(mu)
    puissance = -1* (np.dot(vect_diff, vect_diff)) / (2*math.pow(sig, 2))
    return coef*np.exp(puissance)   