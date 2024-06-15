#!/bin/bash




function build() {
  if [ -z ${back_branch} ]
  then
     back_branch="master"
  fi
  if [ -d "api-backend" ]
  then
    echo "already cloned"
  else
    git clone https://${username}:${password}@bitbucket.org/deviare/api-backend.git -b develop
  fi
}

while getopts "u:p:o:b:h" opt; do
  case ${opt} in
    u ) username=$OPTARG
      ;;
    p ) password=$OPTARG
      ;;
    o ) orch_branch=$OPTARG
      ;;
    b ) back_branch=$OPTARG
      ;;
    h ) echo "Usage:"
      echo "    Clones Backend/Orchestration code and builds docker image"
      echo "    $0 -u <username> -p <password> -o <orch_branch> -b <backend_branch> "
      echo "               username  : username of bit bucket repository"
      echo "               password : password of bit bucket repository"
      echo "               orch_branch  : python-cloud  Bit Bucket Branch"
      echo "               backend_branch  : criterioncloudez  Bit Bucket Branch"
      exit 0
      ;;
    \? ) echo "Invalid option: -$OPTARG"
      exit 1
      ;;
  esac
done

set -e

build

exit 0

