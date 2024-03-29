# GuideRobotOfflineRL - Offline Reinforcement Learning-Based Human Guide Robot for Visually Impaired Navigation

## ! Project under development !

## Overview

This project illustrates a scenario in which an agent, referred to as the guide robot, is tasked with guiding a visually impaired individual through a two-dimensional obstacle-filled map towards a goal. The guide robot is connected to the individual by a leash, and the goal is to safely navigate through obstacles while ensuring the individual's safety.

## Scenario Description

In this scenario, the guide robot possesses complete knowledge of the map layout, including obstacles and the location of the visually impaired individual, throughout all time-steps. The visually impaired individual, represented in blue, lacks visibility of the map details and can only perceive a directional signal aligned with the leash's direction, indicating the leash's maximum extension.

## Unique Challenges

- **Limited Perception**: The visually impaired individual can only perceive a directional signal aligned with the leash's direction, limiting their understanding of the environment.
- **Human-like Behavior**: The visually impaired individual may act irrationally at times, influencing the situation unpredictably.

## Data Collection

Data collection in this project involves letting human players to play the interactive game a recording various parameters such as:
- Guide robot's positions and actions
- Visually impaired individual's positions and actions
- Obstacles positions
- Goal positions

A data collection human-human interaction game (a failed one):

<p align="center">
<img src="https://github.com/hadar-hai/GuideRobotOfflineRL/assets/64587231/d097fe0c-f899-40dd-8ff4-17ee6caf7300" width="800" alt="data_collection_2_players">
</p>

## Partners

- [Anushka Deshpande](https://github.com/Anna4142)
- [Gil Gur-Arieh](https://github.com/gilgurarieh)
- [Hadar Hai](https://github.com/hadar-hai)

## Project Supervisors

- [Prop. Sarah Keren](https://sarahk.cs.technion.ac.il/)
- [Or Rivlin](https://github.com/orrivlin)

## Repository Contents

- `README.md`: This file provides an overview of the project, scenario description, and unique challenges using offline RL.
- main.py
- Game.py
- continue!

## Usage

This project is primarily intended for research and educational purposes to explore the challenges and dynamics of guiding visually impaired individuals in complex environments.

## Contributions

Contributions to this project are welcome. If you have any suggestions, improvements, or bug fixes, please feel free to submit a pull request or open an issue in the repository.

## License



---
*Note: This project is a simulation and does not involve real-world interactions with visually impaired individuals. It is meant for educational and research purposes only.*

*The project was created as a part of course CS236006 of Computer Science faculty, Technion.*

