
# RESEARCH PAPER INCLUDED IN REPO: CAML HSEF.PDF

Purpose:

More than 50% of diagnosed cancers are detected at a late stage, resulting in poor prognosis and high fatality rates (WHO, 2022). Current diagnostic methods necessitate in-person visits or specific test requests, leading to undetected cases until patients see the necessity when they experience health decline. Relatively few standard cancer screening protocols exist, and almost none of them are based on medication exposure history. Our solution, Cancer Assessment by Machine Learning (CAML), plans to revolutionize early detection by fixating on three silos of data: medications taken, associated relative risks, and associated cancers. Certain medications, such as Insulin, have an association with certain cancers, such as pancreatic cancer (De Souza et al., 2016). Other medications, such as tamoxifen, directly increase the risks of cancers due to their active ingredients, such as endometrial cancer (ACOG, 2006). Using an initial database from current research, CAML will leverage specific fields of Artificial Intelligence (AI) to map associations and identify patterns through decision tree regression methods. CAML’s accuracy is then evaluated through error, correlation, and variance calculations. By leveraging this new field in medicine, CAML is envisioned to become a critical tool for medical professionals, predicting relative cancer risks and revolutionizing the early detection of cancers while also adapting to new data.




How to Run:
1. Download Visual Studio Code
2. Download all the Required Extensions 
3. Run the program and open the link in the terminal

Required Extensions and terminal installs:
1. Python (install both the extension and from the official website)
   
2. SQLite
   
3. SQLite Viewer
   
4. SQL Tools

5.pandas (run "pip install pandas" in the terminal)

6.scikit-learn (run "pip install scikit-learn" in the terminal)

7.matplotlib (run "pip install matplotlib" in the terminal)

8.Flask (run "pip install Flask" in the terminal)

9.Flask-SQLAlchemy (run "pip install Flask-SQLAlchemy" in the terminal)

10.scipy (run "pip install scipy" in the terminal)


Description of each component:

1.app.py is the master conroller of the program --- TO RUN THE APP, RUN THIS PAGE IN TERMINAL ----- 
It controls the flow of the functions and other pages. 
It also chooses when to run the model and when to display different pages.

2. calculations.py is responsible for the creation of the translation of the initial_database/InitialDB.sql into a .db file.
 It also calcuates relative risk from collected data to expand upon the initial initial_database.

3. regression_model.py is responsible for control of the regression mode -- both training and testing.
 It also calculates the MSE and displays visuals/graphs in the static folder.

4. The instanace folder stores the collected dat in site.db and the translated initial database in relative_risk.db



QUESTION: 
CONTACT mohammad.rashid7337@gmail.com
