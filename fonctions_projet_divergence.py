#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fonctions stage
"""
DataFolder="C:/Users/Julie_000/Desktop/Stage/Python" 

# Importation des librairies
from mat4py import loadmat #pour charger des .mat
import matplotlib.pyplot as plt # pour tracer les figures
import os # pour modifier le dossier de travail
import numpy as np # pour travailler avec des array
from pathlib import Path # Pour rendre les Path compatibles entre Mac et Windows
from matplotlib import rc #Les trois prochaines lignes pour que Ã§a ressemble Ã  latex
rc('font', size=16)
rc('text', usetex=True)

import matplotlib.cm as cm #colormaps
from matplotlib.colors import Normalize #Pour l'utilisation des couleurs dans quiver

import scipy as sc #pour l'analyse
from matplotlib.ticker import MaxNLocator #pour les courbes de niveau
from scipy.ndimage import gaussian_filter #Filtrage gaussien


# Definition des fonctions
def PIV(prof,manips): 
    """retourne les données des plans pour la bonne profondeur"""
    
    if prof==5:
        piv=manips['piv5']
    elif prof==10:
        piv=manips['piv10']
    elif prof==15:
        piv=manips['piv15']
    else:
        return("prof n'a pas une valeur acceptable")   
    return(piv)

def donnees(prof,plan,manips):
    """Retourne les tableaux de données pour le plan choisi de la profondeur donnée"""
    
    piv=PIV(prof,manips)
    u=np.array(piv[plan]['u'])
    v=np.array(piv[plan]['v'])
    x=np.array(piv[plan]['x'])
    y=np.array(piv[plan]['y'])
    return(u,v,x,y)




def deriv(y,x,axis):
    """Dérive un tableau 2D y par rapport à x suivant un axe donné"""
    if axis==0:
        return((y[1:,:]-y[:-1,:])/(x[1:,:]-x[:-1,:]))#Donc là le tableau est de taille (n-1,n)
    if axis==1:
        return((y[:,1:]-y[:,:-1])/(x[:,1:]-x[:,:-1]))#Donc là le tableau est de taille (n,n-1)
    return("deriv ne fonctionne que pour des tableaux 2D")
    

def abcisse(x,axis):
    """somme discrète x[i+1]+x[i]/2 suivant un axe donné"""
    if axis==0:
        return((x[1:,:]+x[:-1,:])/2)
    if axis==1:
        return((x[:,1:]+x[:,:-1])/2)
    return("abcisse ne fonctionne que pour des tableaux 2D")
        
    
def good_shape(a):
    "remise à la bonne shape des tableaux a et b pour pouvoir ensuite les sommer"
    "Ne fonctionne que dans ce cas précis avec des tableaux (n,n-1) et (n-1,n) et donne un tableau (n-1,n-1)"
    #donc on perd des données, je ne sais pas comment faire autrement...
    n=np.max(np.shape(a))
    if np.shape(a)[0]==n:
        return(a[:-1,:])
    if np.shape(a)[1]==n:
        return(a[:,:-1])
    return("les dimensions des array ne conviennent pas pour l'usage de good_shape, ou problème avec n")
 
    
def somme(a,b):
    "juste somme d'array"
    if np.shape(a)==np.shape(b):
        return(a+b)
    return("les array n'ont pas la bonne shape")




def masque_carre(a):
    "Enlève les données sous le nageur (forme de carré)"
    b=a
    shape=np.shape(b)
    if np.size(shape)==2:#cas la plupart du temps
        b[27:33,27:33]=np.zeros((6,6))
        
    elif np.size(shape)==3:#pour gérer cas divergence/filtrage/masque
        l=shape[0]
        for i in range(l):
            b[i,27:33,27:33]=np.zeros((6,6))
    return(b)

def masque(a,x,y,dx,dy):
    "applique un masque rond"
    b=a
    r=np.sqrt(dx**2+dy**2)
    shape=np.shape(b)
    if np.size(shape)==2:
        if shape[0]==59:
            return(np.where(r>6,b,0))
        elif shape[0]==60:
            r=np.sqrt(x**2+y**2)
            return(np.where(r>6,b,0))
    elif np.size(shape)==3:#pour gérer cas divergence/filtrage/masque
        l=shape[0]
        if shape[1]==59:
            for i in range(l):
                b[i,:,:]=np.where(r>6,b[i,:,:],0)
            return(b)
        elif shape[1]==60:
            r=np.sqrt(x**2+y**2)
            for i in range(l):
                b[i,:,:]=np.where(r>6,b[i,:,:],0)
            return(b)

def masque_puis_filtregauss(a,sigma):
    "Applique le masque puis le filtre gaussien et s'adapte à la taille de sigma"
    if np.size(sigma)==1:
        return(gaussian_filter(masque(a),sigma))
    else :
        return("sigma n'a pas la bonne taille")

    

def filtregauss_puis_masque(a,sigma):
    "Applique le filtre gaussien puis le masque et s'adapte à la taille de sigma"
    if np.size(sigma)==1:
        return(masque(gaussian_filter(a,sigma)))
    else :
        return("sigma n'a pas la bonne taille")
    
    

def Filtres(sigmas,div, ordre) :
    "Tableau des divergence filtrées suivant l'odre donné : 0 pour le masque d'abord, 1 pour le filtre d'abord, 2 sans masque"
    #boucle de création des tableaux
    l=np.shape(sigmas)[0]
    n=np.shape(div)[0]
    Filtres=np.zeros((l,n,n))#création du tableau de tableau
    if ordre==0:
        for i in range(np.shape(sigmas)[0]):
            Filtres[i]=masque_puis_filtregauss(div,sigmas[i])
        return(Filtres)
    
    elif ordre==1:
        for i in range(np.shape(sigmas)[0]):
            Filtres[i]=filtregauss_puis_masque(div,sigmas[i])
        return(Filtres)
    
    elif ordre==2:
        for i in range(np.shape(sigmas)[0]):
            Filtres[i]=gaussian_filter(div,sigmas[i])
        return(Filtres)
    return("order n'a pas la bonne valeur")
               



def dUfiltre(Ufiltre,x,axis):
    "Dérive et remet à la bonne taille donne un tableau (l,n-1,n-1)"
    l=np.shape(Ufiltre)[0]
    n=np.shape(Ufiltre)[1]
    dU=np.zeros((l,n-1,n-1))
    for i in range(l):
        dU[i]=good_shape(deriv(Ufiltre[i], x, axis))
    return(dU)


def somme3D(a,b):
    "somme les tableaux a et b suivant le premier axe"
    S=np.zeros(np.shape(a))
    if np.shape(a)==np.shape(b):
        l=np.shape(a)[0]
        for i in range(l):
            S[i]=a[i]+b[i]
        return(S)
    else:
        return("a et b n'ont pas la même shape")
 
def divergence2D_gauss(u,v,x,y,sigma):
    "Applique le programme de divergence2D avec filtre gaussien sur la vitesse"

    #Filtrage
    u_filtre=gaussian_filter(u,sigma)
    v_filtre=gaussian_filter(v,sigma)
    #dérivation
    du_filtre,dv_filtre=deriv(u_filtre,x,1),deriv(v_filtre,y,0)
    dx=abcisse(x,1)
    dy=abcisse(y,0)
    #shape
    du_filtre,dv_filtre=good_shape(du_filtre),good_shape(dv_filtre)
    dx,dy=good_shape(dx),good_shape(dy)
    #somme
    div = somme(du_filtre,dv_filtre)
    #masque
    div_masque=masque(div,x,y,dx,dy)
    return(div_masque,dx,dy)


def divergence2D(u,v,x,y):
    "Applique le programme de divergence2D sans filtre"
    #Dérivation
    du,dv=deriv(u,x,1),deriv(v,y,0)
    dx,dy=abcisse(x,1),abcisse(y,0)
    #Remise à la bonne taille
    du,dv=good_shape(du),good_shape(dv)
    dx,dy=good_shape(dx),good_shape(dy)
    #somme des tableaux
    div = somme(du,dv)
    #masque
    div_masque=masque(div,x,y,dx,dy)
    return(div_masque,dx,dy)
    
#Fonctions de plot
        
def plot_superposition (div0,div1,title,m):
    "Tracé des divergences pour ordre de filtrage différents"
    #norme
    extremums=np.array([np.max(div0),np.min(div0),np.max(div1),np.min(div1)])
    vmax,vmin=np.max(extremums),np.min(extremums)
    norm=Normalize(vmin=vmin, vmax=vmax)
    if m==2:
        fig, (l0,l1) = plt.subplots(nrows=2,ncols=1,num=title)
        #l0
        im0 = l0.contourf(dx,dy,div0,levels=levels, cmap=colormap2,norm=norm)
        l0.set_title("Filtre avant dérivation")
        fig.colorbar(im0,ax=l0)
        im1=l0.quiver(x[::2,::2],y[::2,::2],u[::2,::2]/velocity[::2,::2],v[::2,::2]/velocity[::2,::2],colors[::2,::2])
        fig.colorbar(im1, ax=l0)
        #l1
        im2 = l1.contourf(dx,dy,div1,levels=levels, cmap=colormap2,norm=norm)
        l1.set_title("Filtre après dérivation")
        fig.colorbar(im2,ax=l1)
        im3=l1.quiver(x[::2,::2],y[::2,::2],u[::2,::2]/velocity[::2,::2],v[::2,::2]/velocity[::2,::2],colors[::2,::2])
        fig.colorbar(im3, ax=l1) 
        
        
    if m==1:
        fig, l0 = plt.subplots(nrows=1,ncols=1,num=title)
        #l0
        im0 = l0.contourf(dx,dy,div0,levels=levels, cmap=colormap2,norm=norm)
        l0.set_title("Filtre avant dérivation")
        fig.colorbar(im0,ax=l0)
        im1=l0.quiver(x[::2,::2],y[::2,::2],u[::2,::2]/velocity[::2,::2],v[::2,::2]/velocity[::2,::2],colors[::2,::2])
        fig.colorbar(im1, ax=l0)
        
    fig.tight_layout(pad=3.2)
    fig.suptitle(title,fontsize=16)
    plt.show()

