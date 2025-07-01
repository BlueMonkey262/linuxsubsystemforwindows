@echo off
setlocal enabledelayedexpansion

set /a target=%random% %% 100 + 1
set tries=0

:guess
set /p guess=Guess a number between 1 and 100:
set /a tries+=1

if "!guess!"=="%target%" (
    echo Correct! You guessed it in !tries! tries.
    goto end
) else (
    if !guess! lss %target% (
        echo Too low, try again.
    ) else (
        echo Too high, try again.
    )
    goto guess
)

:end
pause
