# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 10:08:25 2023

@author: nacho
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 09:31:43 2023

@author: prpa
"""

from multiprocessing import Process, Manager, current_process
from multiprocessing import Semaphore, Lock
from multiprocessing import Value
from random import randint , random
from time import sleep


N_prods=8
vueltas= 8

def delay(factor = 3):
    sleep(random()/factor)

def uno_no_terminado(values):
    
    for i in range(N_prods):
        if(values[i].value!=-1):
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


def consumer(values,non_empty,empty,result):
    for i in range (N_prods):
        non_empty[i].acquire()
    
    while uno_no_terminado(values):
        values_aux= [v.value for v in values]
        ind_minim=minimo_no_neg(values_aux)
        minim=values_aux[ind_minim]
        values[ind_minim].value = -2
        empty[ind_minim].release()
        print (f"consumer consumiendo {minim} ")
        delay()
        result.append((minim,ind_minim))
        non_empty[ind_minim].acquire()
        print ("consumer desalmacenando")
    
    
def producer(val,non_empty,empty):
    cont = 0
    for j in range(vueltas):
        print (f"producer {current_process().name} produciendo ")
        delay(6)
        cont = cont + randint(1, 10) #Produce
        empty.acquire()
        val.value = cont
        non_empty.release()
        print (f"producer {current_process().name} almacenado {cont} ")
        
    empty.acquire()
    val.value=-1
    non_empty.release()

def main():
    
    manager=Manager()
    result=manager.list()
    
    values=[Value('i',-2)
            for _ in range (N_prods)]
    
    non_empty=[Semaphore(0)
            for _ in range(N_prods)]
    
    empty=[Lock()
           for _ in range(N_prods)]
    
        
    prodlst = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(values[i],non_empty[i],empty[i]))
                for i in range(N_prods) ]
    
    cons = Process(target=consumer,
                      name='consumidor',
                      args=(values,non_empty,empty,result))
    
    prodlst.append(cons)
    
    for p in prodlst:
        p.start()


    for p in prodlst:
        p.join()
     
    print(result)

if __name__ == '__main__':
    main()