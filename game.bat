@echo off
setlocal

echo Guess the secret color!
echo Options: red, blue, green
set secret=blue

:guess
set /p guess=Enter your guess:

if /i "%guess%"=="%secret%" (
    echo Correct! You guessed the secret color.
    goto end
) else (
    echo Nope, try again.
    goto guess
)

:end
pause
