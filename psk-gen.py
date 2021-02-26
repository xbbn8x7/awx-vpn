import random
import string

output_string = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))

f = open ('psk.txt','w')
#print(output_string)
psklab = "psk: "
pskval = psklab + output_string
f.write((pskval))
f.close()