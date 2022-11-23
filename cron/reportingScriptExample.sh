echo "Some setting up"

myPython="<path to>/python3.9"
myPath="<path to repo>/QT"
echo "Using python:"
echo $myPython
echo "Using path:"
echo $myPath

$myPython $myPath/Strips_stages/loopfile.py
$myPython $myPath/Strips_UK_cluster/loopfile.py
$myPython $myPath/Pixels_stages/loopfile.py
$myPython $myPath/Strips_trashed/loopfile.py

