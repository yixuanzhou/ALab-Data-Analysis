import numpy as np
import scipy
import pandas as pd
import matplotlib.pyplot as plt
from process import readlvm

def baseQ(filename, lambda0, slope, modulation_coefficient):
	modulation_coefficients = {"Red": 0.025, "Purple": 0.036, "Gary": 0.0083, "Black": 0.038,
							   "Green": 0.033, "Blue": 0.049, "Orange": 0.036, "white": 0.043,
							   "Pink": 0.089, "Yellow": 0.052}

	base = readlvm(filename)
	time = base[:,0]
	taper = base[:,1]

	print(lambda0, slope, modulation_coefficient)

	lambda0 = float(lambda0) 
	slope = float(slope)
	mc = modulation_coefficients[modulation_coefficient]

	base_name = filename[:-5]
	Qs = [None] * 9
	couplings = [None] * 9
	for x in range(0,9):
		Qs[x], couplings[x] = calculateQ(base_name+str(x+1)+".lvm", time, taper, lambda0, slope, mc)
		#print(Qs[x], couplings[x])
	#plt.scatter(couplings, Qs, c="red")
	#plt.show()
	return Qs, couplings

def calculateQ(filename, time, taper, lambda0, slope, modulation_coefficient):
	q = readlvm(filename)
	q = q.ravel()
	q = q / taper - 1
	valley =  q.min()
	valley_index = np.argmin(q)
	q_valley = q[valley_index-5000 : valley_index+5000]

	from scipy.signal import find_peaks, peak_widths
	q_valley = q_valley * -1
	peaks, peak_info = find_peaks(q_valley, height=-valley)
	results_half = peak_widths(q_valley, peaks, rel_height=0.5)

	from lmfit.models import LorentzianModel
	mod = LorentzianModel()
	x = np.asarray(list(range(0,10000)))
	pars = mod.guess(q_valley, x=x)
	out = mod.fit(q_valley, pars, x=x)

	res = out.fit_report()
	info = res.split("\n")

	height = info[-4]
	height = height.replace(" ", "")
	h_res = height.split(":")[1]
	h_res = h_res[:h_res.find("+")]

	fwhm = info[-5]
	fwhm = fwhm.replace(" ", "")
	w_res = fwhm.split(":")[1]
	w_res = w_res[:w_res.find("+")]

	center = info[-7]
	center = center.replace(" ", "")
	c_res = center.split(":")[1]
	c_res = c_res[:c_res.find("+")]
	#print(h_res, w_res, c_res)
	
	l = lambda0 + float(c_res) / taper.size * (time[-1]-time[0]) * slope * modulation_coefficient
	d_lambda = float(w_res) / taper.size * (time[-1]-time[0]) * slope * modulation_coefficient
	Q = l / d_lambda
	return Q, float(h_res)*100

#baseQ("Q/Q-1553.350-00.lvm")