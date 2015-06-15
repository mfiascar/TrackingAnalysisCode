# setup ROOT
# check Root environment setup. Allow for external setup script.
if [ ! $ROOTSYS ]; then
  export CWD=$PWD
  cd /home/mfiascar/root/root
  source bin/thisroot.sh
  cd $CWD
fi

# check Root environment setup again
if [ ! $ROOTSYS ]; then
  echo "Warning: No valid Root environment (ROOTSYS) defined. Please do so first!"
  return
fi

if [ ! $LD_LIBRARY_PATH ]; then
  echo "Warning: so far you haven't setup your ROOT enviroment properly (no LD_LIBRARY_PATH)"
  return
fi

# put root & python stuff into PATH, LD_LIBRARY_PATH
export SPYROOT=$PWD
export PYTHONPATH=/usr/lib/python2.7/lib-dynload:${PYTHONPATH}
export PATH=$SPYROOT/bin:$ROOTSYS/bin:${PATH}
export LD_LIBRARY_PATH=$ROOTSYS/lib:$PYTHONDIR/lib:${LD_LIBRARY_PATH}
export PYTHONPATH=$SPYROOT/python:$ROOTSYS/lib/root:$PYTHONPATH


