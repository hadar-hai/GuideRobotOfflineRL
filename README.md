# GuideRobotOfflineRL

This project illustrates a scenario in which an agent, referred to as the guide robot, is tasked with guiding a visually impaired individual through a two-dimensional obstacle-filled map towards a goal. The guide robot is connected to the individual by a leash, and the goal is to safely navigate through obstacles while ensuring the individual's safety.

Overview
In this scenario, the guide robot possesses complete knowledge of the map layout, including obstacles and the location of the visually impaired individual, throughout all time-steps. The visually impaired individual, represented in blue, lacks visibility of the map details and can only perceive a directional signal aligned with the leash's direction, indicating the leash's maximum extension.

Scenario Description
The figure provided in the project repository (Figure \ref{fig:example_2d}) displays the agent represented in red and the visually impaired individual represented in blue. The agent's objective is to maneuver the individual through obstacles to reach the goal while ensuring they do not collide with any obstacles.

Unique Challenges
Limited Perception: The visually impaired individual can only perceive a directional signal aligned with the leash's direction, limiting their understanding of the environment.
Human-like Behavior: The visually impaired individual may act irrationally at times, influencing the situation unpredictably.
Dynamic Leash Interaction: If the leash reaches its maximum length and the individual moves in the opposite direction, they can pull the agent, presenting unique challenges for navigation.
Repository Contents
README.md: This file provides an overview of the project, scenario description, and unique challenges.
example_2d.png: Image depicting the scenario with the agent and visually impaired individual on a two-dimensional map.
Additional project files and code may be included as development progresses.
Usage
This project is primarily intended for research and educational purposes to explore the challenges and dynamics of guiding visually impaired individuals in complex environments.

Contributions
Contributions to this project are welcome. If you have any suggestions, improvements, or bug fixes, please feel free to submit a pull request or open an issue in the repository.

License
This project is licensed under the MIT License. You are free to use, modify, and distribute the code for any purpose. Please see the LICENSE file for more details.

Note: This project is a simulation and does not involve real-world interactions with visually impaired individuals. It is meant for educational and research purposes only.
