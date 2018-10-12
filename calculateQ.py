import numpy as np
import matplotlib.pyplot as plt
from process import readlvm
import glob
import os
from scipy.signal import find_peaks
from lmfit.models import ExponentialModel, LorentzianModel


def baseQ(filename, lambda0, slope, modulation_coefficient, mode, rg=4500):
	base = readlvm(filename)
	time = base[:,0]
	taper = base[:,1]

	print(lambda0, slope, modulation_coefficient)

	lambda0 = float(lambda0) 
	slope = float(slope)
	mc = float(modulation_coefficient.split()[0])

	path = os.path.dirname(os.path.abspath(filename))
	Qs = []
	couplings = []
	lambdas = []
	#files = glob.glob(path+"\*.lvm")
	files = glob.glob(path+"/*.lvm")
	for file in files:
		print(file)
		if file == filename:
			print("basefile")
			continue
		if mode == 1:
			Q, coupling, clambda = calculateQ_1peak(file, time, taper, lambda0, slope, mc, rg)
			Qs.append(Q)
			couplings.append(coupling)
			lambdas.append(clambda)
		else:
			Q1, coupling1, lambda1, Q2, coupling2, lambda2 = calculateQ_2peaks(file, time, taper, lambda0, slope, mc, rg)
			if Q1 == None or coupling1*coupling2 < 0:
				continue
			# if abs(coupling1) < 100:
			# 	Qs.append(Q1)
			# 	couplings.append(coupling1)
			# if abs(coupling2) < 100:
			# 	Qs.append(Q2)				
			# 	couplings.append(coupling2)		
			#print(file)
			Qs.append(Q1)
			couplings.append(coupling1)
			lambdas.append(lambda1)
			Qs.append(Q2)				
			couplings.append(coupling2)
			lambdas.append(lambda2)		

	return Qs, couplings, lambdas
	

def calculateQ_1peak(filename, time, taper, lambda0, slope, modulation_coefficient, rg):
	q = readlvm(filename)
	q = q.ravel()
	q = q / taper - 1
	valley =  q.min()
	valley_index = np.argmin(q)
	q_valley = q[valley_index-rg : valley_index+rg]
	l_valley = time[valley_index-rg : valley_index+rg]

	q_valley = q_valley * -1
	peaks, peak_info = find_peaks(q_valley, height=-valley)
	#results_half = peak_widths(q_valley, peaks, rel_height=0.5)

	mod = LorentzianModel()
	x = np.asarray(list(range(0,2*rg)))
	pars = mod.guess(q_valley, x=x)
	out = mod.fit(q_valley, pars, x=x)

	res = out.fit_report()
	info = res.split("\n")
	variables = parse_info(info, 1)

	h_res, w_res, c_res = variables['height'], variables['fwhm'], variables['center']
	print(h_res, w_res, c_res)
	l = lambda0 + l_valley[int(float(c_res))] * slope * modulation_coefficient
	d_lambda = (l_valley[1] - l_valley[0]) * float(w_res) * slope * modulation_coefficient
	Q = l / d_lambda

	return Q, float(h_res)*100, l


def calculateQ_2peaks(filename, time, taper, lambda0, slope, modulation_coefficient, rg):
	q = readlvm(filename)
	q = q.ravel()
	q = q / taper - 1
	valley = q.min()
	valley_index = np.argmin(q)
	max_height = -1 * q[valley_index]
	q_valley = q[valley_index-rg:valley_index+rg]
	l_valley = time[valley_index-rg:valley_index+rg]	
	
	q_valley = q_valley * -1
	peaks, peak_info = find_peaks(q_valley, height = max_height*0.6, prominence=0.05, distance=50)
	#results_half = peak_widths(q_valley, peaks, rel_height=0.5)

	if len(peaks) != 2:
		print("Wrong peaks with num:", len(peaks))
		return None, None, None, None, None, None

	x = np.asarray(list(range(0,2*rg)))
	y = q_valley

	# One peak guess to get width
	g_mod = LorentzianModel()
	g_pars = g_mod.guess(y, x=x)
	g_out = g_mod.fit(y, g_pars, x=x)
	g_res = g_out.fit_report()
	g_info = g_res.split("\n")
	g_variables = parse_info(g_info, 1)
	guessedWidth = float(g_variables['fwhm']) / 2

	exp_mod = ExponentialModel(prefix='exp_')
	pars = exp_mod.guess(y, x=x)

	lorenz1 = LorentzianModel(prefix='l1_')
	pars.update(lorenz1.make_params())
	pars['l1_center'].set(peaks[0])
	pars['l1_sigma'].set(guessedWidth)
	pars['l1_amplitude'].set(np.pi*guessedWidth*q_valley[peaks[0]])

	lorenz2 = LorentzianModel(prefix='l2_')
	pars.update(lorenz2.make_params())
	pars['l2_center'].set(peaks[1])
	pars['l2_sigma'].set(guessedWidth)
	pars['l2_amplitude'].set(np.pi*guessedWidth*q_valley[peaks[1]])

	mod = lorenz1 + lorenz2 + exp_mod
	init = mod.eval(pars, x=x)
	out = mod.fit(y, pars, x=x)
	res = out.fit_report()
	info = res.split("\n")
	variables = parse_info(info, 2)

	l1_h_res, l1_w_res, l1_c_res = variables['l1_height'], variables['l1_fwhm'], variables['l1_center']
	print(l1_h_res, l1_w_res, l1_c_res)
	l1 = lambda0 + l_valley[int(float(l1_c_res))] * slope * modulation_coefficient
	d_lambda1 = (l_valley[1] - l_valley[0]) * float(l1_w_res) * slope * modulation_coefficient
	Q1 = l1 / d_lambda1


	l2_h_res, l2_w_res, l2_c_res = variables['l2_height'], variables['l2_fwhm'], variables['l2_center']
	print(l2_h_res, l2_w_res, l2_c_res)
	l2 = lambda0 + l_valley[int(float(l2_c_res))] * slope * modulation_coefficient
	d_lambda2 = (l_valley[1] - l_valley[0]) * float(l2_w_res) * slope * modulation_coefficient
	Q2 = l2 / d_lambda2

	return Q1, float(l1_h_res)*100, l1, Q2, float(l2_h_res)*100, l2


def parse_info(info, mode):
	variables = dict()
	for i in range(len(info)):
	    #info[i] = info[i].replace(" ", "")
	    if info[i] == "[[Variables]]":
	    	if mode == 1:
		        for j in range(1, 6):
		            info[i+j] = info[i+j].replace(" ", "")
		            attr = info[i+j].split(":")[0]
		            var = info[i+j].split(":")[1]
		            variables[attr] = var[:var.find("+")]
	    	else:
		        for j in range(3, 13):
		            info[i+j] = info[i+j].replace(" ", "")
		            attr = info[i+j].split(":")[0]
		            var = info[i+j].split(":")[1]
		            variables[attr] = var[:var.find("+")]
	return variables