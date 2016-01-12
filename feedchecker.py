#!/usr/bin/python

import sys
import zipfile
import re
import collections
import csv

csv.field_size_limit(sys.maxsize)
feedFile = sys.argv[1]
delim = "|"
catIds = list()
prodIds = list()
parentProdIds = list()
recommendable = dict()
if(sys.argv[2]):
	delim=sys.argv[2]
##Open files method. Used to open a file and return the descriptor
ff = open(feedFile,'r+')

##Counts if the number of fields per line are consistent with the header
def fieldCount(f,zipF):
	ff = zipF.open(f)
	perLine = ff.readlines()
	print "Header Line: "+perLine[0]
	mainCount = perLine[0].count(delim)
	mainCount = mainCount + 1
	ct = 0
	colCountErr = list()
	print "Number of fields sent are: ",mainCount
	for line in perLine :		
		pipeCount = line.count(delim)
		if ((pipeCount+1) != mainCount):
			#print perLine
			colCountErr.append(ct)
		ct = ct + 1
	return colCountErr


##File Name Format Check 
def fileNameCheck(feedFile):
	print "Feed file Name ----> ", feedFile
	pattern = re.search('^catalog_full.*.zip',feedFile)
	if(pattern is None):
		print '------------------------------------------------------------------------------------'
		print '|The catalog filename format doesn\'t match the format catalog_full_sitename_.*.zip|'
		print '------------------------------------------------------------------------------------'
	else: 
		print '-------------------------------------'
		print '|Catalog filename format check ---->|' 
		print '-------------------------------------'

##Zip file open and process
def zf(feedFile):
	zipF = zipfile.ZipFile(feedFile)
	fileArr = zipF.namelist()
	print 'Following are the contents of the catalog feed file'
	print '---------------------------------------------------'
	print fileArr
	c = len(fileArr)
	fileArr.sort()
	fileArr1 = [None]*10
	fileStr = delim.join(fileArr)
	feedStatus = flatFileChecker(fileStr,c)
	if feedStatus is 'pass':
		print 'Next steps are DATA Validation'
	#for f in fileArr:
	#	if re.search('^category_full.*.txt',f): 
	#categoryFullCheck(fileArr[0],zipF,fileArr)
	#	elif re.search('^product_full.*.txt',f):
	#productFullCheck(fileArr[2],zipF,fileArr)
	#	elif re.search('^product_in_category.*.txt',f):
	#prodCatCheck(fileArr[3],zipF,fileArr)
	#	elif re.search('^product_attribute.*.txt',f):
	#prodAttCheck(fileArr[1],zipF,fileArr)
	#	else: 
	#		print 'Unidentified file type ---------> ', f
		#	exit(0)
	for f in fileArr:
		if re.search('^category_full.*.txt',f):
			fileArr1[0] = f
		elif re.search('^product_full.*.txt',f):
			fileArr1[1] = f
		elif re.search('^product_in_category.*.txt',f):
			fileArr1[2] = f
		elif re.search('^product_attribute.*.txt',f):
			fileArr1[3] = f
		elif re.search('^localized_product.*.txt',f):
			fileArr1[4] = f
	if(fileArr1[0]):
		categoryFullCheck(fileArr1[0],zipF,fileArr)
	if(fileArr1[1]):
		productFullCheck(fileArr1[1],zipF,fileArr)
	if(fileArr1[2]):
		prodCatCheck(fileArr1[2],zipF,fileArr)
	if(fileArr1[3]):
		prodAttCheck(fileArr1[3],zipF,fileArr)
	if(fileArr1[4]):
		localProdCheck(fileArr1[4],zipF,fileArr)
	#	else: 
	#		print 'Unidentified file type ---------> ', f

#Category Full file Checker
def categoryFullCheck(f,zipF,files):
	cfD = zipF.open(f) 
	print '-----------------------------------------------'
	print f + ' File validation in progress'
	print '-----------------------------------------------'
	catLine = cfD.readlines()
	theDict = fileOpen(f,zipF)
	catCount = fieldCount(f,zipF)
	#catDict = csv.DictReader(cfD2,delimiter='|')
	catHeader = catLine[0].rstrip()
	catHeaderRes = headerCheck(catHeader,f)
	if catCount:
		print "Column Count Check Status ----> FAILED ",catCount
	else:
		print "Column Count Check Status ----> SUCCESS"

	if catHeaderRes is 1: 
		print 'Category File Headers Check Status ----> SUCCESS'
	else:
		print 'Category File Headers Check Status ----> FAILED'

	parents = list()
	for rows in theDict:	
		if('parent_id' in rows.keys()):
			parents.append(rows['parent_id'])
		catIds.append(rows['category_id'])
	theDict1 = fileOpen(f,zipF)
	numOfCategories = len(catIds)
	chkSetofCat = len(set(catIds))
	catSet = set(catIds)
	catIdRepeat = list()
	#catIdRepeat = set ([x for x in catIds if catIds.count(x)>1])
	for c in catIds:
		if c in catSet:
			catSet.remove(c)
		else:
			catIdRepeat.append(c)

	if(numOfCategories!=chkSetofCat):
		print "The following are repeating category ids:"
		for y in catIdRepeat:
			print y
		print '----------->'

	parents = set(parents)
	#print parents
	uniqueParentCount = len(parents)
	listDict = list(theDict1)
	if(rows['parent_id']):
		for item in parents:
			flag = 0
			if item != '':
				for rows in listDict:
					if item == rows['category_id']:
						flag = 1
						break
					
				if flag != 1 :
					print "INVALID PARENT ---->", item
	print "Number of unique categories are:", len(set(catIds))

#Product Full file Checker
def productFullCheck(f,zipF,files):
	pfD = zipF.open(f) 
	print '-----------------------------------------------'
	print f + ' File validation in progress'
	print '-----------------------------------------------'
	prodLine = pfD.readlines()
	prodDict = fileOpen(f,zipF)
	prodCount = fieldCount(f,zipF)
	#catDict = csv.DictReader(pfD2,delimiter='|')
	prodHeader = prodLine[0].rstrip()
	prodHeaderRes = headerCheck(prodHeader,f)
	if prodHeaderRes is 1: 
		print 'Product Full File Headers check status ----> SUCCESS'
	else:
		print 'Product Full Headers check status ----> FAILED'

	if prodCount:
		print "Column Count Check Status ----> FAILED ",prodCount
	else:
		print "Column Count Check Status ----> SUCCESS"

	noPriceCount = 0
	noRecCount = 0
	for rows in prodDict:	
		prodIds.append(rows['product_id'])
		if('product_parent_id' in rows):
			if(rows['product_parent_id']):
				parentProdIds.append(rows['product_parent_id'])
		#recommendable[rows['product_id']] = rows['price']
		if rows['price']== '':
			noPriceCount += 1
		if('recommendable' in rows):
			if rows['recommendable'] == 'false' or rows['recommendable'] == '' or rows['recommendable'] == '0':
				noRecCount += 1
	print "Number of Products with no Price ---->", noPriceCount
	print "Number of Products with recommendable as False ---->", noRecCount
	theDict1 = fileOpen(f,zipF)
	numOfProd = len(prodIds)
	chkSetofProd = len(set(prodIds))
	prodSet = set(prodIds)
	parentProdSet  = set(parentProdIds)
	prodIdRepeat = list()
	#prodIdRepeat = set ([x for x in prodIds if prodIds.count(x)>1])
	for p in prodIds:
		if p in prodSet:
			prodSet.remove(p)
		else:
			prodIdRepeat.append(p)

	if(numOfProd!=chkSetofProd):
		print "The following are repeating product ids:"
		print set(prodIdRepeat)
		print '----------->'
	else: 
		print "Product Ids uniqueness Check ----> SUCCESS"
	listDict = list(theDict1)
	for item in parentProdSet:
		flag = 0
		if item != '':
			for row in listDict:
				if item == row['product_id']:
					flag = 1
					break
				
			if flag != 1 :
				print "INVALID PARENT PRODUCT ---->", item
		



#Product in Category file Checker
def prodCatCheck(f,zipF,files):
	pcfD = zipF.open(f) 
	print '-----------------------------------------------'
	print f + ' File validation in progress'
	print '-----------------------------------------------'
	pcLine = pcfD.readlines()
	pcDict = fileOpen(f,zipF)
	pcCount = fieldCount(f,zipF)
	pcHeader = pcLine[0].rstrip()
	pcHeaderRes = headerCheck(pcHeader,f)
	if pcHeaderRes is 1: 
		print 'Product in Category File Headers check status ----> SUCCESS'
	else:
		print 'Product in Category File Headers check status ----> FAILED'

	if pcCount:
		print "Column Count Check Status ----> FAILED ",pcCount
	else:
		print "Column Count Check Status ----> SUCCESS"
	pcProd = list()
	pcCat = list()
	for rows in pcDict:	
		pcProd.append(rows['product_id'])
		pcCat.append(rows['category_id'])
	invalidProd = list()
	invalidCat = list()
	setProd = set(prodIds)
	setCat = set(catIds)
	pcProdSet = set(pcProd)
	pcCatSet = set(pcCat)
	'''
	for prod in set(pcProd):
		if prod not in set(prodIds):
			invalidProd.append(prod)
	#print "CAT IDS in set --->", set(pcCat)
	#print "MASTER CAT --->", catIds
	for cat in set(pcCat):
		if cat not in set(catIds):
			invalidCat.append(cat)
	'''
	#print 'MASTER CAT SET---->',setCat 
	#print 'pc CAT SET',pcCatSet
	invalidProd = list(pcProdSet - setProd)
	invalidCat = list(pcCatSet - setCat)
	if invalidCat:
		print "Categories not in the category_full file are: ----> FAILED", invalidCat
	else:
		print "Categories are all valid ----> SUCCESS"
	if invalidProd:
		print "Products not in the product_full file are: ----> FAILED", invalidProd
	else:
		print "Products are all valid ----> SUCCESS"



#Product Attribute File Checker
def prodAttCheck(f,zipF,files):
	pAttfD = zipF.open(f) 
	print '-----------------------------------------------'
	print f + ' File validation in progress'
	print '-----------------------------------------------'
	pAttLine = pAttfD.readlines()
	pAttDict = fileOpen(f,zipF)
	pAttCount = fieldCount(f,zipF)
	pAttHeader = pAttLine[0].rstrip()
	pAttHeaderRes = headerCheck(pAttHeader,f)
	if pAttHeaderRes is 1: 
		print 'Product in Category File Headers check status ----> SUCCESS'
	else:
		print 'Product in Category File Headers check status ----> FAILED'

	if pAttCount:
		print "Column Count Check Status ----> FAILED ",pAttCount
	else:
		print "Column Count Check Status ----> SUCCESS"
	pAttProd = list()
	for rows in pAttDict:
		pAttProd.append(rows['product_id'])
	invalidProdAtt = list()
	setProd = set(prodIds)
	pAttProdSet = set(pAttProd)
	invalidProdAtt = list(pAttProdSet - setProd)
	if invalidProdAtt:
		print "Products not in the product_full file are: ----> FAILED", invalidProdAtt
	else:
		print "Products are all valid ----> SUCCESS"
	print "Product Att",len(pAttProd)
	print "Product Att Set",len(pAttProdSet)
	print "Product Full",len(setProd)

#localized_product check
def localProdCheck(f,zipF,files):
	loProdfD = zipF.open(f) 
	print '-----------------------------------------------'
	print f + ' File validation in progress'
	print '-----------------------------------------------'
	loProdLine = loProdfD.readlines()
	loProdDict = fileOpen(f,zipF)
	loProdCount = fieldCount(f,zipF)
	loProdHeader = loProdLine[0].rstrip()
	loProdHeaderRes = headerCheck(loProdHeader,f)
	if loProdHeaderRes is 1: 
		print 'Localized Product File Headers check status ----> SUCCESS'
	else:
		print 'Localized Product  File Headers check status ----> FAILED'

	if loProdCount:
		print "Column Count Check Status ----> FAILED ",loProdCount
	else:
		print "Column Count Check Status ----> SUCCESS"
	loProdProd = list()
	for rows in loProdDict:
		loProdProd.append(rows['product_id'])
	invalidloProd = list()
	setProd = set(prodIds)
	loProdProdSet = set(loProdProd)
	invalidloProd = list(loProdProdSet - setProd)
	if invalidloProd:
		print "Products not in the product_full file are: ----> FAILED", invalidloProd
	else:
		print "Products are all valid ----> SUCCESS"
	print "Product Att",len(loProdProd)
	print "Product Att Set",len(loProdProdSet)
	print "Product Full",len(setProd)


#Zip Content File Open and Reset
def fileOpen(f,zipF):
	fd = zipF.open(f) 
	theDict = csv.DictReader(fd,delimiter=delim)
	return theDict


#Header Check Function 
def headerCheck(header,f):
	if re.search('^category_full.*.txt',f):
		checkArray = ['category_id','parent_id','name']	
	elif re.search('^product_full.*.txt',f):
		checkArray = ['product_id','name','price','recommendable','link_url','image_url']  
        elif re.search('^product_in_category.*.txt',f):
	        checkArray = ['category_id','product_id']  
        elif re.search('^product_attribute.*.txt',f):
                checkArray = ['product_id','attr_name','attr_value']   
        elif re.search('^localized_product.*.txt',f):
                checkArray = ['product_id','name','description','language_tag','image_url','link_url']   
        else:
		print 'Unidentified file type ---------> ', f
	flag1 = 1
	for i in checkArray:
		if re.search(i,header):
			flag1 = flag1 and flag1  
        	else:
			flag1 = 0
		if flag1 is 0:
			print 'Following field in header needs review ---->',i 
	return flag1

##Flat File Name Checker
def flatFileChecker(fileStr,c):
	if c is 4:
		fileFormat = ['product_full','category_full','product_in_category','product_attribute']
	elif c is 3:
		fileFormat = ['product_full','category_full','product_in_category'] 
	else: 
		fileFormat = fileStr
		print "The catalog file is invalid! Kindly check contents...", fileStr
	countPass = 0 
	for f in fileFormat:
		flag = 0
		patt = f+'.*.txt'
		resPat = re.search(patt,fileStr)
		print 'Checking for file presence and format...',patt 
		if resPat != None:
			flag =  1 
			countPass = countPass + 1
		if flag is 1:
			print 'File Name Check ----> SUCCESS'
		else:
			print 'File Name Check ----> FAILED'
	if countPass != c:
		print 'File names within catalog feed aren\'t per required format' 
		return 'pass'
	else:
		return 'pass'

##Function to parse zip and pass on catalog files for checks
#fieldCount()
fileNameCheck(feedFile)
zf(feedFile)
#uniqueProdIdCheck()
ff.close()
	
