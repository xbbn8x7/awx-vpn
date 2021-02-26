import random
import string
import fileinput

output_string = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))

#f = open ('psk.txt','w')
##print(output_string)
psklab = "psk: "
pskval = psklab + output_string
#f.write((pskval))
#f.close()

match_string = 'bgp_as:'

with open("clientData", 'r+') as fd:
	contents = fd.readlines()
	if match_string in contents[-1]:
		contents.append(pskval)
	else:
		for index, line in enumerate(contents):
			if match_string in line and pskval not in contents[index + 1]:
				contents.insert(index + 1, pskval)
				break
	fd.seek(0)
	fd.writelines(contents)