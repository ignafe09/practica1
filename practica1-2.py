#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 10:40:18 2023

@author: prpa
"""
#Comentario: No he puesto un semaforo mutex ya que no es necesario al 
#no interrumpirse los procesos

from multiprocessing import Process, Manager, current_process
from multiprocessing import Semaphore, BoundedSemaphore
from random import randint , random
from time import sleep


N_prods=5
vueltas= 6
K=2

def delay(factor = 3):
    sleep(random()/factor)

def uno_no_terminado(values,posiciones_cons):  
    for i in range(N_prods):
        if(values[i][posiciones_cons[i]]!=-1):
            return True
        
    return False

def minimo_no_neg(values_aux):
    result = 0
    while values_aux[result] < 0:
        result = result +1
    lim_inf = result
    for x in range(lim_inf, N_prods):
        if values_aux[x]>=0 and values_aux[x]<values_aux[result]:
            result = x
    
    return result

def lista_valores(values, posiciones_cons):
    lst=[]
    for i in range (N_prods):
        lst.append(values[i][posiciones_cons[i]])
    return lst

def consumer(values,non_empty,empty,result,posiciones_cons):
    
    for i in range (N_prods):
        non_empty[i].acquire()
    
    while uno_no_terminado(values,posiciones_cons):
        values_aux= lista_valores(values, posiciones_cons)
        ind_minim=minimo_no_neg(values_aux)
        minim=values[ind_minim][posiciones_cons[ind_minim]]
        values[ind_minim][posiciones_cons[ind_minim]]=-2
        posiciones_cons[ind_minim] = (posiciones_cons[ind_minim] + 1) % K
        empty[ind_minim].release()
        delay(6)
        print (f"consumer consumiendo {minim}")
        delay()
        result.append((minim,ind_minim))
        non_empty[ind_minim].acquire()
        print ("consumer desalmacenando")
    
    
def producer(vals,non_empty,empty):
    cont = 0
    pos = 0
    for j in range(vueltas):
        print (f"producer {current_process().name} produciendo")
        cont = cont + randint(1, 10) #Produce
        empty.acquire()
        vals[pos]=cont
        pos=(pos+1)%K
        non_empty.release()
        print (f"producer {current_process().name} almacenado {cont}")
        
    empty.acquire()
    vals[pos]=-1
    non_empty.release() 

def main():
    
    manager=Manager()
    result=manager.list()
    
    posiciones_cons=[0]*N_prods
    
    values=[manager.list([-2]*K)
            for _ in range (N_prods)]
    
    non_empty=[Semaphore(0)
            for _ in range(N_prods)]
    
    empty=[BoundedSemaphore(K)
           for _ in range(N_prods)]
    
        
    prodlst = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(values[i],non_empty[i],empty[i]))
                for i in range(N_prods) ]
    
    cons = Process(target=consumer,
                      name='consumidor',
                      args=(values,non_empty,empty,result,posiciones_cons))
    
    prodlst.append(cons)
    
    for p in prodlst:
        p.start()


    for p in prodlst:
        p.join()
     
    print(result)

if __name__ == '__main__':
    main()
