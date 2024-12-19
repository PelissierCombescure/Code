import pandas as pd
import math 
import numpy as np

from utils_comparaison import gaussian


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



##################### Autres métriques
def get_poids_from_BVS(BVS, categorie, labels_us, data_us_cam):
    poids_modelnet = []; poids_us = []
    df_modelenet = BVS[categorie]['modelnet']['df']; df_us = BVS[categorie]['US']['df']

    ## Poids des 8 caméras
    df_both = pd.DataFrame(columns=['label', 'poids_modelnet', 'poids_us', 'poids_modelnet_norm', 'poids_us_norm'])
    for label in labels_us:
        poids_modelnet.append(df_modelenet.loc[df_modelenet['label'] == label]['poids'].values[0])
        poids_us.append(df_us.loc[df_us['label'] == label]['poids'].values[0])
    df_both['label'] = labels_us; df_both['poids_modelnet'] = poids_modelnet; df_both['poids_us'] = poids_us
    
    df_both['poids_modelnet_norm'] = np.around(poids_modelnet/max(poids_modelnet), 3)
    df_both['poids_us_norm'] = np.around(poids_us/max(poids_us), 3)  

    ## Version symetrique
    already_checked = []
    df_both_sym = pd.DataFrame(columns=['label', 'poids_modelnet_norm', 'poids_us_norm'])
    for label in labels_us:
        # ij du labels
        i_label = data_us_cam.loc[data_us_cam['label'] == label]['i'].values[0]
        j_label = data_us_cam.loc[data_us_cam['label'] == label]['j'].values[0]
        # poids du label
        poids_label_m = df_both[df_both['label'] == label]['poids_modelnet_norm'].values[0]
        poids_label_u = df_both[df_both['label'] == label]['poids_us_norm'].values[0]
        # Symetrique ?
        sym = get_sym([i_label, j_label], data_us_cam)
        if (sym[0]):
            if (sym[-1] not in already_checked) :
                label_sym = sym[-1]; already_checked.append(label_sym); already_checked.append(label)
                poids_label_sym_m = df_both[df_both['label'] == label_sym]['poids_modelnet_norm'].values[0]
                poids_label_sym_u = df_both[df_both['label'] == label_sym]['poids_us_norm'].values[0]
                df_both_sym.loc[len(df_both_sym)] = [label, np.mean([poids_label_m, poids_label_sym_m]), np.mean([poids_label_u, poids_label_sym_u])]   
            else : continue
        else :
            df_both_sym.loc[len(df_both_sym)] = [label, poids_label_m, poids_label_u]
            
    return df_both, df_both_sym
            


