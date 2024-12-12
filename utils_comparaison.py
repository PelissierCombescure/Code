import numpy as np
import trimesh
import pickle

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

