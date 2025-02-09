import random
import binascii
from functools import reduce

def generate_uid():
    uid = ''.join(format(random.randint(0, 255), '02x') for _ in range(4)).upper() # 4 byte random uid range 0x00 - 0xff
    bcc = format(reduce(lambda x, y: x ^ y, (int(uid[i:i+2], 16) for i in range(0, 8, 2))), '02x').upper() # XOR the first four bytes of the UID together. An incorrect BCC could brick the tag.
    sak = format(0x08, '02x').upper() # 0x08 for 1k or 0x18 for 4k cards. This script is for 1k cards.
    atqa = format(0x0400, '04x').upper()
    oem = ''.join(format(random.randint(0, 255), '02x') for _ in range(8)).upper() # 8 bytes of manufacturer data
    print(f"uid = {uid}, bcc = {bcc}, sak = {sak}, atqa = {atqa}, oem = {oem}")
    return uid + bcc + sak + atqa + oem

def generate_block4(privKeyA, privKeyB): # Generate block 4 (sector 0)
    keyA = binascii.hexlify(bytearray(privKeyA)).decode().upper()
    keyB = binascii.hexlify(bytearray(privKeyB)).decode().upper()
    accessCondtions = format(0xff0780, '06x').upper()
    undefinedByte = format(0x5a, '02x').upper()
    return keyA + accessCondtions + undefinedByte + keyB

def main():
    privKeyA = [0x7F, 0x33, 0x62, 0x5B, 0xC1, 0x29] # unique keys (funct. will be expanded on later)
    privKeyB = [0x6A, 0x19, 0x87, 0xC4, 0x0A, 0x21]

    dataInString = [generate_uid()] # create list with generated uid, this is block 0 / sector 0
    dataInString.append(["00"] * 32) # fill blocks 1-2 with 00s (sector 0)
    dataInString.append([generate_block4(privKeyA, privKeyB)[i:i+2] for i in range(0, 32, 2)]) # block 3 / sector 0

    genericSector = [
        "00000000000000000000000000000000", # generic sector to fill out rest of the data dump. Uses generic ff keys.
        "00000000000000000000000000000000",
        "00000000000000000000000000000000",
        "ffffffffffffff078069ffffffffffff"
    ]

    dataInString.extend(
        [[genericSector[i][j:j+2] for j in range(0, len(genericSector[i]), 2)] for _ in range(15) for i in range(4)] # fill out the rest of the data dump
    )

    with open("test.bin", "wb") as f: # write to binary file
        for block in dataInString:
            f.write(bytearray.fromhex(''.join(block)))

if __name__ == "__main__":
    main()
