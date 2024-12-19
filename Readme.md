`cam_pose_rep_etude.csv` : coordonnées 3D des caméras utilisées dans l'étude utilisateur

`comparaison_user_study.ipynb` : TODO

--- 

### Alignement/

`*.js` : code js pour lancer l'interface permettant de vérifeir si les orientations sont o, et sinon enregistre les nom des fichiers qui ne sont pas conformes. Il faut lancer dans une fenetre localhost:8000. Et si pbl, il faut relancer le serveur **depuis ce dossier** (voir commentaires dans `app.js`) 

`align_mesh`: réalise l'acp pour aligner les mesh PUIS permet d'appliquer une rotation de 180° pour les mesh qui ont été élignés mais qui n'ont pas la m^me orientation que la mesh de référénce. Le **mesh de référence** de chaque catégorire est enrgistré dans un fichier txt dans Dataset-aligner/CATEGORIE/CATEGORIE_source_mesh.txt.

`Dataset-Aligned/CATEGORIE/*/test ou /train`: contient 

- les fichiers **_aligned.obj** des mesh qui ont été alignés avec les mesh de référence de la catégorie, MAIS pas forcément avec la même orientation

- les fichiers **_aligned_ok.obj**:  alignés + même orentiation

- les fichiers **_aligned_ok.pkl**: contient les transformations appliqués au mesh pour les positionner comme le mesh de référence (identité ou rotation ou autre)

- les fichiers **_aligned_ok_US.*** : mesh alignés avec le modèle de l'étude utilisateur et toutes les transformations nécéssaires.
