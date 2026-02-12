@echo off
echo Adding files...
"C:\Program Files\Git\cmd\git.exe" add .

echo Committing...
"C:\Program Files\Git\cmd\git.exe" commit -m "Initial commit of Student Grade Predictor"

echo Renaming branch...
"C:\Program Files\Git\cmd\git.exe" branch -M main

echo Adding remote...
"C:\Program Files\Git\cmd\git.exe" remote add origin https://github.com/99240041085-prog/Prediction.git || "C:\Program Files\Git\cmd\git.exe" remote set-url origin https://github.com/99240041085-prog/Prediction.git

echo Pushing to GitHub...
"C:\Program Files\Git\cmd\git.exe" push -u origin main

echo Done.
pause
