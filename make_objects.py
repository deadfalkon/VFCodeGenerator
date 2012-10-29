#! /usr/bin/env python

import plistlib
import os
import getopt
import sys

#userHeader =  "#import \"_$classname$.h\"\n\n"
#userHeader +=  "@interface $classname$ : _$classname$\n\n\n"
#userHeader += "@end"
#
#userImplementation =  "#import \"$classname$.h\"\n\n"
#userImplementation +=  "@implementation $classname$\n\n\n"
#userImplementation += "@end"

params = ["config-file=","template-directory=","output-folder="]

baseFolder =  os.path.join(os.getcwd(),os.path.split(sys.argv[0])[0])
os.chdir(baseFolder)

def useage():
	print "possible params:"
	for param in params:
		explanation = "(add this param to enable the feature)"
		if param.endswith("="):
			explanation = "(a string)"	
		print "["+param[0:1]+"]"+param[1:]+" "+explanation

try:
	opts, args = getopt.getopt(sys.argv[1:], ":cto", params)
except getopt.GetoptError, err:
	# print help information and exit:
	print str(err) # will print something like "option -a not recognized"
	sys.exit(2)

#argument parsing

output = "."
configFile = None
folder = None

for o, a in opts:
	if  o in ("-c", "--config-file"):
		configFile = os.path.join(baseFolder,a)
	elif o in ("-t", "--template-directory"):
		folder = os.path.join(baseFolder,a)
	elif o in ("-o", "--output-folder"):
		output = os.path.join(baseFolder,a)
	else:
		assert False, "unhandled option"

if configFile is None or folder is None:
	print "no config-file and template-folder set"
	useage()
	sys.exit(1)

config = plistlib.readPlist(configFile)

#argument templating

headerProperties = ""
 
implementationProperties = ""

for className, content in config.items():	
	implementationProperties = ""
	headerProperties = ""
	
	properties = content['properties']
	for property in properties:
		type = property["type"]
		retainType = property["retainType"]
		name = property["name"]
		nameForMethod = name[0:1].upper()+""+name[1:]
		property["Name"] = nameForMethod
	
		print "found a property called " + name
		
		implementationPropertyTemplate = open(folder + "/implementation_property_" + type.replace("*","") + ".txt", 'r').read()
		headerPropertyTemplate = open(folder + "/header_property_" + type.replace("*","") + ".txt", 'r').read()
		for propertyKey, propertyValue in property.items():
			print "replacing $"+propertyKey+"$ with " + propertyValue
			implementationPropertyTemplate = implementationPropertyTemplate.replace("$"+propertyKey+"$", propertyValue)
			headerPropertyTemplate = headerPropertyTemplate.replace("$"+propertyKey+"$", propertyValue)	
		implementationProperties += implementationPropertyTemplate +"\n"
		headerProperties += headerPropertyTemplate +"\n"

	print "###########"		
	
	
	headerTemplate = open(folder + "/header.txt", 'r').read()
	implementationTemplate = open(folder + "/implementation.txt", 'r').read()
	
	for propertyKey, propertyValue in content["customKeys"].items():
		print "replacing $"+propertyKey+"$ with " + propertyValue
		headerTemplate = headerTemplate.replace("$"+propertyKey+"$", propertyValue)
		implementationTemplate = implementationTemplate.replace("$"+propertyKey+"$", propertyValue)
	
#	_className =  "_" + className
	_className =   className
	
	headerTemplate = headerTemplate.replace("$$properties$$", headerProperties)
	headerTemplate = headerTemplate.replace("$classname$", _className)
	
	
	implementationTemplate = implementationTemplate.replace("$$properties$$", implementationProperties)
	implementationTemplate = implementationTemplate.replace("$classname$", _className)
	
	_headerFileName = os.path.join(output,_className+".h")
	_implementationFileName = os.path.join(output,_className+".m")
	
#	if not os.path.exists(className + ".h"):
#		file = open(className + ".h",'w')
#		file.write(userHeader.replace("$classname$", className))
#		file.close()
#		
#	if not os.path.exists(className + ".m"):
#		file = open(className + ".m",'w')
#		file.write(userImplementation.replace("$classname$", className))
#		file.close()
	
	localFile = open(_headerFileName, 'w')
	localFile.write(headerTemplate)
	localFile.close()

	localFile = open(_implementationFileName, 'w')
	localFile.write(implementationTemplate)
	localFile.close()
sys.exit(0)

	