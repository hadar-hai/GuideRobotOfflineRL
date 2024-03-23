Processed data for Guiding Robot Project!

contents:

1. 'game_data' -  has the modified game data files:
	a. miliseconds were artificially added to the timestamp using interpolation
	b. added column "elapsed time" to data - miliseconds since the game started
	c. final step score was manually added:
		(1) +10,000 if P2_reach_goal is true
		(2) -100,000 if P2_collide is true
		(3) 0 otherwise (if game was manually closed or crashed)
	d. added column "total score" to data - sum of both players score
	e. data rows where both players chose no action (4) were deleted to make the problem Markovian.

2. 'game_and_map_data' - has the entire map data added to every game_data row, for ease of use.

3. 'all_data_no_timestamp.csv' - one file containing all the data, with the following modifications:
	a. 'players_id' column was added - unique players_id for every set of human players.
	b. 'game_id' column was added - game_id for every game played by specific players.
	c. 'timestamp' was removed for technical reasons - it is the only column to not contain a number (and 'elapsed time' can replace it)