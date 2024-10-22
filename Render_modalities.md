*  Su 15 :
  
  * Circular config 12 AVEC élévation de $30^{\circ}$
  
  * Dodecahedral config 20 caméras et 4 rendus/caméras (80 vues au total)

* Wang 17 Dominant set : 
  
  * Circular config 12 AVEC élévation de 30° par rapport à l'équateur == 'vue légérement de haut' (with an elevation of 30 degrees from the ground plane)

* Chen 18 Veram : 
  
  * sample discrete views at every 30 degrees both in latitude and longitude --> grid 12x12 --> 244 vues

* Kanezaki 18 RotationNet : 3 configs
  
  * Circular config 12 pour objet avec upright orientation AVEC OU SANS élévation
  
  * Dodecahedral config 20 pour objet sans upright orientation

* Feng 18 Group-view CNN :
  * Circular config 8 : 8 vues séparées de 45° sur l'équateur
  * Circular config 12 : 12 vues séparées de 30° sur l'équateur
    /!\ Vu les images dans l'article, je soupçonne que les caméras sont élevées de 30° par rapport à l'équateur. 

* Yang 19 RelationNet : 
  
  * Circular config 12 AVEC élévation de 30° par rapport à l'équateur == 'vue légérement de haut'

* Zhou 19 en cours …

* Wei 20 view-Graph-CN 
  
  * Circular config 12 AVEC élévation de 30° par rapport à l'équateur.
  
  * Dodecahedral config avec 20 vues

* Qi 21 review : XX

* Hambi 21 MVTN : dépend des options (circular ou spherical) et du nbre de vue N demandé
  
  * Circular config N : N vues séparées équitablement (= 360/N°) sur l'équateur AVEC une élévation de 30°
  
  * Spherical config N : N vues 'equally-spaced on a sphere' ~ dodécahedral

* Hou 24 MVSelect : d'après ce qu'il y a dans le git
  * Circular config 12 AVEC élévation 30°
  * Dodécahédral 20 vues

----------------------------------------------------------------------

--> Différentes config :
Toutes les circular config sont centrées au centroid de l'objet 3D, cf figure 4 [Wei 20]

1. Circular config 8 : 8 vues séparées de 45° sur l'équateur
2. Circular config 12 : 12 vues séparées de 30° sur l'équateur

--> Les rendues avec Circular config 12 ET Dodecahedral 20, sont déjà disponoble sur le git de [Hou 24] : https://github.com/hou-yz/MVSelect



--> Positionner les vpts sur une sphere : ref cité dans Hamdi 21
Markus Deserno. How to generate equidistributed points on the surface of a sphere.
Code :
points = []
for _ in range(N):
    z = random.uniform(-r, r) # Choisir z uniformément dans [-r, r]. [1]
    phi = random.uniform(0, 2 * math.pi) # Choisir phi uniformément dans [0, 2pi]. [1]
    x = math.sqrt(r**2 - z**2) * math.cos(phi) # Calculer x. [2]
    y = math.sqrt(r**2 - z**2) * math.sin(phi) # Calculer y. [2]
    points.append((x, y, z))
