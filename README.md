## Deskription:
***tg-lftable***: telegram bot which provides an easy way to get the law faculty's timetable (BSU).

http://t.me/lftable_bot

## Installation and launch:

1. Run **setup.sh**  file to create virtual enviroment and install dependencies from **requirements.txt**.  
Check if virtual eviroment was succesfully created (the 'venv' directory).

3. Create **'tokens.py'** file in **'src/'** directory.   
Place here your tokens as **'release'** and **'develop'** **python string variables**.

4. Run following commands to launch the bot:

   $ source /venv/bin/activate  
   $ python3 tg-lftable.py --mode **\<MODE\>**

   The mode can be either 'release' or 'develop'.  
   Use **'-\-help'** parameter to learn about other arguments.
