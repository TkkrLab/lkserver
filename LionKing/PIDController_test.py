#   Copyright (C) 2018 Renze Nicolai

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

from PIDController import PIDController
import time
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import spline

def test_pid(P = 0.2, I = 0.0, D = 0.0, L = 100):
	pid = PIDController(P, I, D)
	pid.setTarget(0.0)
	END = L
	feedback = 0
	feedback_list = []
	time_list = []
	target_list = []
	
	for i in range(1, END):
		pid.step(feedback)
		print("P",pid.stateP,"I",pid.stateI,"D",pid.stateD)
		output = pid.result
		if pid.targetValue > 0:
			feedback += (output - (1/i))
		if i>9:
			pid.targetValue = 1
		time.sleep(0.02)

		feedback_list.append(feedback)
		target_list.append(pid.targetValue)
		time_list.append(i)

	time_sm = np.array(time_list)
	time_smooth = np.linspace(time_sm.min(), time_sm.max(), 300)
	feedback_smooth = spline(time_list, feedback_list, time_smooth)

	plt.plot(time_smooth, feedback_smooth)
	plt.plot(time_list, target_list)
	plt.xlim((0, L))
	plt.ylim((min(feedback_list)-0.5, max(feedback_list)+0.5))
	plt.xlabel('time (s)')
	plt.ylabel('PID (PV)')
	plt.title('TEST PID')

	plt.ylim((1-0.5, 1+0.5))

	plt.grid(True)
	plt.show()
	
if __name__ == "__main__":
	test_pid(1.2, 1, 0.001, L=50)
