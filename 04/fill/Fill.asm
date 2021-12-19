// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
    @fill
    M=-1
    @is_white
    M=0
    @i
    M=0

(WAIT)
    @is_white
    D=M
    D=D-1
    D=-D
    M=D
    @WAIT_WHEN_WHITE
    D;JGT
    @WAIT_WHEN_BLACK
    0;JMP

(WAIT_WHEN_WHITE)
    @KBD
    D=M
    @PRESS
    D;JGT
    @WAIT_WHEN_WHITE
    0;JMP
(PRESS)
    @fill
    M=-1
    @INIT_I
    0;JMP

(WAIT_WHEN_BLACK)
    @KBD
    D=M
    @NO_PRESS
    D;JEQ
    @WAIT_WHEN_BLACK
    0;JMP
(NO_PRESS)
    @fill
    M=0

(INIT_I)
    @i
    M=0

(LOOP)
    @i
    D=M
    @32
    D=D-A
    @WAIT
    D;JGE

    @SCREEN
    D=A
    @i
    D=D+M
    @0
    M=D
    @fill
    D=M
    @0
    A=M
    M=D

    @i
    M=M+1
    @LOOP
    0;JMP

(END)
    @END
    0;JMP
