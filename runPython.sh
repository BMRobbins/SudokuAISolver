#!/bin/bash
echo "LCV MRV FC"
python3 bin/Main.pyc LCV MRV FC Boards
echo "NOR MRV LCV"
python3 bin/Main.pyc NOR MRV LCV Boards
echo "NOR MAD LCV"
python3 bin/Main.pyc NOR MAD LCV Boards
echo "FC MRV"
python3 bin/Main.pyc MRV FC Boards
echo "LCV FC"
python3 bin/Main.pyc LCV FC Boards
echo "NOR"
python3 bin/Main.pyc NOR Boards
echo "FC"
python3 bin/Main.pyc FC Boards
echo "NOR DEG LCV"
python3 bin/Main.pyc NOR DEG LCV Boards

