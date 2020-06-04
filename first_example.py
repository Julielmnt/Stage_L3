# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 09:04:38 2020

@author: clement.gouiller
"""

DataFolder="e:/Clément/Julie/"


from mat4py import loadmat #pour charger des .mat
import matplotlib.pyplot as plt # pour tracer les figures
plt.rcParams['figure.figsize'] = [8, 4.5] # taille par dÃ©faut des figures qu'on trace
import os # pour modifier le dossier de travail
import numpy as np # pour travailler avec des array
from pathlib import Path # Pour rendre les Path compatibles entre Mac et Windows
from matplotlib import rc #Les trois prochaines lignes pour que Ã§a ressemble Ã  latex
rc('font', size=16)
rc('text', usetex=True)
import sys
import matplotlib.cm as cm #colormaps
from matplotlib.colors import Normalize #Pour l'utilisation des couleurs dans quiver

# Chargement des données:
os.chdir(Path(DataFolder)) # se place dans le dossier où est rangée la manip
manips=loadmat('PIVnagseul.mat') # Charge les données dans la variable manip

prof=10 # Choisi sur quelle profondeur d'eau travailler (5, 10 ou 15 mm)
plan=16 # Choisi dans quel plan on se place (0=surface, et le max dépend de la profondeur)

# La suite affiche le plan choisi :
# On charge les bonnes données pour (x,y,u,v)
if prof==5:
    piv=manips['piv5']
elif prof==10:
    piv=manips['piv10']
elif prof==15:
    piv=manips['piv15']
else:
    print("prof n'a pas une valeur acceptable")
    sys.exit()
u=np.array(piv[plan]['u'])
v=np.array(piv[plan]['v'])
x=np.array(piv[plan]['x'])
y=np.array(piv[plan]['y'])


# Pour mieux les représenter, je bidouille la colormap
velocity=np.sqrt(u**2+v**2)
velmax=np.mean(velocity)+3*np.std(velocity)
colors = velocity
colors[velocity>velmax]=velmax
colormap=cm.viridis
norm = Normalize()
norm.autoscale(colors)

plt.quiver(x,y,u/velocity,v/velocity,colors)


