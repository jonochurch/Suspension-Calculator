# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 07:39:32 2021

@author: Jono Church
"""



import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numpy import diff
from statsmodels.nonparametric.smoothers_lowess import lowess
import math
from matplotlib.figure import Figure
import glob
# import matplotlib
# matplotlib.use( 'tkagg' )
txtfiles = []
for file in glob.glob("Leverage Files/*_Shock Compression.txt"):
    txtfiles.append(file)



frame = st.selectbox('Select Frame File', options=txtfiles)
bike = {
    
        'Ratio' : np.array(pd.read_csv(f'{frame}', usecols=[2], delim_whitespace=' ')),
        'Position' : np.array(pd.read_csv(f'{frame}', usecols=[0], delim_whitespace=' ')),
        'Shock' : np.array(pd.read_csv(f'{frame}', usecols=[1], delim_whitespace=' '))
        }
    

position = bike['Position'].reshape(-1,)
shock = bike['Shock'].reshape(-1,)
ratio = 1/bike['Ratio'].reshape(-1,)
pro = int((((ratio[0]/ratio[-1])-1)*100)) #calculate progression from beginning to end

row1_spacer1, row1_1, row1_spacer2, row1_2, row1_spacer3 = st.beta_columns(
    (.1, 3, 0.1, 4, .1))
    
with row1_1:    
    riderweight=st.number_input('Riding Weight(kg)', value = 75) #kg
    bikeweight=st.number_input('Bike Total Weight(kg)', value = 15) #kg

with row1_2:
    weightbalance=st.slider('Weight Distribution', min_value=0.0, max_value=1.0, value=0.6) #%of weight on rear wheel
    rearweight = (riderweight + (bikeweight*0.8)) * weightbalance #rear sprung weight
    travel = position[-1] #bike travel
    stroke = shock[-1] #shock stroke
    
    spring = st.number_input('Spring Rate (lb/in)', value = 450)#lb/in



mspring = spring * 0.175 #covert to N/mm
Force =[]
for x in shock:      #changes spring force to wheel force
    f = mspring * x
    Force.append(f)
wheel = Force / ratio

n =  (rearweight*9.81) #weight on wheel in N
sag = np.round(np.interp(n, wheel, position),1)
sagpc = np.round((sag/travel)*100, 1)               
sagratio = np.round(np.interp(sag, position, ratio),1)
shockforce = n*sagratio
sagforce=shockforce/mspring
shocksagpc = np.round((sagforce/stroke)*100,1)
bottom = (wheel[-1]/9.81)
g=np.round(bottom/rearweight,1) #number of g's to bottom out
work=np.round(np.trapz(wheel, position/1000)) #trapezoidal integration to calculate work 

Rate = diff(wheel)/diff(position)
filtered = lowess(Rate, position[1:], frac=0.3, it=0)
filteredrate = (filtered[:,1]).reshape(-1,)
filteredposition = (filtered[:,0]).reshape(-1,)

ratechange = diff(filteredrate)/diff(filteredposition)
midstroke = np.round(np.interp(sag, filteredposition[1:], ratechange ),2)
midstroke_score = midstroke * 1000
def natural_frequency(k, m) :
    Wo = math.sqrt(k/m)
    return Wo

freq = []
Fn = []
for x in filteredrate:
    b = natural_frequency((x*1000), rearweight)
    freq.append(b)
    Fn.append(b/6.28) 

def dampingrate(f, m, r):
    damping = 2 * r * f * m #natural freq in rad/s x weight x damping ratio
    return damping
FF = np.round(np.interp(sag, filteredposition, Fn ),1)    

dr = (0.1,0.2,0.4,0.5) #damping ratios

row1_spacer1, row1_1, row1_spacer2, row1_2, row1_spacer3 = st.beta_columns(
    (.1, 3, 0.1, 3, .1)
    )
with row1_1:
    st.text(f'Sag @ rear wheel = {sagpc}%')#sag at the wheel
    st.text(f'Sag @ shock = {shocksagpc}%')
    st.text(f'Wheelsag {sag} mm')
    st.text(f'Shock sag {np.round((sagforce),1)} mm')
    st.text(f'Bottoming Force = {int(bottom)}kg')
    st.text(f'Bottoming Gs = {g} g')
    st.text(f'Work Done = {int(work)}J')
    proscore=np.mean(ratechange) * 1000
    st.text(f'Progression Score = {int(proscore)}')
    st.text(f'Progression = {pro}%')
    st.text(f'Mid Stroke Score = {int(midstroke_score)}')
    st.text(f'Natural Frequency @ Sag ={FF}')

with row1_2:

    fig1 = Figure()
    ax = fig1.subplots()
    ax.plot(position, ratio, label =f'Progression = {pro}%')
    ax.set_title("Leverage Ratio", fontname='Heavitas')
    ax.set_ylabel("Ratio")
    ax.set_xlabel('Position')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True)
    ax.legend()
    ax.axvline(x=sag, ls='--')
    fig1.tight_layout()
    st.pyplot(fig1)



row1_spacer1, row1_1, row1_spacer2, row1_2, row1_spacer3 = st.beta_columns(
    (.1, 3, 0.1, 3, .1)
    )
with row1_1:



    fig2 = Figure()
    ax = fig2.subplots()
    ax.plot(position, wheel)
    ax.set_title("Force", fontname='Heavitas')
    ax.set_ylabel("Force (N)")
    ax.set_xlabel('Position')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True)
    ax.axvline(x=sag, ls='--')
    fig2.tight_layout()
    st.pyplot(fig2)



with row1_2:


    fig3 = Figure()
    ax = fig3.subplots()
    ax.plot(filteredposition, filteredrate, 'b')
    ax.set_title("Wheel Rate", fontname='Heavitas')
    ax.set_ylabel("Rate (N/mm)")
    ax.set_xlabel('Position')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True)
    ax.axvline(x=sag, ls='--')
    fig3.tight_layout()
    st.pyplot(fig3)

row1_spacer1, row1_1, row1_spacer2, row1_2, row1_spacer3 = st.beta_columns(
    (.1, 3, 0.1, 3, .1)
    )
with row1_1:


    
    
    fig4 = Figure()
    ax = fig4.subplots()
    ax.plot(filteredposition[1:], ratechange)
    ax.set_title("Change in Rate", fontname='Heavitas')
    ax.set_ylabel("Diff Rate(N/m/mm")
    ax.set_xlabel('Position')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True)
    ax.axhline(y=0, ls='--')
    ax.axvline(x=sag, ls='--')
    fig4.tight_layout()
    st.pyplot(fig4)


with row1_2:

    
    fig5 = Figure()
    ax = fig5.subplots()
    ax.plot(position[1:], Fn)
    ax.set_title("Natural Frequency", fontname='Heavitas')
    ax.set_ylabel("Frequency(Hz)")
    ax.set_xlabel('Position')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True)
    ax.axvline(x=sag, ls='--')
    fig5.tight_layout()
    st.pyplot(fig5)

row1_spacer1, row1_1, row1_spacer2, row1_2, row1_spacer3 = st.beta_columns(
    (.1, 3, 0.1, 3, .1)
    )
with row1_1:
    
    fig6 = Figure()
    ax = fig6.subplots()
    for dampingratio in dr:
        damprate=[]
        for f in freq:
            rate = dampingrate(f, rearweight, dampingratio)
            damprate.append(rate) # in N/m/s
        
        ax.plot(position[1:], damprate, label = f'Damping Ratio={dampingratio}')
        ax.set_title("Wheel Damping Rate", fontname='Heavitas')
        ax.set_ylabel("Damping Rate (N/m/s)")
        ax.set_xlabel('Position')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True)
        ax.axvline(x=sag, ls='--')
        ax.legend()
        
    st.pyplot(fig6)

with row1_2:        
    fig7 = Figure()
    ax = fig7.subplots()
    for dampingratio in dr:
        damprate=[]
        for f in freq:
            rate = dampingrate(f, rearweight, dampingratio)
            damprate.append(rate) # in N/m/s
        shockdampingrate = damprate*(ratio[1:]**2) #N/m/s
        
        
        ax.plot(shock[1:], shockdampingrate, label =f'Damping Ratio = {dampingratio}')
        ax.set_title("Shock Damping Rate", fontname='Heavitas')
        ax.set_ylabel("Damping Rate (N/m/s)")
        ax.set_xlabel('Position')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True)
        ax.axvline(x=sagforce, ls='--')
        ax.legend()
    st.pyplot(fig7)
   



    for dampingratio in dr:
        damprate=[]
        for f in freq:
            rate = dampingrate(f, rearweight, dampingratio)
            damprate.append(rate) # in N/m/s
        shockdampingrate = damprate*(ratio[1:]**2) #N/m/s
        plt.plot(shock[1:], shockdampingrate, label =f'Damping Ratio = {dampingratio}')
        plt.title("Shock Damping Rate", fontname='Heavitas')
        plt.ylabel("Damping Rate (N/m/s)")
        plt.xlabel('Position')
        plt.legend()
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.grid(True)
        plt.xscale('linear')
        plt.axvline(x=shocksag, ls='--')
    plt.show()









