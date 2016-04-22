# The MIT License (MIT)
#
# Copyright (c) 2011, 2013 OpenWorm.
# http://openworm.org
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the MIT License
# which accompanies this distribution, and is available at
# http://opensource.org/licenses/MIT
#
# Contributors:
#      OpenWorm - http://openworm.org/people.html
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
# USE OR OTHER DEALINGS IN THE SOFTWARE.

'''
Created on 18.04.2016

@author: nmsutton
'''

#from Generator import Generator
from Particle import Particle, Float4
from Const import Const

class ConfigSectsIO(object):
	def import_conf(self, in_file):
		boundbox_sect = True
		particle_sect = False
		bounding_box = []
		particles = []

		with open(in_file, "r") as ins:
			for line in ins:
				if line.rstrip() == "[velocity]":
					particle_sect = False
				elif line.rstrip() == "[position]":
					boundbox_sect = False
					particle_sect = True
				elif boundbox_sect == True and line.rstrip() != "":
					bounding_box.append(float(line.rstrip()))					
				elif particle_sect == True and line.rstrip() != "":
					p_x,p_y,p_z,p_t = line.rstrip().split("\t")
					p_type = "{0:.1g}".format(float(p_t))
					particle = Particle(float(p_x),float(p_y),float(p_z),p_type)
					particle.setVelocity(Float4(0.0,0.0,0.0,p_type))
					particles.append(particle)

		return bounding_box, particles

	def export_conf(self, out_file, bounding_box):
		in_p_file = "/CompNeuro/Software/openworm/sibernetic_config_gen/configurations/position_muscle.txt"
		in_v_file = "/CompNeuro/Software/openworm/sibernetic_config_gen/configurations/velocity_muscle.txt"
		in_c_file = "/CompNeuro/Software/openworm/sibernetic_config_gen/configurations/connection_muscle.txt"

		output_f = open(out_file,"w")

		'''output_f.write("0\n")
		output_f.write("100.2\n") #
		#output_f.write("88.844\n")
		output_f.write("0\n")
		output_f.write("66.8\n") #
		#output_f.write("88.8440217622\n")
		output_f.write("0\n")
		output_f.write("668\n") #"
		#output_f.write("88.8439782378\n")'''
		for bb_point in bounding_box:
			output_f.write(str(bb_point))
			output_f.write("\n")
		output_f.write("[position]\n")

		with open(in_p_file, "r") as ins:
			for line in ins:
				output_f.write(line)

		output_f.write("[velocity]\n")

		with open(in_v_file, "r") as ins:
			for line in ins:
				output_f.write(line)

		output_f.write("[connection]\n")

		with open(in_c_file, "r") as ins:
			for line in ins:
				output_f.write(line)

		output_f.write("[end]\n")
		output_f.close()