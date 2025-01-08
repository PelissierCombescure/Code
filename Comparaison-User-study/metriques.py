import pandas as pd
import math 
import numpy as np
import numpy as np
from scipy.stats import wasserstein_distance
from scipy.fftpack import fft
from scipy.spatial.distance import cdist
from utils_comparaison import gaussian
import trimesh

from utils_comparaison import show_some_cams


def get_coord_from_ij(i, j, df_data_cams):
        # Assuming 'data_us_cam' is your DataFrame
    filtered_df = df_data_cams[(df_data_cams['i'] == i) & (df_data_cams['j'] == j)]
    # Extract the values of X_rep_etude, Y_rep_etude, Z_rep_etude
    return  [filtered_df['X_rep_etude'].values[0], filtered_df['Y_rep_etude'].values[0], filtered_df['Z_rep_etude'].values[0]]

def get_label_from_ij(i, j, df_data_cams):
        # Assuming 'data_us_cam' is your DataFrame
    filtered_df = df_data_cams[(df_data_cams['i'] == i) & (df_data_cams['j'] == j)]
    # Extract the values of X_rep_etude, Y_rep_etude, Z_rep_etude
    return  filtered_df['label'].values[0]

def get_sym(ij_pov, df_data_cams):
    i_pov = ij_pov[0]; j_pov = int(ij_pov[1])
    if i_pov in [1,2,3,5,6,7]:
        if i_pov == 1 : 
            return (True, [7, j_pov], get_coord_from_ij(7, j_pov, df_data_cams), get_label_from_ij(7, j_pov, df_data_cams))
        elif i_pov == 2 : 
            return (True, [6, j_pov], get_coord_from_ij(6, j_pov, df_data_cams), get_label_from_ij(6, j_pov, df_data_cams))
        elif i_pov == 3 : 
            return (True, [5, j_pov], get_coord_from_ij(5, j_pov, df_data_cams), get_label_from_ij(5, j_pov, df_data_cams))
        elif i_pov == 5 : 
            return (True, [3, j_pov], get_coord_from_ij(3, j_pov, df_data_cams), get_label_from_ij(3, j_pov, df_data_cams))
        elif i_pov == 6 : 
            return (True, [2, j_pov], get_coord_from_ij(2, j_pov, df_data_cams), get_label_from_ij(2, j_pov, df_data_cams))
        elif i_pov == 7 : 
            return (True, [1, j_pov], get_coord_from_ij(1, j_pov, df_data_cams), get_label_from_ij(1, j_pov, df_data_cams))
    else : return (False, None, None, None)

def get_ds2(coord_U, coord_M, sig, epsilon):
    coef_denom = math.pow((2*math.pi), 3/2)*math.pow(sig, 3)
    return np.round(gaussian(sig, coord_U, coord_M)*coef_denom, epsilon)

# renvoie (poids du pov) / max(histo des poids) --> valeur entre 0 et 1
def get_poids1(ij_m, label_m, df_poids_US, df_data_cams):
    df_poids = df_poids_US['df']
    ## Poids du label m
    poids_label_m = list(df_poids.loc[df_poids['label'] == label_m]['poids'])[0]
    poids_max = max(list(df_poids['poids']))
    ## S'il le pov_m a un symétrique, on prend le max des deux poids
    sym_to_m = get_sym(ij_m, df_data_cams)
    if sym_to_m[0]:
        label_m_sym = sym_to_m[3]
        poids_label_m_sym = list(df_poids.loc[df_poids['label'] == label_m_sym]['poids'])[0]
        return max(poids_label_m, poids_label_m_sym)/poids_max, sym_to_m # to check
    ## Si pas de symetrique
    else :
        return poids_label_m/poids_max, None

def score_proximite(BVS, categorie_us, path_mesh_us, list_meshs_sym, df_coords, dir_outputs,  sig=1.3, epsilon=2, scores_Ds = [0,0,1]):
    bvs_courant = BVS[categorie_us]; cam_pov_u_sym = None
    ## bvs US
    ij_pov_u = list(BVS[categorie_us]['US']['ij'])[0]; cam_pov_u = np.around(list(BVS[categorie_us]['US']['cam'])[0], 2) ; print('pov_u', cam_pov_u, ij_pov_u)
    ## bvs Modelnet
    ij_pov_m = list(BVS[categorie_us]['modelnet']['ij'])[0]; cam_pov_m = np.around(list(BVS[categorie_us]['modelnet']['cam'])[0], 2) ; print('pov_m', cam_pov_m, ij_pov_m)
    label_pov_m = list(BVS[categorie_us]['modelnet']['label'])[0]
    #####################################################
    #### Distance sémantique DS de la catégroie courantez
    ## Si les pov sont les mêmes
    if np.array_equal(ij_pov_u, ij_pov_m) : Ds = scores_Ds[-1]; print("cool c'est le meme pov")
    ## Categorie avec des objets NON symetriques
    elif not(categorie_us in list_meshs_sym):  Ds = get_ds2(cam_pov_u, cam_pov_m, sig, epsilon); print("cat pas sym")
    ## categorie symetrique 
    else : ## Est ce que pov_u a un symetrique
        sym_to_u = get_sym(ij_pov_u, df_coords); print("cat sym")
        if sym_to_u[0]: 
            print("pov a un sym")
            # symetrique de ij_pov_u
            ij_pov_u_sym = sym_to_u[1]
            cam_pov_u_sym = np.around(sym_to_u[2],2); print('sym', ij_pov_u_sym, cam_pov_u_sym)
            # si le pov_u_sym == pov de la methode
            if np.array_equal(ij_pov_u_sym, ij_pov_m) : Ds = scores_Ds[-1]; print("c'est les memes")
            ##S'il n'y a pas de symetrique au pov
            else : 
                Ds = max(get_ds2(cam_pov_u, cam_pov_m, sig, epsilon), 
                            get_ds2(cam_pov_u_sym, cam_pov_m, sig, epsilon)); print("mais pas les memes")
        ## Symetrique MAIS le pov_u n'a pas de symétique : ex : pov_u == Face pour les voitutres 
        else :  Ds = get_ds2(cam_pov_u, cam_pov_m, sig, epsilon); print("pov n'a pas de sym")

    #####################################################
    #### Impact -- Poids de la categorie courante
    Poids, _ = get_poids1(ij_pov_m, label_pov_m, bvs_courant['US'], df_coords)
    score =  max(Ds, Poids)
    print("Ds",Ds, "- W", Poids)
    
    ## Visualisation cam_u, cam_m, cam_u_sym
    mesh_us = trimesh.load_mesh(path_mesh_us)
    cams = [cam_pov_u, cam_pov_m]; colors = [[1,0,1], [0,1,0]]
    if cam_pov_u_sym is not None : cams.append(cam_pov_u_sym); colors.append([0,0,1])
    show_some_cams(mesh_us, f"{categorie_us}_poriximity_score-{len(BVS[categorie_us]['US']['df'])}cams", cams, colors, dir_outputs)

    return score
##################### Autres métriques
def get_poids_from_BVS(BVS, categorie, labels_us, data_us_cam):
    poids_modelnet = []; poids_us = []
    df_modelenet = BVS[categorie]['modelnet']['df']; df_us = BVS[categorie]['US']['df']

    ## Poids des 8 caméras
    df_both = pd.DataFrame(columns=['cat', 'label', 'poids_modelnet', 'poids_us', 'poids_modelnet_norm', 'poids_us_norm'])
    df_both['cat'] = [categorie for _ in range(len(labels_us))]
    for label in labels_us:
        poids_modelnet.append(df_modelenet.loc[df_modelenet['label'] == label]['poids'].values[0])
        poids_us.append(df_us.loc[df_us['label'] == label]['poids'].values[0])
    df_both['label'] = labels_us; df_both['poids_modelnet'] = poids_modelnet; df_both['poids_us'] = poids_us
    
    # df_both['poids_modelnet_norm'] = np.around(poids_modelnet/max(poids_modelnet), 3)
    # df_both['poids_us_norm'] = np.around(poids_us/max(poids_us), 3) 
    
    ## Normalisation, on divise par la somme pour avoir une densité de proba
    df_both['poids_modelnet_norm'] = np.around(poids_modelnet/np.sum(poids_modelnet), 3)
    df_both['poids_us_norm'] = np.around(poids_us/np.sum(poids_us), 3)  

    ## Version symetrique
    already_checked = []
    df_both_sym = pd.DataFrame(columns=['cat', 'label', 'poids_modelnet', 'poids_us', 'poids_modelnet_norm', 'poids_us_norm'])
    for label in labels_us:
        # ij du labels
        i_label = data_us_cam.loc[data_us_cam['label'] == label]['i'].values[0]
        j_label = data_us_cam.loc[data_us_cam['label'] == label]['j'].values[0]
        # poids du label
        poids_label_m = df_both[df_both['label'] == label]['poids_modelnet'].values[0]    
        poids_label_u = df_both[df_both['label'] == label]['poids_us'].values[0]
        # poids_label_m_norm = df_both[df_both['label'] == label]['poids_modelnet_norm'].values[0]
        # poids_label_u_norm = df_both[df_both['label'] == label]['poids_us_norm'].values[0]
        # Symetrique ?
        sym = get_sym([i_label, j_label], data_us_cam)
        if (sym[0]):
            if (sym[-1] not in already_checked) :
                label_sym = sym[-1]; already_checked.append(label_sym); already_checked.append(label)
                poids_label_sym_m = df_both[df_both['label'] == label_sym]['poids_modelnet'].values[0]
                poids_label_sym_u = df_both[df_both['label'] == label_sym]['poids_us'].values[0]
                poids_label_sym_m_norm = df_both[df_both['label'] == label_sym]['poids_modelnet_norm'].values[0]
                poids_label_sym_u_norm = df_both[df_both['label'] == label_sym]['poids_us_norm'].values[0]
                # On somme les poids des symétriques car chaque poids à un impact de 1, on perdrait cet impact si on prend le max
                df_both_sym.loc[len(df_both_sym)] = [categorie, label, 
                                                     np.sum([poids_label_m, poids_label_sym_m]), 
                                                     np.sum([poids_label_u, poids_label_sym_u]),
                                                     -1, 
                                                     -1]   
             
            else : continue
        else :
            df_both_sym.loc[len(df_both_sym)] = [categorie, label, poids_label_m, poids_label_u, -1, -1]
    df_both_sym['cat'] = [categorie for _ in range(len(df_both_sym))]  
    
    ## Normalisation, on divise par la somme pour avoir une densité de proba
    df_both_sym['poids_modelnet_norm'] = np.around(df_both_sym['poids_modelnet']/np.sum(df_both_sym['poids_modelnet']), 3)  
    df_both_sym['poids_us_norm'] = np.around(df_both_sym['poids_us']/np.sum(df_both_sym['poids_us']), 3)
    
   
    return df_both, df_both_sym


# 1. Distance de Wasserstein circulaire
def wasserstein_circular(weights1, weights2, positions):
    n = len(weights1)
    cost_matrix = cdist(positions, positions, metric='euclidean')
    circular_costs = np.minimum(cost_matrix, np.max(cost_matrix) - cost_matrix)
    return np.sum(circular_costs * np.abs(weights1[:, None] - weights2[None, :]))

# 2. Réindexation circulaire
def cyclic_reindexing(weights1, weights2):
    n = len(weights1)
    min_distance = float('inf')
    for shift in range(n):
        shifted_weights2 = np.roll(weights2, shift)
        distance = np.linalg.norm(weights1 - shifted_weights2)  # Euclidean distance
        min_distance = min(min_distance, distance)
    return min_distance


# 3. Similarité basée sur Fourier
def fourier_similarity(weights1, weights2):
    fft1 = fft(weights1)
    fft2 = fft(weights2)
    return np.linalg.norm(fft1 - fft2)


# 4. Distance pondérée par les positions géométriques
def weighted_geometric_distance(weights1, weights2, positions):
    weighted_positions1 = weights1[:, None] * positions
    weighted_positions2 = weights2[:, None] * positions
    return np.linalg.norm(weighted_positions1 - weighted_positions2)

