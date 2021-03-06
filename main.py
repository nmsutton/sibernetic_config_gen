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

from __future__ import with_statement
'''
Created on 13.02.2013

@author: Serg
'''
from Generator.Generator import Generator
from Generator.Const import Const
from Generator.ConfigSectsIO import ConfigSectsIO
from XMLWriter.XMLWriter import XMLWriter
import sys, getopt

def put_configto_file(generator, filename="./configurations/configuration.txt"):
	'''
	Create configuration file and put information
	about particle position, velocity and elastic 
	connections.
	TODO: create more check 
	'''
	output_f = open(filename,"w")
	output_f.write("Position\n")
	for  p in generator.particles:
		s_temp = "%s\t%s\t%s\t%s\n"%(p.position.x,p.position.y,p.position.z,p.type)
		output_f.write(s_temp)
	output_f.write("Velocity\n")
	for  p in generator.particles:
		s_temp = "%s\t%s\t%s\t%s\n"%(p.velocity.x,p.velocity.y,p.velocity.z,p.velocity.val)
		output_f.write(s_temp)
	output_f.write("ElasticConnection\n")
	output_f.write(str(len(generator.elasticConnections)) + '\n')
	for  e_c in generator.elasticConnections:
		s_temp = "%s\t%s\t%s\t%s\n"%(e_c.particle_j,e_c.r_ij, e_c.val1, e_c.val2)
		output_f.write(s_temp)
	output_f.close()
	print "Generation have Finished result in file %s"%(filename)
def put_configto_file_temp(generator, pos_file="./configurations/position.txt", vel_file="./configurations/velocity.txt", \
		con_file="./configurations/connection.txt", m_file="./configurations/membranes.txt", \
		pmi_file="./configurations/part_memb_index.txt"):
	'''
	Create configuration file and put information
	about particle position, velocity and elastic 
	connections.
	TODO: create more check 
	'''
	output_f_p = open(pos_file,"w")
	for  p in generator.particles:
		s_temp = "%s\t%s\t%s\t%s\n"%(p.position.x,p.position.y,p.position.z,p.type)
		output_f_p.write(s_temp)
	output_f_v = open(vel_file,"w")
	for  p in generator.particles:
		s_temp = "%s\t%s\t%s\t%s\n"%(p.velocity.x,p.velocity.y,p.velocity.z,p.velocity.val)
		output_f_v.write(s_temp)
	output_f_v.close()
	output_f_conn = open(con_file, "w")
	for  e_c in generator.elasticConnections:
		s_temp = "%s\t%s\t%s\t%s\n"%(e_c.particle_j,e_c.r_ij, e_c.val1, e_c.val2)
		output_f_conn.write(s_temp)
	output_f_conn.close()
	output_f_memb = open(m_file, "w")	
	for m in generator.membranes:
		s_temp = "%s\t%s\t%s\n"%(m[0],m[1],m[2])
		output_f_memb.write(s_temp)
	output_f_memb.close()
	output_f_pmi = open(pmi_file, "w")	
	for pmi in generator.part_memb_index:
		s_temp = "%s\n"%(pmi)
		output_f_pmi.write(s_temp)
	output_f_pmi.close()
	print "Generation have Finished result in file %s"%(pos_file)
	print "Generation have Finished result in file %s"%(vel_file)
	print "Generation have Finished result in file %s"%(con_file)
	print "Generation have Finished result in file %s"%(m_file)
	print "Generation have Finished result in file %s"%(pmi_file)

def create_xml_file(filename,generator):
	xml_writer = XMLWriter(filename)
	for p in generator.particles:
		xml_writer.add_particle(p)
	for c in generator.elasticConnections:
		xml_writer.add_connection(c)
	xml_writer.printtoFile()
def return_args():
	in_file = ''
	out_file = ''
	phy_file = ''
	phy_val = 1.67
	dist_scalar = 1.0
	dist_exp = 1.0
	help_output = False
	kwargs, args = getopt.getopt(sys.argv[1:],"i:p:m:o:", ["dsca=","dexp=", "help"])
	for flag, arg_val in kwargs:
		if flag == '-i':
			in_file = arg_val
		elif flag == '-o':
			out_file = arg_val
		elif flag == '-p':
			phy_val = arg_val
		elif flag == '-m':
			phy_file = arg_val			
		elif flag in ('--dsca'):
			dist_scalar = arg_val
		elif flag in ('--dexp'):
			dist_exp = arg_val		
		elif flag in ('--help'):
			help_output = True

	return in_file, out_file, phy_val, phy_file, dist_scalar, dist_exp, help_output
if __name__ == '__main__':
	p_file = "./configurations/position_muscle.txt"
	v_file = "./configurations/velocity_muscle.txt"
	c_file = "./configurations/connection_muscle.txt"
	m_file = "./configurations/membranes.txt"
	pmi_file = "./configurations/part_memb_index.txt"
	conf_file_group = [p_file, v_file, c_file, m_file, pmi_file]
	in_file, out_file, phy_val, phy_file, dist_scalar, dist_exp, help_output = return_args()
	h = 20.0 * Const.h
	w = 12.0 * Const.h
	d = 20.0 * Const.h
	print('\nRun --help for command line argument options description\n')
	if help_output == True:
		print('example usage of this program:')
		print('$ python main.py')
		print('runs in demo mode where a basic scene is made')
		print('Arguments that can be used:')
		print('-i = input collada file to import')
		print('-o = output config file for sibernetic')
		print('--dsca = number to multiply to distance formula for')
		print('generating elastic connections')
		print('--dexp = exponent to apply to distance formula\n')
		print('Example run with args:')
		print('python main.py -i ./3d_modelling/proto_down_wrm.dae -o ./3d_modelling/proto_down_wrm --dsca 100.0 --dexp 1.5')
		print('For more info see: http://sibernetic-config-gen-docs.readthedocs.io/')
	elif in_file != '' and out_file != '':
		print('importing and exporting scene')
		print("in_file",in_file)
		print("out_file",out_file)		
		conf_ops = ConfigSectsIO()
		boundry_box, particles_imported, connections_imported, membranes, part_memb_index = \
		conf_ops.import_collada(col_file=in_file, dist_scalar=dist_scalar, dist_exp=dist_exp)
		h, w, d = boundry_box[1:6:2]
		g = Generator(h, w, d, phy_val=phy_val)				
		part_phys_mod = phy_val
		g.genConfiguration(gen_elastic=True,gen_muscle=True,gen_liquid=False,particles_imported=particles_imported, \
			part_phys_mod=part_phys_mod,connections_imported=connections_imported)
		g.membranes = membranes
		g.part_memb_index = part_memb_index
		put_configto_file_temp(g,p_file,v_file,c_file,m_file,pmi_file)
		conf_ops.export_conf(out_file=out_file, boundry_box=boundry_box, conf_file_group=conf_file_group)
	else:
		print('importing and exporting scene is not active')
		g = Generator(h, w, d)
		g.genConfiguration(gen_elastic=True,gen_muscle=True,gen_liquid=False)
		put_configto_file_temp(g,p_file,v_file,c_file)
	#put_configto_file(g)
	#create_xml_file("configuration_xml_test", g)
	
