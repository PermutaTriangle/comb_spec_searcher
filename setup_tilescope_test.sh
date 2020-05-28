if [ -d .tilings ]
then
    cd .tilings
    git pull
    cd ..
else
    git clone --depth 1 https://github.com/PermutaTriangle/Tilings.git .tilings
fi
cd .tilings
./setup.py install
cd ..
