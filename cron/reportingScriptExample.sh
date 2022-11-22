echo "Some setting up"
#export AC1=YOUR_AC1
#export AC2=YOUR_AC2
#dpCode=YOUR_DATAPANE_CODE
myPython="/usr/local/bin/python3.9"
myPath="/home/ppe/z/zrozario/QT"
echo "Using python:"
echo $myPython
echo "Using path:"
echo $myPath

$myPython $myPath/Strips_stages/loopfile.py #> $myPath/Strips_stages/caveman.out
$myPython $myPath/Strips_UK_cluster/loopfile.py #> $myPath/Strips_UK_cluster/caveman.out
$myPython $myPath/Pixels_stages/loopfile.py
$myPython $myPath/Strips_trashed/loopfile.py
#$myPython $myPath/parameterComparison.py --file $myPath/testSpecComp.json --dataPaneCode $dpCode > $myPath/cronComp.out
#$myPython $myPath/testTypeDashboard.py --file $myPath/testSpecDashIV.json --dataPaneCode $dpCode > $myPath/cronDash.out
