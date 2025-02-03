import random
import binascii


dataInString = []

privKeyA = [0x7F, 0x33, 0x62, 0x5B, 0xC1, 0x29] # 7f33625bc129
privKeyB = [0x6A, 0x19, 0x87, 0xC4, 0x0A, 0x21] # 6a1987c40a21

# Block 0 / Sector 0
# generate a random uid (range: 0x00 - 0xff)
uid = []
for i in range(4): # 4 bytes uid
    uid.append(random.randint(0, 255)) # generate a random number between 0 and 255
uid = ''.join(format(x, '02x') for x in uid) # convert uid to hex string
uid = uid.upper() # convert to uppercase
print("uid: ", uid)

# the next 12 bytes are the manufacturer data
# Block 0 / Sector 0

# The BCC value is calculated by XORing the first four bytes of the UID together.
# If the BCC value doesn't match, the card could be bricked.
# The BCC is stored in the last byte of the UID.
bcc = uid[0:2]
for i in range(2, 8, 2): # iterate through the first four bytes of the UID
    bcc = int(bcc, 16) ^ int(uid[i:i+2], 16) # XOR the first four bytes of the UID together
    bcc = format(bcc, '02x') # convert to hex
bcc = bcc.upper()
print("BCC: ", bcc)
uid = uid + bcc # append the BCC to the UID

# The SAK value can either be 0x08 or 0x18 for 4k cards. Howver, this script is 1k card.
sak = 0x08 # randomly choose between 0x08 and 0x18
sak = format(sak, '02x').upper() # convert to hex string
print("SAK: ", sak)
uid = uid + sak # append the SAK to the UID

# The ATQA value is 0x0004 for 1k cards, which is 04 00.
atqa = 0x0400
atqa = format(atqa, '04x').upper()
print("ATQA:", atqa)
uid = uid + atqa # append the ATQA to the UID


# OEM data
# 8 bytes of Manufacturer data
# Block 0 / Sector 0
oem = []
for i in range(8):
    oem.append(random.randint(0, 255))
oem = ''.join(format(x, '02x') for x in oem)
oem = oem.upper()
print("OEM: ", oem)
uid = uid + oem # append the OEM data to the UID
dataInString.append(uid) # first line for hex string array making up data of the key

# First line is finished, now to space it apart for correct formatting
newDataInString = []
for i in dataInString:
    i = [i[j:j+2] for j in range(0, len(i), 2)]
    newDataInString.append(i)
dataInString = newDataInString

# Block 2+3 / Sector 0 (32 bytes of 00)
blankblockdata = "00" * 16

# split into 2 characters each then add to datainstring
blankblockdata = [blankblockdata[j:j+2] for j in range(0, len(blankblockdata), 2)]
dataInString.append(blankblockdata * 2) # add to array


# The last block contains Key A, access conditions, an undefined byte,and Key B
# In most cases, Key A is 0xFFFFFFFFFFFF, Key B is 0xFFFFFFFFFFFF
# Block 4 / Sector 0
keyA = str(binascii.hexlify(bytearray(privKeyA)))[2:-1].upper() # convert to hex string
keyB = str(binascii.hexlify(bytearray(privKeyB)))[2:-1].upper() # convert to hex string
accessCondtions = 0xff0780
undefinedByte = 0x5a
block4 = keyA + format(accessCondtions, '06x').upper() + format(undefinedByte, '02x').upper() + keyB
block4 = [block4[j:j+2] for j in range(0, len(block4), 2)] # split into 2 characters each
dataInString.append(block4) # add to array (end of sector 0)

# Sectors 1-4 will be 0x00 with the last block being generic
genericSector = [
"00000000000000000000000000000000",
"00000000000000000000000000000000",
"00000000000000000000000000000000",
"ffffffffffffff078069ffffffffffff"]

for s in range(15): # iterate through the sectors (1-15)
    for i in range(4): # iterate though blocks within the sector
        block = [genericSector[i][j:j+2] for j in range(0, len(genericSector[i]), 2)] # split into 2 characters each
        dataInString.append(block) # add to array  


print("This is the data: ", dataInString)

# write string as hex to binary file
with open("test.bin", "wb") as f: # open file in write binary mode
    print("Writing to test.bin")
    for i in dataInString: # iterate through the data
        f.write(bytearray.fromhex(''.join(i))) # write as hex to binary file
