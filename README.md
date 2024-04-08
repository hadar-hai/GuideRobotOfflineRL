# GuideRobotOfflineRL - Offline Reinforcement Learning-Based Human Guide Robot for Visually Impaired Navigation


<div align="center">

<img src="https://github.com/hadar-hai/GuideRobotOfflineRL/assets/64587231/bc6c72ac-66ba-4f78-8a3e-af4bf0c8072f" width="300" height="200">

BC Agent Successes

</div>

<div align="center">

<img src="https://github.com/hadar-hai/GuideRobotOfflineRL/assets/64587231/892670e7-7b61-4be3-a594-733ea1613788" width="300" height="200">

Data Collection Game 

</div>


## Overview

This project presents a scenario where an agent, known as the guide robot, assists a visually impaired individual in navigating a two-dimensional obstacle-filled map towards a goal. The guide robot, connected to the individual by a leash, must safely navigate through obstacles while ensuring the individual's safety.

## Scenario Description for Data Collection Human-Human Interaction

In this scenario, the guide robot has complete knowledge of the map layout, including obstacles and the visually impaired individual's location, throughout all time-steps. The visually impaired individual lacks detailed visibility of the map and can only perceive a directional signal aligned with the leash's direction, indicating its maximum extension.

## Unique Challenges

- **Limited Perception**: The visually impaired individual's restricted understanding of the environment due to their reliance on the leash's directional signal.
- **Human-like Behavior**: Unpredictable actions from the visually impaired individual, akin to human behavior, adding complexity to the navigation task.

## Data Collection

Data collection involves human players interacting with the game, recording various parameters such as the guide robot's positions and actions, visually impaired individual's positions and actions, obstacles positions, and goal positions.

## AI Agents

The project aims to create a robust agent that learns from human demonstrations using Behavior Cloning (BC) as a baseline approach. It extends BC with Advantage-Filtered Behavioral Cloning (AFBC), a method that selectively replicates advantageous actions based on an estimated advantage function.

### Dataset

The data utilized for training was collected through human-human interactions in a designed environment. A total of 100 games were played, focusing on navigation tasks for visually impaired individuals.

### Pre-processing and Representation of Data

The collected data was pre-processed to fit the algorithm and model. Non-Markovian behavior was removed from the data to ensure consistency. Different representations of the state were explored, with the "Lidar"-like beam representation showing the best results.

### Setup

Three agents were tested: Baseline agent, Behavior Cloning (BC) agent, and Advantage-Filtered Behavior Cloning (AFBC) agent. Tests were conducted on maps with varying obstacles and initial player positions. Each agent played a total of 200 games.

### Results

Success rates for all three agents were recorded. In obstacle-free environments, the baseline agent showed higher success rates, while AFBC exhibited better performance overall, even in the presence of obstacles.

### Discussion

The results highlight the effectiveness of AFBC in navigation tasks, showcasing its ability to handle obstacles and adapt to varying environments. Both BC and AFBC agents occasionally exhibited "policy loops", leading to near-goal states but eventual failure.

## Partners

- [Anushka Deshpande](https://github.com/Anna4142)
- [Gil Gur-Arieh](https://github.com/gilgurarieh)
- [Hadar Hai](https://github.com/hadar-hai)

## Project Supervisors

- [Prof. Sarah Keren](https://sarahk.cs.technion.ac.il/)
- [Or Rivlin](https://github.com/orrivlin)

## Repository Contents

- `README.md`: Overview of the project, scenario description, and unique challenges using offline RL.
- `main.py`: Main script for executing the project.
- `Game.py`: Script containing the game logic.
- Continue!

## Usage

This project is designed for research and educational purposes, allowing exploration of the challenges and dynamics involved in guiding visually impaired individuals in complex environments.

## Contributions

Contributions to this project are encouraged. Feel free to submit pull requests or open issues for suggestions, improvements, or bug fixes.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

---
*Note: This project is a simulation and does not involve real-world interactions with visually impaired individuals. It is meant for educational and research purposes only.*

*The project was created as part of course CS236006 of the Computer Science faculty at Technion.*
