import math

BYTE_LEN = 8 # in bits

"""
convert dec to binary 
    postiive to direct codes
    negative to extra codes
"""
def idec2bin(number: int):
    absNum = abs(number)
    res = ""
    while absNum != 0:
        res += str(absNum % 2)
        absNum //= 2
    
    remainder = len(res) % BYTE_LEN
    extraZeroes = "0"*(BYTE_LEN - remainder) if (remainder != 0) or (len(res) == 0) else ""

    if (number >= 0):
        return extraZeroes + res[::-1]
    else:
        return direct2extra("1" + (extraZeroes + res[::-1])[1:])

def _floatPart(number: float):
    return number - math.trunc(number)

def _fdec2binWithDOT(number: float, precision: int = 5):
    absNum = abs(number)
    intPart, floatPart = math.trunc(absNum), _floatPart(absNum)
    res = idec2bin(intPart) + "."
    prec = 0

    while floatPart != 0.0 and prec < precision:
        floatPart *= 2
        res += str(math.trunc(floatPart))
        floatPart = _floatPart(floatPart)
        prec += 1
    
    return res
    
EXP = 127
FLOAT_MANTIS_LEN = 23

def fdec2bin(number: float, precision: int = 5):
    bNum = _fdec2binWithDOT(number, precision) #without sign
    sign = "1" if number < 0 else "0"
    exp = bNum.find(".") - bNum.find("1")
    exp += (-1 if exp > 0 else 0) + EXP

    mantis = bNum.replace(".", "").strip("0")[1:]
    mantis += "0"*(FLOAT_MANTIS_LEN - len(mantis))

    return sign + idec2bin(exp) + mantis

"""swap chars in string"""
def swapChars(string: str, ch1: str, ch2: str):
    return string.replace(ch1, "\0")\
                 .replace(ch2, ch1)\
                 .replace("\0", ch2)

def swapBits(string: str):
    return swapChars(string, "1", "0")

"""convert direct code of binary number to reverse code"""
def direct2reverse(number: str):
    number = alignStr(number)
    return number[0] + swapBits(number[1:])

"""convert direct code of binary number to extra code"""
def direct2extra(number: str):
    number = alignStr(number)
    return sum(number[0] + swapBits(number[1:]), "1")

def extra2direct(number: str):
    return direct2extra(alignStr(number))

##########################################

def alignStr(num: str):
    remainder = len(num) % 8
    if num == "":
        return "0"*8

    if remainder == 0:
        return num
    
    return num.rjust(len(num) + BYTE_LEN - remainder, "0")

def equalize(fst: str, snd: str):
    rem = len(fst) - len(snd)
    if rem == 0:
        return (fst, snd)

    if rem > 0:
        return (fst, ("0"*rem + snd))

    return (("0"*(-rem) + fst), snd)


"""
    sum two numbers(can be positive or negative)
    positive should be in direct codes
    negative should be in extra codes
"""
def sum(fst: str, snd: str):
    fst, snd = alignStr(fst), alignStr(snd)
    fstRev, sndRev = fst[::-1], snd[::-1]
    res, remainder = "", 0

    for i, j in zip(fstRev, sndRev):
        tmpSum = int(i) + remainder
        tmpDigit, remainder = tmpSum % 2, tmpSum // 2

        tmpSum = int(j) + tmpDigit
        newDigit = tmpSum % 2
        remainder += tmpSum // 2

        res += str(newDigit)

    return res[::-1]

def _getExp(number: str):
    return int(number[1:-FLOAT_MANTIS_LEN], 2)

def _getMantiss(number: str):
    return "1" + number[-FLOAT_MANTIS_LEN:]

def _toDegree(mAndExp: tuple[str, int], toDegree: int):
    offset = mAndExp[1] - toDegree
    if offset > 0:
        return (mAndExp[0] + "0"*offset, toDegree)
    elif offset < 0:
        return ("0"*abs(offset) + mAndExp[0][:offset], toDegree)
    
    return (mAndExp[0], toDegree)

def _2extraIfNegative(number: str):
    return direct2extra(number) if sign(number) else number

FLOAT_MANTIS_REMAINDER = 7
def fsum(fst: str, snd: str):
    mantissAndExp1 = (_getMantiss(fst), _getExp(fst))
    mantissAndExp2 = ( _getMantiss(snd), _getExp(snd))

    toExp = max(mantissAndExp1[1], mantissAndExp2[1])
    mantissAndExp1 = _toDegree(mantissAndExp1, toExp)
    mantissAndExp2 = _toDegree(mantissAndExp2, toExp)

    signedMantiss1 = _2extraIfNegative(str(sign(fst)) + "0"*FLOAT_MANTIS_REMAINDER + mantissAndExp1[0])
    signedMantiss2 = _2extraIfNegative(str(sign(snd)) + "0"*FLOAT_MANTIS_REMAINDER + mantissAndExp2[0])

    # extra2direct and direct2extra is equal functions
    # direct2extra(direct2extra(x)) == x
    mantisSum = _2extraIfNegative(sum(signedMantiss1, signedMantiss2)) 

    resultSign = str(sign(mantisSum))
    dExp = 7 - mantisSum[1:].find("1")
    resultExp = idec2bin(toExp + dExp + (-1 if dExp > 0 else 0))
    resultMantiss = mantisSum[1:].lstrip("0")[1:]

    return resultSign + \
           resultExp + \
           resultMantiss + \
           "0"*(FLOAT_MANTIS_LEN - len(resultMantiss))

##########################################

"""negate number in any code"""
def negate(number: str):
    number = alignStr(number)
    return ("1", "0")[int(number[0])] + number[1:]

"""
    subtract to numbers
    positive should be in direct codes
    negative should be in extra codes
"""
def subtract(fst: str, snd: str):
    return sum(fst, negate(direct2extra(snd)))

##########################################

def absolute(number: str):
    return "0" + alignStr(number)[1:]

"""
    return 1 if negative
    return 0 if positive
"""
def sign(number: str):
    return int(alignStr(number)[0])

"""multiply numbers"""
def multiply(fst: str, snd: str):
    fstRev, sndRev, _sign = _convertToCompatible(fst, snd)
    fstRev, sndRev = fstRev[::-1], sndRev[::-1]

    res, degreeOf10 = "0"*BYTE_LEN, 0

    for i in map(int, sndRev):
        tmpRes = ""
        for j in map(int, fstRev):
            tmpDigit = (i*j) % 2
            tmpRes += str(tmpDigit)

        res = sum(res[::-1], tmpRes[::-1]+"0"*degreeOf10)[::-1]
        degreeOf10 += 1

    return str(_sign) + alignStr(res)[::-1][1:]
    # 1 0 1
    # 0 1 0
    # 0 0 0

##################################################

"""
    return 1 if fst < snd
    return 0 if fst >= snd
"""
def less(fst: str, snd: str):
    return sign(subtract(fst, snd))

def _convertToCompatible(fst: str, snd: str):
    _sign = sign(fst) ^ sign(snd)

    if sign(snd):
        snd = absolute(extra2direct(snd))

    if sign(fst):
        fst = absolute(extra2direct(fst))

    return (fst, snd, _sign)


"""
    dividing two numbers
    positive should be in direct codes
    negative should be in extra codes
"""
def div(fst: str, snd: str, presicion: int = 5):
    quot, rem, presicionCounter = "0", "0", 0

    fst, snd, _sign = _convertToCompatible(fst, snd)

    while not less(fst, snd):
        quot = sum(quot, "1")
        fst = subtract(fst, snd)
    
    fst = multiply(fst, "10")
    remStr = ""
    while not sign(fst) and presicionCounter <= presicion: 
        if less(fst, snd):
            fst = multiply(fst, "10")
            presicionCounter += 1
            remStr += rem
            rem = "0"
            continue

        rem = sum(rem, "1").lstrip("0")
        fst = subtract(fst, snd)
    
    return str(_sign) + quot[1:] + "." + remStr

##################################################

def sumFloat(fst: str, snd: str):
    pass