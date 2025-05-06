# gtp
Final project for evolutionary game theory.

======= USING THE PROGRAM =========

To run simulation, run the main.py program in terminal.
    - a GUI will be loaded with inputs for initial game state configurations
    - Select a game from the drop down menu then press "run" to start simulation

Learning Dynamics, Interaction Radius, Strategy Distribution, and Payoff Matrix can
be adjusted through GUI inputs. In order to apply changes the current simulation must
be stopped and reset to initial game state. All configurations must be applied before 
running the new simulation.

===== Documentation ======

The parent directory includes two programs and 2 folder:

        - main.py : program used to run the GUI and take user input
        - simulation.py : used to configure and run simulation
        - sim : contains class objects that are used to structure simulation
             -- agent.py : provides definitions of methods for agent objects
             -- dynamics.py : provides definitions of methods for learning dynamics
             -- game.py : provides definitions of methods for each game
        - results : saves metrics from previous simulations

This project was created in collaboration between Daniel Zhan, Eric Rothman, and Fabricio Rua.