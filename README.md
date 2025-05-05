# Maxima Patent Retrieval Application

### Breakdown of the application

The purpose of the code within this repository is to create a "patents.html" file that displays information about Medtronics patents. This file is created by running the **visualize_patents.py**. 

However, the actual data that is used in the html file is gathered by two separate scripts. The first, **google_scraper.py** will create the **patent_family_set_status.json** file within the **patent_status_data** folder, with information on all of the patents listed within **patent_family_set.json**.

If you wish to get the latest available information on all of the patents that already exist in the repository, refer to the "**Updating existing patents**" section below.

If you wish to also get the newest patents created by Medtronic, you will need to update the **patent_family_set.json** file with the patent families of all included patents. One of the limitations of this repository currently is that it relies on having an API key for "The Lens" in order to retrieve full extended patent families. If you do not have this API key, unfortunately new patents will have to be manually added to the patent_family_set.json file. If you do have an API key, refer to the later section on how to do this.

We recommend checking out the European Patent Office's API service as a free alternative to The Lens.

### Use Instructions

#### Installations Required 

In order to run the following programs, you will need python version 3.13.2 or later. 

This program also uses selenium to run web scraping processes. While the newest versions of selenium should not require it, you may need to download a driver for your browser if the program cannot find your webdriver.

#### Installing Required Libraries

The required python libraries are the following:
- Selenium
```
pip install selenium
```
- Dotenv
```
pip install python-dotenv
```

A requirements.txt file is also provided if you wish to use it to install dependencies.

While dotenv is not strictly needed, it is used to keep track of the API key if The Lens is used.

#### Manually installing required libraries (Windows)

If you are having trouble installing dependencies, here are step by step instructions on how to create a virtual python environment and install the dependencies on Windows. 
##### 1. Create a virtual environment

Open terminal, navigate to the folder your code is in, and enter the following command:
``` 
py -m venv .venv 
```
This will create a virtual python environment with the name ".venv" within the directory of the project.

##### 2. Active the virtual environment
Now run the following command:
``` 
.venv\Scripts\activate
```
This will activate the environment and run your code within it. It should be done every time a new terminal is opened. You can tell that the environment is active because there will be a (.venv) at the beginning of the terminal
##### 3. Download dependencies
With the environment active, you can run the following to download dependencies. Refer to earlier for the dependencies that are needed, but in general you can do so by running:
```
pip install [package]
```

### Running the program
##### Updating pre-existing patents
If you wish to get the latest available information on all of the patents that already exist in the repository, run the **google_scraper.py** file and then the **visualize_patents.py** file.

This can be done by activating your virtual environment and running 
```
python .\google_scraper.py
```
Then, once the script has completed,
```
python .\visualize_patents.py
```

##### Getting new patent families
As mentioned previously, if there is no API access for The Lens, the patent_family_set.json must be updated manually by checking The Lens (or other database including extended patent families) and adding any new patents to the list.

If there is API access, there are four steps for updating the patent families:
1. Create a file within the repository named ".env", and add the following text to the file:
```
API_KEY=[insert API key here]
```
2. List patents that need to be retrieved in **input.txt**

3. Run the **patent_retrieval_Lens.py** script (Note: Be sure to clear previous data of patent data responses, including patent families, if updating the patent families)
```
python patent_retrieval_Lens.py
```
4. Run the **patent_family_retrieval_Lens.py** script
```
python patent_family_retrieval_Lens.py
```
After this completes, you can then follow the steps of "**Updating pre-existing patents**" to update the html file with the new patent data.
