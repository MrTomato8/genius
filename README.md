### How to install
	
1. Clone the project

   ```
   git clone https://github.com/theimip/genius.git
   cd genius
   ```
   
2. Create virtualenv
	
	```
   virtualenv venv
   ```
   
3. Install project requirements
	
	```
   venv/bin/pip install -r gap/requirements.txt
  	```
  	
4. Syncdb & Migrate
	
	```
   venv/bin/python gap/manage.py syncdb
   venv/bin/python gap/manage.py migrate
   ```
   
5. Install GruntJS
	
	```
	npm install
	```
	
6. Build project staticfiles
	
	```
	grunt build
	```