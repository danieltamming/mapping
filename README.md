# mapping
### Idea
Imagine Jack and Jill have plans to go to Bill's house. Jack has a vehicle and Jill does not. Jack and Jill agree that Jill will take the TTC (Toronto's public transit) to a place where it is convenient for Jack to pick Jill up. **What is the optimal pickup location**? 

What if Jack is willing to go out of his way in order to save Jill time? What if we decide Jill's time is twice as valuable as Jack's time, or vice versa? What if Jill is willing to walk a certain distance? How many times is Jill wishing to get off one bus (or subway or streetcar) and get onto another? We'd like to find the optimal meetup location given these (and possibly other) parameters. 

### Tasks
 - [x] Get google maps API key
 - [x] Download TTC route information
 - [x] Create graph of TTC routes
 - [ ] Create basic TTC navigation algorithm that tells users how to get from point A to point B
 - [ ] Create optimal meetup location finder that assumes Jill is willing to walk 1 minute between stops and Jack refuses to go out of his way
 - [ ] Introduce more parameters
 - [ ] Introduce time constraints based on TTC schedule. Prior to this it assumes that each bus/streetcar/subway arrives after a constant number of minutes, an unrealistic but greatly simplifying assumption. 

### Notes
 - These algorithms will only work within range of the TTC
 - Until the final step the time that a TTC unit takes to get from A to B is incorporated, but the time that a TTC unit takes to pick up an individual at a stop is assumed to be constant. 

### Getting Started
```
git clone https://github.com/danitamm/mapping.git
cd mapping
source setup.sh
python main.py
```
The _setup.sh_ file downloads the data and creates a virtual environment. 

### TODO
 - make google maps api key mandatory, write brief guide to securing one and storing it
 - add algorithm to find directions for driver and transit user to meet up while maintaining a low number of calls to the google maps api
 - add logic to the algorithm to allow user to add a weighting of how much to value the driver's vs the transit user's time, or minimize distance traveled by car

### Figures
![alt text](figures/Figure_1.png)
