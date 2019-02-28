#!/bin/sh

# The name of the virtualenv util.
# May vary depending on the operating system.
VENV_UTIL='/usr/bin/virtualenv'

# The directory where virtual enviroment will be located.
VENV_NAME='lftable-venv'


#  The message is shown if no arguments where passed.
if [ -z $1 ]; then
	echo "Use this command with '-c' option to create virtualenv in the './$VENV_NAME' directory."
	echo "The virtualenv util (now it's '$VENV_UTIL') may be changed in the script."
	exit 0
fi


# Creating virtualenv.
if [ -d $VENV_NAME ]; then
	echo "The directory './$VENV_NAME' already exists. Exit."
	exit 0
fi

echo "Creating virtualenv in the '$VENV_NAME' directory."
echo "------------------------------------------------------\n"
$VENV_UTIL -p python3 $VENV_NAME 


# Installing needed packages.
$VENV_NAME/bin/pip3 install pytz python-telegram-bot

echo "\n-------------------------------------------------------"
echo "Done. Exit."



