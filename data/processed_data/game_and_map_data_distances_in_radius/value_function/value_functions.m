clear all; close all; clc;

gamma = 0.95; %discount factor

dataset = 3;
games = 20;
for game = 0:1:games-1
    
    % Get file, and score vector
    filename = sprintf("../dataset_%d_game_%02d_distances_in_radius_data.csv",dataset,game);
    data = readtable(filename);
    N = height(data);
    
    rewards = zeros(N, 1);
    
    for row = 1:N
        reward = immediate_reward(data,row);
        rewards(row) = reward;
    end
    
    %% Calculate value functions using discounted rewards
    value_function = zeros(size(rewards));
    value_function(N) = rewards(N);
    
    for row = (N-1):-1:1 %go backwards
        value_function(row) = rewards(row) + gamma*value_function(row+1);
    end
    
    %% Save value functions to table and lable file
    value_func_table = array2table(value_function, 'VariableNames', {'value_function_label'});
    savefilename = sprintf("vf_label_dataset_%d_game_%02d.csv", dataset, game);
    writetable(value_func_table, savefilename)
end
%% Customized Immediate reward function
function reward = immediate_reward(data, step)
    % parameters
    no_obs = 50;
    w_score = 1;
    w_goal = 10;
    w_obs = 10;

    % Get immediate scores vector
    if step == 1
        % score = table2array(data(1,"reward"));
        score = 0; % initial score=200 is for human convenience
    else % immediate score and not total score
        score = table2array(data(step,"reward")) - table2array(data(step-1, "reward"));
    end
    
    % Get human distance to goal
    p2_dist_to_goal = table2array(data(step, "P2_to_goal_distance"));
    if p2_dist_to_goal < 10^(-5) % avoiding division by zero
        p2_dist_to_goal = 10^(-5);
    end

    % Get human distance from nearest obstacle
    obs_dists = zeros(1, no_obs);
    for obs_id = 0:1:(no_obs-1)
        column_name=sprintf("P2_to_obs_point_%d_distance", obs_id);
        obs_dists(obs_id+1) = table2array(data(step, column_name));
    end

    dist_to_nearest_obs = min(obs_dists);
    if dist_to_nearest_obs < 10^(-5)
        dist_to_nearest_obs = 10^(-5);
    end
    
    % Calculate reward
    reward = w_score*score + w_goal/p2_dist_to_goal + w_obs/dist_to_nearest_obs;
end