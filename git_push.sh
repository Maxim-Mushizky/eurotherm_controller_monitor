# this macro performs all necessary git actions to push to remote of this repo
# only data that is needed is the commit name and branch name

#!/usr/bin/bash

git add .
git commit -m $1
git push -u origin $2 


