@echo off
setlocal enabledelayedexpansion

set /a target=%random% %% 100 + 1
set tries=0

:guess
set /p guess=Guess a number between 1 and 100:

:: Validate input is a number
echo %guess%| findstr /r "^[0-9][0-9]*$" >nul
if errorlevel 1 (
    echo Please enter a valid number.
    goto guess
)

set /a tries+=1

:: Now numeric compare
if %guess%==%target% (
    echo Correct! You guessed it in %tries% tries.
    goto end
) else (
    if %guess% lss %target% (
        echo Too low, try again.
    ) else (
        echo Too high, try again.
    )
    goto guess
)

:end
pause
