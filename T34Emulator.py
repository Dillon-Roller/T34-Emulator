import sys

STACK = ['00'] * 256
SP = 'FF'
PC = 0
AC = '00'
XR = '00'
YR = '00'
INS = '00'
OP1 = '--'
OP2 = '--'
AMOD = 'impl'
FLAGS = ['0'] * 8
FLAGS[2] = 1


def main():
    if len(sys.argv) > 1:
        data = loadObj(sys.argv[1])
    else:
        data = ['00'] * 65536
    monitor(data)
    return


def loadObj(filename):
    '''
    CURRENTLY ONLY READS ONE LINE OF OBJ. WILL UPDATE FOR NEXT PART
    :param filename:
    :return:
    '''
    try:
        f = open(filename)
    except FileNotFoundError:
        print("File not found, running without input:")
        print()
        return ['00']*65536
        
    intelHex = f.read()

    byte_count = int(intelHex[1:3], 16)
    address = intelHex[3:7]
    address_int = int(address, 16)

    data = ['00'] * 65536
    data_hex = []
    actual_data = intelHex[9:9 + (byte_count * 2)]
    i = 0
    j = 2
    while i < len(actual_data):
        data_hex.append(actual_data[i:j])
        i += 2
        j += 2

    i = 0
    while i < len(data_hex):
        data[address_int + i] = data_hex[i]
        i += 1

    
    return data


def monitor(data):
    choice = ' '

    while choice != 'exit':
        print("> ", end=" ")
        
        try:
            choice = str(input())
        except EOFError:
            raise SystemExit
        
        if choice.find('R') != -1:
            runAtAddr(data, choice)

        elif choice.find(':') != -1:
            editMem(data, choice)
            
        elif choice.find('.') != -1:
            showRange(data, choice)
            
        else:
            showAddr(data, choice)
    return

def showAddr(data, choice):
    if choice != 'exit':
        try:
            print(" " + choice + "  " + data[int(choice, 16)])
        except ValueError:
            raise SystemExit
    return

def showRange(data, choice):
    choice = choice.split('.')
    if int(choice[0], 16) > 65536 or int(choice[1], 16) > 65536:
        print("Memory Address out of range")
        print()
        return
    difference = int(choice[1], 16) - int(choice[0], 16) + 1
    
    start = int(choice[0], 16)
    i = 0
    print(" " + choice[0] + "  ", end="")
    while i < difference:
        if start < 0:
            break

        print(data[start + i].zfill(2), end=" ")
        i += 1
        if i % 8 == 0:
            print()
            if i != difference:
                val = hex(int(choice[0], 16) + i)[2:].upper().zfill(3)
                print(" " + str(val) + "  ", end='')
    print()
    return

def editMem(data, choice):
    full_choice = choice.split(' ')
    choice = full_choice[0].strip(':')
    del full_choice[0]

    i = 0
    start_index = int(choice, 16)
    while i < len(full_choice):
        if start_index < 0:
            break
        if start_index + i > len(data) - 1:
            data.append('00')

        data[start_index + i] = full_choice[i].upper()
        i += 1
    return

def runAtAddr(data, choice):
    global INS, AMOD, SP, AC, XR, YR, FLAGS, PC, OP1, OP2
    
    choice = choice.strip('R')
    print(" PC  OPC  INS   AMOD OPRND  AC XR YR SP NV-BDIZC")

    PC = int(choice, 16)
    if(data[PC] == '00'):
        print("No data here or break")
        return
    else:
        while(data[PC] != '00'):
            print(" " + hex(PC)[2:].upper().zfill(3), end='  ')
            print(data[PC], end='')
            computeInfo(data)
            print("  " + INS + "   " + AMOD + " " + OP1 + " " + OP2 + "  " + str(AC).zfill(2) + " " + str(XR).zfill(2) + " " + str(YR).zfill(2) + " " + str(SP).zfill(2) + " ", end='')
            for j in FLAGS:
                print(j, end='')
            print()
        computeInfo(data)
        print(" " + hex(PC)[2:].upper().zfill(3), end='  ')
        print(data[PC], end='')
        print("  " + INS + "   " + AMOD + " " + OP1 + " " + OP2 + "  " + str(AC).zfill(2) + " " + str(XR).zfill(2) + " " + str(YR).zfill(2) + " " + str(SP).zfill(2) + " ", end='')
        for j in FLAGS:
            print(j, end='')
        print()
    return

def ASL(data, mode):
    global AC, FLAGS, AMOD, INS, OP1, OP2, PC
    INS = 'ASL'
    OP1 = data[PC + 1]
    OP2 = '--'
    if(mode == 'acc'):
        OP1 = '--'
        AMOD = '   A'
        acc = int(AC, 16)
        acc = acc * 2

        checkNeg(acc)
        checkZero(acc)
        checkCarry(acc)
        AC = str(hex(acc)[2:].upper())

    if(mode == 'zpg'):
        AMOD = ' zpg'
        acc = int(data[int(OP1, 16)], 16)
        acc = acc * 2
        checkNeg(acc)
        checkZero(acc)
        checkCarry(acc)
        data[int(OP1, 16)] = str(hex(acc)[2:].upper())

    if(mode == 'abs'):
        AMOD = ' abs'
        OP2 = data[PC + 2]
        acc = int(data[int(OP2 + OP1, 16)], 16)
        acc = acc * 2
        checkNeg(acc)
        checkZero(acc)
        checkCarry(acc)
        data[int(OP2 + OP1, 16)] = str(hex(acc)[2:].upper())

    return

def BIT(data, mode):
    global AC, PC, OP1, OP2, AMOD, INS, FLAGS
    INS = 'BIT'
    OP1 = data[PC + 1]
    OP2 = '--'
    int_ac = int(AC, 16)
    if (mode == 'zpg'):
        AMOD = ' zpg'
        mem = int(data[int(OP1, 16)], 16)
        bin_mem = bin(mem)[2:]
        FLAGS[0] = bin_mem[0]
        FLAGS[1] = bin_mem[1]

    if (mode == 'abs'):
        AMOD = ' abs'
        OP2 = data[PC + 2]
        mem = int(data[int(OP2 + OP1, 16)], 16)
        bin_mem = bin(mem)[2:]
        FLAGS[0] = bin_mem[0]
        FLAGS[1] = bin_mem[1]

    result = int_ac & mem
    checkZero(result)
    return

def BRK():
    global SP, FLAGS, AMOD, INS, OP1, OP2
    OP1 = '--'
    OP2 = '--'
    INS = 'BRK'
    AMOD = 'impl'
    FLAGS[5] = '1'
    FLAGS[3] = '1'
    _SP = int(SP, 16)
    _SP = _SP - 3
    SP = str(hex(_SP)[2:].upper())
    return

def CLC():
    global FLAGS, AMOD, INS, OP1, OP2
    INS = 'CLC'
    AMOD = 'impl'
    FLAGS[7] = '0'
    OP1 = '--'
    OP2 = '--'
    
    return

def CLD():
    global FLAGS, AMOD, INS, OP1, OP2
    INS = 'CLD'
    AMOD = 'impl'
    FLAGS[4] = '0'
    OP1 = '--'
    OP2 = '--'
    
    return

def CLI():
    global FLAGS, AMOD, INS, OP1, OP2
    INS = 'CLI'
    AMOD = 'impl'
    FLAGS[5] = '0'
    OP1 = '--'
    OP2 = '--'
        
    return

def CLV():
    global FLAGS, AMOD, INS, OP1, OP2
    INS = 'CLV'
    AMOD = 'impl'
    FLAGS[1] = '0'
    OP1 = '--'
    OP2 = '--'
    
    return

def DEX():
    global XR, FLAGS, AMOD, INS, OP1, OP2
    INS = 'DEX'
    AMOD = 'impl'
    OP1 = '--'
    OP2 = '--'
    x = int(XR, 16)
    x = x - 1
    checkNeg(x)
    checkZero(x)
    XR = str(hex(x)[2:].upper())
    return

def DEY():
    global YR, FLAGS, AMOD, INS, OP1, OP2
    OP1 = '--'
    OP2 = '--'
    INS = 'DEY'
    AMOD = 'impl'
    y = int(YR, 16)
    y = y - 1
    checkNeg(y)
    checkZero(y)
    YR = str(hex(y)[2:].upper())
    return

def INX():
    global XR, FLAGS, AMOD, INS, OP1, OP2
    INS = 'INX'
    AMOD = 'impl'
    OP1 = '--'
    OP2 = '--'
    x = int(XR, 16)
    x = x + 1
    checkNeg(x)
    checkZero(x)
    XR = str(hex(x)[2:].upper())
    
    return
    

def INY():
    global YR, FLAGS, AMOD, INS, OP1, OP2
    INS = 'INY'
    AMOD = 'impl'
    OP1 = '--'
    OP2 = '--'
    y = int(YR, 16)
    y = y + 1
    checkNeg(y)
    checkZero(y)
    YR = str(hex(y)[2:].upper())
    return

def LSR(data, mode):
    global AC, AMOD, INS, FLAGS, OP1, OP2, PC, FLAGS
    INS = 'LSR'
    OP1 = data[PC + 1]
    OP2 = '--'

    if(mode == 'acc'):
        OP1 = '--'
        AMOD = '   A'
        int_ac = int(AC, 16)
        FLAGS[7] = str(int_ac)[0]
        int_ac = int_ac >> 1
        checkZero(int_ac)
        checkCarry(int_ac)
        AC = str(hex(int_ac)[2:].upper())

    if(mode == 'zpg'):
        AMOD = ' zpg'
        int_ac = int(data[int(OP1, 16)], 16)
        FLAGS[7] = str(int_ac)[0]
        int_ac = int_ac >> 1
        checkZero(int_ac)
        checkCarry(int_ac)
        data[int(OP1, 16)] = str(hex(int_ac)[2:].upper())

    if (mode == 'abs'):
        AMOD = ' abs'
        OP2 = data[PC + 2]
        int_ac = int(data[int(OP2 + OP1, 16)], 16)
        FLAGS[7] = str(int_ac)[0]
        int_ac = int_ac >> 1
        checkZero(int_ac)
        checkCarry(int_ac)
        data[int(OP2 + OP1, 16)] = str(hex(int_ac)[2:].upper())

    return

def NOP():
    global YR, FLAGS, AMOD, INS, OP1, OP2
    INS = 'NOP'
    AMOD = 'impl'
    OP1 = '--'
    OP2 = '--'
    return

def PHA():
    global AC, SP, STACK, AMOD, INS, OP1, OP2
    INS = 'PHA'
    AMOD = 'impl'
    OP1 = '--'
    OP2 = '--'
    _SP = int(SP, 16)
    STACK[_SP] = AC
    SP = str(hex(_SP - 1)[2:].upper())
    return

def PHP():
    global SP, STACK, AMOD, INS, FLAGS, OP1, OP2
    INS = 'PHP'
    AMOD = 'impl'
    OP1 = '--'
    OP2 = '--'
    SR = str(hex(int(FLAGS, 2))[2:].upper())
    _SP = int(SP, 16)
    STACK[_SP] = SR
    SP = str(hex(_SP - 1)[2:].upper())
    return

def PLA():
    global SP, STACK, INS, AMOD, FLAGS, AC, OP1, OP2
    INS = 'PLA'
    AMOD = 'impl'
    OP1 = '--'
    OP2 = '--'
    _SP = int(SP, 16)
    _SP = _SP + 1
    AC = str(STACK[_SP])
    SP = str(hex(_SP)[2:].upper())

    acc = int(AC, 16)

    checkNeg(acc)
    checkZero(acc)
    
    return

def PLP():
    global SP, STACK, AMOD, INS, FLAGS, OP1, OP2
    INS = 'PLP'
    AMOD = 'impl'
    OP1 = '--'
    OP2 = '--'
    int_flag = int(FLAGS, 16)
    FLAGS = str(bin(int_flag)[2:])
    return

def ROL(data, mode):
    global SP, STACK, PC, AMOD, INS, FLAGS, AC, OP1, OP2
    INS = 'ROL'
    OP1 = data[PC + 1]
    OP2 = '--'
    if(mode == 'acc'):
        OP1 = '--'
        AMOD = '   A'
        int_ac = int(AC, 16)

    if(mode == 'zpg'):
        AMOD = ' zpg'
        int_ac = int(data[int(OP1, 16)], 16)

    if (mode == 'abs'):
        AMOD = ' abs'
        OP2 = data[PC + 2]
        int_ac = int(data[int(OP2 + OP1, 16)], 16)

    INT_BITS = 8
    int_ac = (int_ac << 1) | (int_ac >> (INT_BITS - 1))  # shifted

    checkNeg(int_ac)
    checkZero(int_ac)
    checkCarry(int_ac)

    if (mode == 'acc'):
        AC = str(hex(int_ac)[2:].upper())
    if (mode == 'zpg'):
        data[int(OP1), 16] = str(hex(int_ac)[2:].upper())
    if(mode == 'abs'):
        data[int(OP2 + OP1, 16)] = str(hex(int_ac)[2:].upper())
    return

def ROR(data, mode):
    global SP, STACK, AMOD, INS, FLAGS, AC, OP1, OP2, PC
    INS = 'ROR'
    OP1 = data[PC + 1]
    OP2 = '--'
    if(mode == 'acc'):
        OP1 = '--'
        AMOD = '   A'
        int_ac = int(AC, 16)

    if(mode == 'zpg'):
        AMOD = ' zpg'
        int_ac = int(data[int(OP1, 16)], 16)

    if (mode == 'abs'):
        AMOD = ' abs'
        OP2 = data[PC + 2]
        int_ac = int(data[int(OP2 + OP1, 16)], 16)

    INT_BITS = 8
    int_ac = (int_ac >> 1) | (int_ac << (INT_BITS-1)) & 0xFFFFFFFF

    checkZero(int_ac)
    checkNeg(int_ac)
    int_ac = checkCarry(int_ac)

    if (mode == 'acc'):
        AC = str(hex(int_ac)[2:].upper())
    if(mode == 'zpg'):
        data[int(OP1), 16] = str(hex(int_ac)[2:].upper())
    if (mode == 'abs'):
        data[int(OP2 + OP1, 16)] = str(hex(int_ac)[2:].upper())

    return

def SEC():
    global AMOD, INS, FLAGS, OP1, OP2
    INS = 'SEC'
    AMOD = 'impl'
    FLAGS[7] = '1'
    OP1 = '--'
    OP2 = '--'
    return

def SED():
    global AMOD, INS, FLAGS, OP1, OP2
    INS = 'SED'
    AMOD = 'impl'
    FLAGS[4] = '1'
    OP1 = '--'
    OP2 = '--'
    return

def SEI():
    global AMOD, INS, FLAGS, OP1, OP2
    INS = 'SEI'
    AMOD = 'impl'
    FLAGS[5] = '1'
    OP1 = '--'
    OP2 = '--'
    return

def TAX():
    global AC, XR, AMOD, INS, FLAGS, OP1, OP2
    INS = 'TAX'
    AMOD = 'impl'
    OP1 = '--'
    OP2 = '--'
    XR = AC
    checkNeg(int(XR, 16))
    checkZero(int(XR, 16))
    return

def TAY():
    global AC, YR, AMOD, INS, FLAGS, OP1, OP2
    INS = 'TAY'
    AMOD = 'impl'
    OP1 = '--'
    OP2 = '--'
    YR = AC
    checkNeg(int(YR, 16))
    checkZero(int(YR, 16))
    return

def TSX():
    global SP, XR, AMOD, INS, FLAGS, OP1, OP2
    INS = 'TSX'
    AMOD = 'impl'
    OP1 = '--'
    OP2 = '--'
    XR = SP
    checkNeg(int(XR, 16))
    checkZero(int(XR, 16))
    return

def TXA():
    global AC, XR, AMOD, INS, FLAGS, OP1, OP2
    INS = 'TXA'
    AMOD = 'impl'
    OP1 = '--'
    OP2 = '--'
    AC = XR
    checkNeg(int(AC, 16))
    checkZero(int(AC, 16))
    return

def TXS():
    global SP, XR, AMOD, INS, FLAGS, OP1, OP2
    INS = 'TXS'
    AMOD = 'impl'
    OP1 = '--'
    OP2 = '--'
    SP = XR
    return

def TYA():
    global AC, YR, AMOD, INS, FLAGS, OP1, OP2
    INS = 'TYA'
    AMOD = 'impl'
    OP1 = '--'
    OP2 = '--'
    AC = YR
    int_AC = int(str(AC), 16)
    checkNeg(int(AC, 16))
    checkZero(int(AC, 16))
    return

def AND(data, mode):
    global AC, PC, OP1, OP2, AMOD, INS
    INS = 'AND'
    ac = int(AC, 16)
    OP1 = data[PC + 1]
    OP2 = '--'

    if(mode == 'imm'):
        AMOD = '   #'
        mem = int(OP1, 16)

    if(mode == 'zpg'):
        AMOD = ' zpg'
        mem = int(data[int(OP1, 16)], 16)

    if(mode == 'abs'):
        OP2 = data[PC + 2]
        AMOD = ' abs'
        mem = int(data[int(OP2 + OP1), 16], 16)

    result = ac & mem
    checkNeg(result)
    checkZero(result)
    AC = str(hex(result)[2:].upper())
    return

def ADC(data, mode):
    global AC, PC, OP1, OP2, AMOD, INS, FLAGS
    INS = 'ADC'
    OP1 = data[PC + 1]
    OP2 = '--'
    int_ac = int(AC, 16)

    if(mode == 'imm'):
        AMOD = '   #'
        int_mem = int(data[PC + 1], 16)

    if(mode == 'zpg'):
        AMOD = ' zpg'
        int_mem = int(data[int(OP1, 16)], 16)

    if(mode == 'abs'):
        OP2 = data[PC + 2]
        AMOD = ' abs'
        int_mem = int(data[int(OP2 + OP1, 16)], 16)

    result = int_ac + int_mem + int(FLAGS[7], 10)

    checkOverflow(int_ac, int_mem, result)
    result = checkCarry(result)
    checkNeg(result)
    checkZero(result)
    AC = str(hex(result)[2:].upper())
    return


def STA(data, mode):
    global AC, PC, OP1, OP2, AMOD, INS
    INS = 'STA'
    OP1 = data[PC + 1]
    OP2 = '--'
    if(mode == 'zpg'):
        AMOD = ' zpg'
        data[int(OP1, 16)] = AC

    if (mode == 'abs'):
        AMOD = ' abs'
        OP2 = data[PC + 2]
        data[int(OP2 + OP1, 16)] = AC
    return

def EOR(data, mode):
    global AC, PC, OP1, OP2, AMOD, INS
    INS = 'EOR'
    OP1 = data[PC + 1]
    OP2 = '--'
    if(mode == 'imm'):
        AMOD = '   #'
        result = int(AC, 16) ^ int(OP1, 16)

    if(mode == 'zpg'):
        AMOD = ' zpg'
        result = int(AC, 16) ^ int(data[int(OP1, 16)], 16)

    if (mode == 'abs'):
        AMOD = ' abs'
        OP2 = data[PC + 2]
        result = int(AC, 16) ^ int(data[int(OP2 + OP1, 16)], 16)

    checkNeg(result)
    checkZero(result)
    AC = str(hex(result)[2:].upper())
    return

def CMP(data, mode):
    global AC, PC, OP1, OP2, AMOD, INS
    INS = 'CMP'
    OP1 = data[PC + 1]
    OP2 = '--'
    int_ac = int(AC, 16)
    if(mode == 'imm'):
        AMOD = '   #'
        mem = int(OP1, 16)

    if(mode == 'zpg'):
        AMOD = ' zpg'
        mem = int(data[int(OP1, 16)], 16)

    if (mode == 'abs'):
        AMOD = ' abs'
        OP2 = data[PC + 2]
        mem = int(data[int(OP2 + OP1, 16)], 16)

    result = int_ac + (0b11111111 - mem)
    result = checkCarry(result)
    result = result + 1

    result = checkCarry(result)
    checkNeg(result)
    checkZero(result)

    return

def CPX(data, mode):
    global AC, PC, OP1, OP2, AMOD, INS, XR
    INS = 'CPX'
    OP1 = data[PC + 1]
    OP2 = '--'
    int_x = int(XR, 16)
    if(mode == 'imm'):
        AMOD = '   #'
        mem = int(OP1, 16)

    if(mode == 'zpg'):
        AMOD = ' zpg'
        mem = int(data[int(OP1, 16)], 16)

    if (mode == 'abs'):
        AMOD = ' abs'
        OP2 = data[PC + 2]
        mem = int(data[int(OP2 + OP1, 16)], 16)

    result = int_x - mem
    checkNeg(result)
    checkZero(result)
    checkCarry(result)
    return

def CPY(data, mode):
    global AC, PC, OP1, OP2, AMOD, INS, YR
    INS = 'CPX'
    OP1 = data[PC + 1]
    OP2 = '--'
    int_y = int(YR, 16)
    if(mode == 'imm'):
        AMOD = '   #'
        mem = int(OP1, 16)

    if(mode == 'zpg'):
        AMOD = ' zpg'
        mem = int(data[int(OP1, 16)], 16)

    if (mode == 'abs'):
        AMOD = ' abs'
        OP2 = data[PC + 2]
        mem = int(data[int(OP2 + OP1, 16)], 16)

    result = int_y - mem
    checkNeg(result)
    checkZero(result)
    checkCarry(result)
    return

def LDA(data, mode):
    global AC, PC, OP1, OP2, AMOD, INS
    INS = 'LDA'
    OP1 = data[PC + 1]
    OP2 = '--'
    if(mode == 'imm'):
        AMOD = '   #'
        result = OP1

    if(mode == 'zpg'):
        AMOD = ' zpg'
        result = data[int(OP1, 16)]

    if (mode == 'abs'):
        AMOD = ' abs'
        OP2 = data[PC + 2]
        result = data[int(OP2 + OP1, 16)]

    result = int(result, 16)
    checkNeg(result)
    checkZero(result)
    AC = str(hex(result)[2:].upper())

def LDX(data, mode):
    global XR, PC, OP1, OP2, AMOD, INS
    INS = 'LDX'
    OP1 = data[PC + 1]
    OP2 = '--'
    if(mode == 'imm'):
        AMOD = '   #'
        result = OP1

    if(mode == 'zpg'):
        AMOD = ' zpg'
        result = data[int(OP1, 16)]

    if (mode == 'abs'):
        AMOD = ' abs'
        OP2 = data[PC + 2]
        result = data[int(OP2 + OP1, 16)]

    result = int(result, 16)
    checkNeg(result)
    checkZero(result)
    XR = str(hex(result)[2:].upper())
    return

def LDY(data, mode):
    global YR, PC, OP1, OP2, AMOD, INS
    INS = 'LDY'
    OP1 = data[PC + 1]
    OP2 = '--'
    if(mode == 'imm'):
        AMOD = '   #'
        result = OP1

    if(mode == 'zpg'):
        AMOD = ' zpg'
        result = data[int(OP1, 16)]

    if (mode == 'abs'):
        AMOD = ' abs'
        result = data[int(OP2 + OP1, 16)]

    result = int(result, 16)
    checkNeg(result)
    checkZero(result)
    YR = str(hex(result)[2:].upper())
    return

def ORA(data, mode):
    global AC, PC, OP1, OP2, AMOD, INS
    INS = 'ORA'
    OP1 = data[PC + 1]
    OP2 = '--'
    if(mode == 'imm'):
        AMOD = '   #'
        mem = int(OP1, 16)

    if(mode == 'zpg'):
        AMOD = ' zpg'
        mem = int(data[int(OP1, 16)], 16)

    if (mode == 'abs'):
        AMOD = ' abs'
        OP2 = data[PC + 2]
        mem = int(data[int(OP2 + OP1, 16)], 16)

    int_ac = int(AC, 16)
    result = int_ac | mem
    checkNeg(result)
    checkZero(result)
    AC = str(hex(result)[2:].upper())
    return

def SBC(data, mode):
    global AC, PC, OP1, OP2, AMOD, INS, FLAGS
    INS = 'SBC'
    OP1 = data[PC + 1]
    OP2 = '--'
    int_ac = int(AC, 16)
    if (mode == 'imm'):
        AMOD = '   #'
        mem = int(OP1, 16)

    if (mode == 'zpg'):
        AMOD = ' zpg'
        mem = int(data[int(OP1, 16)], 16)

    if (mode == 'abs'):
        AMOD = ' abs'
        OP2 = data[PC + 2]
        mem = int(data[int(OP2 + OP1, 16)], 16)

    result = int_ac - mem - (1 - int(FLAGS[7], 10))
    checkNeg(result)
    checkZero(result)
    checkCarry(result)
    checkOverflow(result)
    AC = str(hex(result)[2:].upper())
    return

def STX(data, mode):
    global AC, PC, OP1, OP2, AMOD, INS, XR
    INS = 'STX'
    OP1 = data[PC + 1]
    OP2 = '--'

    if (mode == 'zpg'):
        AMOD = ' zpg'
        data[int(OP1, 16)] = XR

    if (mode == 'abs'):
        AMOD = ' abs'
        OP2 = data[PC + 2]
        data[int(OP2 + OP1, 16)] = XR

    return


def STY(data, mode):
    global AC, PC, OP1, OP2, AMOD, INS, YR
    INS = 'STY'
    OP1 = data[PC + 1]
    OP2 = '--'

    if (mode == 'zpg'):
        AMOD = ' zpg'
        data[int(OP1, 16)] = YR

    if (mode == 'abs'):
        AMOD = ' abs'
        data[int(OP2 + OP1, 16)] = YR
    return



def DEC(data, mode):
    global AC, PC, OP1, OP2, AMOD, INS
    INS = 'DEC'
    OP1 = data[PC + 1]
    OP2 = '--'

    if (mode == 'zpg'):
        AMOD = ' zpg'
        result = int(data[int(OP1, 16)], 16) - 1
        checkNeg(result)
        checkZero(result)
        data[int(OP1, 16)] = str(hex(result)[2:].upper())

    if (mode == 'abs'):
        AMOD = ' abs'
        OP2 = data[PC + 2]
        result = int(data[int(OP2 + OP1, 16)], 16) - 1
        checkNeg(result)
        checkZero(result)
        data[int(OP2 + OP1, 16)] = str(hex(result)[2:].upper())

    return

def INC(data, mode):
    global AC, PC, OP1, OP2, AMOD, INS
    INS = 'INC'
    OP1 = data[PC + 1]
    OP2 = '--'

    if (mode == 'zpg'):
        AMOD = ' zpg'
        result = int(data[int(OP1, 16)], 16) + 1
        checkNeg(result)
        checkZero(result)
        data[int(OP1, 16)] = str(hex(result)[2:].upper())

    if (mode == 'abs'):
        AMOD = ' abs'
        OP2 = data[PC + 2]
        result = int(data[int(OP2 + OP1, 16)], 16) + 1
        checkNeg(result)
        checkZero(result)
        data[int(OP2 + OP1, 16)] = str(hex(result)[2:].upper())

    return

def checkNeg(result):
    global FLAGS
    if(result > 127):
        FLAGS[0] = '1'
    else:
        FLAGS[0] = '0'
    return

def checkZero(result):
    global FLAGS
    if(result == 0):
        FLAGS[6] = '1'
    else:
        FLAGS[6] = '0'
    return

def checkCarry(result):
    global FLAGS
    if (result > 255):
        result %= 256
        FLAGS[7] = '1'
    return result

def checkOverflow(op1, op2, result):
    global FLAGS
    result = result % 256
    if(op1 < 127 and op2 < 127 and result > 127):
        FLAGS[1] = '1'
    if(op1 > 127 and op2 > 127 and result < 127):
        FLAGS[1] = '1'
    return


def BCC(data):
    global AC, OP1, OP2, AMOD, INS, FLAGS
    INS = 'BCC'
    OP1 = data[PC + 1]
    OP2 = '--'
    AMOD = ' rel'
    int_op1 = int(OP1, 16)
    if(FLAGS[7] == '0'):
        addPC(int_op1)
    return


def addPC(num):
    global PC
    if(num > 127):
        num = -1 * (128 - (num - 128))
    PC = PC + num

def BCS(data):
    global AC, OP1, OP2, AMOD, INS, FLAGS
    INS = 'BCS'
    OP1 = data[PC + 1]
    OP2 = '--'
    AMOD = ' rel'
    int_op1 = int(OP1, 16)
    if (FLAGS[7] == '1'):
        addPC(int_op1)
    return


def BEQ(data):
    global AC, OP1, OP2, AMOD, INS, FLAGS
    INS = 'BEQ'
    OP1 = data[PC + 1]
    OP2 = '--'
    AMOD = ' rel'
    int_op1 = int(OP1, 16)
    if (FLAGS[6] == '1'):
        addPC(int_op1)
    return

def BMI(data):
    global AC, OP1, OP2, AMOD, INS, FLAGS
    INS = 'BMI'
    OP1 = data[PC + 1]
    OP2 = '--'
    AMOD = ' rel'
    int_op1 = int(OP1, 16)
    if (FLAGS[0] == '1'):
        addPC(int_op1)
    return

def BNE(data):
    global AC, OP1, OP2, AMOD, INS, FLAGS
    INS = 'BNE'
    OP1 = data[PC + 1]
    OP2 = '--'
    AMOD = ' rel'
    int_op1 = int(OP1, 16)
    if (FLAGS[6] == '0'):
        addPC(int_op1)
    return

def BPL(data):
    global AC, OP1, OP2, AMOD, INS, FLAGS
    INS = 'BPL'
    OP1 = data[PC + 1]
    OP2 = '--'
    AMOD = ' rel'
    int_op1 = int(OP1, 16)
    if (FLAGS[0] == '0'):
        addPC(int_op1)
    return

def BVC(data):
    global AC, OP1, OP2, AMOD, INS, FLAGS
    INS = 'BVC'
    OP1 = data[PC + 1]
    OP2 = '--'
    AMOD = ' rel'
    int_op1 = int(OP1, 16)
    if (FLAGS[1] == '0'):
        addPC(int_op1)
    return

def BVS(data):
    global AC, OP1, OP2, AMOD, INS, FLAGS
    INS = 'BVS'
    OP1 = data[PC + 1]
    OP2 = '--'
    AMOD = ' rel'
    int_op1 = int(OP1, 16)
    if (FLAGS[1] == '1'):
        addPC(int_op1)
    return

def JMP(data, mode):
    global AC, OP1, OP2, AMOD, INS, FLAGS, PC
    INS = 'JMP'
    OP1 = data[PC + 1]
    OP2 = data[PC + 2]
    if(mode == 'ind'):
        AMOD = ' ind'
        hex_op = OP2 + OP1
        int_op = int(hex_op, 16)
        result = data[int_op + 1] + data[int_op]
        PC = int(result, 16)

    if(mode == 'abs'):
        AMOD = ' abs'
        PC = int(OP2 + OP1, 16)



    return

def JSR(data):
    global AC, OP1, OP2, AMOD, INS, FLAGS, PC, STACK, SP
    INS = 'JSR'
    OP1 = data[PC + 1]
    OP2 = data[PC + 2]

    AMOD = ' abs'

    STACK[int(SP, 16)] = str(hex(PC + 2)[2:].upper()).zfill(4)[2:4]
    STACK[int(SP, 16) - 1] = str(hex(PC + 2)[2:].upper()).zfill(4)[0:2]

    int_sp = int(SP, 16)
    int_sp = int_sp - 2
    SP = str(hex(int_sp)[2:].upper())

    PC = int(OP2 + OP1, 16)

    return

def RTS(data):
    global AC, OP1, OP2, AMOD, INS, FLAGS, PC, STACK, SP
    INS = 'RTS'
    OP1 = '--'
    OP2 = '--'
    AMOD = 'impl'

    int_sp = int(SP, 16)
    int_sp = int_sp + 2
    SP = str(hex(int_sp)[2:].upper())

    PC = int(STACK[int(SP, 16) - 1] + STACK[int(SP, 16)], 16)


def computeInfo(data):
    global PC
    opc = data[PC]

    if(opc == '90'): BCC(data); PC = PC + 2
    if(opc == 'B0'): BCS(data); PC = PC + 2
    if(opc == 'F0'): BEQ(data); PC = PC + 2
    if(opc == '30'): BMI(data); PC = PC + 2
    if(opc == 'D0'): BNE(data); PC = PC + 2
    if(opc == '10'): BPL(data); PC = PC + 2
    if(opc == '50'): BVC(data); PC = PC + 2
    if(opc == '70'): BVS(data); PC = PC + 2
    if(opc == '4C'): JMP(data, 'abs')
    if(opc == '6C'): JMP(data, 'ind')
    if(opc == '20'): JSR(data);
    if(opc == '60'): RTS(data); PC = PC + 1

    if(opc == '0A'): ASL(data, 'acc'); PC = PC + 1
    if(opc == '06'): ASL(data, 'zpg'); PC = PC + 2
    if(opc == '0E'): ASL(data, 'abs'); PC = PC + 3
    if(opc == '00'): BRK();
    if(opc == '18'): CLC(); PC = PC + 1
    if(opc == 'D8'): CLD(); PC = PC + 1
    if(opc == '58'): CLI(); PC = PC + 1
    if(opc == 'B8'): CLV(); PC = PC + 1
    if(opc == 'CA'): DEX(); PC = PC + 1
    if(opc == '88'): DEY(); PC = PC + 1
    if(opc == 'E8'): INX(); PC = PC + 1
    if(opc == 'C8'): INY(); PC = PC + 1
    if(opc == '4A'): LSR(data, 'acc'); PC = PC + 1
    if(opc == '46'): LSR(data, 'zpg'); PC = PC + 2
    if(opc == '4E'): LSR(data, 'abs'); PC = PC + 3
    if(opc == 'EA'): NOP(); PC = PC + 1
    if(opc == '48'): PHA(); PC = PC + 1
    if(opc == '08'): PHP(); PC = PC + 1
    if(opc == '68'): PLA(); PC = PC + 1
    if(opc == '28'): PLP(); PC = PC + 1
    if(opc == '2A'): ROL(data, 'acc'); PC = PC + 1
    if(opc == '26'): ROL(data, 'zpg'); PC = PC + 2
    if(opc == '2E'): ROL(data, 'abs'); PC = PC + 3
    if(opc == '6A'): ROR(data, 'acc'); PC = PC + 1
    if(opc == '66'): ROR(data, 'zpg'); PC = PC + 2
    if(opc == '6E'): ROR(data, 'abs'); PC = PC + 3
    if(opc == '38'): SEC(); PC = PC + 1
    if(opc == 'F8'): SED(); PC = PC + 1
    if(opc == '78'): SEI(); PC = PC + 1
    if(opc == 'AA'): TAX(); PC = PC + 1
    if(opc == 'A8'): TAY(); PC = PC + 1
    if(opc == 'BA'): TSX(); PC = PC + 1
    if(opc == '8A'): TXA(); PC = PC + 1
    if(opc == '9A'): TXS(); PC = PC + 1
    if(opc == '98'): TYA(); PC = PC + 1

    if(opc == '29'): AND(data, 'imm'); PC = PC + 2
    if(opc == '25'): AND(data, 'zpg'); PC = PC + 2
    if(opc == '2D'): AND(data, 'abs'); PC = PC + 3
    if(opc == '69'): ADC(data, 'imm'); PC = PC + 2
    if(opc == '65'): ADC(data, 'zpg'); PC = PC + 2
    if(opc == '6D'): ADC(data, 'abs'); PC = PC + 3
    if(opc == '24'): BIT(data, 'zpg'); PC = PC + 2
    if(opc == '2C'): BIT(data, 'abs'); PC = PC + 3
    if(opc == 'C9'): CMP(data, 'imm'); PC = PC + 2
    if(opc == 'C5'): CMP(data, 'zpg'); PC = PC + 2
    if(opc == 'CD'): CMP(data, 'abs'); PC = PC + 3
    if(opc == 'E0'): CPX(data, 'imm'); PC = PC + 2
    if(opc == 'E4'): CPX(data, 'zpg'); PC = PC + 2
    if(opc == 'EC'): CPX(data, 'abs'); PC = PC + 3
    if(opc == 'C0'): CPY(data, 'imm'); PC = PC + 2
    if(opc == 'C4'): CPY(data, 'zpg'); PC = PC + 2
    if(opc == 'CC'): CPY(data, 'abs'); PC = PC + 3
    if(opc == 'C6'): DEC(data, 'zpg'); PC = PC + 2
    if(opc == 'CE'): DEC(data, 'abs'); PC = PC + 3
    if(opc == 'E6'): INC(data, 'zpg'); PC = PC + 2
    if(opc == 'EE'): INC(data, 'abs'); PC = PC + 3
    if(opc == 'A9'): LDA(data, 'imm'); PC = PC + 2
    if(opc == 'A5'): LDA(data, 'zpg'); PC = PC + 2
    if(opc == 'AD'): LDA(data, 'abs'); PC = PC + 3
    if(opc == 'A2'): LDX(data, 'imm'); PC = PC + 2
    if(opc == 'A6'): LDX(data, 'zpg'); PC = PC + 2
    if(opc == 'AE'): LDX(data, 'abs'); PC = PC + 3
    if(opc == 'A0'): LDY(data, 'imm'); PC = PC + 2
    if(opc == 'A4'): LDY(data, 'zpg'); PC = PC + 2
    if(opc == 'AC'): LDY(data, 'abs'); PC = PC + 3
    if(opc == '85'): STA(data, 'zpg'); PC = PC + 2
    if(opc == '8D'): STA(data, 'abs'); PC = PC + 3
    if(opc == '49'): EOR(data, 'imm'); PC = PC + 2
    if(opc == '45'): EOR(data, 'zpg'); PC = PC + 2
    if(opc == '4D'): EOR(data, 'abs'); PC = PC + 3
    if(opc == '09'): ORA(data, 'imm'); PC = PC + 2
    if(opc == '05'): ORA(data, 'zpg'); PC = PC + 2
    if(opc == '0D'): ORA(data, 'abs'); PC = PC + 3
    if(opc == 'E9'): SBC(data, 'imm'); PC = PC + 2
    if(opc == 'E5'): SBC(data, 'zpg'); PC = PC + 2
    if(opc == 'ED'): SBC(data, 'abs'); PC = PC + 3
    if(opc == '86'): STX(data, 'zpg'); PC = PC + 2
    if(opc == '8E'): STX(data, 'abs'); PC = PC + 3
    if(opc == '84'): STY(data, 'zpg'); PC = PC + 2
    if(opc == '8C'): STY(data, 'abs'); PC = PC + 3

    return




if __name__ == "__main__":
    main()
