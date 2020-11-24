<div align="center">

<img src="wireframes/mockup.png" alt="Mockup on all Devices"/>
 
 </div>

# Table of contents
1. [Introduction](#introduction)
    * [Objective](#objective)
    * [User stories](#users)
    * [Wireframes](#wireframes)
    * [Design Notes](#design)
2. [UX](#design)
3. [Features](#features)
    * [Existing Features](#existing_feat)
    * [Features left to implment](#future_feat)
4. [Information Architecture](#models)
5. [Technologies Used](#technologies)
6. [Testing](#testing)
7. [Deployment](#deploying)
    * [Run Locally](#local)
    * [Deploy to Heroku](#heroku)
8. [Credits](#credits)
    * [Content](#content)
    * [Media](#media)
    * [Acknowledgements](#acknowledgements)

# Introduction <a name="introduction"></a>

## Objective <a name="strategy"></a>
+ To sell trips to outer space 


## User Stories <a name="users"></a>
"As a user, I would like to ___________"
+ View the different types of trips available
+ View individual trips in more detail
+ Book my place on a trip
+ Provide details of the number of passengers and passenger information
+ Review booking before placing it
+ Easily Enter Payment information
+ Feel my personal and payment information is secure
+ View my order confirmation after checkout
+ Receive a confirmation email after the checokout is complete
+ Modifiy my booking details
+ View my bookings


"As a buisness owner I would like to _________"
+ Add new trips and experiences
+ View the number of seats available for each trip



## Wireframes <a name="wireframes"></a>
<div align="center">

<img src="media/wireframes/home.png" alt="login view"/>
 
 </div>

 <div align="center">

<img src="media/wireframes/products_trips.png" alt="profile view"/>
 
 </div>

 <div align="center">

<img src="media/wireframes/detail.png" alt="detail view"/>
 
 </div>

## Design Notes <a name="design"></a>
### Typography
+ The fonts chosen for this project are <b>"Orbitron,"</b> <b>"Euphoria"</b> and <b>"."</b> from google fonts

<div align="center">

<img src="media/wireframes/colourpalette.png" alt="colors"/>
<img src="media/wireframes/colourpalette2nd.png" alt="colors"/>
 
 </div>

# Information Architecture <a name="models"></a>
## Models

***

<p>&nbsp;</p>

## Profile

<p>&nbsp;</p>

### Profile:

| Name           | Key in db              | Field Type          | Options                                      |
|:---------------|:-----------------------|:--------------------|:---------------------------------------------|
| User           | user                   | OneToOneField(User) | on_delete=CASCADE                            |
| Address 1      | default_address1       | CharField           | max_length=80, null=true, blank=True         |
| Address 2      | default_address2       | CharField           | max_length=80, null=true, blank=True         |        
| Postcode       | default_postcode       | CharField           | max_length=20, null=true, blank=True         |
| City           | default_town_or_city   | CharField           | max_length=40,  null=true, blank=True        |
| Country        | default_country        | CountryField        | blank_label="Country", null=true, blank=True |
| Medical Rating | default_medical_rating | IntegerField        | null=true, blank=True                        |

<p>&nbsp;</p>

* * *

<p>&nbsp;</ 

## Booking

<p>&nbsp;</p>

### Booking:

| Name              | Key in db      | Field Type              | Validation                                                  |
|:------------------|:---------------|:------------------------|:------------------------------------------------------------|
| Booking Reference | booking_ref    | CharField               | primary_key=True, max_length=20, null=False, editable=False |
| Trip              | trip           | ForeignKey(Trip)        | on_delete=SET_NULL, null=False, blank=False                 |
| User Profile      | user_profile   | ForeignKey(UserProfile) | on_delete=SET_NULL, null=True, blank=True                   |
| Booking Total     | booking_total  | DecimalField            | max_digits=10, decimal_places=2, null=False, default=0      |
| Stripe Payment ID | stripe_pid     | CharField               | max_length=254, null=False, blank=False default=""          |
| Full Name         | full_name      | TextField               | max_length=50, null=False, blank=False                      |
| Email             | email          | EmailField              | max_length=254, null=False, blank=False                     |

<p>&nbsp;</p>

### Passengers:

| Name               | Key in db          | Field Type             | Validation                                         |
|:-------------------|:-------------------|:-----------------------|:---------------------------------------------------|
| Booking            | booking            | ForeignKey(Booking)    | on_delete=CASCADE,                                 |
| First Name         | first_name         | CharField              | on_delete=SET_NULL, null=False, blank=False        |
| Last Name          | last_name          | CharField              | on_delete=SET_NULL, null=True, blank=True          |
| Email              | email              | EmailField             | max_length=254, null=False, blank=False            |
| Medical Assessment | medical_assessment | OneToOneField(Medical) | on_delete_CASCADE, null=True, blank=True           |
| Medical Rating     | medical_rating     | IntegerField           | max_digits=3, null=False, blank=False, default=0   |

<p>&nbsp;</p>

### Booking Line Items:

| Name       | Key in db  | Field Type             | Validation                                                              |
|:-----------|:-----------|:-----------------------|:------------------------------------------------------------------------|
| Booking    | booking    | ForeignKey(Booking)    | on_delete=SET_NULL, null=False, blank=False, on_delete=CASCADE          |
| Product    | product    | OneToOneField(Product) | on_delete=SET_NULL, null=False, blank=False, on_delete=CASCADE          |
| Quantity   | quantity   | IntegerField           | null=False, blank=False, default=0                                      |
| Line Total | line_total | DecimalField           | max_digits=7, decimal_places=2, null=False, blank=False, editable=False |

<p>&nbsp;</p>

* * *

<p>&nbsp;</p>

## Products

<p>&nbsp;</p>

### Product:

| Name            | Key in db     | Field Type           | Validation                                |
|:----------------|:--------------|:---------------------|:------------------------------------------|
| Category        | category      | ForeignKey(Category) | null=True, blank=True, on_delete=SET_NULL |
| Name            | name          | CharField            | max_length=254                            |
| Product ID      | product_id    | CharField            | max_length=254                            |
| Description     | description   | TextField            |                                           |
| Price           | price         | DecimalField         | max_digits=6, decimal_places=2            |
| Image           | image         | ImageField           | null=True, blank=True                     |
| Image URL       | image_url     | URLField             | max_length=1024, null=True, blank=True    |
| Image Thumbnail | image_thumb   | ImageField           | null=True, blank=True                     |

<p>&nbsp;</p>

### Category:

| Name          | Key in db     | Field Type | Validation                |
|:--------------|:--------------|:-----------|:--------------------------|
| Name          | name          | CharField  | max_length=75             |
| Friendly Name | friendly_name | CharField  | max_length=75, blank=True |

<p>&nbsp;</p>

### Destination (Product):

| Name                      | Key in db             | Field Type    | Validation    |
|:--------------------------|:----------------------|:--------------|:--------------|
| Maximum Passengers        | max_passengers        | IntegerField  | |
| Duration                  | duration              | CharField     | max_lenght=20 |
| Minimal Medical Threshold | min_medical_threshold | IntegerField  | blank=True    |

<p>&nbsp;</p>

### Add-On (Product):

| Name                      | Key in db             | Field Type   | Validation |
|:--------------------------|:----------------------|:-------------|:-----------|
| Minimal Medical Threshold | min_medical_threshold | IntegerField | |


<p>&nbsp;</p>

### Insurance (Product):

| Name          | Key in db     | Field Type | Validation                |
|:--------------|:--------------|:-----------|:--------------------------|
| Friendly Name | friendly_name | CharField  | max_length=75, blank=True |

<p>&nbsp;</p>

### Trip:

| Name            | Key in db       | Field Type              | Validation                                 |
|:----------------|:----------------|:------------------------|:-------------------------------------------|
| Destination     | destination     | ForeignKey(Destination) | null=True, blank=False, on_delete=SET_NULL |
| Date            | date            | DateField               |             |
| Seats Available | seats_available | IntergerField           | null=False, blank=False, editable=False    |

<p>&nbsp;</p>

***

<p>&nbsp;</p>

<div align="center">

<img src="media/wireframes/schema.png" alt="schema"/>
 
</div>

<p>&nbsp;</p>


# Deployment <a name="deploying"></a>

 ## Run Locally <a name="local"></a>

 > In order to run the project locally, you will need an IDE, PIP, Python (version 3) and Git installed.
You will need to set up a free account with Stripe and with AWS for a S3 bucket.

1. Visit the 2infinity repository on Github; [https://github.com/fdeboo/to-infinity](https://github.com/fdeboo/to-infinity) and click on ![Code](media/screenshots/clone.png) to clone or download it.

2. Either: 
    * Copy the web url. In the terminal of your IDE, change directory / `cd` to  where you want the project saved on your system.
    * Type `git clone` and paste in the copied web url to complete the command _(as below)_: 

            git clone https://github.com/fdeboo/to-infinity.git
    
    
    **_or_**

    * Click to **Download Zip** and save the folder somewhere on your local system
    * File > Open the project from within your IDE
    
3. Activate a virtual environment. For this, I recommend using the **pipenv** package which manages the virtualenv and automatically adds/removes packages to a Pipfile when they are un/installed.   
    * On MacOS, pipenv is installed simply by typing `brew install pipenv` in the Mac Terminal. You can read more about pipenv and its installation using other software [here](https://pypi.org/project/pipenv/). 


        > _NOTE: The Pipfile created by **pipenv** supersedes the requirements.txt_
    
    * Once pipenv insalled, activate it with the following command:

        <pre><code>pipenv shell</code></pre>

4. Install the project dependencies detailed in the Pipfile by typing  

        pipenv install

5. Set up a .env file in the project root and provide the folllowing environment variables: 

    >_Important! Make sure you set up a .gitignore file and list .env in it so that it is ignored in commits to GitHub_

        SECRET_KEY=your_secret_key
        STRIPE_PUBLIC_KEY=your_stripe_public_key
        STRIPE_SECRET_KEY=your_stripe_secret_key
        STRIPE_WH_SECRET=your_stripe_wh_secret
        DEVELOPMENT=True

    _*for guidance on where to obtain these values click [here](#guidance)_

6. If using VSCode, or else if necessary, restart the IDE and reactivate the virtual environment (as per step 3)

7. Migrate the admin panel models to create the database template:

        python3 manage.py migrate

9. Create a 'superuser' account for access to the django admin panel: 

        python3 manage.py createsuperuser

10. Finally, run the app locally with the following command:
    
        python3 manage.py runserver

 ## Deploying to Heroku <a name="heroku"></a>
> _NOTE: The Pipfile created by **pipenv** supersedes the requirements.txt and contains all information for the dependencies of the project. Therefore a requirements.txt is not necessary in this project._

1. Type the following command into the Terminal to create a Procfile:
        
        echo web: python app.py > Procfile

2. Change the contents of the Procfile to: 

        web: gunicorn 2infinity.wsgi:application
    
3. Login to Heroku and click **New** from your Personal dashboard to **Create a New App**.

4. Give the app a unique name and choose the relevant region.

5. In the dashboard for the newly created app, set the **Deployment Method** (found under **Deploy** tab) to Connect to Github.

6. Fill out your Github details and search for your repository. Click to connect.

7. Choose whether you want to deploy Automatically or Manually.

8. Navigate to **Resources** and search for _postgres_ in the Add-ons search bar. Choose **Heroku Postgres** from the dropdown.

9.  Make sure the 'Plan name' is set to **Hobby Dev - Free**

    ![Hobby_Dev - Free](media/screenshots/hobby_dev.png)

10. Navigate to **Settings** and click on **Reveal Config Vars**.

11. Ensure the following are set:

    _*for guidance on where to obtain these values click [here](#guidance)_

    ![Heroku Config Vars](media/screenshots/blurred_heroku_vars.png)
    
    <br>

    ***    

    ## Guidance

    <p>&nbsp;</p>

     AWS_ACCESS_KEY_ID: 
    
     + Create an account / Sign in to AWS and navigate to the **AWS Management Console**
     + Search for S3 in AWS Services and **Create a bucket**. Follow the AWS [documentation.](https://docs.aws.amazon.com/AmazonS3/latest/user-guide/create-configure-bucket.html)
     + Create a User via the IAM service provided by aws

    AWS_SECRET_ACCESS_KEY:

    + As above
    + copy the Secret Access Key

    DATABASE_URL _(for production)_    
    + This value is pre-populated by Heroku in the Config Vars. Alternatively, you can type `Heroku config` in the CLI

    EMAIL_HOST_USER: 
    + Your gmail account address
    
    EMAIL_HOST_PASS (steps are based on gmail server): 
    + Sign in to gmail and go to **Settings** > _See all settings_.  
    + Navigate to **Accounts &amp; Import** > **Other Google Account Settings.**
    + From the side menu, click on **Security** and follow the steps to turn on 2-Step Verification.
    + Click on **App Passwords**, choose 'Mail' from the first dropdown and 'other' from the second, giving it a reference i.e 'Django'

    SECRET_KEY:
    + Type `python3` in the terminal and then type `import secrets` and hit enter. Type `secrets.token_urlsafe(48)` to generate a secure randomized byte string containing 48 bytes.

    STRIPE_PUBLIC_KEY:
    + Create an account / Sign in to Stripe
    + From the side menu, click on **Developers** > **API Keys**
    + Copy the Publishable Key token

    STRIPE_SECRET_KEY:
    + As above
    + Copy the Secret Key token

    STRIPE_WH_SECRET:
    + As above
    + From the side menu, click on **Developers** > **Webhooks**
    + Click on button to '+ Add endpoint'.
    + Provide your endpoint url. If you are working locally, you may need to take these extra steps for a temporary url:
        - Install ngrok. (On MacOs, `brew install ngrok`)
        - Type `ngrok http  8000` in the terminal
        - Add the temporary server address to ALLOWED_HOSTS in the app settings eg. `[“9e96e1506ea8.ngrok.io”, “127.0.0.1”]`   

        <br>

        > Remember to append the path for the checkout to the end of the url, including the trailing '/':  `/checkout/wh/`    
        


    + Click the link alternative to **'receive all events'** in the 'Events to send' section and then 'Add endpoint'
    + Copy the Signing secret provided.

    USE_AWS:
    + Set this to True

    <p>&nbsp;</p>

    *** 


12. Migrate changes to the database models

13. Commit any changes to GitHub (master branch) and deploy to Heroku. If this is not set to happen automatically, click **Deploy** from Heroku dashboard and navigate to **Manual Deploy** at the bottom of the page. Select the master branch and click **Deploy Branch**. 

14. Once the build is complete, click on **Open app** to view the site.


# Bugs <a name="bugs"></a>
1.  Circular import issue.  

    **Cause:** I initially listed the 'Trip' model within the products app. I imported the 'Booking' model from the bookings app so that I could place an aggregate Query on the Booking objects and use the data returned to update the trip object. In the bookings app, I required the Trip model to be imported and used as a positional argument in a ForeignKey within the Booking model. This resulted in a circular import and caused an Import Error.

    **Solution:** There were a couple of solutions to this issue.  One option was to use lazy evaluation and pass products.Trip as a string in the ForeignKey, instead of just defining the model name. This would the alleviate the need to create an import. However, I did not want to use a lazy lookup so as to protect the performance. Instead, I reconsidered the arrangement of the models within the app and was able to solve the issue quite easily by moving the Trip model to the booking app and updating the imports as necessary.


# Credits
## Content
The flow of the form was inspired by [Kenmore Air](https://www.kenmoreair.com)
## Media
The majority of images used in this project were sourced from Pexels. Thanks to [Pixabay](https://www.pexels.com/@pixabay)
## Code
+ The [Try DJANGO Tutorial](https://www.youtube.com/watch?v=6oOHlcHkX2U&list=PLEsfXFp6DpzTD1BD1aWNxS2Ep06vIkaeW&index=23) youtube series _(Episode 23-28)_, by Coding Entrepreneurs helped me understand the advantages of Django Forms

+ [HTML5 Date Input With Django Forms](https://www.youtube.com/watch?v=I2-JYxnSiB0) by Pretty Printed

+ Stack overflow 
[For forms](https://stackoverflow.com/questions/34781524/django-populate-a-form-choicefield-field-from-a-queryset-and-relate-the-choice-b)