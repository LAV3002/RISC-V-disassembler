import sys

def get_submaski(mask, left, right):
    size = len(mask) - 1
    returned = ""
    for i in range(size - left, size - right + 1):
        returned += mask[i]
    return int(returned, 2)


def get_submask(mask, left, right):
    size = len(mask) - 1
    returned = ""
    for i in range(size - left, size - right + 1):
        returned += mask[i]
    return returned


def get_bytes_value(start, size):
    b = bytes()
    for i in range(start, start + size):
        b += data[i]
    return int.from_bytes(b, byteorder="little")

def get_bytes_value_big(start, size):
    b = bytes()
    for i in range(start, start + size):
        b += data[i]
    return int.from_bytes(b, byteorder="big")

def get_addr(e_shoff, e_shentsize, type):
    i = 0
    while get_bytes_value(e_shoff + e_shentsize * i + 4, 4) != type:
        i += 1
    return get_bytes_value(e_shoff + e_shentsize * i + 12, 4)


def get_offset(e_shoff, e_shentsize, type):
    i = 0
    while get_bytes_value(e_shoff + e_shentsize * i + 4, 4) != type:
        i += 1
    return get_bytes_value(e_shoff + e_shentsize * i + 16, 4)


def get_size(e_shoff, e_shentsize, type):
    i = 0
    while get_bytes_value(e_shoff + e_shentsize * i + 4, 4) != type:
        i += 1
    return get_bytes_value(e_shoff + e_shentsize * i + 20, 4)


def get_entsize(e_shoff, e_shentsize, type):
    i = 0
    while get_bytes_value(e_shoff + e_shentsize * i + 4, 4) != type:
        i += 1
    return get_bytes_value(e_shoff + e_shentsize * i + 36, 4)

def get_string(offset, index):
    s = ""
    i = index
    ch = chr(int.from_bytes(data[offset + i], byteorder="little"))
    while ch != '\0':
        s += ch
        i += 1
        ch = chr(int.from_bytes(data[offset + i], byteorder="little"))
    return s


def get_register(number):
    if number == 0:
        return "zero"
    if number == 1:
        return "ra"
    if number == 2:
        return "sp"
    if number == 3:
        return "gp"
    if number == 4:
        return "tp"
    if number <= 7:
        return "t" + str(number - 5)
    if number <= 9:
        return "s" + str(number - 8)
    if number <= 11:
        return "a" + str(number - 10)
    if number <= 17:
        return "a" + str(number - 10)
    if number <= 27:
        return "s" + str(number - 16)
    if number <= 31:
        return "t" + str(number - 25)

def decode_long(command, addr):
    i = str(bin(int.from_bytes(command, byteorder="little")))[2:]
    i = "0" * (32 - len(i)) + i
    opcode = i[-7:]
    flag = True
    if (opcode == "0110111"):
        imm = int(get_submask(i, 31, 12), 2)
        if imm >= 2 ** 19:
            imm -= 2 ** 20
        imm = str(imm)
        #imm = str(int(get_submask(i, 31, 12), 2))
        rd = get_register(get_submaski(i, 11, 7))
        flag = False
        return  "lui " + rd + ", " + imm

    if (opcode == "0010111"):
        imm = str(int(get_submask(i, 31, 12), 2))
        #imm = str(int(get_submask(i, 31, 12), 2))
        rd = get_register(get_submaski(i, 11, 7))
        flag = False
        return  "auipc " + rd + ", " + imm

    if (opcode == "1101111"):
        offset = int(
            get_submask(i, 31, 31)
            + get_submask(i, 19, 12) + get_submask(i, 20, 20)
            + get_submask(i, 30, 21)
            + "0",
            2)
        if offset >= 2 ** 20:
            offset -= 2 ** 21
        hex_addr = str(hex(addr + offset))[2:]
        mark = " LOC_" + hex_addr
        if mt.get(addr + offset) == None:
            mt[addr + offset] = "LOC_" + hex_addr
        else:
            mark = " " + mt[addr + offset]
        offset = str(offset)
        rd = get_register(get_submaski(i, 11, 7))
        flag = False
        return "jal " + rd + ", " + offset + mark

    if (opcode == "1100111"):
        offset = int(get_submask(i, 31, 20), 2)
        if offset >= 2 ** 11:
            offset -= 2 ** 12
        offset = str(offset)
        rd = get_register(get_submaski(i, 11, 7))
        rs1 = get_register(get_submaski(i, 19, 15))
        flag = False
        return "jalr " + rd + ", " + rs1 + ", " + offset

    if (opcode == "1100011"):
        rs1 = get_register(get_submaski(i, 19, 15))
        rs2 = get_register(get_submaski(i, 24, 20))
        offset = int(get_submask(i, 31, 31) + get_submask(i, 7, 7) + get_submask(i, 30, 25) + get_submask(i, 11, 8) + "0", 2)
        if offset >= 2 ** 12:
            offset -= 2 ** 13
        hex_addr = str(hex(addr + offset))[2:]
        mark = " LOC_" + hex_addr
        if mt.get(addr + offset) == None:
            mt[addr + offset] = "LOC_" + hex_addr
        else:
            mark = " " + mt[addr + offset]
        offset = str(offset)
        type = get_submask(i, 14, 12)
        d = {"000": "beq", "001": "bne", "010": "", "011": "", "100": "blt", "101": "bge", "110": "bltu", "111": "bgeu"}
        name = d[type]
        flag = False
        return name + " " + rs1 + ", " + rs2 + ", " + offset + mark

    if (opcode == "0000011"):
        rs1 = get_register(get_submaski(i, 19, 15))
        rd = get_register(get_submaski(i, 11, 7))
        imm = int(get_submask(i, 31, 20), 2)
        if imm >= 2 ** 11:
            imm -= 2 ** 12
        imm = str(imm)
        type = get_submask(i, 14, 12)
        d = {"000": "lb", "001": "lh", "010": "lw", "011": "", "100": "lbu", "101": "lhu", "110": "", "111": ""}
        name = d[type]
        flag = False
        return name + " " + rd + ", " + imm + "(" + rs1 + ")"

    if (opcode == "0100011"):
        rs1 = get_register(get_submaski(i, 19, 15))
        rs2 = get_register(get_submaski(i, 24, 20))
        imm = int(get_submask(i, 31, 25) + get_submask(i, 11, 7), 2)
        if imm >= 2 ** 11:
            imm -= 2 ** 12
        imm = str(imm)
        type = get_submask(i, 14, 12)
        d = {"000": "sb", "001": "sh", "010": "sw", "011": "", "100": "", "101": "", "110": "", "111": ""}
        name = d[type]
        flag = False
        return name + " " + rs2 + ", " + imm + "(" + rs1 + ")"

    if (opcode == "0010011"):
        type = get_submask(i, 14, 12)
        if not (type in ["001", "101"]):
            rs1 = get_register(get_submaski(i, 19, 15))
            rd = get_register(get_submaski(i, 11, 7))
            imm = int(get_submask(i, 31, 20), 2)
            if imm >= 2 ** 11:
                imm -= 2 ** 12
            imm = str(imm)
            d = {"000": "addi", "001": "",
                 "010": "slti", "011": "sltiu",
                 "100": "xori", "101": "",
                 "110": "ori", "111": "andi"}
            name = d[type]
            flag = False
            return name + " " + rd + ", " + rs1 + ", " + imm
        else:
            name = ""
            begin = get_submask(i, 31, 30)
            shamt = get_submaski(i, 24, 20)
            if shamt >= 2 ** 4:
                shamt -= 2 ** 5
            shamt = str(shamt)
            rs1 = get_register(get_submaski(i, 19, 15))
            rd = get_register(get_submaski(i, 11, 7))
            if (type == "001"):
                name = "slli"
            else:
                if begin == "00":
                    name = "srli"
                else:
                    name = "srai"
            flag = False
            return name + " " + rd + ", " + rs1 + ", " + shamt
    if (opcode == "0110011"):
        begin = get_submask(i, 31, 25)
        d = {}
        if begin == "0000000":
            d = {"000": "add", "001": "sll", "010": "slt", "011": "sltu", "100": "xor", "101": "srl", "110": "or",
                 "111": "and"}
        if begin == "0100000":
            d = {"000": "sub", "001": "", "010": "", "011": "", "100": "", "101": "sra", "110": "", "111": ""}
        if begin == "0000001":
            d = {"000": "mul", "001": "mulh", "010": "mulhsu", "011": "mulhu", "100": "div", "101": "divu",
                 "110": "rem", "111": "remu"}
        rs1 = get_register(get_submaski(i, 19, 15))
        rs2 = get_register(get_submaski(i, 24, 20))
        rd = get_register(get_submaski(i, 11, 7))
        type = get_submask(i, 14, 12)
        name = d[type]
        flag = False
        return name + " " + rd + ", " + rs1 + ", " + rs2
    if (opcode == "0001111"):
        type = get_submask(i, 14, 12)
        if type == "000":
            pred = str(get_submaski(i, 27, 24))
            succ = str(get_submaski(i, 23, 20))
            name = "fence"
            flag = False
            return name + " " + pred + ", " + succ
        else:
            name = "fence.i"
            flag = False
            return name
    if (opcode == "1110011"):
        type = get_submask(i, 14, 12)
        begin = get_submaski(i, 31, 20)
        if type == "000":
            name = "ecall"
            if begin == "000000000001":
                name = "ebreak"
            flag = False
            return name
        else:
            d = {"000": "ecall", "001": "csrrw", "010": "csrrs", "011": "csrrc", "100": "", "101": "scrrwi",
                 "110": "csrrsi", "111": "csrrci"}
            csr = str(get_submaski(i, 31, 20))
            rd = get_register(get_submaski(i, 11, 7))
            name = d[type]
            if type in ["001", "010", "011"]:
                rs1 = get_register(get_submaski(i, 19, 15))
                flag = False
                return name + " " + rd + ", " + csr + ", " + rs1
            else:
                zimm = str(get_submaski(i, 19, 15))
                flag = False
                return name + " " + rd + ", " + csr + ", " + zimm
    return "unknown_command"

def decode_short(command, addr):
    i = str(bin(int.from_bytes(command, byteorder="little")))[2:]
    i = "0" * (16 - len(i)) + i
    flag = True
    op = get_submask(i, 1, 0)
    type = get_submask(i, 15, 13)
    if type == "000" and op == "00":
        zimm = str(int(get_submask(i, 10, 7) + get_submask(i, 12, 11) + get_submask(i, 5, 5) + get_submask(i, 6, 6) + "00", 2))
        rd = get_register(get_submaski(i, 4, 2))
        flag = False
        return "c.addi4spn" + " " + rd + ", sp, " + zimm
    if type == "001" and op == "00":
        uimm = str(int(get_submask(i, 6, 5) + get_submask(i, 12, 10) + "000", 2))
        rs1 = get_register(get_submaski(i, 9, 7))
        rd = get_register(get_submaski(i, 4, 2))
        flag = False
        return "c.fld" + " " + rd + ", " + uimm + "(" + rs1 + ")"
    if type == "010" and op == "00":
        uimm = str(int(get_submask(i, 5, 5) + get_submask(i, 12, 10) + get_submask(i, 6, 6) + "00", 2))
        rs1 = get_register(get_submaski(i, 9, 7))
        rd = get_register(get_submaski(i, 4, 2))
        flag = False
        return "c.lw" + " " + rd + ", " + uimm + "(" + rs1 + ")"
    if type == "011" and op == "00":
        uimm = str(int(get_submask(i, 5, 5) + get_submask(i, 12, 10) + get_submask(i, 6, 6) + "00", 2))
        rs1 = get_register(get_submaski(i, 9, 7))
        rd = get_register(get_submaski(i, 4, 2))
        flag = False
        return "c.flw" + " " + rd + ", " + uimm + "(" + rs1 + ")"
    if type == "101" and op == "00":
        uimm = str(int(get_submask(i, 6, 5) + get_submask(i, 12, 10)+ "000", 2))
        rs1 = get_register(get_submaski(i, 9, 7))
        rd = get_register(get_submaski(i, 4, 2))
        flag = False
        return "c.fsd" + " " + rd + ", " + uimm + "(" + rs1 + ")"
    if type == "110" and op == "00":
        uimm = str(int(get_submask(i, 5, 5) + get_submask(i, 12, 10) + get_submask(i, 6, 6) + "00", 2))
        rs1 = get_register(get_submaski(i, 9, 7))
        rs2 = get_register(get_submaski(i, 4, 2))
        flag = False
        return "c.sw" + " " + rs2 + ", " + uimm + "(" + rs1 + ")"
    if type == "111" and op == "00":
        uimm = str(int(get_submask(i, 5, 5) + get_submask(i, 12, 10) + get_submask(i, 6, 6) + "00", 2))
        rs1 = get_register(get_submaski(i, 9, 7))
        rs2 = get_register(get_submaski(i, 4, 2))
        flag = False
        return "c.fsw" + " " + rs2 + ", " + uimm + "(" + rs1 + ")"
    if type == "000" and op == "01":
        cmd = get_submaski(i, 15, 0)
        flag = False
        if cmd == 1:
            return "c.nop"
        else:
            rd = get_register(get_submaski(i, 11, 7))
            imm = int(get_submask(i, 12, 12) + get_submask(i, 6, 2), 2)
            if imm >= 2 ** 5:
                imm -= 2 ** 6
            imm = str(imm)
            return "c.addi" + " " + rd + ", " + imm
    if type == "001" and op == "01":
        imm = (get_submask(i, 12, 12) +
        get_submask(i, 8, 8) +
        get_submask(i, 10, 9) +
        get_submask(i, 6, 6) +
        get_submask(i, 7, 7) +
        get_submask(i, 2, 2) +
        get_submask(i, 11, 11) +
        get_submask(i, 5, 3) +
        "0")
        offset = int(imm, 2)
        hex_addr = str(hex(addr + offset))[2:]
        mark = " LOC_" + hex_addr
        if mt.get(addr + offset) == None:
            mt[addr + offset] = "LOC_" + hex_addr
        else:
            mark = " " + mt[addr + offset]
        offset = str(offset)
        flag = False
        return "c.jal" + " " + offset + mark
    if type == "010" and op == "01":
        imm = (get_submask(i, 12, 12) +
        get_submask(i, 6, 2))
        imm = int(imm, 2)
        if imm >= 2 ** 5:
            imm -= 2 ** 6
        uimm = str(imm)
        rd = get_register(get_submaski(i, 11, 7))
        flag = False
        return "c.li" + " " + rd + ", " + uimm
    if type == "011" and op == "01":
        rd = get_register(get_submaski(i, 11, 7))
        if rd == 2:
            imm = (get_submask(i, 12, 12) +
                   get_submask(i, 4, 3) +
                   get_submask(i, 5, 5) +
                   get_submask(i, 2, 2) +
                   get_submask(i, 6, 6))
            imm = str(int(imm, 2))
            flag = False
            return "c.addi16sp" + " sp, " + imm
        else:
            imm = (get_submask(i, 12, 12) +
                   get_submask(i, 6, 2))
            uimm = str(int(imm, 2))
            flag = False
            return "c.lui" + " " + rd + ", "+ uimm
    if type == "100" and op == "01":
        rd = get_register(get_submaski(i, 9, 7))
        type2 = get_submask(i, 11, 10)
        name = ""
        if type2 != "11":
            if type2 == "00":
                name = "c.srli"
                if get_submask(i, 12, 12) == "1":
                    name = "s.srli64"
            if type2 == "01":
                name = "c.srai"
                if get_submask(i, 12, 12) == "1":
                    name = "s.srai64"
            if type2 == "10":
                name = "s.andi"
            imm = (get_submask(i, 12, 12) +
                   get_submask(i, 6, 2))
            imm = str(int(imm, 2))
            flag = False
            return name + " " + rd + ", " + imm
        else:
            type3 = get_submask(i, 6, 5)
            type4 = get_submask(i, 12, 12)
            rsd = get_register(get_submaski(i, 9, 7))
            rs2 = get_register(get_submaski(i, 4, 2))
            if (type4 == "0"):
                name = {"00" : "c.sub", "01" : "c.xor", "10":"c.or", "11":"c.and"}
            else:
                name = {"00": "c.sub2", "01": "c.addw"}
            name = name[type3]
            flag = False
            return name + " " + rsd + ", " + rs2
    if type == "101" and op == "01":
        imm = (get_submask(i, 12, 12) +
               get_submask(i, 8, 8) +
               get_submask(i, 10, 9) +
               get_submask(i, 6, 6) +
               get_submask(i, 7, 7) +
               get_submask(i, 2, 2) +
               get_submask(i, 11, 11) +
               get_submask(i, 5, 3) +
               "0")
        offset = int(imm, 2)
        if offset >= 2 ** 11:
            offset -= 2 ** 12
        hex_addr = str(hex(addr + offset))[2:]
        mark = " LOC_" + hex_addr
        if mt.get(addr + offset) == None:
            mt[addr + offset] = "LOC_" + hex_addr
        else:
            mark = " " + mt[addr + offset]
        offset = str(offset)
        flag = False
        return "c.j" + " " + offset + mark
    if type == "110" and op == "01":
        imm = (get_submask(i, 12, 12) +
               get_submask(i, 6, 5) +
               get_submask(i, 2, 2) +
               get_submask(i, 11, 10) +
               get_submask(i, 4, 3) +
               "0")
        offset = int(imm, 2)
        if offset >= 2 ** 8:
            offset -= 2 ** 9
        hex_addr = str(hex(addr + offset))[2:]
        mark = " LOC_" + hex_addr
        if mt.get(addr + offset) == None:
            mt[addr + offset] = "LOC_" + hex_addr
        else:
            mark = " " + mt[addr + offset]
        offset = str(offset)
        rs = get_register(get_submaski(i, 9, 7))
        flag = False
        return "c.beqz" + " " + rs + ", " + offset + mark
    if type == "111" and op == "01":
        imm = (get_submask(i, 12, 12) +
               get_submask(i, 6, 5) +
               get_submask(i, 2, 2) +
               get_submask(i, 11, 10) +
               get_submask(i, 4, 3) +
               "0")
        offset = int(imm, 2)
        if offset >= 2 ** 8:
            offset -= 2 ** 9
        hex_addr = str(hex(addr + offset))[2:]
        mark = " LOC_" + hex_addr
        if mt.get(addr + offset) == None:
            mt[addr + offset] = "LOC_" + hex_addr
        else:
            mark = " " + mt[addr + offset]
        offset = str(offset)
        rs = get_register(get_submaski(i, 9, 7))
        flag = False
        return "c.bnez" + " " + rs + ", " + offset + mark
    if type == "000" and op == "10":
        rd = get_register(get_submaski(i, 11, 7))
        imm = (get_submask(i, 12, 12) +
               get_submask(i, 6, 2))
        imm = str(int(imm, 2))
        flag = False
        return "c.slli" + " " + rd + ", " + imm
    if type == "001" and op == "10":
        rd = get_register(get_submaski(i, 11, 7))
        imm = (get_submask(i, 4, 2) +
               get_submask(i, 12, 12) +
               get_submask(i, 6, 5) +
                "000")
        imm = str(int(imm, 2))
        flag = False
        return "c.fldsp" + " " + rd + ", " + imm + "(sp)"
    if (type == "010" or type == "011") and op == "10":
        name = "c.lwsp"
        if type == "011":
            name = "c.flwsp"
        rd = get_register(get_submaski(i, 11, 7))
        imm = (get_submask(i, 3, 2) +
               get_submask(i, 12, 12) +
               get_submask(i, 6, 4) +
                "00")
        imm = str(int(imm, 2))
        flag = False
        return name + " " + rd + ", " + imm + "(sp)"
    if type == "100" and op == "10":
        type2 = get_submask(i, 12, 12)
        rsd = get_register(get_submaski(i, 11, 7))
        rs2 = get_register(get_submaski(i, 6, 2))
        if type2 == "0" and rsd != "zero" and rs2 == "zero":
            flag = False
            return "c.jr" + " " + rsd
        if type2 == "0" and rsd != "zero" and rs2 != "zero":
            flag = False
            return "c.mv" + " " + rsd + ", " + rs2
        if type2 == "1" and rsd == "zero" and rs2 == "zero":
            flag = False
            return "c.ebreak"
        if type2 == "1" and rsd != "zero" and rs2 == "zero":
            flag = False
            return "c.jalr" + " " + rsd
        if type2 == "1" and rsd != "zero" and rs2 != "zero":
            flag = False
            return "c.add" + " " + rsd + ", " + rs2
    if type == "101" and op == "10":
        rs2 = get_register(get_submaski(i, 4, 2))
        imm = (get_submask(i, 9, 7) +
               get_submask(i, 12, 10) +
               "000")
        imm = str(int(imm, 2))
        flag = False
        return "c.fsdsp" + " " + rs2 + ", " + imm + "(sp)"
    if type == "110" and op == "10":
        rs2 = get_register(get_submaski(i, 4, 2))
        imm = (get_submask(i, 8, 7) +
               get_submask(i, 12, 9) +
               "00")
        imm = str(int(imm, 2))
        flag = False
        return "c.swsp" + " " + rs2 + ", " + imm + "(sp)"
    if type == "111" and op == "10":
        rs2 = get_register(get_submaski(i, 4, 2))
        imm = (get_submask(i, 8, 7) +
               get_submask(i, 12, 9) +
               "00")
        imm = str(int(imm, 2))
        flag = False
        return "c.fswsp" + " " + rs2 + ", " + imm + "(sp)"
    return "unknown_command"


f = open(sys.argv[1], "rb")
data = []
mt = {}
i = f.read(1)
while i:
    data.append(i)
    i = f.read(1)
f.close()

if (len(data) < 4):
    print("Too short file!")
    exit(0)

ELF = get_bytes_value_big(0, 4)
if ELF != 2135247942:
    print("It's not ELF!")
    exit(0)

EI_CLASS = get_bytes_value(4, 1)
if EI_CLASS != 1:
    print("It's not 32-bit format!")
    exit(0)

EI_DATA = get_bytes_value(5, 1)
if EI_DATA != 1:
    print("It's not little!")
    exit(0)

e_machine = get_bytes_value(18, 2)
if e_machine != 243:
    print("It's not RISC-V!")
    exit(0)

e_shoff = get_bytes_value(32, 4)

e_shentsize = get_bytes_value(46, 2)

e_shnum = get_bytes_value(48, 2)

text_addr = get_addr(e_shoff, e_shentsize, 1)

text_offset = get_offset(e_shoff, e_shentsize, 1)

text_size = get_size(e_shoff, e_shentsize, 1)

symtab_offset = get_offset(e_shoff, e_shentsize, 2)

symtab_size = get_size(e_shoff, e_shentsize, 2)

symtab_entsize = get_entsize(e_shoff, e_shentsize, 2)

strtab_offset = get_offset(e_shoff, e_shentsize, 3)

strtab_size = get_size(e_shoff, e_shentsize, 3)

commands = []
i = text_offset
while i < text_offset + text_size:
    b = data[i] + data[i + 1]
    opcode = str(bin(int.from_bytes(b, byteorder="little")))[2:]
    if (opcode[-2:] == "11"):
        b += data[i + 2] + data[i + 3]
        i += 4
    else:
        i += 2
    commands.append(b)

symbol = []
for i in range(symtab_offset, symtab_offset + symtab_size, symtab_entsize):
    b = bytes()
    for j in range(i, i + symtab_entsize):
        b += data[j]
    symbol.append(b)

symtab = ["Symbol Value            Size Type     Bind     Vis       Index Name" + '\n']
pos = -1
binds = {0: "LOCAL", 1: "GLOBAL", 2: "WEAK", 13: "LOPROC", 15: "HIPROC"}
types = {0: "NOTYPE", 1: "OBJECT", 2: "FUNC", 3: "SECTION", 4: "FILE", 13: "LOPROC", 15: "HIPROC"}
indexs = {0: "UNDEF", 65280: "LORESERVE", 65311: "HIPROC", 65521: "ABS", 65522: "COMMON", 65535: "HIRESERVE"}
others = {0:"DEFAULT", 1:"INTERNAL", 2:"HIDDEN", 3:"PROTECTED", 4:"EXPORTED", 5:"SINGLETON", 6:"ELIMINATE"}
for i in symbol:
    pos += 1
    name = int.from_bytes(i[0:4], byteorder="little")
    name = get_string(strtab_offset, name)
    value = str(hex(int.from_bytes(i[4:8], byteorder="little")))
    size = int.from_bytes(i[8:12], byteorder="little")
    info = int.from_bytes(i[12:13], byteorder="little")
    bind = info >> 4
    type = info & 15
    other = int.from_bytes(i[13:14], byteorder="little")
    other = others[other]
    shndx = int.from_bytes(i[14:16], byteorder="little")
    index = indexs.get(shndx, str(shndx))
    s = ""
    s += "[" + " " * (4 - len(str(hex(pos))[2::]))
    s += str(hex(pos))[2::]
    s += "]" + " "
    s += value
    s += " " * (14 - len(value)) + " " * (7 - len(str(size)))
    s += str(size)
    s += " "
    s += types[type]
    s += " " * (9 - len(types[type]))
    s += binds[bind]
    s += " " * (9 - len(binds[bind]))
    s += other
    s += " " * (10 - len(other)) + " " * (5 - len(index))
    s += index
    s += " "
    s += name
    s += '\n'
    symtab.append(s)
    if types[type] == "FUNC":
        mt[int.from_bytes(i[4:8], byteorder="little")] = name

addr = text_addr
text = []
for i in commands:
    s = ""
    lst = addr
    if len(i) == 4:
        s += decode_long(i, addr)
        addr += 4
    else:
        s += decode_short(i, addr)
        addr += 2
    s += '\n'
    text.append([lst, s])

f = open(sys.argv[2], "w", encoding="utf-8")

f.write(".text\n")
for i in text:
    w = "000" + str(hex(i[0]))[2:]
    mrk = mt.get(i[0], "")
    if mrk != "":
        mrk += ": "
    w += " " * max(0, (13 - len(mrk))) + mrk
    f.write(w)
    f.write(i[1])
f.write('\n')

f.write(".symtab\n")
for i in symtab:
    f.write(i)
f.close()
