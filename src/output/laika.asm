LD R0 #23
LD R1 #8
ADD.i R2 R0 R1
ST @23 R2

LD R0 #2.5
LD R1 #0
FL.i R1 R1
MUL.f R2 R0 R1
ST @print R2

ERROR

LD R0 #5
ST @x R0

LD R0 #10
LD R1 @x
MUL.i R2 R0 R1
ST @print R2

ERROR

LD R0 @x
LD R1 #5
FL.i R0 R0
FL.i R1 R1
NE.f R2 R0 R1
ST @print R2

LD R0 #2
LD R1 #5
ADD.i R2 R0 R1
ST @2 R2

LD R0 #0
LD R1 @x
LD R2 #0
LD R3 #4
MUL.i R4 R2 R3
ADD.i R5 R1 R4
ST R5 R0
LD R2 #1
LD R3 #4
MUL.i R4 R2 R3
ADD.i R5 R1 R4
ST R5 R0

LD R0 @x
LD R1 #1
LD R2 #4
MUL.i R3 R1 R2
ADD.i R4 R0 R3
LD R5 R4
ST @print R5

LD R0 @x
LD R1 #0
LD R2 #4
MUL.i R3 R1 R2
ADD.i R4 R0 R3
LD R5 R4
LD R6 @x
LD R7 #1
LD R8 #4
MUL.i R9 R7 R8
ADD.i R10 R6 R9
LD R11 R10
ADD.i R12 R5 R11
ST @print R12

ERROR

LD R0 @x
LD R1 #1
LD R2 #4
MUL.i R3 R1 R2
ADD.i R4 R0 R3
LD R5 #2
ST R4 R5

LD R0 @x
LD R1 #0
LD R2 #4
MUL.i R3 R1 R2
ADD.i R4 R0 R3
LD R5 R4
LD R6 #2
ADD.i R7 R5 R6
ST @print R7

LD R0 #3
LD R1 #2
ADD.i R2 R0 R1
ST @z R2

LD R0 #3
LD R1 #2
MUL.i R2 R0 R1
ST @d R2

LD R0 #3
LD R1 #2
DIV.i R2 R0 R1
ST @e R2

ERROR

LD R0 #2
ST @g R0

LD R0 #1
LD R1 #2
SUB.i R2 R0 R1
ST @print R2

